from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert
from models.stock_models import StockDailyPrice, Ticker
import pandas as pd


def guardar_ticker_si_no_existe(db: Session, ticker: str):
    existe = db.query(Ticker).filter(Ticker.symbol == ticker).first()
    if not existe:
        nuevo_ticker = Ticker(symbol=ticker)
        db.add(nuevo_ticker)
        db.commit()


def guardar_precios_diarios(db: Session, ticker: str, datos: pd.DataFrame):
    # datos limpio, daily_return calculado desde el service
    filas_guardadas = 0

    for fecha, fila in datos.iterrows():
        valores = {
            "ticker": ticker,
            "date": fecha.date(),
            "open": float(fila["Open"]),
            "high": float(fila["High"]),
            "low": float(fila["Low"]),
            "close": float(fila["Close"]),
            "volume": float(fila["Volume"]),
            "daily_return": None if pd.isna(fila["daily_return"]) else float(fila["daily_return"]),
        }

        # Upsert
        stmt = insert(StockDailyPrice).values(**valores)
        stmt = stmt.on_conflict_do_update(
            index_elements=["ticker", "date"],
            set_=valores,
        )
        db.execute(stmt)
        filas_guardadas += 1

    db.commit()
    return filas_guardadas

def obtener_historico(db: Session, ticker: str, start_date=None, end_date=None, limit: int = 100, offset: int = 0):
    query = db.query(StockDailyPrice).filter(StockDailyPrice.ticker == ticker.upper())

    if start_date:
        query = query.filter(StockDailyPrice.date >= start_date)
    if end_date:
        query = query.filter(StockDailyPrice.date <= end_date)

    query = query.order_by(StockDailyPrice.date)
    query = query.offset(offset).limit(limit)

    return query.all()

from sqlalchemy import func


def obtener_resumen_analitico(db: Session):
    resultados = (
        db.query(
            StockDailyPrice.ticker,
            func.min(StockDailyPrice.low).label("precio_minimo"),
            func.max(StockDailyPrice.high).label("precio_maximo"),
            func.avg(StockDailyPrice.volume).label("volumen_promedio"),
        )
        .group_by(StockDailyPrice.ticker)
        .all()
    )
    return resultados


def obtener_retorno_acumulado(db: Session, ticker: str):
    # el retorno acumulado se calcula con el primer y ultimo Close del periodo, no es una suma de los daily_return 
    primer_registro = (
        db.query(StockDailyPrice)
        .filter(StockDailyPrice.ticker == ticker)
        .order_by(StockDailyPrice.date.asc())
        .first()
    )
    ultimo_registro = (
        db.query(StockDailyPrice)
        .filter(StockDailyPrice.ticker == ticker)
        .order_by(StockDailyPrice.date.desc())
        .first()
    )

    if not primer_registro or not ultimo_registro:
        return None

    retorno_acumulado = (ultimo_registro.close - primer_registro.close) / primer_registro.close
    return retorno_acumulado

def calcular_media_movil(db: Session, ticker: str, window_size: int):
    registros = (
        db.query(StockDailyPrice)
        .filter(StockDailyPrice.ticker == ticker.upper())
        .order_by(StockDailyPrice.date.asc())
        .all()
    )

    if not registros:
        return None

    fechas = [r.date for r in registros]
    precios_cierre = [r.close for r in registros]

    serie = pd.Series(precios_cierre, index=fechas)
    sma = serie.rolling(window=window_size).mean()

    resultado = [
        {"date": str(fecha), "close": precio, "sma": None if pd.isna(valor_sma) else valor_sma}
        for fecha, precio, valor_sma in zip(fechas, precios_cierre, sma)
    ]
    return resultado


import math


def calcular_volatilidad_anualizada(db: Session, ticker: str):
    registros = (
        db.query(StockDailyPrice.daily_return)
        .filter(StockDailyPrice.ticker == ticker, StockDailyPrice.daily_return.isnot(None))
        .all()
    )

    retornos = [r[0] for r in registros]

    if len(retornos) < 2:
        return None

    serie = pd.Series(retornos)
    desviacion_diaria = serie.std()
    volatilidad_anualizada = desviacion_diaria * math.sqrt(252)

    return volatilidad_anualizada