> **Actualización más reciente:** Gate 2 técnicamente cerrado: instalación limpia, 4/4 criterios PASS, incremental PASS, CI SUCCESS, Gemini real con cita contrastada, rechazo interactivo y abstención real PASS. Autoevaluación 81,0%. Entrega institucional registrada el 26/11/2026; evaluación pendiente. Los apartados históricos siguientes conservan el estado de etapas anteriores.

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

## Evidencia Windows y Gemini real — 26/11/2026

Evidencia aportada por el estudiante desde PowerShell, commit de código validado `42dcf9d`.

- Entorno anterior: 18/18 pruebas del núcleo (0,073 s), pero E2E Chroma omitido y modos reales fallidos por dependencia ausente. Se resolvió con instalación limpia de `.venv-gate2`, Python 3.12.8, requirements.txt completo, langchain-chroma 1.2.0, chromadb 1.5.9, langchain-core 1.8.5, langgraph 1.2.24, langchain-google-genai 4.4.3 y pytest 9.2.0. `pip check`: No broken requirements found. Clave definida, .env ignorado, sin exponer valor.
- Cuatro pruebas no compensables: `4 passed in 9.12s` (pipeline, fuentes, logs sin contenido crudo/PII ficticia y pausa/reanudación con aprobación y rechazo).
- Incremental: `Ran 1 test in 21.723s / OK`; Chroma temporal con corpus copiado, embeddings sintéticos, conserva vectores y no duplica. No se alteró el índice real.
- Ensayo: índice simulado creado con 5 documentos y 10 chunks. Dos ejecuciones posteriores reutilizaron índice sin re-embedding, ambas con respuesta citada, trazas distintas y supervisión demo que conservó DEMO-001 confirmada. El ataque ficticio activó BC-02, tres patrones, REQUIERE_REVISION antes del LLM. Limitación: la consulta simulada de privacidad citó 02_disponibilidad.md; el ensayo comprueba contratos del flujo, no relevancia semántica ni calidad de Gemini.
- Preflight real: 5 fuentes/10 chunks, entorno listo. Corrida real `servicio_rag.py --modo real --supervision interactiva`, modelo gemini-3.5-flash-lite, prompt v3-gate2 SHA-256/12 `8a9459e020b8`, trace_id `gate2-a5f73d7e84764ce1`, estado RESPONDIDA. Chroma reutilizado, 3 chunks, 0 descartados, citas [1] y [3] de 03_reprogramacion.md.
- Contraste documental efectuado: 03_reprogramacion.md confirma distinción entre información y transacción, identidad/titularidad/disponibilidad mediante backend autorizado, confirmación válida del usuario y resultado exitoso de API; asimismo confirma que RAG no autoriza mover una cita y que el asistente académico no gestiona reservas reales. La respuesta real se ajusta a esa fuente.
- Latencias reales (una muestra): apertura y validación de índice 5366,464 ms; recuperación 11680,548 ms; generación 1927,341 ms; consulta total 13612,390 ms (sin apertura inicial). La recuperación domina esta muestra; no inferir un rendimiento promedio. Tokens reales 419 entrada, 137 salida, 556 total; estimación ficticia USD 0,0000967 de chat, no facturación ni costo de embeddings.
- Advertencia del proveedor: el modelo usa valores de muestreo fijos e ignora temperature; no fue un error de ejecución y no se debe prometer generación determinista.
- Supervisión interactiva: interrupt antes de cancelar DEMO-001, resultado de consola rechazado, estado confirmada, aprobado=False, ejecutada=False, PASS de pausa y reanudación. La aprobación positiva se verificó en test_4, no como aprobación humana manual en esta corrida. No hay autenticación de operador ni reservas reales.
- Código de salida final 0; git status solo archivo preexistente no rastreado verificar_tuning.py, preservar.
- [CI de la corrección](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/45907697658): ambos jobs SUCCESS, incluidas las cuatro pruebas, E2E Chroma, incremental, ensayo y servicio simulado. No sustituye la evidencia Windows ni la corrida real.
- Autoevaluación propia 81,0%, cuatro criterios PASS. La comprobación adicional de abstención real también fue validada; ver evidencia de cierre a continuación. Gate 2 no enviado.

## Cierre técnico final — abstención Gemini real (26/11/2026)

- Evidencia de PowerShell aportada por el estudiante: fast-forward `42dcf9d..07bcd69`; cinco archivos de documentación y autoevaluación sincronizados.
- Ejecución `servicio_rag.py --modo real --supervision ninguna` con pregunta sobre el precio real vigente de un corte en AES Barber y las horas libres de mañana.
- Trace ID `gate2-f15a7843839f4f6f`, prompt `v3-gate2` SHA-256/12 `8a9459e020b8`, `simulado=false`, 5 fuentes/10 chunks, índice existente sin re-embedding; 3 chunks recuperados, 0 descartados.
- **PASS funcional de abstención:** estado RESPONDIDA, pero el contenido explícitamente indica que RAG no confirma precios reales ni disponibilidad; no entrega precios ni franjas inventadas. Citas [1] `01_servicios.md` y [3] `02_disponibilidad.md`, contrastadas con ambos documentos originales del repositorio. El primero prohíbe inventar precios y exige catálogo autorizado; el segundo establece que la disponibilidad proviene del backend transaccional en tiempo de consulta.
- Latencias observadas: apertura/validación del índice 15180,217 ms; recuperación 1118,188 ms; generación 1915,507 ms; consulta total 3043,731 ms, excluida apertura inicial. Una muestra, no benchmark promedio.
- Tokens reales: 545 entrada, 89 salida, 634 total. Costo didáctico estimado de chat USD 0,0000901 según tarifas ficticias B28; no es facturación real ni incluye embeddings. Advertencia de temperature ignorada por Gemini, sin fallo.
- Código de salida inmediato 0. `rubrica_gate2.py`: 81,0% de autoevaluación, cuatro no compensables PASS, `LISTO PARA ENTREGAR SEGÚN AUTOCHEQUEO: True`. `git status --short`: únicamente `?? verificar_tuning.py` en la salida completa observada; preservar.
- **Veredicto:** Gate 2 técnicamente completado y entregado en Skillnest el 26/11/2026; nota y aprobación institucional pendientes. La prueba negativa es una muestra de comportamiento, no garantía universal de abstención. Persisten los límites académicos: no hay backend real, autenticación de revisores, persistencia durable de supervisión ni revisión humana BC-02 completa.
- Siguiente acción: iniciar Módulo 3 / U3.1 con la fuente oficial. El acuse de entrega ya fue aportado.
- Tiempo efectivo de estudio: no informado; no inferir de marcas de tiempo de las consultas.

## Confirmación institucional — 26/11/2026

- Evidencia: captura de Skillnest LifeCycle aportada por el estudiante, actividad «Bloque S1 - Gate 2 - Integración y orquestación [Core]», estado «Entrega registrada», enviada el 26/11/2026 y en revisión por el instructor.
- **Gate 2 entregado institucionalmente; calificación y aprobación oficial pendientes.** Autoevaluación propia 81,0%, cuatro no compensables PASS; no equivalen a una nota oficial.
- Versión de entrega recomendada: `ccd05d4bae11bf0e288c1309a5ee966096a5b924`. El acuse confirma el envío, no verifica el URL exacto presentado. Se mantiene inmutable la versión preparada; esta actualización solo documenta el acuse, sin modificar código ni reenviar la tarea.
- Próximo punto académico: Módulo 3 — Integración profesional, U3.1 Diseño funcional del proyecto según perfil de salida, Bloque 33 / De la idea al alcance: problema, requerimientos, MVP. Revisar el material oficial antes de implementar.
- Tiempo efectivo de estudio no informado. Sin confirmación de sincronización local posterior al commit de entrega.
