# U2.5 / Bloque 24 / Lección 3 — Indexar corpus propio y persistir embeddings

**Programa:** Especialización IA 2026 · Skillnest / Accenture / CChIA  
**Fecha de preparación:** 13/11/2026 (Chile)  
**Fuente principal:** consigna oficial «Indexa tu corpus y persiste los embeddings en un vector store [Actividad práctica]» compartida por el estudiante.  
**Estado:** solución desarrollada en rama; **indexación real Windows y verificación posterior aún no recibidas**. No declarar entrega institucional sin confirmación del estudiante.

## 1. Criterios oficiales de la actividad

La consigna solicita:

1. **Corpus propio** con un mínimo de cinco documentos relacionados.
2. **Chunking aplicado a cada documento antes** de calcular embeddings, justificando splitter y parámetros.
3. Embeddings **reales** de `GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")`, no vectores inventados.
4. **Chroma persistente en disco**, consultable desde otro proceso con `Chroma(persist_directory=...)`, sin recalcular embeddings.
5. Carpeta de índice ignorada por Git, junto con credenciales y entorno. Entregar scripts de indexación y dependencias versionadas.
6. **Validación**: al menos cinco fuentes, índice físicamente creado, reabrir por separado y comprobar `count()`.

La consigna usa `Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory="vectorstore/")`. Esta solución utiliza ese mismo método con una colección explícita e IDs deterministas para mejorar reproducibilidad. No se modifica ningún archivo de Booking Core ni se consultan reservas.

## 2. Diseño que implementamos

- **Cinco documentos independientes** (no cinco secciones del mismo archivo): `data/corpus_b24_l3/01_servicios.md`, `02_disponibilidad.md`, `03_reprogramacion.md`, `04_cancelacion.md` y `05_privacidad.md`. Todos declaran **EJEMPLO FICTICIO**. Documentan el contexto académico del agente y no son políticas de AES Barber.
- **Splitter elegido**: `RecursiveCharacterTextSplitter(chunk_size=550, chunk_overlap=80)` (≈14,5 %). En B24/L2, 110 caracteres generaba encabezados aislados. El nuevo splitter trabaja por archivo; integra el título con el cuerpo antes de dividir para preservar contexto. Los títulos también viajan en `metadata['titulo']` de cada fragmento. No se garantiza que todos los fragmentos tengan el mismo tamaño ni que el overlap se materialice como exactamente 80 caracteres.
- **Metadatos**: `fuente`, `titulo`, `origen=FICTICIO_ACADEMICO`, `indice_chunk`, `metodo_chunking=recursivo`.
- **IDs deterministas**: SHA-256 de nombre de archivo e índice ordinal del fragmento.
- **Vector store nuevo**: `vectorstore/`, colección `booking_core_b24_l3`. Es distinto de `.local/chroma_b24` de B24/L1; ambos permanecen fuera de Git.
- **Índice reproducible**: `indexar_corpus.py` crea un manifiesto local `vectorstore/manifiesto_b24_l3.json` con hash del corpus, IDs, modelo y configuración. Si la misma entrada ya está indexada, **no vuelve a ejecutar Gemini ni `from_documents`**; si el corpus cambió, avisa y se detiene, sin sobrescribir automáticamente el índice.
- **Verificador independiente**: `verificar_vectorstore_b24.py` reabre la colección con `Chroma(..., embedding_function=None)`, ejecuta `get()` y comprueba IDs/archivos/count del manifiesto, sin inicializar Gemini ni reindexar.

### ¿Por qué no guardamos disponibilidad horaria en RAG?

Porque las horas libres cambian con las transacciones. El capstone sigue siendo conectar un agente a la agenda real de Booking Core (AES Barber piloto), usando *herramientas autorizadas* para disponibilidad y cambios. RAG aporta documentación estática y explicaciones, **no sustituye el backend**.

## 3. Preparación Windows (PowerShell)

Desde `C:\Users\nbello\dev\especializacion-ia-2026`, estando en la rama `feature/u2-5-b24-rag-booking-core`:

```powershell
git status --short
# Si hay cambios locales, revisarlos antes de actualizar la rama.
git pull --ff-only

python --version
python -c "import sys; print('Entorno virtual activo' if sys.prefix != sys.base_prefix else 'Sin entorno virtual activo')"
python -m pip install -r requirements-rag.txt
python -m pip check
```

**Requisitos:** Python ≥3.10 (en este proyecto usamos 3.12), `.venv` activo, `GEMINI_API_KEY` local en `.env`, nunca enviada al chat. `requirements.txt` conserva la base versionada y `requirements-rag.txt` añade `langchain-chroma` y `chromadb` sin borrar versiones históricas; **no sobrescribir `requirements.txt` indiscriminadamente con `pip freeze`**.

## 4. Ejecución real (consume cuota de Gemini solo al crear)

```powershell
# 1) Pruebas offline sin API ni uso de la clave
python -m unittest discover -s tests -p "test_indexacion_b24_booking_core.py" -v

# 2) Indexación: primera vez calcula embeddings reales
python indexar_corpus.py

# 3) Proceso distinto: abre Chroma sin calcular ningún embedding
python verificar_vectorstore_b24.py

# 4) Segunda ejecución: debe detectar el índice y saltarse los embeddings
python indexar_corpus.py
```

En la primera ejecución, verificar **Documentos fuente: 5**, **Chunks indexados: N (N ≥ 5)** y la ruta `vectorstore/`. El conteo exacto depende del splitter y de la versión del paquete: registrar el valor observado, no inventarlo. La comprobación debe mostrar **Persistencia confirmada** y el mismo total de chunks. La repetición debe indicar **existente; sin re-embedding**.

La presencia de `chroma.sqlite3` y del manifiesto confirma la existencia del índice nuevo. En Git, `git status --short` **no debe incluir** `vectorstore/` ni `.env`.

## 5. Manejo seguro de fallos

- **`GEMINI_API_KEY` ausente o inválida:** revisar `.env` local sin compartir la clave. Se usan mensajes resumidos para no imprimir errores externos que podrían contener datos sensibles.
- **429 / cuota:** la consigna recomienda reintentar más tarde. No reindexar por cada consulta.
- **Índice parcial** (fallo durante `from_documents` antes del manifiesto): no borramos automáticamente el directorio. Revisar la ruta **específica** `vectorstore/` y, si corresponde, renombrarla como respaldo antes de reindexar con la clave válida.
- **Corpus modificado después de indexar:** el manifiesto lo detecta y exige crear una nueva versión. Los IDs estables evitan duplicación simple, pero no implican reconciliación automática de borrados; por eso no se sobrescribe a ciegas.
- **Windows y archivos bloqueados:** la prueba de persistencia usa procesos separados para que Windows libere descriptores Chroma antes de limpiar directorios temporales.

## 6. Estado de verificación

Las pruebas offline usan embeddings falsos **solo en tests**, para demostrar Chroma y persistencia sin consumir la cuota de Gemini. La ejecución `python indexar_corpus.py` de la actividad académica, por el contrario, **sí usa Gemini real** a través de `crear_embeddings()`. No confundir las dos evidencias.

**Pruebas CI verificadas:** [GitHub Actions #43530916089](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43530916089) aprobó ambos jobs. En el job RAG se ejecutaron **26/26 pruebas B24** (11 L1 + 7 L2 + 8 L3), incluida una indexación Chroma real con **embeddings simulados**, recarga desde otro proceso y reutilización sin recalcular vectores. Estas pruebas CI NO equivalen a utilizar Gemini real para esta nueva actividad.

**Evidencia Windows recibida:** la indexación real con Gemini creó **10 chunks a partir de 5 documentos**, la apertura independiente confirmó **10 chunks sin llamar a Gemini** y la segunda ejecución detectó **«existente; sin re-embedding»**. El gate funcional de la consigna está satisfecho. **Queda pendiente únicamente repetir la suite Windows después de corregir el problema de decodificación de la salida de un subproceso** (7/8 inicialmente).

## 7. Entrega y continuación

Código a versionar: `indexar_corpus.py`, `verificar_vectorstore_b24.py`, `data/corpus_b24_l3/*.md`, `tests/test_indexacion_b24_booking_core.py`, `requirements.txt` + `requirements-rag.txt` y `.gitignore`. El código ya se publica en la rama; no versionar `vectorstore/` ni claves.

**Siguiente bloque oficial:** Bloque 25, indexación de un corpus de ejemplo distinto y troubleshooting. El Bloque 27 evaluará precisión y recall; no afirmar que una configuración es óptima por la cantidad de chunks generada.


## 8. Ejecución real Windows y diagnóstico B24-WIN-002 · 13/11/2026

**Entorno y Git:** desde `(.venv)`, Python **3.12.8**, verificación `Entorno virtual activo`. `git status --short` vacío antes y después; `git pull --ff-only` fast-forward **`0c700ca..6b467b7`** sin conflictos.

**Indexación con Gemini real** (`python indexar_corpus.py`):

```text
Estado: creado con embeddings
Documentos fuente: 5
Chunks indexados: 10
Índice persistido: C:\Users\nbello\dev\especializacion-ia-2026\vectorstore
El vectorstore anterior .local/chroma_b24 no se modifica.
```

**Persistencia sin API** (`python verificar_vectorstore_b24.py`): resultado **«Persistencia confirmada: Chroma reabierto sin reindexación ni Gemini»**, **5 documentos de origen, 10 chunks persistidos**; nombres de archivo `01_servicios.md` a `05_privacidad.md`. La segunda invocación de `python indexar_corpus.py` produjo **«Estado: existente; sin re-embedding»** y mantuvo los 10 chunks. `git check-ignore -v vectorstore/chroma.sqlite3` verificó la exclusión por `.gitignore:31:vectorstore/`.

**Incidente B24-WIN-002, limitado a tests automatizados:** primera ejecución de `python -m unittest discover -s tests -p "test_indexacion_b24_booking_core.py" -v` terminó **7/8 aprobados**, `Ran 8 tests in 14.317s / FAILED (errors=1)`. La prueba de Chroma usaba `subprocess.run(..., text=True, encoding="utf-8")` pero el subproceso de PowerShell devolvió un byte **0xf3**, inválido en esa posición para UTF-8. El hilo lector interno levantó `UnicodeDecodeError` y devolvió `stdout=None`; el `TypeError` posterior en `assertIn` es consecuencia de esa falla de decodificación, **no** evidencia de que el índice Chroma o los embeddings hayan fallado.

**Corrección aplicada a las pruebas en rama:** `ejecutar_subproceso_utf8()` fuerza `PYTHONIOENCODING=utf-8` y `PYTHONUTF8=1`, usa `encoding="utf-8", errors="replace"` en pipes y centraliza los procesos de indexación, reutilización y verificación. Se agregó una **novena prueba B24/L3 de regresión** con caracteres acentuados. **No cambia `indexar_corpus.py` ni el vectorstore del estudiante.**

**CI posterior al fix:** [GitHub Actions #43531505453](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43531505453), ambos jobs aprobados; **27/27 pruebas B24** con la nueva prueba de acentos y persistencia entre procesos (`Ran 27 tests in 7.958s / OK`), sin Gemini. En el PC Windows sigue pendiente repetir las **9 pruebas específicas de L3**. La ejecución CI no reemplaza esa verificación local.

**Estado técnico:** objetivo funcional de la actividad **verificado** (cinco fuentes, chunking, embeddings reales, persistencia en disco y apertura independiente). **QA Windows 9/9 posterior a la corrección pendiente**; no declarar aprobación formal de Skillnest ni tiempo de estudio desconocido.

**Próxima acción exacta:** sincronizar rama limpia y ejecutar solo `python -m unittest discover -s tests -p "test_indexacion_b24_booking_core.py" -v`, que ya no necesita Gemini ni modifica el índice local. Luego registrar 9/9 o el error observado antes del cierre definitivo del Bloque 24.
