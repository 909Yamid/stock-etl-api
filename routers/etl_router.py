from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from models.database import obtener_sesion, SessionLocal
from services.etl_service import ejecutar_pipeline_etl
from datetime import date

router = APIRouter()


@router.post("/etl/sync")
def sincronizar(tickers: list[str], fecha_inicio: date, fecha_fin: date, db: Session = Depends(obtener_sesion)):
    if fecha_inicio > fecha_fin:
        raise HTTPException(status_code=400, detail="fecha_inicio no puede ser mayor que fecha_fin")

    resultado = {}
    for ticker in tickers:
        resultado[ticker.upper()] = ejecutar_pipeline_etl(ticker, str(fecha_inicio), str(fecha_fin), db)

    hubo_error = any("error" in r for r in resultado.values())
    if hubo_error and len(tickers) == 1:
        raise HTTPException(status_code=404, detail=f"no se encontraron datos para: {tickers[0]}")

    return resultado


def ejecutar_sync_en_segundo_plano(tickers: list[str], fecha_inicio: date, fecha_fin: date):
    db = SessionLocal()
    try:
        for ticker in tickers:
            ejecutar_pipeline_etl(ticker, str(fecha_inicio), str(fecha_fin), db)
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