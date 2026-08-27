# Stock ETL API

Prueba tecnica - Desarrollador Python Backend.

API REST que extrae datos historicos de acciones desde Yahoo Finance, los limpia y valida, los guarda en SQLite, y expone endpoints de consulta con analitica financiera.

## Como correrlo

1. Clonar el repositorio
2. Crear entorno virtual e instalar dependencias requirements.txt
3. Levantar el servidor: `uvicorn main:app --reload`
4. Abrir `http://127.0.0.1:8000/docs` para probar los endpoints desde Swagger UI

### Con Docker (alternativa)

1. `docker build -t stock-etl-api .`
2. `docker run -p 8000:8000 stock-etl-api`
3. Abrir `http://127.0.0.1:8000/docs`

## Formato de fechas

Todas las fechas se reciben en formato `YYYY-MM-DD` (ej: 2026-01-15), siguiendo el estandar ISO 8601. FastAPI valida automaticamente este formato y devuelve error 422 si no se cumple.

## Endpoints

- `GET /health` - estado del servicio
- `POST /etl/sync` - ejecuta el pipeline ETL para uno o varios tickers en un rango de fechas, espera a que termine y devuelve el detalle (filas guardadas, eventos de log)
- `POST /etl/sync-async` - version en segundo plano del sync: responde de inmediato y procesa en background (bonus de concurrencia)
- `GET /stocks/{ticker}/history` - historico de un ticker, con filtros opcionales de fecha y paginacion
- `GET /analytics/summary` - resumen financiero por cada ticker almacenado (min, max, volumen promedio, retorno acumulado, volatilidad anualizada)
- `GET /analytics/movingaverage` - media movil simple sobre el precio de cierre

## Arquitectura

El proyecto separa responsabilidades en capas:

- `routers/` - reciben las peticiones HTTP, no contienen logica de negocio
- `services/` - logica de negocio: extraccion, limpieza, validacion, calculos
- `repositories/` - unica capa que habla directamente con SQLite
- `models/` - definicion de las tablas (Ticker, StockDailyPrice) y conexion a la base de datos
- `tests/` - pruebas unitarias de transformacion y extraccion (con mocks, sin llamadas de red)

## Idempotencia

El endpoint `/etl/sync` puede ejecutarse multiples veces con el mismo ticker y rango de fechas sin generar duplicados. Esto se logra con una restriccion UNIQUE sobre (ticker, date) en la tabla StockDailyPrice, y un upsert (INSERT ... ON CONFLICT DO UPDATE) en el repository.

## Logs de anomalias

Cada fila descartada por inconsistencia matematica (Low > High, Volume negativo, precio <= 0) o rellenada por forward-fill queda registrada con ticker, fecha, tipo, campo y motivo, tanto en la respuesta de `/etl/sync` como en un archivo `etl_log.jsonl` que se genera en la raiz del proyecto.

## Tests

Correr con:

```
pytest -v
```

Cubren la capa de transformacion (forward-fill, validacion de inconsistencias, calculo de retorno diario, escritura de logs) y la capa de extraccion (con mock de yfinance, sin llamadas de red reales).

## Documentacion adicional

Las respuestas a la parte teorica de la prueba estan en `TEORIA.md`, en la raiz del repositorio.

## Bonus implementados

- Volatilidad historica anualizada en `/analytics/summary`
- Dockerfile funcional para levantar el microservicio
- Ejecucion asincrona de la sincronizacion via `/etl/sync-async` con BackgroundTasks