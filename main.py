# Enrutador

from fastapi import FastAPI
from routers import health_router, etl_router, stocks_router, analytics_router

app = FastAPI(title="Stock ETL API")

app.include_router(health_router.router)
app.include_router(etl_router.router)
app.include_router(stocks_router.router)
app.include_router(analytics_router.router)

# Tablas

from models.database import Base, engine
from models import stock_models

Base.metadata.create_all(bind=engine)