import pandas as pd
from services.etl_service import limpiar_y_validar, calcular_retorno_diario


def test_forward_fill_rellena_nulos():
    datos = pd.DataFrame({
        "Open": [100.0, 101.0],
        "High": [105.0, 106.0],
        "Low": [99.0, 100.0],
        "Close": [102.0, None],
        "Volume": [1000, 1100],
    }, index=pd.to_datetime(["2026-01-01", "2026-01-02"]))

    datos_limpios, log = limpiar_y_validar(datos, "AAPL")

    assert datos_limpios["Close"].iloc[1] == 102.0
    assert len(log) == 1
    assert log[0]["tipo"] == "forward_fill"


def test_descarta_fila_con_low_mayor_a_high():
    datos = pd.DataFrame({
        "Open": [100.0],
        "High": [90.0],
        "Low": [95.0],
        "Close": [92.0],
        "Volume": [1000],
    }, index=pd.to_datetime(["2026-01-01"]))

    datos_limpios, log = limpiar_y_validar(datos, "AAPL")

    assert len(datos_limpios) == 0
    assert log[0]["tipo"] == "fila_descartada"


def test_descarta_precio_negativo_o_cero():
    datos = pd.DataFrame({
        "Open": [100.0],
        "High": [105.0],
        "Low": [-5.0],
        "Close": [100.0],
        "Volume": [1000],
    }, index=pd.to_datetime(["2026-01-01"]))

    datos_limpios, log = limpiar_y_validar(datos, "AAPL")

    assert len(datos_limpios) == 0


def test_calcula_retorno_diario_correctamente():
    datos = pd.DataFrame({
        "Close": [100.0, 110.0],
    }, index=pd.to_datetime(["2026-01-01", "2026-01-02"]))

    resultado = calcular_retorno_diario(datos)

    assert abs(resultado["daily_return"].iloc[1] - 0.1) < 0.0001
    assert pd.isna(resultado["daily_return"].iloc[0])

from services.etl_service import guardar_log_en_archivo


def test_log_se_escribe_en_archivo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    log_eventos = [
        {"ticker": "PRUEBA", "fecha": "2026-01-01", "tipo": "fila_descartada", "campo": None, "motivo": "Low mayor que High"}
    ]

    guardar_log_en_archivo(log_eventos)

    archivo_generado = tmp_path / "etl_log.jsonl"
    assert archivo_generado.exists()

    contenido = archivo_generado.read_text(encoding="utf-8")
    assert "Low mayor que High" in contenido
    assert "PRUEBA" in contenido