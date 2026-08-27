from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import obtener_sesion
from repositories.stock_repository import obtener_resumen_analitico, obtener_retorno_acumulado, calcular_volatilidad_anualizada

router = APIRouter()


@router.get("/analytics/summary")
def resumen_analitico(db: Session = Depends(obtener_sesion)):
    resultados = obtener_resumen_analitico(db)

    resumen = []
    for fila in resultados:
        retorno = obtener_retorno_acumulado(db, fila.ticker)
        volatilidad = calcular_volatilidad_anualizada(db, fila.ticker)
        resumen.append({
            "ticker": fila.ticker,
            "precio_minimo": fila.precio_minimo,
            "precio_maximo": fila.precio_maximo,
            "volumen_promedio": fila.volumen_promedio,
            "retorno_acumulado": retorno,
            "volatilidad_anualizada": volatilidad,
        })

    return resumen

from fastapi import HTTPException
from repositories.stock_repository import calcular_media_movil


@router.get("/analytics/movingaverage")
def media_movil(ticker: str, window_size: int, db: Session = Depends(obtener_sesion)):
    resultado = calcular_media_movil(db, ticker, window_size)

    if resultado is None:
        raise HTTPException(status_code=404, detail=f"no hay datos guardados para el ticker {ticker}")

    return resultado