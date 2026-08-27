from sqlalchemy import Column, Integer, String, Float, Date, UniqueConstraint
from models.database import Base

# Tablas

class Ticker(Base):
    __tablename__ = "tickers"

    symbol = Column(String, primary_key=True)  # ej: AAPL, MSFT
    nombre = Column(String, nullable=True)


class StockDailyPrice(Base):
    __tablename__ = "stock_daily_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    daily_return = Column(Float, nullable=True)  # No hay dato anterior al primer día


# Ticker+date no se puede repetir
    __table_args__ = (
        UniqueConstraint("ticker", "date", name="uix_ticker_date"),
    )