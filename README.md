\# Stock ETL API



Prueba técnica - Desarrollador Python Backend.



API REST que extrae datos históricos de acciones desde Yahoo Finance, los limpia y valida, los guarda en SQLite, y expone endpoints de consulta con analítica financiera.



\## Cómo correrlo



1\. Clonar el repositorio

2\. Crear entorno virtual .venv e instalar dependencias requirements.txt

3\. Levantar el servidor: `uvicorn main:app --reload`

4\. Abrir `http://127.0.0.1:8000/docs` para probar los endpoints desde Swagger UI



\## Formato de fechas



Todas las fechas se reciben en formato `YYYY-MM-DD` (ej: 2026-01-15), siguiendo el estándar ISO 8601. FastAPI lo valida, error 422 por si no se cumple.



\## Endpoints



\- `GET /health` - estado del servicio

\- `POST /etl/sync` - ejecuta el pipeline ETL para uno o varios tickers en un rango de fechas

\- `GET /stocks/{ticker}/history` - histórico de un ticker, con filtros opcionales de fecha y paginación

\- `GET /analytics/summary` - resumen financiero por cada ticker almacenado

\- `GET /analytics/movingaverage` - media móvil simple sobre el precio de cierre



\## Arquitectura



El proyecto separa responsabilidades en capas:



\- `routers/` - reciben las peticiones HTTP, no contienen lógica de negocio

\- `services/` - lógica de negocio: extracción, limpieza, validación, cálculos

\- `repositories/` - unica capa que habla directamente con SQLite

\- `models/` - definición de las tablas (Ticker, StockDailyPrice) y conexión a la base de datos

\- `tests/` - pruebas unitarias de transformación y extracción (con mocks, sin llamadas de red)



\## Idempotencia



El endpoint `/etl/sync` puede ejecutarse multiples veces con el mismo ticker y rango de fechas sin generar duplicados. Esto se logra con una restricción UNIQUE sobre (ticker, date) en la tabla StockDailyPrice, y un upsert (INSERT ... ON CONFLICT DO UPDATE) en el repository.



\## Tests



Correr con: pytest -v

Cubren la capa de transformación (forward-fill, validación de inconsistencias, calculo de retorno diario) y la capa de extracción (con mock de yfinance, sin llamadas de red reales).

