# U2.5 · Bloque 27 / Lección 2 — Evaluar el flujo RAG con un conjunto de casos

**Fuente oficial:** Skillnest, «Evaluación de la recuperación: precisión y exhaustividad / Cómo evaluar si el flujo RAG recupera lo pertinente», recibido el **18/11/2026**. Requisito **«Ver»**. El ejemplo principal es Python estándar sin Chroma, Gemini ni credenciales.

**Estado previo:** U2.5 **10/15**, B27/L1 completada; entrega institucional de B26/L3 aún no confirmada.

## 1. Qué indica el curso

La precisión y el recall para una sola pregunta no permiten detectar si un cambio perjudicó otros casos. Se necesitan **varias preguntas representativas** y, **antes de consultar al retriever**, una lista de los IDs relevantes etiquetados por una persona leyendo los documentos. Un chunk se considera relevante cuando por sí solo responde toda la pregunta o una parte central, **no** por compartir palabras. Puede haber múltiples relevantes o ninguno.

El curso propone cuatro casos para practicar y sugiere aproximadamente **15–30 preguntas** para un dataset más útil en un corpus propio (orientación, no requisito formal de esta lección):

| Pregunta | Chunk relevante |
| --- | --- |
| que hace el cliente si una llamada tarda demasiado | doc0 |
| que pasa si la clave de api es invalida | doc1 |
| como se calcula el costo de una llamada | doc2 |
| como decide el agente que herramienta usar | doc3 |

Las listas recuperadas son **simuladas**, no salidas del índice real:

| Caso | Top-3 simulado | Precisión@3 | Recall@3 |
| --- | --- | ---: | ---: |
| Demora | doc0, doc4, doc2 | 0.333 | 1.0 |
| API inválida | doc2, doc4, doc3 | 0.000 | 0.0 |
| Costo | doc2, doc0, doc4 | 0.333 | 1.0 |
| Elección de herramienta | doc4, doc3, doc1 | 0.333 | 1.0 |

**Resultado oficial:** precisión promedio **0.25**, recall promedio **0.75**. El caso de clave API inválida da **P=0, R=0**, porque el relevante doc1 no aparece. El análisis por pregunta permite hallar ese fallo, que un promedio solo ocultaría.

## 2. Cambio importante de B27/L1 a B27/L2

En esta lección Skillnest **redefine** las funciones para manejar casos no evaluables:

- `precision_at_k([], {"doc0"})` devuelve **0.0**, sin división por cero.
- `recall_at_k(["doc0"], set())` devuelve **None**, porque no hay ningún relevante para recuperar.
- `promediar` **excluye None** y devuelve 0.0 si no queda ningún valor.
- El promedio de precisión sí cuenta los casos sin relevantes con P=0 si trae documentos. **Abstención del generador** no queda medida por esta métrica; requiere evaluación adicional.

B27/L1 trabajaba con una sola consulta y denominadores no vacíos; las diferencias de comportamiento son **parte del material oficial**, no un error que deba corregirse en el archivo anterior.

## 3. Implementación versionada

**Código:** [evaluacion_rag.py](../evaluacion_rag.py)  
**Tests:** [tests/test_evaluacion_rag_b27.py](../tests/test_evaluacion_rag_b27.py)

El CLI implementa las cuatro preguntas, las cuatro listas simuladas, promedios y casos borde del curso. La función `evaluar_recuperacion(retriever, casos, k=3)` queda disponible para recibir documentos `Document.id`, pero **no se invoca con un retriever real en la demostración principal**.

**Ampliaciones nuestras:** 18 pruebas offline, validación del formato set[str] de etiquetas y k positivo, y rechazo de IDs recuperados ausentes o duplicados para no interpretar como cero un desajuste con el índice. No se añaden dependencias.

### PowerShell

~~~powershell
git status --short
git pull --ff-only

python evaluacion_rag.py
python -m unittest discover -s tests -p "test_evaluacion_rag_b27.py" -v

git status --short
~~~

La salida esperada termina con:

~~~text
precision promedio: 0.25
recall promedio: 0.75

0.0
None
~~~

No ejecutar `indexar_corpus.py` ni reconstruir `vectorstore/`.

## 4. Qué NO se ha medido de Booking Core AI

El índice propio B24/L3 contiene **10 chunks en cinco archivos académicos**, con IDs SHA-256. **No** tienen IDs `doc0` a `doc4`. Por ello los promedios **0.25 / 0.75** del curso **no representan** el rendimiento real de Booking Core AI.

B27/L3 anuncia evaluación contra el recuperador real: (1) inspeccionar los IDs originales de esos 10 chunks; (2) **etiquetar manualmente la relevancia antes** de observar las recuperaciones; (3) comprobar que los `Document.id` devueltos coincidan exactamente con los IDs etiquetados; y (4) calcular métricas por caso y agregadas. No reindexar únicamente para forzar IDs como `doc0`. No inferir etiquetas de la distancia vectorial o del modelo de lenguaje.

## 5. Seguimiento

La lección «Ver» puede darse por estudiada tras comprobar la ejecución offline, sin entrega institucional exigida. Tras CI satisfactoria: **B27 2/3, U2.5 11/15**. La reproducción Windows sería evidencia adicional; se conserva el PR #26 como **borrador sin merge**, y la entrega B26/L3 en Skillnest sigue sin confirmarse. Tiempo efectivo de estudio: no informado.

**Siguiente punto exacto:** B27/L3 «La recuperación de tu flujo RAG»; aguardar consigna oficial antes de fabricar etiquetas o generar resultados con Gemini.
