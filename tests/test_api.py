from fastapi.testclient import TestClient
from main import app

cliente = TestClient(app)


def test_etl_sync_rechaza_fecha_invertida():
    respuesta = cliente.post(
        "/etl/sync?fecha_inicio=2026-01-15&fecha_fin=2026-01-01",
        json=["AAPL"],
    )
    assert respuesta.status_code == 400


def test_history_ticker_sin_datos_devuelve_404():
    respuesta = cliente.get("/stocks/ZZZZ/history")
    assert respuesta.status_code == 404