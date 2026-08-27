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