from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import obtener_sesion
from services.analytics_service import construir_resumen_analitico
from repositories.stock_repository import calcular_media_movil

router = APIRouter()


@router.get("/analytics/summary")
def resumen_analitico(db: Session = Depends(obtener_sesion)):
    return construir_resumen_analitico(db)


@router.get("/analytics/movingaverage")
def media_movil(ticker: str, window_size: int, db: Session = Depends(obtener_sesion)):
    if window_size <= 0:
        raise HTTPException(status_code=400, detail="window_size debe ser mayor a 0")

    resultado = calcular_media_movil(db, ticker, window_size)

    if resultado is None:
        raise HTTPException(status_code=404, detail=f"no hay datos guardados para el ticker {ticker}")

    return resultado