import yfinance as yf
import pandas as pd
import json


from datetime import datetime, timedelta

def extraer_datos_historicos(ticker: str, fecha_inicio: str, fecha_fin: str):
    # Arquitectura, yfinance trata 'end' como exclusivo, sumamos 1 dia para que el rango que pide el usuario sea inclusivo de ambos extremos
    fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d") + timedelta(days=1)
    fecha_fin_ajustada = fecha_fin_dt.strftime("%Y-%m-%d")

    datos = yf.download(
        ticker,
        start=fecha_inicio,
        end=fecha_fin_ajustada,
        progress=False,
    )
    if isinstance(datos.columns, pd.MultiIndex):
        datos.columns = datos.columns.get_level_values(0)
    return datos


def limpiar_y_validar(datos: pd.DataFrame, ticker: str):
    # log descartes
    log_eventos = []

    if datos.empty:
        return datos, log_eventos

    columnas_clave = ["Open", "High", "Low", "Close", "Volume"]

    # PASO 1: forward-fill para nulos dentro de filas que si vinieron
    for columna in columnas_clave:
        nulos_antes = datos[columna].isna()
        if nulos_antes.any():
            for fecha_nula in datos.index[nulos_antes]:
                log_eventos.append({
                    "ticker": ticker,
                    "fecha": str(fecha_nula.date()),
                    "tipo": "forward_fill",
                    "campo": columna,
                    "motivo": "valor nulo, se relleno con el dato del dia anterior (dato provisional)",
                })
            datos[columna] = datos[columna].ffill()

    # inconsistencias matematicas
    filas_validas = []
    for fecha, fila in datos.iterrows():
        problema = None

        if fila["Low"] > fila["High"]:
            problema = "Low mayor que High"
        elif fila["Volume"] < 0:
            problema = "Volume negativo"
        elif fila["Open"] <= 0 or fila["High"] <= 0 or fila["Low"] <= 0 or fila["Close"] <= 0:
            problema = "precio menor o igual a cero"

        if problema:
            log_eventos.append({
                "ticker": ticker,
                "fecha": str(fecha.date()),
                "tipo": "fila_descartada",
                "campo": None,
                "motivo": problema,
            })
        else:
            filas_validas.append(fecha)

    datos_limpios = datos.loc[filas_validas]

    return datos_limpios, log_eventos

def guardar_log_en_archivo(log_eventos: list):
    if not log_eventos:
        return

    with open("etl_log.jsonl", "a", encoding="utf-8") as archivo:
        for evento in log_eventos:
            evento_con_fecha = dict(evento)
            evento_con_fecha["timestamp"] = datetime.now().isoformat()
            archivo.write(json.dumps(evento_con_fecha, ensure_ascii=False) + "\n")



def calcular_retorno_diario(datos: pd.DataFrame):
    # Daily Return = (Close_t - Close_t-1) / Close_t-1
    datos["daily_return"] = datos["Close"].pct_change()
    return datos


