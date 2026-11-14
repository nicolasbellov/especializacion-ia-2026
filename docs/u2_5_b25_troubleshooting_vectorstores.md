# U2.5 · Bloque 25 · Lección 2 — Guía de troubleshooting de vector stores

**Fuente principal:** material oficial Skillnest, «Réplica guiada de indexación sobre corpus de ejemplo (Bloque 25) / Guía de troubleshooting de vector stores», compartido el 13/11/2026 (hora Chile).  
**Tipo de lección:** referencia conceptual y diagnóstico por etapas; **no exige indexar un corpus nuevo ni repetir llamadas reales de Gemini**.  
**Contexto previo validado:** B24 3/3 completado; B25/L1 completada en Windows con **3 chunks Gemini** y **7/7 tests**, U2.5 4/15 antes de esta lección.

## 1. Punto de partida oficial: configuración correcta

La guía presupone Python ≥ 3.10, `.venv` activo, `langchain-google-genai`, `langchain-text-splitters`, `langchain-chroma`, `chromadb`, `python-dotenv`, `GEMINI_API_KEY` configurada y carpeta de persistencia con permisos de escritura.

El estado de referencia que presenta Skillnest define:

```python
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()
PERSIST_DIR = os.path.abspath("vectorstore")
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = Chroma(
    collection_name="corpus_ejemplo",
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR,
)
print("Ruta del índice:", PERSIST_DIR)
print("Colección:", vectorstore._collection.name)
print("Chunks:", vectorstore._collection.count())
```

En el ejemplo oficial, `count()=0` corresponde a una colección nueva vacía. **La misma ruta absoluta y el mismo nombre de colección** deben emplearse al indexar y recuperar. Una ruta correcta con colección equivocada también puede aparentar un índice vacío.

**Aplicación a nuestros índices existentes:** el ejemplo anterior es **ilustrativo**; NO debe ejecutarse sobre `vectorstore/` cambiándole `collection_name` a `corpus_ejemplo`, porque nosotros ya tenemos allí la colección `booking_core_b24_l3` con diez chunks. No se mezclan ni se renombran las colecciones.

## 2. Mapa de errores de Skillnest

| Etapa | Error o síntoma | Diagnóstico/acción indicada por el curso |
| --- | --- | --- |
| Instalación | `sqlite3` de versión inferior a 3.35 para Chroma | Si el entorno afectado lo admite, parche `pysqlite3-binary` **antes** de importar Chroma |
| Instalación | `ModuleNotFoundError: langchain_chroma` (o otro paquete) | Revisar `.venv`, `pip install` y dependencias declaradas para reproducibilidad |
| Inicialización | `ValidationError ... API key required` | `GEMINI_API_KEY` ausente o no cargada mediante `load_dotenv()`, antes de llamar a la API |
| Autenticación API | `API key not valid` | Existe clave, pero proveedor rechaza su validez; revisar sin compartirla |
| Cuota API | `429 RESOURCE_EXHAUSTED` | Reintentos limitados con espera exponencial 5/10/20 segundos, repropagando el último error |
| Persistencia | Colección recargada con `count()=0` | Comparar rutas absolutas de indexación y recuperación, y verificar misma colección |
| Permisos | `PermissionError` / base de datos de solo lectura | Usar ruta escribible, revisar permisos y programas/procesos con índice abierto |
| Consistencia | Dimensiones incompatibles (ej. 768 vs 1536) | No mezclar vectores de modelos distintos; reconstruir con configuración homogénea |
| Calidad | Retrieval devuelve textos irrelevantes | Revisar corpus, chunking, modelo de embeddings y posible mezcla de vectores |
| Colección | Nombre inválido | Usar nombre conforme al patrón del curso: 3–512 caracteres alfanuméricos/punto/guion/guion bajo, inicio y final alfanuméricos |
| Configuración | Valor por defecto `collection_name="langchain"` en todos los scripts | Establecer colección explícita y distinta para cada corpus |

**Nota de plataforma:** el parche `pysqlite3-binary` se menciona para algunos Linux; no hay evidencia de que Windows Python 3.12.8 de este proyecto requiera ese parche. No instalarlo a ciegas.

## 3. Patrón 429 del curso y límites de seguridad

El curso presenta `con_reintentos(operacion, max_intentos=4, espera_inicial=5)`. En ausencia de error retorna en el primer intento; con `429` o `RESOURCE_EXHAUSTED`, hace **hasta 4 intentos**, con 3 esperas de **5, 10 y 20 segundos**. Si se agota el máximo, **propaga la excepción**. No reintenta errores de autenticación ni de permisos.

**Complemento propio:** [`src/diagnosticar_chroma_b25.py`](../src/diagnosticar_chroma_b25.py) contiene `con_reintentos_cuota()` con esa semántica. Permite inyectar `dormir` y `registrar` para comprobar el backoff con pruebas simuladas (sin esperas ni Gemini). No lo hemos integrado como un wrapper sobre la indexación real.

**Límite importante para aplicaciones reales:** repetir ciegamente un `Chroma.from_documents(...)` sobre un índice parcialmente escrito podría generar duplicados si sus IDs fueran aleatorios o quedar en un estado inconsistente. Antes de aplicar reintentos automáticos a una operación con efectos persistentes se necesita **idempotencia**, IDs estables y controles sobre indexaciones incompletas. Nuestros scripts de B24/L3 y B25/L1 tienen manifiestos y se niegan a mezclar configuraciones; no se cambia su comportamiento durante esta lección.

La clasificación por subcadena `"429" in str(error)` es la heurística de la guía, no un reconocedor infalible de excepciones tipadas del proveedor; en producción convendría verificar el código de estado de una excepción específica.

## 4. Diagnóstico propio sobre los tres índices reales (sin API ni escritura)

Los índices ya validados en Windows son independientes:

| Selección | Ruta relativa a raíz | Nombre explícito de colección | Fuente |
| --- | --- | --- | --- |
| `b24_l1` | `.local/chroma_b24/` | `booking_core_rag_demo_b24` | Primer laboratorio RAG |
| `b24_l3` | `vectorstore/` | `booking_core_b24_l3` | Cinco documentos, diez chunks reales |
| `b25_receta` | `.local/chroma_b25_receta/` | `receta_b25_ejemplo` | Tres textos, tres chunks reales |

Creamos una herramienta **complementaria**, independiente del ejercicio literal del curso:

```powershell
python -m src.diagnosticar_chroma_b25 --indice todos
# Alternativa para consultar solo un índice:
python -m src.diagnosticar_chroma_b25 --indice b25_receta
```

Comprueba versión de Python/SQLite, actividad de venv, importación posible de dependencias, **solo si GEMINI_API_KEY existe como variable de proceso** (no lee `.env` ni muestra valor), rutas absolutas, `chroma.sqlite3`, `PRAGMA quick_check` de SQLite **con conexión `mode=ro`**, y correspondencia de la colección indicada en los manifiestos cuando existen.

**Limitaciones deliberadas:** `PRAGMA quick_check=ok` solo comprueba la integridad interna de SQLite, no asegura que las búsquedas sean correctas ni que las dimensiones/modelo de embeddings coincidan. Los «chunks según manifiesto» **no son el resultado real de `Chroma._collection.count()`**. Para el conteo real usar `python verificar_vectorstore_b24.py` (B24/L3) o `python -m src.receta_indexacion_b25 --modo verificar` (B25/L1). `b24_l1` no tiene manifiesto y eso es normal.

La herramienta no llama Gemini, no importa Chroma, no cambia permisos, no crea índices, no ejecuta `Chroma.from_documents`, no imprime `.env`, no borra colecciones y cierra las conexiones SQLite para evitar bloqueos en Windows.

## 5. Práctica complementaria y regresiones de casos reales

```powershell
python -m unittest discover -s tests -p "test_troubleshooting_b25.py" -v
```

Las 11 pruebas offline incluyen clasificación de 429 versus 401/403/permiso SQLite, backoff **5/10/20** sin esperar, propagación del error final, restricciones de parámetros, comprobación SQLite/JSON en carpetas temporales sin mutación, índice inexistente sin creación, claves secretas protegidas y CLI local sin API.

**Experiencia propia del proyecto, no parte de la guía oficial:**

- **B24-WIN-001:** Windows podía retener archivos Chroma abiertos al borrar un `TemporaryDirectory` (`WinError 32`). Solución aplicada: procesos separados, salida limpia y cierre de conexiones.
- **B24-WIN-002:** `UnicodeDecodeError` / `TypeError` al leer stdout en UTF-8 cuando un proceso Windows emitía CP1252; solucionado forzando `PYTHONIOENCODING=utf-8`, `PYTHONUTF8=1` y decodificación robusta en tests. **9/9 QA Windows** de B24/L3 ya verificados.

## 6. Criterio de estudio y siguiente lección

Skillnest presenta B25/L2 como **guía de consulta («Ver»), no como actividad práctica obligatoria**. Revisar los errores por etapa, el mecanismo de backoff y las condiciones de seguridad es el objetivo de esta lección. Las pruebas nuevas son material complementario; no requieren volver a gastar Gemini.

**Validación complementaria verificada:** [GitHub Actions #43533641828](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43533641828) aprobó ambos jobs. **11/11 pruebas nuevas del troubleshooting** (`Ran 11 tests in 0.036s / OK`), además de **27/27 B24** y **7/7 B25/L1**. `python -m src.diagnosticar_chroma_b25 --indice todos` se ejecutó en CI y finalizó con «Diagnóstico local completado. Sin API, sin cambios en los índices.» En CI no existen las bases locales del estudiante, por lo que esta salida prueba el funcionamiento del diagnóstico, **no el estado de los índices Windows**.

**Cierre de la lección:** contenido de troubleshooting **estudiado y documentado**, con ejemplos y tests opcionales aprobados. **B25 2/3; U2.5 5/15 lecciones**. La guía es de tipo «Ver», sin ejercicio obligatorio de indexación; no confundir con calificación formal de Skillnest.\n\n**Siguiente paso anunciado por el curso:** B25/L3 «Indexación y persistencia de tu corpus» (réplica con un corpus de ejemplo dado según el último apartado del material). No asumir aún datos, tamaños de chunks ni actividades adicionales que no se hayan compartido.

No tocar `vectorstore/` ni `.local/chroma_b24/` ni `.local/chroma_b25_receta/` salvo validaciones read-only. No confundir el cierre conceptual del contenido con entrega o evaluación institucional.
