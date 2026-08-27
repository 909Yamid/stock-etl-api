from sqlalchemy.orm import Session
from repositories.stock_repository import (
    obtener_resumen_analitico,
    obtener_retorno_acumulado,
    calcular_volatilidad_anualizada,
)


def construir_resumen_analitico(db: Session):
    resultados = obtener_resumen_analitico(db)

    resumen = []
    for fila in resultados:
        retorno = obtener_retorno_acumulado(db, fila.ticker)
        volatilidad = calcular_volatilidad_anualizada(db, fila.ticker)
        resumen.append({
            "ticker": fila.ticker,
            "precio_minimo": fila.precio_minimo,
            "precio_maximo": fila.precio_maximo,
            "volumen_promedio": fila.volumen_promedio,
            "retorno_acumulado": retorno,
            "volatilidad_anualizada": volatilidad,
        })

    return resumen