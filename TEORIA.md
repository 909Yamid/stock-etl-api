\# Teoría



\## 1.1 Arquitectura y Principios de Diseño



\### a) Revisando mi propia implementación con mas cuidado, note que aunque separe la extraccion en una funcion propia (extraer_datos_historicos), el service sigue importando y llamando directamente a yf.download(...), entonces en realidad no hay una inversion de dependencias real, solo una organizacion mas limpia del codigo. El service todavia depende de la implementacion concreta de Yahoo Finance, no de una abstraccion.

Una aplicacion real de DIP seria definir una interfaz (un contrato) que el service conozca, sin importar la fuente concreta:

```python
from abc import ABC, abstractmethod

class ProveedorDeDatos(ABC):
    @abstractmethod
    def obtener_precios(self, ticker, fecha_inicio, fecha_fin):
        pass

class ProveedorYahooFinance(ProveedorDeDatos):
    def obtener_precios(self, ticker, fecha_inicio, fecha_fin):
        import yfinance as yf
        return yf.download(ticker, start=fecha_inicio, end=fecha_fin)

class ProveedorBaseDatos(ProveedorDeDatos):
    def obtener_precios(self, ticker, fecha_inicio, fecha_fin):
        # aqui consultaria una base de datos relacional en vez de una API externa
        pass

# el service recibe CUALQUIER proveedor que cumpla el contrato, sin saber cual es
def ejecutar_etl(proveedor: ProveedorDeDatos, ticker, fecha_inicio, fecha_fin):
    datos = proveedor.obtener_precios(ticker, fecha_inicio, fecha_fin)
    # la logica de limpieza y calculo no cambia sin importar el proveedor
```

Con esto, si mañana cambio de Yahoo Finance a otra fuente, o quiero leer de una base de datos en vez de una API, solo creo un nuevo ProveedorX que cumpla el contrato, sin tocar la logica de negocio. En mi implementacion actual de este proyecto, esto seria una mejora pendiente: el service (etl_service.py) todavia importa yfinance directamente, en vez de recibir un proveedor abstracto.

Ya habia aplicado una version mas simple de esta idea antes, sin llamarla DIP: en un bot de categorizacion que traduje de una macro VBA a Python, separe la funcion que categoriza transacciones de la funcion que lee el archivo de origen, para que la logica de categorizacion no dependiera del formato del banco.



\### b) Si mezclo la lógica de negocio (limpiar datos, calcular retornos, decidir si una fila es válida) dentro de las funciones que reciben peticiones HTTP, esto trae varios problemas concretos, no solo en teoría, sino que ya los viví en este mismo proyecto



Primero, no podría testear la lógica sin simular una petición HTTP completa. Acá pude testear limpiar\_y\_validar con datos inventados directamente en pytest, sin necesitar levantar el servidor ni pasar por FastAPI, entonces si esa lógica estuviera metida dentro del router, tendría que simular requests HTTP para probar algo tan simple como que una fila con Low mayor a High se descarta



Segundo, si en algún momento cambio de framework web, de FastAPI a Flask por ejemplo, tendría que reescribir también la lógica de negocio, porque quedaría atada a cómo FastAPI recibe los parámetros. Separado, solo cambio el router, y el service sigue funcionando igual. Y al final, mezclar responsabilidades hace el código más difícil de mantener, porque un cambio en una parte puede romper otra sin que sea obvio por qué



\## 1.2 Fundamentos de IA \& NLP



\### a) Un modelo discriminativo clasifica algo dado, eligiendo entre categorías que ya conoce. Un caso de uso sería el mismo bot de categorización que mencioné arriba: dado el texto o código de una transacción, decide si es "Transferencia", "Gtos Financieros", etc. También en proyectos académicos tomamos bases de datos dadas en .csv para determinar la viabilidad de préstamos



Un modelo generativo, en cambio, crea contenido nuevo que no existía antes, no elige entre opciones fijas. Como contexto, en otro desarrollo personal (una herramienta que armé para leer y responder preguntas sobre PDFs) uso Gemini para redactar respuestas en lenguaje natural a partir de esos documentos, entonces el modelo no está clasificando, está generando una respuesta original basada en lo que encuentra en el PDF



\### b) Un embedding es una forma de convertir texto, o cualquier dato, en una lista de números, de manera que textos con significado parecido terminen con números parecidos entre sí. Por ejemplo, "transferencia internacional" y "envío de dinero al exterior" tendrían embeddings cercanos, aunque no compartan las mismas palabras



El flujo de datos en un sistema de búsqueda semántica sería más o menos así: primero se convierten todos los documentos o registros a embeddings y se guardan, luego cuando alguien hace una búsqueda, su consulta también se convierte a un embedding, después el sistema busca qué embeddings guardados están más cerca matemáticamente del embedding de la consulta, y al final devuelve esos documentos, aunque no compartan texto exacto con la búsqueda



\### c) Fine-tuning es reentrenar un modelo con ejemplos específicos para que aprenda un patrón o comportamiento particular, mientras que RAG es dejar que el modelo busque información en documentos reales antes de responder, sin modificar el modelo en sí.



Recomendaría RAG cuando la fuente de verdad son documentos que ya existen y son confiables, por ejemplo normativa oficial en PDFs, porque es más rápido de implementar, más barato, y las respuestas se pueden verificar contra la fuente original. Retomando el mismo desarrollo de PDFs que mencioné antes, uso este enfoque ahí: el modelo busca en los PDFs de normativa antes de responder, en vez de inventar basado solo en lo que aprendió en su entrenamiento.



Recomendaría fine-tuning cuando necesito que el modelo aprenda un patrón de decisión muy específico y repetitivo, con muchos ejemplos históricos disponibles, por ejemplo si tuviera cientos de extractos ya categorizados manualmente y quisiera que un modelo aprenda exactamente mi criterio de categorización en vez de solo buscar información.

