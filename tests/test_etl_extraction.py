from unittest.mock import patch
import pandas as pd
from services.etl_service import extraer_datos_historicos


@patch("services.etl_service.yf.download")
def test_extraer_datos_no_llama_a_internet_real(mock_download):
    
    datos_falsos = pd.DataFrame({
        "Open": [100.0],
        "High": [105.0],
        "Low": [99.0],
        "Close": [102.0],
        "Volume": [1000],
    }, index=pd.to_datetime(["2026-01-01"]))
    mock_download.return_value = datos_falsos

    resultado = extraer_datos_historicos("AAPL", "2026-01-01", "2026-01-02")

    mock_download.assert_called_once()
    assert resultado["Close"].iloc[0] == 102.0


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from models.database import Base
from models import stock_models
from services.etl_service import ejecutar_pipeline_etl


def test_pipeline_etl_completo_extract_transform_load():
    
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SesionPrueba = sessionmaker(bind=engine)
    db = SesionPrueba()

    
    datos_falsos = pd.DataFrame({
        "Open": [100.0, 101.0, 100.0],
        "High": [105.0, 106.0, 90.0],
        "Low": [99.0, 100.0, 95.0],
        "Close": [102.0, None, 92.0],
        "Volume": [1000, 1100, 1000],
    }, index=pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"]))

    with patch("services.etl_service.yf.download", return_value=datos_falsos):
        resultado = ejecutar_pipeline_etl("AAPL", "2026-01-01", "2026-01-03", db)

    from models.stock_models import StockDailyPrice

    filas_en_bd = db.query(StockDailyPrice).filter(StockDailyPrice.ticker == "AAPL").all()


    assert resultado["filas_guardadas"] == 2  # dia 1 y dia 2 (relleno), dia 3 descartado
    assert len(filas_en_bd) == 2
    assert len(resultado["eventos_log"]) == 2  # 1 forward_fill + 1 fila_descartada