# U2.5 · Bloque 26 / Lección 1 — Buscar por significado, no por palabra

**Fuente principal:** material oficial Skillnest «Recuperación semántica y prompt dinámico con fuente citada (Bloque 26) / Buscar por significado, no por palabra: recuperación semántica», compartido el 14/11/2026 (Chile).

**Situación previa:** B24 **3/3** y B25 **3/3**. El índice B25/L1 contiene **3 chunks reales** sobre reintentos, costos y pruebas unitarias, generados con models/gemini-embedding-001. En Skillnest B26/L1 es una lección de tipo **«Ver»**; la implementación reproducible es una extensión académica, no una entrega requerida.

## 1. Lo que explica Skillnest

Después de **indexar** viene **recuperar**: el embedding de la pregunta se compara con vectores previamente persistidos para buscar los fragmentos relacionados por significado. Ejemplo:

- Pregunta: «¿Qué pasa si mi conexión tarda demasiado?»
- Texto relevante: «El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente».
- La recuperación semántica puede relacionarlos aunque no compartan las mismas palabras.

| Interfaz oficial | Devuelve | Uso |
| --- | --- | --- |
| similarity_search(pregunta, k=3) | Lista de Document ordenados, con page_content y metadata | Recuperar textos |
| similarity_search_with_score(pregunta, k=3) | Pares (Document, distancia) | Inspeccionar cercanía |
| as_retriever(search_kwargs={"k": 2}).invoke(pregunta) | Document mediante interfaz invoke | Componer una cadena RAG |

**Importante:** para similarity_search_with_score, Chroma devuelve **distancias**; **menor distancia = mayor cercanía**. No es porcentaje de similitud. La configuración por defecto suele representar distancia euclidiana al cuadrado; no asumir un umbral absoluto para otros modelos o índices. Si pedimos k=10 y solo existen 3 chunks, Chroma devuelve como máximo 3. Una colección vacía puede producir [] sin excepción.

## 2. Prueba del curso con embeddings ficticios, sin red

La lección proporciona cinco documentos sobre TimeoutError, errores de autenticación, costos totalTokenCount, agentes U2.4 y tests con mocks. Los metadatos de ejemplo son fuente=doc0.md hasta fuente=doc4.md.

DeterministicFakeEmbedding(size=16) produce vectores deterministas **sin significado semántico**, solo para probar la mecánica (API, k, metadatos, distancias e interfaz Retriever). El curso muestra que el documento de costos puede quedar antes del documento sobre TimeoutError en la pregunta de demoras. **No es un fallo de Chroma ni una evaluación semántica válida.** Los números ilustrativos del curso tampoco deben exigirse literalmente en diferentes versiones de librerías.

Nuestro ejemplo mantiene una colección **efímera y única por ejecución**, aislada de índices persistidos, en lugar de reutilizar nombres de colección y arriesgar «colecciones fantasma».

## 3. Implementación y ejecución

**Código:** [src/recuperacion_semantica_b26.py](../src/recuperacion_semantica_b26.py).  
**Pruebas:** [tests/test_recuperacion_semantica_b26.py](../tests/test_recuperacion_semantica_b26.py).

El script usa dos vías. Fake recrea el corpus oficial de 5 documentos con embeddings sin API. Real **reabre** el índice existente B25/L1 (.local/chroma_b25_receta/, colección receta_b25_ejemplo), comprobando antes el manifiesto, los IDs y los 3 chunks, y calcula **solo el embedding de la pregunta** con Gemini. No inserta ni actualiza ningún documento.

En PowerShell, desde la raíz con .venv activo:

~~~powershell
git status --short
git pull --ff-only

# Obligatorio antes de gastar cuota: demo y pruebas sin Gemini
python -m src.recuperacion_semantica_b26 --modo fake
python -m unittest discover -s tests -p "test_recuperacion_semantica_b26.py" -v

# Recuperación semántica real en índice preexistente; una consulta Gemini
python -m src.recuperacion_semantica_b26 --modo real

# Opcionales: otras interfaces que hacen otra consulta al proveedor
python -m src.recuperacion_semantica_b26 --modo real-search
python -m src.recuperacion_semantica_b26 --modo real-retriever

git status --short
~~~

Opciones: --pregunta "texto" y --k 2. Una pregunta vacía y un k no positivo son inválidos.

**Modos:** fake demuestra las tres APIs sin Gemini; real usa similarity_search_with_score en B25/L1; real-search usa similarity_search; real-retriever utiliza as_retriever(...).invoke(...). Cada ejecución REAL usa cuota para generar el embedding de consulta; ninguna requiere reindexar documentos.

## 4. Criterios técnicos y límites

La suite offline confirma: el corpus oficial, k=3 con 3 Document y metadatos, distancias numéricas y ascendentes, retriever.invoke con k=2, k mayor al número de documentos, parámetros inválidos, protección contra crear silenciosamente un índice real ausente y CLI sin credenciales.

**CI con fake no confirma calidad semántica.** Para interpretar el orden real debemos revisar la salida Windows del modo real. La hipótesis es que la pregunta sobre demoras acerque el documento de TimeoutError: podría ser primero, pero **no se da por hecho**. Con k=3 sobre un corpus de solo 3 documentos, recuperaremos todos: lo que importa será su orden y las distancias. No mezclar los embeddings fake de 16 dimensiones y Gemini real (3072 dimensiones observadas en B24) en la misma colección.

**Aplicación conceptual a Booking Core:** recuperar documentación estática con metadata.fuente es útil para fundamentar respuestas RAG, pero todavía no genera respuestas ni citas verificables. Horarios y reservas son datos transaccionales y requerirán APIs autorizadas, fuera de este laboratorio ficticio.

**Evidencia CI validada:** [GitHub Actions #43553593077](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43553593077), ambos jobs exitosos: **9/9 B26/L1 OK** (`Ran 9 tests in 2.403s`) y regresiones **27/27 B24, 7/7 B25/L1, 11/11 B25/L2, 8/8 B25/L3**. Las 9 pruebas se ejecutaron con el paquete Chroma instalado en el job RAG, todas offline. La demo `--modo fake` también corrió sin Gemini. **No acredita ranking real con Gemini**, pendiente de Windows.

**Incidente B26-CI-001 resuelto:** el job genérico de Gate 1 instala únicamente `requirements.txt`; al descubrir la suite nueva B26 falló por `ModuleNotFoundError: langchain_chroma`. Se ajustó la suite para omitir las pruebas que exigen Chroma en ese job (donde no está instalado) y ejecutarlas **todas** en el job RAG especializado con `requirements-rag.txt`. Ambos jobs quedaron verdes sin alterar los paquetes del job base.

## 5. Continuidad académica

**B26/L1 completada técnicamente:** el estudiante ejecutó en Windows la demostración con embeddings ficticios, **9/9 tests offline**, y una consulta **Gemini real** contra el índice B25/L1. El documento de `TimeoutError` quedó **primero** a una distancia de **0.5494**. **U2.5: 7/15 lecciones**; B24 3/3, B25 3/3, B26/L1 completada. No consta entrega ni calificación institucional.

**Siguiente lección anunciada:** Bloque 26/L2 «Por qué la respuesta debe citar su fuente», sobre reutilizar metadata para citas. No anticipar requisitos antes de que se comparta la consigna.

## 6. Evidencia definitiva Windows · 14/11/2026

**Actualización local:** `git status --short` limpio antes y después; `git pull --ff-only` fast-forward `96ec7e1..c914d0e` en la rama de trabajo.

**Reproducción oficial con vectores ficticios:** modo `fake` recuperó 5 chunks indexados y `k=3` en este orden: `doc2.md` (costo), `doc4.md` (pruebas con mocks) y `doc0.md` (TimeoutError). Distancias **19.9059, 20.8040, 24.8037**, que reproducen las de la lección. La consulta con `as_retriever.invoke(k=2)` obtuvo `doc2.md` y `doc4.md`. **Este ranking se explica por los hashes; no demuestra semántica.**

**Suite Windows:** `Ran 9 tests in 5.082s / OK` (**9/9**). Sin llamadas Gemini durante la suite.

**Búsqueda semántica real:** modo `real`, colección Chroma existente `receta_b25_ejemplo`, ruta `.local/chroma_b25_receta/`, **3 chunks**. Pregunta: «que pasa si la conexion tarda demasiado». Resultado con `similarity_search_with_score`:

| Ranking | `metadata.fuente` | Resumen del fragmento | Distancia |
| --- | --- | --- | ---: |
| **1.º** | `ejemplo_skillnest_1` | Reintentar hasta 3 veces tras `TimeoutError` con espera creciente | **0.5494** |
| 2.º | `ejemplo_skillnest_3` | Pruebas unitarias con mocks | 0.7277 |
| 3.º | `ejemplo_skillnest_2` | Costo por `totalTokenCount` | 0.7557 |

**Interpretación técnica:** el texto correcto apareció primero pese a diferencias léxicas con la pregunta. La distancia menor representa mayor cercanía **en esta colección**; los números no son porcentajes y **no son comparables con los scores fake de 16 dimensiones**. Es evidencia de recuperación relevante para **una consulta individual**, no una prueba estadística de precisión. El índice original no se reconstruyó: Gemini solo embebió la pregunta, y Chroma devolvió los documentos persistidos junto con sus fuentes.

**Resultado académico:** B26/L1 **cerrada técnicamente**, U2.5 **7/15 lecciones**. La lección de Skillnest es de tipo «Ver». No hay nota ni envío institucional informado. **Tiempo efectivo de estudio desconocido**; los 5.082 segundos son solo las pruebas.

**Próximo material:** B26/L2 «Por qué la respuesta debe citar su fuente», que anuncia el uso de `metadata` en las citas. Esperar contenido oficial antes de implementar pasos nuevos.
