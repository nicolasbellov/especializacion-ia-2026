> **Actualización posterior:** rúbrica oficial S1, ensayo y Core recibidos el 26/11/2026. Se supersede la preparación provisional con el cierre de requisitos descrito al final y en [U2_8_GATE2_CORE_ENTREGA.md](U2_8_GATE2_CORE_ENTREGA.md).

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

## Handoff actualizado tras recepción de rúbrica oficial

- Pesos oficiales 25/15/10/15/15/20, mínimo 80%, cuatro no compensables, máximo tres oportunidades. La consigna exige índice incremental, métricas propias, costo/latencia, decisión de personalización, logging, filtro, versiones, supervisión real, matriz >=5 y README reproducible.
- Reutilizados reportes B27 reales k3 0.306/1.000, k5 0.183/1.000; 5 corridas B28 reales; RAG 2 frente a PEFT 1 y fine-tuning 0.
- Publicado: servicio_rag.py, gate2/indice.py, gate2/supervision.py, gate2/prompt.py, gate2/medicion.py, verificar_entorno.py, test_gate2.py (4 tests), ensayo_gate2.py, test incremental, matriz Gate2, rubrica_gate2.py, README y portada Core. No se modificó la rama ya entregada U2.7 ni Booking Core productivo.
- Se agregó v3 efectiva al registro independiente Gate2; v2 B32 permanece propuesta. BC-01 ahora pausa y reanuda cancelación ficticia; BC-02 bloquea y requiere revisión sin ejecutar LLM. Controles productivos pendientes.
- Autoevaluación provisional 81.0%; cuatro no compensables None hasta corrida final. CI del código nuevo pendiente de verificar; no declarar listo para entregar.
- Próximo paso Windows: git fetch/switch rama Gate2, pull, crear .venv-gate2 desde el Python del venv previo; instalar requirements.txt, pip check, ejecutar preflight, pytest test_gate2.py -v, suite incremental, ensayo y servicio simulado dos veces. Real: verificar entorno, servicio_rag.py --modo real --supervision interactiva; responder n o s para DEMO-001, contrastar cita y enviar evidencia. Mantener verificar_tuning.py sin rastrear; no borrar ni publicar .env/vectorstore.
- Estado institucional: se recibió captura del formulario Gate 2, todavía sin envío ni calificación. U2.7 registrada, evaluación pendiente.
