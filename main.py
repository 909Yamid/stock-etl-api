from fastapi import FastAPI
from routers import health_router

app = FastAPI(title="Stock ETL API")

app.include_router(health_router.router)