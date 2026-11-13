# U2.5 · Bloque 24 / Lección 1 — RAG por dentro (Booking Core AI)

**Programa:** Especialización IA 2026 · Skillnest / Accenture / CChIA  
**Fecha:** 13/11/2026 (Chile)  
**Fuente:** material completo de la lección «RAG por dentro: chunking, embeddings y vector stores» aportado por el estudiante.  
**Estado (13/11/2026):** entorno virtual Windows instalado, `pip check` satisfactorio y **embedding real Gemini verificado (3072 dimensiones)**. Prueba Chroma local: 10/11 iniciales; corrección de limpieza Windows preparada en la rama, pendiente de repetición en el PC. Indexación Gemini de corpus y evaluación Skillnest no verificadas.

## Objetivo sostenido del proyecto integrador

Conectar un agente conversacional con la **agenda real de Booking Core**, con **AES Barber** como piloto. Booking Core es el sistema SaaS multi-tenant existente (otro repositorio). El laboratorio de la especialización es `nicolasbellov/especializacion-ia-2026`.

No confundir dos fuentes de información:

| Necesidad | Fuente prevista | RAG |
| --- | --- | --- |
| FAQ y documentación estática autorizada | Corpus documental versionado / Chroma | Sí |
| Consultar horarios disponibles **actuales** | API de Booking Core con autorización del tenant | No |
| Crear/reprogramar/cancelar reserva | Backend transaccional de Booking Core y controles de aprobación | No |
| Consultar datos privados de clientes | API autorizada, autenticación y permisos | No |

**No se ha conectado aún ningún componente del agente a Booking Core o Supabase reales.** Tampoco se ha autorizado una escritura real. El corpus incluido es íntegramente ficticio.

## Qué enseña Skillnest en esta lección

1. **Chunking:** fragmentar documentos para recuperar la sección relevante.
2. **Embeddings:** convertir fragmentos y preguntas en vectores numéricos. El ejemplo oficial usa `GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")`, `embed_query(...)` y espera 3072 dimensiones por defecto.
3. **Vector store:** guardar embeddings y recuperar vectores cercanos; el curso utiliza Chroma local con `persist_directory`.
4. **Dos fases:** indexar el corpus cuando cambia; recuperar fragmentos en cada pregunta.
5. **Limitaciones:** RAG no garantiza respuestas correctas; evaluar relevancia, costos y latencia en bloques posteriores.

La lección **no exige entrega**. El código de este repositorio es un complemento del ejercicio oficial para mantener la continuidad con la agenda de barbería.

## Archivos incorporados

- [src/rag_b24_booking_core.py](../src/rag_b24_booking_core.py): demo conceptual; `embedding`, `indexar` y `buscar`.
- [data/rag_demo_booking_core.md](../data/rag_demo_booking_core.md): cinco secciones totalmente ficticias y no personales.
- [tests/test_rag_b24_booking_core.py](../tests/test_rag_b24_booking_core.py): pruebas con store falso, sin peticiones reales ni escrituras de agenda.
- [requirements-rag.txt](../requirements-rag.txt): instalación incremental para esta unidad.
- [.gitignore](../.gitignore): excluye índices Chroma locales.

### Decisiones de diseño

- **Un chunk por sección `##`:** estrategia didáctica para la primera lección; aún no se ha comparado con otras políticas de chunking (segunda lección).
- **Metadatos:** `fuente`, `seccion` y `origen=FICTICIO_ACADEMICO`. Permiten asociar fragmentos recuperados a su texto de origen.
- **IDs deterministas:** SHA-256 de fuente y sección. Repetir la indexación actualiza los mismos IDs con Chroma en lugar de crear nuevas claves para la misma sección.
- **Borrado de secciones:** no implementado; si se elimina una sección, borrar la carpeta local `.local/chroma_b24` y reconstruir para no dejar chunks obsoletos. Hacerlo solo sobre este índice ficticio.
- **Persistencia:** `.local/chroma_b24`, fuera de Git. No contiene registros reales de reservas.
- **Sin integración prematura:** esta demo no modifica agentes B21–B23, tablas, endpoints ni permisos de Booking Core.

## Ejecución en Windows / PowerShell

Desde `C:\Users\nbello\dev\especializacion-ia-2026`:

```powershell
git status --short
git fetch origin
git switch feature/u2-5-b24-rag-booking-core
# Si hay cambios locales, revisar antes de cambiar de rama; NO descartarlos.
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

# Instalar en el entorno virtual (NO en el Python global).
python -m pip install -r requirements-rag.txt
python -m pip check

# Pruebas offline (sin consumo de Gemini).
python -m unittest discover -s tests -p "test_rag_b24_booking_core.py" -v

# Demostración oficial del concepto (requiere GEMINI_API_KEY local).
python -m src.rag_b24_booking_core --modo embedding

# Extensión práctica opcional (requiere acceso a API Gemini).
python -m src.rag_b24_booking_core --modo indexar
python -m src.rag_b24_booking_core --modo buscar --pregunta "¿Cómo solicito cambiar una cita?"
```

Antes de hacer `git switch`, comprobar si hay cambios propios sin commitear y actuar sin sobrescribirlos. Si se utiliza `venv` en lugar de `.venv`, ajustar la ruta.

**Importante:** el registro de instalación aportado el 13/11/2026 utilizó `python -m pip` y muestra que algunas dependencias quedaron en `AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages` (Python global), con `langchain==1.5.0` y `langchain-google-genai==4.5.0`. El repositorio fijaba `langchain==1.4.9` y `langchain-google-genai==4.4.3`. No asumir que las versiones globales son las del `.venv`. Este archivo incremental respeta el conjunto histórico y deja que pip resuelva las nuevas dependencias; registrar versiones efectivamente resueltas tras ejecutar.

## Criterios de validación

| Control | Resultado exigido |
| --- | --- |
| Paquetes | `pip check` sin conflictos en `.venv` |
| Tests sin API | Todas las pruebas B24 verdes |
| Embedding real | `len(vector)==3072` (modelo y configuración por defecto del curso) |
| Indexación | 5 chunks ficticios en el directorio local |
| Recuperación | Devuelve texto y metadatos de secciones del corpus ficticio |
| Integridad | `.env`, `.local/` y cualquier cliente/reserva real fuera del commit |
| Booking Core | Sin acceso o mutación de producción |

## Arquitectura incremental futura

`Usuario → agente con herramientas → (FAQ/documentación: retrieval RAG) o (agenda viva: API Booking Core) → respuesta`.

En el Gate 2, conectar herramientas de lectura bajo identidad y tenant autorizado; para cambios de reservas, autenticación, autorización, consentimiento cuando corresponda, idempotencia, validaciones y trazabilidad deben existir en el **backend**, no únicamente en el prompt o vector store.

## Evidencia Windows y corrección de limpieza de Chroma — 13/11/2026

**Ejecución aportada por el estudiante:** PowerShell en `.venv`, `python -m pip install -r requirements-rag.txt`, `python -m pip check` (**No broken requirements found**), 11 pruebas y una llamada real a Gemini. Versiones instaladas en el entorno virtual: `chromadb==1.5.9`, `langchain-chroma==1.1.0`, `langchain==1.4.9`, `langchain-google-genai==4.4.3`; así se distingue del Python global.

**Embedding real verificado:**

```text
Dimensiones: 3072
Primeros cinco valores: [-0.001601775, 0.02089852, 0.01956536, -0.065919146, -0.0064969533]
```

**Incidente B24-WIN-001:** la primera ejecución de pruebas local terminó en **10/11 casos**, con un `PermissionError: [WinError 32]` al salir de `TemporaryDirectory()`: Chroma aún mantenía abierto un archivo HNSW `data_level0.bin`. La traza ocurre dentro de `tempfile.cleanup()`, no en el algoritmo de recuperación. El job Linux de GitHub Actions previo había aprobado 11/11 y no detectaba ese problema específico de Windows.

**Corrección propuesta:** ejecutar la escritura, cierre y relectura persistente de Chroma en **subprocesos Python independientes**, sin red y con embeddings ficticios, ambos finalizados antes de limpiar el directorio temporal desde el proceso principal. Esto comprueba persistencia **entre procesos** y libera los handles de archivo al terminar cada subproceso. No se modificó la lógica del agente, ni se alteró Booking Core/Supabase.

**Validación GitHub Actions de la corrección:** [ejecución #43527127870](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43527127870) aprobada con **11/11 pruebas B24**, persistencia entre procesos y `pip check` satisfactorio, además de regresión. **Validación final Windows:** el estudiante repitió el test tras `git pull --ff-only` y obtuvo **Ran 11 tests in 10.604s / OK**; el error WinError 32 no reapareció. El embedding real de Gemini generó 3072 dimensiones. **Pendiente** indexación y recuperación semántica reales sobre los cinco chunks del corpus ficticio.

## Próximo punto exacto

1. En PowerShell sobre `feature/u2-5-b24-rag-booking-core` ejecutar `git status --short`; si está limpio, `git pull --ff-only`.
2. Repetir `python -m unittest discover -s tests -p "test_rag_b24_booking_core.py" -v` y verificar **11/11 PASS en Windows**.
3. Ejecutar `python -m src.rag_b24_booking_core --modo indexar` y luego `--modo buscar --pregunta "¿Cómo cambio una cita?"` (consumen llamadas de Gemini; corpus ficticio).
4. Documentar recuperación y citar la sección encontrada; avanzar a Bloque 24, Lección 2 (comparación de chunking).
5. Mantener tiempos efectivos y evaluación institucional pendientes hasta contar con evidencias.
