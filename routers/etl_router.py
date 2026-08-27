from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from models.database import obtener_sesion
from services.etl_service import extraer_datos_historicos, limpiar_y_validar, guardar_log_en_archivo, calcular_retorno_diario
from repositories.stock_repository import guardar_ticker_si_no_existe, guardar_precios_diarios
from datetime import date

router = APIRouter()


@router.post("/etl/sync")
def sincronizar(tickers: list[str], fecha_inicio: date, fecha_fin: date, db: Session = Depends(obtener_sesion)):
    if fecha_inicio > fecha_fin:
        raise HTTPException(status_code=400, detail="fecha_inicio no puede ser mayor que fecha_fin")

    resultado = {}

    for ticker in tickers:
        ticker = ticker.upper()
        datos_crudos = extraer_datos_historicos(ticker, str(fecha_inicio), str(fecha_fin))

        if datos_crudos.empty:
            resultado[ticker] = {"error": "no se encontraron datos para ese ticker/rango"}
            continue

        datos_limpios, log_eventos = limpiar_y_validar(datos_crudos, ticker)
        guardar_log_en_archivo(log_eventos)
        datos_final = calcular_retorno_diario(datos_limpios)

        guardar_ticker_si_no_existe(db, ticker)
        filas_guardadas = guardar_precios_diarios(db, ticker, datos_final)

        resultado[ticker] = {
            "filas_guardadas": filas_guardadas,
            "eventos_log": log_eventos,
        }

    return resultado



def ejecutar_sync_en_segundo_plano(tickers: list[str], fecha_inicio: date, fecha_fin: date):
    # esta funcion corre en background, por eso abre su propia sesion de base de datos
    from models.database import SessionLocal
    db = SessionLocal()
    try:
        for ticker in tickers:
            ticker = ticker.upper()
            datos_crudos = extraer_datos_historicos(ticker, str(fecha_inicio), str(fecha_fin))

            if datos_crudos.empty:
                continue

            datos_limpios, log_eventos = limpiar_y_validar(datos_crudos, ticker)
            datos_final = calcular_retorno_diario(datos_limpios)

            guardar_ticker_si_no_existe(db, ticker)
            guardar_precios_diarios(db, ticker, datos_final)
    finally:
        db.close()


@router.post("/etl/sync-async")
def sincronizar_en_segundo_plano(
    tickers: list[str],
    fecha_inicio: date,
    fecha_fin: date,
    background_tasks: BackgroundTasks,
):
    if fecha_inicio > fecha_fin:
        raise HTTPException(status_code=400, detail="fecha_inicio no puede ser mayor que fecha_fin")

    background_tasks.add_task(ejecutar_sync_en_segundo_plano, tickers, fecha_inicio, fecha_fin)

    return {"mensaje": "sincronizacion iniciada en segundo plano", "tickers": tickers}