# CHECKPOINT / HANDOFF — U2.8 Gate 2 — Booking Core AI

**Fecha:** jueves 26/11/2026, America/Santiago.
**Objetivo:** integrar servicio IA modular con RAG y demostrar indexar -> recuperar -> responder; alinear primero a rúbrica real.
**Proyecto académico:** nicolasbellov/especializacion-ia-2026.
**Rama:** feature/u2-8-gate2-rag-booking-core-ai, creada desde el estado entregado de U2.7.
**Método:** GitHub -> fetch/switch/pull Windows -> pruebas -> evidencia -> checkpoint.
**Separación:** no cambiar nicolasbellov/booking-core productivo ni borrar verificar_tuning.py local.

## Estado académico de partida

- U2.7 Core: entrega registrada exitosamente en Skillnest el 26/11/2026, evaluación del instructor pendiente, 30/30 pruebas de la entrega verificadas localmente.
- U2.8 Gate 2: el usuario compartió el índice de tres páginas S1: (1) rúbrica y exigencia funcional id=20481, (2) verificación en vivo indexar/recuperar/responder id=20482, (3) actividad Core id=20483.
- **Los contenidos de esas tres páginas NO están aún disponibles**, los enlaces no pudieron abrirse sin sesión. No adjudicar criterios provisionales a Skillnest ni declarar Gate2 aprobado/entregado.

## Artefactos avanzados y su alcance

1. gate2/servicio.py: RAG modular con retrieval inyectable, filtro y gate anti-inyección BC-02, contexto numerado, respuesta con citas, usage_metadata y trace_id.
2. gate2_servicio.py: modo demo OFFLINE, inspeccionar índice existente SIN Gemini, indexar explícito, recuperar real y responder real. Los últimos usan la API opcionalmente.
3. tests/test_gate2_servicio.py: 18 pruebas offline de contratos, seguridad y trazabilidad.
4. tests/test_gate2_e2e_chroma.py: integración de Chroma REAL temporal, embeddings y LLM FICTICIOS, 5 fuentes, 10 chunks y citas. Sin tocar vectorstore/ original.
5. .github/workflows/pruebas-offline.yml: prueba E2E Chroma incorporada al CI.
6. docs/U2_8_GATE2_INTEGRACION_BOOKING_CORE.md: arquitectura, comandos y límites.

La validación CI del commit 4811dad terminó exitosamente en ambos jobs, incluyendo el E2E Chroma temporal. Ver sección de evidencia CI al final.

## Comandos previstos para ejecutar en Windows

~~~powershell
cd C:\Users\nbello\dev\especializacion-ia-2026
git status --short
git fetch origin
git switch --track origin/feature/u2-8-gate2-rag-booking-core-ai
git pull --ff-only

.\venv\Scripts\python.exe -m pip check
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_gate2_servicio.py" -v
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_gate2_e2e_chroma.py" -v
.\venv\Scripts\python.exe gate2_servicio.py --modo demo
$LASTEXITCODE
.\venv\Scripts\python.exe gate2_servicio.py --modo inspeccionar
$LASTEXITCODE
git status --short
~~~

Si una suite Chroma termina SKIPPED por dependencias, no equivale a prueba E2E; instalar requirements-rag.txt en venv académico. No subir .env, vectorstore/ ni el archivo local verificar_tuning.py.

## Próximos criterios y límites

- Validar CLI y tests en Windows.
- Leer rúbrica S1 y actividad Core oficiales antes de decidir si se requieren endpoints HTTP/FastAPI, otro formato o un nuevo servicio.
- Hacer recuperación y generación con Gemini REAL desde la sesión local autorizada cuando corresponda, para demostrar funcionalidad en vivo.
- Validar citas semánticamente y abstención ante preguntas fuera del corpus.
- El gate BC-02 solo detecta firmas regex conocidas, NO todos los ataques.
- Mantener v2 de prompt B32 como propuesta, sin instalarla en un backend real.
- **Aún no se ha entregado Gate2 ni recibido su nota**.
- Tiempo efectivo de estudio: no informado, no inferir.

## Resultado CI confirmado (GitHub Actions, 26/11/2026)

- [Workflow Gate 2 / commit 4811dad](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/45906945875): ambos jobs finalizaron **SUCCESS**.
- Job general: `python -m unittest discover -s tests -p "test_*.py" -v` → **313 tests ejecutados / OK (30 skips por dependencias opcionales)**; incluye los 18 tests del servicio Gate2. La suite Chroma aparece omitida en ese job SIN dependencias RAG, como corresponde.
- Job RAG con requirements-rag.txt: `python -m unittest discover -s tests -p "test_gate2_e2e_chroma.py" -v` → **Ran 1 test in 1.071s / OK**, sin omisiones. El test crea Chroma real temporal, lo reabre y comprueba respuesta citada con embeddings y LLM sintéticos.
- **No equiparar el CI con Gemini real ni con Windows.** La ejecución de recuperación y generación real sigue pendiente. La rúbrica oficial S1 sigue sin estar disponible.
