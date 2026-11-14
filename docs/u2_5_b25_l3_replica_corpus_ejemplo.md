# U2.5 · Bloque 25 · Lección 3 — Réplica de un corpus de ejemplo (tienda ficticia)

**Fuente oficial:** Skillnest, «Réplica guiada de indexación sobre corpus de ejemplo (Bloque 25) / Indexación y persistencia de tu corpus de ejemplo», recibida el 13/11/2026 en Chile.

## Naturaleza del ejercicio

La instrucción del curso es **no entregar ni commitear** esta réplica: se plantea como ejercicio individual para comprender los cinco pasos de indexación. **Decisión de trabajo del estudiante:** versionar voluntariamente **solo el código y las pruebas** en el repositorio GitHub académico, para preservar conocimiento reutilizable y facilitar la revisión; esta extensión **no equivale a envío en Skillnest** y no cambia los requisitos del curso.

El corpus no tiene datos comerciales reales. No contiene información de Booking Core, clientes, AES Barber ni políticas reales. El índice Chroma y el archivo .env **nunca** deben publicarse.

## 1. El ejemplo oficial y la salida de referencia

El curso entrega cinco políticas ficticias: cancelación en 24 h, devoluciones en 30 días, reembolso en 5–10 días hábiles, excepciones de liquidación y costo de envíos devueltos.

- **Chunking:** RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=20), por documento.
- **Fragmentos esperados:** exactamente **5**, de tamaños **[106, 103, 99, 85, 97]** caracteres.
- **Integridad esperada:** 0 vacíos, ningún texto duplicado, **490 caracteres tanto en el corpus como en los chunks**. Ningún documento se divide; por tanto no se materializa overlap entre fragmentos.
- **Embedding:** GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001") sobre los cinco chunks.
- **Persistencia:** Chroma debe guardar **5** chunks en una colección aislada; la recarga debe mostrar **5**, sin recalcular embeddings.

**Resultado final a alcanzar:** confirmación local del preflight, indexación real Gemini, persistencia desde otro proceso y ausencia de duplicados al repetir la indexación.

## 2. Archivo en GitHub y comandos PowerShell

**Script versionado a solicitud del estudiante:** [replica_ejemplo.py](../replica_ejemplo.py). **Tests offline:** [tests/test_replica_ejemplo_b25.py](../tests/test_replica_ejemplo_b25.py). El código conserva el corpus y los parámetros oficiales, añadiendo controles **propios** de integridad, manifiesto, IDs estables y protección contra re-embedding. Es una decisión de ingeniería adicional, no un requisito literal de la consigna.

El índice nuevo se guarda en .local/chroma_b25_tienda_ejemplo/, ignorado por .gitignore; es distinto de .local/chroma_b24/, vectorstore/ y .local/chroma_b25_receta/. La clave se reutiliza desde el .env local en la raíz, sin copiarla ni subirla.

Desde C:\Users\nbello\dev\especializacion-ia-2026, con (.venv) activo:

~~~powershell
git status --short
git pull --ff-only

# Primero: chequeos gratuitos sin Gemini
python replica_ejemplo.py --modo preparar
python -m unittest discover -s tests -p "test_replica_ejemplo_b25.py" -v

# Después de aprobar el preflight: indexación Gemini del nuevo corpus
python replica_ejemplo.py --modo indexar

# Comprobación en otro proceso sin Gemini
python replica_ejemplo.py --modo verificar

# Reutilización idempotente: no repetir las llamadas API
python replica_ejemplo.py --modo indexar

git status --short
~~~

La **primera** indexación legítima sí consume una solicitud al proveedor de embeddings y puede topar con cuotas. Reejecutar indexar sobre el mismo corpus válido solo debe devolver «reutilizado sin re-embedding». Si un índice queda parcial o su manifiesto difiere, el script se detiene en vez de borrarlo automáticamente.

## 3. Evidencia de pruebas y límites

**CI validada:** [GitHub Actions #43536897395](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43536897395) registró **8/8 tests B25/L3 OK** (`Ran 8 tests in 6.614s / OK`), y aprobó las regresiones **27/27 B24 + 7/7 B25/L1 + 11/11 B25/L2**. El preflight reprodujo **5 chunks y 490 caracteres**. Los tests de persistencia usan exclusivamente vectores simulados en carpetas temporales, sin API; no prueban aún Gemini real para este nuevo corpus. La evidencia definitiva deberá provenir del PowerShell del estudiante.

**Estado técnico por confirmar:** la preparación en GitHub y los tests no bastan para marcar B25/L3 cerrada. U2.5 se conserva **5/15** y el Bloque 25 **2/3** hasta recibir y analizar los resultados locales.

**Siguiente bloque anunciado oficialmente:** Bloque 26, «Buscar por significado, no por palabra»: recuperación semántica y construcción del prompt RAG con contexto. No añadir requisitos no compartidos de ese bloque.
