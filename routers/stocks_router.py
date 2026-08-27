from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from models.database import obtener_sesion
from repositories.stock_repository import obtener_historico

router = APIRouter()


@router.get("/stocks/{ticker}/history")
def obtener_historico_ticker(
    ticker: str,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(obtener_sesion),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date no puede ser mayor que end_date")

    resultados = obtener_historico(db, ticker, start_date, end_date, limit, offset)

    if not resultados:
        raise HTTPException(status_code=404, detail=f"no hay datos guardados para el ticker {ticker}")

    return [
        {
            "date": str(fila.date),
            "open": fila.open,
            "high": fila.high,
            "low": fila.low,
            "close": fila.close,
            "volume": fila.volume,
            "daily_return": fila.daily_return,
        }
        for fila in resultados
    ]