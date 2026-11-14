# U2.5 · Bloque 25 · Lección 1 — Cómo indexar y persistir un corpus en un vector store

**Fuente principal:** texto oficial de Skillnest «Réplica guiada de indexación sobre corpus de ejemplo / Cómo indexar y persistir un corpus en un vector store», compartido el 13/11/2026 (Chile).  
**Estado:** lección estudiada, receta preparada en GitHub; aún falta recibir y confirmar su ejecución con el entorno local del estudiante. No se debe confundir pruebas offline con embeddings reales Gemini de este nuevo ejemplo.

## 1. Los cinco pasos oficiales

1. Reunir un corpus de textos o archivos relacionados entre sí.
2. Dividir **cada documento** en chunks con un splitter y `chunk_size` justificado.
3. Calcular embeddings con `GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")`.
4. Guardar fragmentos y vectores usando `Chroma.from_documents(..., persist_directory=...)`.
5. Abrir Chroma desde **otro proceso**, sin recalcular los embeddings existentes.

El código de la lección resume la indexación en la función `indexar_corpus(corpus, persist_directory, chunk_size=200, chunk_overlap=30)` y la recarga en `cargar_vectorstore(persist_directory)`. Para la demostración oficial, el corpus son **tres textos cortos** (reintentos, costo por `totalTokenCount`, pruebas unitarias con mocks), cada uno menor que el tamaño de 200 caracteres; resultado esperado: **3 chunks indexados, 3 persistidos**.

**Precisión técnica complementaria:** `Chroma.from_documents` *no parte* los documentos por sí solo; recibe los `Document` ya divididos por `splitter.create_documents` y, a partir de ellos, calcula los embeddings y los guarda.

## 2. Parámetros, costos y decisiones

- `chunk_size` pequeño (~100): tiende a representar unidades concretas, pero puede perder una idea al cortarla.
- `chunk_size` grande (~500+): suele conservar contexto, pero puede mezclar varios temas. No existe un valor universalmente óptimo.
- `chunk_overlap`: intenta conservar contexto de frontera, con el costo de volver a procesar y almacenar caracteres duplicados. **No garantiza** exactamente esa cantidad de caracteres solapados en cada fragmento.
- **IDs explícitos y estables**: el ejemplo avanzado de Skillnest muestra `add_documents(..., ids=...)` para agregar sin reinsertar los anteriores, y `delete(ids=...)` para eliminar fragmentos concretos.
- **Reconstrucción vs actualización incremental:** el material presenta cambios de corpus/modelo/chunking como situaciones que obligan a actualizar el índice, y también enseña que documentos nuevos se pueden agregar incrementalmente con IDs. En la práctica, **cambiar modelo o fragmentación requiere reconstruir los embeddings afectados para mantener consistencia**; editar un documento puede tratarse selectivamente con IDs y operaciones de actualización/borrado, en vez de reconstruir siempre el índice entero. La receta académica no implementa actualizaciones parciales: detecta cambios y exige un índice distinto antes de mezclar datos.

**Advertencia que importa para Booking Core:** no confundir persistencia documental con sincronización de la agenda. Los embeddings de FAQs o procesos pueden persistir; las horas disponibles deben consultarse siempre por API transaccional autenticada.

## 3. Réplica reutilizable preparada en el repositorio

**Script:** [`src/receta_indexacion_b25.py`](../src/receta_indexacion_b25.py). Contiene las funciones `preparar_chunks`, `indexar_corpus`, `cargar_vectorstore` y `verificar_indice`; la CLI ofrece tres modos:

```powershell
# No usa API ni escribe disco: confirma 3 chunks en memoria.
python -m src.receta_indexacion_b25 --modo preparar

# Solo la primera ejecución calcula embeddings Gemini reales.
python -m src.receta_indexacion_b25 --modo indexar

# Proceso separado: reconecta Chroma, confirma 3 chunks sin Gemini.
python -m src.receta_indexacion_b25 --modo verificar
```

- **Se replica el texto del curso** y su configuración por defecto **200/30**.
- Por seguridad, el índice del ejemplo se guarda en **`.local/chroma_b25_receta/`**, ya ignorado por `.gitignore`, **no** en `vectorstore/`. Así no se alteran el índice de diez chunks de la actividad B24/L3 ni el índice B24/L1 `.local/chroma_b24`.
- Se usan metadatos de fuente, IDs estables y huella del corpus para impedir duplicación accidental al repetir la ejecución y rechazar cambios de documentos/configuración sin reconstrucción explícita. Es una **extensión técnica propia**, no parte literal de la receta oficial.
- Para el mero conteo, `cargar_vectorstore` admite `embedding_function=None`: leer el índice **no necesita** invocar Gemini. Para una búsqueda de similitud posterior, se puede pasar un objeto de embeddings compatible, pero esa consulta sí calcularía el vector de la pregunta.
- Se evita pedir que el estudiante comparta `GEMINI_API_KEY` o `.env`; la función `crear_embeddings` ya utiliza la configuración local de B24.

### Validación sin API (tests)

```powershell
python -m unittest discover -s tests -p "test_receta_b25.py" -v
```

Las pruebas comprueban tres fragmentos del ejemplo, variación de tamaños, parámetros inválidos, IDs/huella deterministas, ruta aislada de B24, CLI sin Gemini y Chroma persistente con **embeddings falsos únicamente dentro de tests**, para comprobar recarga y protección contra reindexado entre procesos. **Evidencia CI:** [GitHub Actions #43532526769](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43532526769) aprobó ambos jobs. La suite B25 registró **7/7 pruebas OK** (`Ran 7 tests in 2.102s / OK`); B24 mantuvo **27/27** y `--modo preparar` imprimió **3 chunks**. **La evidencia de esas pruebas no autoriza afirmar que Gemini haya indexado este nuevo corpus**.

## 4. Fallos frecuentes, según el curso

- **Clave inválida o ausente:** verificar `GEMINI_API_KEY` en `.env` y `load_dotenv()` antes de crear el cliente.
- **`429 RESOURCE_EXHAUSTED`:** límite del proveedor; esperar y reintentar cuando corresponda, sin ocultar el fallo.
- **Dependencias faltantes:** instalar `requirements-rag.txt` dentro de `.venv` para conservar la versión del proyecto.
- **`PermissionError` o base de datos de solo lectura:** usar una carpeta escribible y comprobar que ningún otro proceso tenga el archivo abierto.
- **`count() == 0`:** revisar directorio y nombre de colección, o si se ejecutó la lectura antes de indexar.

## 5. Qué necesitamos verificar en Windows

1. Sincronizar la rama si `git status --short` está limpio.
2. Ejecutar `--modo preparar` → **3 chunks**, sin API.
3. Ejecutar las pruebas offline nuevas → todos los casos `OK`.
4. Si se ejecuta `--modo indexar` con la clave vigente, registrar **3 chunks** persistidos en la nueva ruta; `--modo verificar` debe confirmar **3** en un proceso nuevo; una segunda indexación debe indicar **«reutilizado sin re-embedding»**.
5. No tocar `vectorstore/`, `.local/chroma_b24/`, la base transaccional ni los datos de clientes.

## 6. Continuidad académica

**Lección actual:** B25/L1, resumen-referencia de indexación reutilizable. **Siguiente lección anunciada oficialmente:** «Guía de troubleshooting» (B25/L2), seguida de una réplica práctica sobre un corpus de ejemplo dado (B25/L3). No inventar el contenido preciso de B25/L2 o L3 hasta recibirlo.

**Estado institucional:** ni la ejecución local de esta lección ni una evaluación de Skillnest están confirmadas; no aumentar el progreso de U2.5 más allá de **3/15** todavía. Registrar inicio, término y tiempo real solo si el estudiante lo informa.
