\# Teoría



\## 1.1 Arquitectura y Principios de Diseño



\### a) En este proyecto, la capa de service no sabe si los datos vienen de yfinance, de un CSV, o de otra fuente, la función extraer\_datos\_historicos recibe un ticker y fechas, y devuelve datos ya en un formato esperado, entonces si mañana Yahoo Finance cambia su forma de responder, o decido usar otra fuente de datos, solo tendría que cambiar esa función puntual, sin tocar la lógica de limpieza ni el repository que guarda en SQLite



En un desarrollo anterior (un bot que traduje de una macro VBA a Python, para categorizar transacciones de mvtos bancarios) ya apliqué esta misma separación en código real. La macro original detectaba comisiones bancarias por palabra clave ("comision") o por un monto fijo (19.43 USD), y llenaba automáticamente la categoría "Gtos Financieros". Al traducirlo a Python, separé la función de categorización de la función que lee o adecúa el archivo de origen:



```

def aplicar\_categorizacion(df: pd.DataFrame) -> pd.DataFrame:

&#x20;   """

&#x20;   Detecta comisiones por nombre o monto fijo y rellena

&#x20;   Categoria y Doc.Comp. con 'Gtos Financieros'.

&#x20;   """

&#x20;   if "Categoria" not in df.columns:

&#x20;       df\["Categoria"] = ""

&#x20;   if "Doc.Comp." not in df.columns:

&#x20;       df\["Doc.Comp."] = ""



&#x20;   for idx, fila in df.iterrows():

&#x20;       nombre\_txt = str(fila.get("Nombre", "")).lower().strip()

&#x20;       valor\_num = abs(float(str(fila.get("ValorUSD", 0)).replace(",", ".")))



&#x20;       es\_comision = (

&#x20;           "comision" in nombre\_txt or

&#x20;           abs(valor\_num - 19.43) < 0.01

&#x20;       )



&#x20;       if es\_comision:

&#x20;           df.at\[idx, "Categoria"] = "Gtos Financieros"

&#x20;           df.at\[idx, "Doc.Comp."] = "Gtos Financieros"



&#x20;   return df

```



Esta función no le importa si el DataFrame vino de un extracto de Bancolombia, BTG o Citi, ni cómo se leyó el archivo original, solo recibe una tabla ya normalizada y decide la categoría. Eso es lo mismo que busca el DIP: la lógica de negocio, en este caso categorizar, no depende de la fuente de datos, es decir, del banco o el formato del archivo. Y aplicando la misma idea a este proyecto de la prueba: si mañana necesito traer los precios desde otra fuente distinta a Yahoo Finance, solo tocaría la función de extracción, la lógica de limpieza y cálculo seguiría intacta



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

