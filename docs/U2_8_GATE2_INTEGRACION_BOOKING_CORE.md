# U2.8 — Gate 2: integración y orquestación RAG | Booking Core AI

**Inicio:** 26/11/2026.
**Repo:** nicolasbellov/especializacion-ia-2026.
**Rama:** feature/u2-8-gate2-rag-booking-core-ai.
**Estado:** implementación preliminar versionada y CI offline **SUCCESS** (incluido E2E Chroma real temporal); **sin evidencia Windows ni Gemini real todavía**.

## 1. Lo que dice Skillnest y lo que falta

El índice del programa compartido el 26/11/2026 fija el objetivo «Integrarás y validarás un servicio modular de IA con RAG, verificando su funcionamiento de extremo a extremo» y enumera tres páginas:

1. S1 / Repaso de la rúbrica del Gate 2 y su exigencia funcional (id=20481).
2. S1 / Verificación funcional en vivo: indexar, recuperar y responder (id=20482).
3. S1 / Gate 2 - Integración y orquestación [Actividad core] (id=20483).

**Importante:** por ahora NO tenemos el texto detallado de la rúbrica ni la consigna de entrega Core; los enlaces de Skillnest no fueron accesibles externamente. Por lo tanto los criterios técnicos listados a continuación son **provisionales nuestros**, no requisitos confirmados por Skillnest. Ajustar al recibir la fuente oficial.

## 2. Arquitectura que se reutiliza

- B24/L3: cinco documentos propios 100% ficticios; 10 chunks; Chroma SQLite en vectorstore/ y manifiesto con huella/IDs; indexación idempotente.
- B26/L3: abrir_vectorstore, validación de metadata e IDs, retriever semántico y citas de fuentes enumeradas.
- B31/L2-L3: roles System/Human, delimitación del contexto, detección de inyección, JSON logs con trace_id y registro de usage_metadata.
- B32: registro de prompts v1/v2 y matriz de riesgos. La v2 está propuesta y NO activa en el servicio real.

### Servicio de la nueva unidad

- [gate2/servicio.py](../gate2/servicio.py): orquesta recuperador inyectable -> filtro anti-inyección -> contexto numerado -> generador inyectable -> tokens -> citas.
- [gate2_servicio.py](../gate2_servicio.py): CLI con modos explícitos.
- [tests/test_gate2_servicio.py](../tests/test_gate2_servicio.py): contratos y seguridad sin red.
- [tests/test_gate2_e2e_chroma.py](../tests/test_gate2_e2e_chroma.py): indexación/reapertura/recuperación/generación en **Chroma real TEMPORAL** con embeddings y LLM ficticios, sin tocar vectorstore/ ni consumir Gemini. Usa un proceso hijo para liberar SQLite antes de limpiar en Windows.
- [.github/workflows/pruebas-offline.yml](../.github/workflows/pruebas-offline.yml): agrega E2E Chroma al job RAG del CI.

~~~text
               Chroma persistido B24/L3 (5 fuentes, 10 chunks)
                                 |
                        retriever(k) B26
                                 |
                        Document + metadata
                                 |
                  filtro de inyección B31
                       /             \
                 sospechoso          limpio
                     |                  |
                BC-02 BLOQUEO      contexto [n]
                 sin generar        system/human
                     |                  |
             REQUIERE_REVISION       LLM (opt-in)
                                        |
                                   AIMessage
                                        |
                                 uso/tokens B31
                                        |
                                 validación citas
                                  /          \
                              inválidas     válidas
                                 |             |
                            REVISAR_CITAS    RESPONDIDA
~~~

**Nuevo control académico BC-02:** si aparece CUALQUIER documento sospechoso, bloquea la generación aunque otros documentos sean legítimos. Esto mejora el comportamiento de B31/L3, que descartaba y continuaba. No constituye una revisión humana productiva; el resultado queda retenido para futura integración.

La comprobación de citas es sintáctica: el número debe existir en el mapa recuperado. **No prueba por sí sola que la fuente respalde semánticamente la afirmación**.

## 3. Comandos de instalación y validación (Windows)

El estudiante tiene el repositorio local en C:\Users\nbello\dev\especializacion-ia-2026, con el entorno venv existente. El archivo local no rastreado verificar_tuning.py se conserva intacto.

Primero, pasar desde la rama U2.7 a la nueva rama Gate2 y verificar funcionamiento SIN Gemini:

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

Si falta Chroma, instalar las dependencias SOLO en venv académico desde requirements-rag.txt. Un test omitido por falta de Chroma NO acredita E2E.

### Modos de API reales — solo por decisión explícita del estudiante

~~~powershell
# Solo si falta el índice: primera indexación puede consumir cuota Gemini.
# .\venv\Scripts\python.exe gate2_servicio.py --modo indexar

# RAG parcial: embedding REAL de la pregunta, Chroma real, SIN modelo chat.
# .\venv\Scripts\python.exe gate2_servicio.py --modo recuperar --pregunta "¿Qué se requiere para reprogramar una cita?" --k 3

# RAG completo: embedding de consulta + respuesta Gemini, consume cuota/API.
# .\venv\Scripts\python.exe gate2_servicio.py --modo responder --pregunta "¿Qué se requiere para reprogramar una cita?" --k 3
~~~

Los tres modos NO consultan ni modifican reservas reales de Booking Core. Requieren GEMINI_API_KEY local en .env, nunca subirla al repositorio ni compartirla. No reindexar por cada pregunta.

## 4. Criterios técnicos PROVISIONALES

1. Abrir el índice existente y verificar 5 fuentes, 10 chunks, IDs y metadata, SIN reindexar.
2. Dos preguntas diferentes con contextos/citas que se puedan inspeccionar.
3. Respuesta real del LLM con citas y revisión manual de al menos una afirmación frente al documento original.
4. Abstenerse de inventar precio real, disponibilidad o confirmación de reservas.
5. Ataque indirecto detectado: detener respuesta y registrar evento BC-02.
6. Consumo real de tokens SOLO si el proveedor informa usage_metadata; los tests sintéticos se etiquetan como simulados.
7. Tests offline y Chroma temporal pasando en Windows; verificar CI.
8. Confrontar con la rúbrica y consigna oficiales antes de afirmar cumplimiento o enviar.

## 5. Limitaciones

- Demo offline: 5 documentos propios leídos, pero **recuperador y LLM SIMULADOS**, no embeddings reales.
- Test E2E Chroma: motor Chroma y persistencia REALES, vectores y LLM sintéticos, no llamada Gemini.
- Inspeccionar: valida índice persistido; no modifica bases.
- Real: usa servicios Gemini bajo opt-in y puede consumir cuota. Las respuestas no implican acceso a disponibilidad comercial.
- No hay API HTTP/FastAPI todavía: se ofrece servicio Python modular + CLI. Si la rúbrica pide endpoints REST, incorporarlos después de leerla.
- No hay conexión al backend real, autenticación productiva ni permisos por tenant.
- El prompt v2 sigue siendo solo propuesta. La defensa regex y validación sintáctica de citas no garantizan seguridad general.

## 6. Bitácora y punto de continuidad

- Inicio Gate2: 26/11/2026.
- Base U2.7: desarrollo y entrega Core completados; evaluación del instructor pendiente.
- Publicado: paquete modular, CLI, test offline, test Chroma temporal y paso CI.
- **Pendiente:** rúbrica oficial S1, evidencia de Windows, API Gemini real, revisión de citas y entrega Gate 2 Core.
- Tiempo efectivo de estudio: no informado.
- Continuación: cambiar a rama Gate2, ejecutar tests/demo/preflight y compartir resultados; después leer rúbrica S1 y ejecutar la verificación real.

## Resultado CI confirmado (GitHub Actions, 26/11/2026)

- [Workflow Gate 2 / commit 4811dad](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/45906945875): ambos jobs finalizaron **SUCCESS**.
- Job general: `python -m unittest discover -s tests -p "test_*.py" -v` → **313 tests ejecutados / OK (30 skips por dependencias opcionales)**; incluye los 18 tests del servicio Gate2. La suite Chroma aparece omitida en ese job SIN dependencias RAG, como corresponde.
- Job RAG con requirements-rag.txt: `python -m unittest discover -s tests -p "test_gate2_e2e_chroma.py" -v` → **Ran 1 test in 1.071s / OK**, sin omisiones. El test crea Chroma real temporal, lo reabre y comprueba respuesta citada con embeddings y LLM sintéticos.
- **No equiparar el CI con Gemini real ni con Windows.** La ejecución de recuperación y generación real sigue pendiente. La rúbrica oficial S1 sigue sin estar disponible.
