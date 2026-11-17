# U2.5 · Bloque 27 / Lección 1 — Precisión, exhaustividad y F1

**Fuente principal:** Skillnest «Evaluación de la recuperación: precisión y exhaustividad (Bloque 27) / ¿Tu RAG recupera bien? Precisión y exhaustividad, medidas», compartida el **17/11/2026**. Requisito oficial: **«Ver»**. Se ejecuta con Python estándar, sin Chroma, Gemini ni credenciales.

**Estado previo:** U2.5 **9/15**, Bloques 24, 25 y 26 completados técnicamente; la entrega institucional de B26/L3 todavía no está confirmada.

## 1. Lo que enseña el curso

- **precision@k** = aciertos relevantes entre los k recuperados / número de recuperados. Pregunta: ¿cuánto de lo recuperado sirve?
- **recall@k (exhaustividad)** = aciertos relevantes recuperados / número total de IDs relevantes. Pregunta: ¿qué parte de lo necesario recuperamos?
- **F1** = 2 × precisión × recall / (precisión + recall). Si P=R=0, se define F1=0.

El curso usa un corpus fijo de **cinco textos** y la pregunta «que hace el cliente si una llamada tarda demasiado?». Etiquetado humano: solo **doc0**, sobre TimeoutError, es relevante. Se publican dos listas:

~~~python
ids_relevantes = {"doc0"}
ids_recuperados = ["doc2", "doc0", "doc4"]
ranked = ["doc2", "doc4", "doc0", "doc1", "doc3"]
~~~

La primera lista de recuperados se usa para calcular precision@3 = **1/3** y recall@3 = **1**. La lista ranked es el ranking fijo para experimentar con k. **El top-3 contiene los mismos IDs en diferente orden**: estas métricas cuentan pertenencia al top-k, no la posición exacta de cada documento relevante.

## 2. Tabla oficial con el ranking fijo

| k | IDs recuperados | Precisión | Recall | F1 |
| ---: | --- | ---: | ---: | ---: |
| 1 | doc2 | 0.000 | 0.000 | 0.000 |
| 2 | doc2, doc4 | 0.000 | 0.000 | 0.000 |
| 3 | doc2, doc4, doc0 | 0.333 | 1.000 | 0.500 |
| 4 | doc2, doc4, doc0, doc1 | 0.250 | 1.000 | 0.400 |
| 5 | doc2, doc4, doc0, doc1, doc3 | 0.200 | 1.000 | 0.333 |

Con este ranking, **F1 máximo = 0.500 en k=3**: la primera vez que aparece el único chunk relevante. El recall deja de mejorar y agregar fragmentos irrelevantes perjudica la precisión. En general, recall@k no disminuye con k cuando el ranking y las etiquetas son fijos; **precisión@k puede subir o bajar** dependiendo de si los nuevos fragmentos son relevantes.

Recall bajo impide que el generador encuentre/cite contenido fundamental; precisión baja introduce ruido en el prompt.

## 3. Implementación GitHub

**Código:** [metricas_recuperacion.py](../metricas_recuperacion.py)  
**Pruebas:** [tests/test_metricas_recuperacion_b27.py](../tests/test_metricas_recuperacion_b27.py)

El script reproduce los cinco textos, los IDs, las tres fórmulas y los números de la lección. La función adicional evaluar_ranking evita repetir el bucle y devuelve la tabla. **Ampliaciones propias**: los datos se validan para rechazar listas vacías de recuperados, conjuntos vacíos de relevantes e IDs duplicados, mediante ValueError explícito; la lección original supone datos válidos y advierte sobre división por cero para relevantes vacíos. Se mantienen las fórmulas, sin inventar métricas nuevas.

La suite consta de **15 pruebas offline**: fidelidad al corpus, precision/recall@3, tablas oficiales para k=1..5, F1, máximo en k=3, relevancia con varios positivos, diferencias de orden, resultados sin aciertos, parámetros inválidos, IDs duplicados y reproducción CLI sin API.

### Windows (PowerShell)

~~~powershell
git status --short
git pull --ff-only
python --version
python metricas_recuperacion.py
python -m unittest discover -s tests -p "test_metricas_recuperacion_b27.py" -v
git status --short
~~~

No ejecutar scripts de indexación: los números son resultados de un **ranking ilustrativo fijado por Skillnest**, no de una recuperación real de Gemini. Las pruebas se ejecutan en el job general de GitHub Actions por ser Python puro y sin nuevas dependencias.

## 4. Relación con nuestro corpus real de Booking Core AI

En B24/L3 indexamos **cinco archivos pero diez chunks**, con IDs SHA-256 de fuente e índice ordinal, más metadatos de origen. **Los IDs doc0...doc4 del ejemplo NO corresponden a esos IDs reales.** En B26/L3 sí probamos recuperación Gemini y citas, pero no teníamos etiquetas de relevancia suficientes para evaluar precisión/recall de forma sistemática.

Para medir nuestro retriever real necesitaremos un conjunto de preguntas, etiquetas humanas a **nivel de ID de chunk**, la lista ordenada de IDs devuelta por Chroma y una política para casos sin documentos relevantes. No inferir relevancia de la distancia vectorial ni equiparar nombre de archivo a ID de chunk sin definir antes la unidad de evaluación.

**Próxima lección anunciada por Skillnest:** Bloque 27/L2 «Cómo evaluar si el flujo RAG recupera lo pertinente»; plantea un dataset de evaluación con varias preguntas y sus chunks relevantes etiquetados. No fabricar etiquetas o resultados antes de recibir el material.

## 5. Seguimiento

**Lección B27/L1 de tipo «Ver» completada mediante estudio y prueba offline.** [GitHub Actions #44136512566](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/44136512566) terminó con ambos jobs PASS. Se ejecutaron y aprobaron **15/15 tests específicos B27/L1** dentro del job general; la ejecución independiente del script imprimió **precision@3: 0.3333333333333333**, **recall@3: 1.0**, **k=3: F1=0.500** y **k=5: F1=0.333**. Se mantienen **B27 1/3 y U2.5 10/15**. La reproducción en Windows es opcional y no consta calificación institucional de esta lección «Ver». La entrega/calificación B26/L3 en Skillnest permanece independiente y sin confirmar. Tiempo efectivo de estudio, inicio y término: no informados.
