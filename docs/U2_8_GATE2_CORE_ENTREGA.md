# Gate 2 · Integración y orquestación | Booking Core AI

**Programa:** Especialización IA 2026 · Skillnest / Accenture / CChIA.
**Fecha:** 26/11/2026 · **Oportunidad 1** (preparación).
**Repositorio académico:** nicolasbellov/especializacion-ia-2026.
**Rama:** feature/u2-8-gate2-rag-booking-core-ai.
**Estado:** instalación limpia y cuatro criterios PASS en Windows; Gemini real y rechazo interactivo validados; comprobación adicional de abstención real pendiente. No consta envío ni calificación institucional de Gate 2.

## 1. Alcance

Servicio académico modular de preguntas sobre políticas ficticias de barbería. Integra corpus propio, Chroma persistido, recuperación, filtro, contexto citado, generación, latencia/costo, auditoría y supervisión humana de una cancelación ficticia. No accede a clientes, disponibilidad ni reservas reales. No tiene conexión de escritura a Booking Core. El servicio no es una API HTTP ni un despliegue productivo; Skillnest admite un script Python.

Fuentes oficiales aportadas el 26/11/2026: S1, rúbrica (id 20481), ensayo funcional (20482) y actividad Core (20483). El umbral es 80/100 con cuatro criterios no compensables y hasta tres oportunidades. No basta una media superior a 80.

## 2. Rúbrica oficial y evidencias

| Dimensión | Peso | Artefacto / evidencia | Estado de evidencia |
| --- | ---: | --- | --- |
| Pipeline RAG funcional | 25% | [servicio_rag.py](../servicio_rag.py), [núcleo](../gate2/servicio.py), [indexación](../indexar_corpus.py), [actualización incremental](../gate2/indice.py) | Windows/Gemini real PASS; incremental Chroma PASS con embeddings sintéticos |
| Recuperación y citación | 15% | [etiquetas de 12 preguntas](../data/etiquetas_b27_l3_booking_core.json), [k=3](../resultados_evaluacion.txt), [k=5](../resultados_evaluacion_20261118-193607-330513.txt), [test_gate2.py](../test_gate2.py) | Métricas reales B27; cita de la corrida real contrastada con 03_reprogramacion.md |
| Costo, latencia y checklist | 10% | [mediciones B28](../registros_latencia_costo.jsonl), [estimación de costo](../gate2/medicion.py), [verificador](../verificar_entorno.py) | Mediciones reales previas; tarifas ficticias de B28, no facturación |
| Personalización justificada | 15% | [decisión fundamentada](../decision_personalizacion.md), [script de decisión](../decision.py) | RAG 2, PEFT 1, fine-tuning 0; sensibilidad y supuestos explícitos |
| Observabilidad y trazabilidad | 15% | [núcleo](../gate2/servicio.py), [logger](../logging_rag.py), [ensayo](../ensayo_gate2.py) | Auditoría JSON, trace_id, latencia y tokens reales; test de logs PASS |
| Seguridad, versionado y gobernanza | 20% | [filtro](../src/mitigacion_inyeccion_b31_booking_core.py), [registro histórico](../prompts/booking_core_ai/registro.json), [prompt activo v3](../prompts/booking_core_ai/registro_gate2.json), [supervisión BC-01](../gate2/supervision.py), [matriz Gate 2](../data/matriz_riesgos_gate2.json) | Rechazo interactivo y test aprobación/rechazo PASS; no hay controles productivos |

### Métricas de recuperación reales ya registradas

El corpus académico contiene cinco documentos y diez chunks, parámetros 550/80, con IDs SHA-256 estables. El dataset B27 contiene 12 preguntas (10 con evidencias etiquetadas, 2 sin respuesta factual); las métricas de recall se calculan en los casos evaluables. Dos corridas con Gemini Embedding fueron repetibles.

| Configuración | Precisión media | Recall medio | Repetibilidad |
| --- | ---: | ---: | --- |
| k=3 | 0,306 | 1,000 | PASS |
| k=5 | 0,183 | 1,000 | PASS |

Se elige k=3 por menor ruido con igual recall observado. No afirmar que estos números midan calidad semántica del texto generado ni precisión productiva.

### Costo y latencia: cinco registros reales B28 (18/11/2026)

| Caso | k | Latencia total (ms) | Tokens de chat |
| --- | ---: | ---: | ---: |
| SERV-01, primera corrida | 3 | 2403,19 | 332 |
| SERV-01, segunda corrida | 3 | 2985,67 | 331 |
| DISP-01 | 3 | 2850,92 | 374 |
| PRIV-01 | 3 | 1853,21 | 371 |
| SERV-01 | 6 | 2647,52 | 605 |

Fuente: registros_latencia_costo.jsonl. Los tiempos se midieron realmente con Gemini. El servicio Gate 2 además registra latencia de recuperación, generación y total por trace_id, tokens de AIMessage y costo estimado de generación usando las tarifas **FICTICIAS B28** (0,0001 USD por mil tokens de entrada y 0,0004 de salida); por ejemplo 308 entrada + 24 salida implica USD 0,0000404 estimados, **no un cargo real**, sin embeddings. Si el proveedor no informa tokens, el costo queda null. El modo simulado marca explícitamente sus tokens como sintéticos.

## 3. Los cuatro criterios no compensables

| Criterio | Prueba adaptada | Evidencia de cierre |
| --- | --- | --- |
| Pipeline E2E | test_1_pipeline_sin_excepciones | PASS Windows; corrida real Gemini exit 0 |
| Respuesta cita fuente | test_2_respuesta_cita_fuente | PASS Windows; respuesta real contrastada con fuente original |
| Logs sin PII ni contenido crudo | test_3_logs_sin_contenido_crudo | PASS Windows; auditoría JSON de aplicación sin correo ficticio ni contenido crudo en test |
| Supervisión humana real | test_4_supervision_pausa_y_reanuda | PASS Windows; interrupt y rechazo interactivo, aprobación positiva automatizada |

El punto BC-01 representa la acción de máximo riesgo (cancelación). El grafo bloquea antes de escribir estado, verifica el identificador ficticio y reanuda únicamente tras decisión booleana independiente. En --supervision interactiva el humano responde por consola; un timeout, ausencia de terminal o rechazo no autoriza cambios. Solo cambia un estado en memoria, no una cita real. B32 también incluye grafo de versionado separado. No se ha implementado autenticación de operadores ni persistencia durable.

El filtro B31 usa Document.page_content y metadata reales de LangChain. Si cualquier documento activa una firma sospechosa, se bloquea toda la generación (BC-02), incluso con otros fragmentos limpios. No se reanuda automáticamente; revisión de incidente completa pendiente. Las firmas regex son limitadas y pueden producir falsos positivos/negativos. Para respuestas factuales se exigen citas numeradas válidas; la abstención/bloqueo no se presenta como una respuesta factual.

## 4. Actualización incremental y persistencia

Por defecto el servicio crea si no existe y reutiliza el índice si el corpus no cambió. Nunca reindexa en cada pregunta. Si cambió el corpus, exige --actualizar explícitamente. La actualización compara contenido y metadata por ID, hace upsert solo de chunks nuevos/modificados, elimina IDs obsoletos y conserva los demás. Revisa datos finales y reemplaza manifiesto. Si falla a mitad, deja un marcador de bloqueo; no garantiza rollback transaccional y exige restaurar respaldo. No ejecutarla sobre el índice original sin respaldo ni con otros lectores/escritores.

[Prueba incremental](../tests/test_gate2_incremental.py): usa una copia temporal del corpus, modifica reprogramación, elimina privacidad, añade una nueva fuente, cuenta embeddings nuevos y comprueba una segunda actualización sin cambios. La base original vectorstore/ no se toca. Los embeddings sintéticos están aislados en .local/gate2_simulado/ o una carpeta temporal. El índice real conserva la colección del B24.

## 5. Instalación y reproducción desde cero

Ver [README](../README.md), que contiene los comandos de clonación, venv, dependencias completas y preflight. El índice real y .env no se versionan; el evaluador puede generar el índice con el corpus incluido. Simulado no necesita clave. Real requiere GEMINI_API_KEY válida y puede consumir cuota.

~~~powershell
.\.venv-gate2\Scripts\python.exe verificar_entorno.py --modo simulado --permitir-indice-nuevo
.\.venv-gate2\Scripts\python.exe -m pytest test_gate2.py -v
.\.venv-gate2\Scripts\python.exe -m unittest discover -s tests -p "test_gate2_incremental.py" -v
.\.venv-gate2\Scripts\python.exe ensayo_gate2.py
.\.venv-gate2\Scripts\python.exe servicio_rag.py --modo simulado
.\.venv-gate2\Scripts\python.exe servicio_rag.py --modo simulado
# Validación real (clave local, consume cuota):
.\.venv-gate2\Scripts\python.exe verificar_entorno.py --modo real --permitir-indice-nuevo
.\.venv-gate2\Scripts\python.exe servicio_rag.py --modo real --supervision interactiva
$LASTEXITCODE
.\.venv-gate2\Scripts\python.exe rubrica_gate2.py
~~~

Ejecutar una consulta fuera del corpus, por ejemplo precio real de AES Barber, sin inventar un dato. Comparar una afirmación de la consulta real contra el archivo fuente citado. En la interacción, n conserva DEMO-001 confirmada; s cancela solo la reserva ficticia en memoria. No ejecutar operaciones externas.

## 6. Autoevaluación propia

[rubrica_gate2.py](../rubrica_gate2.py): puntajes estimados 75/75/80/95/85/80, **81,0% ponderado**, no es nota del instructor. Se conservan los puntajes conservadores; los cuatro criterios quedan True por evidencia Windows y corrida real. Esto es un autochequeo, no aprobación institucional. Falta comprobar abstención real adicional antes del envío.

## 7. Registro de ensayo y entrega

26/11/2026: se integraron interfaces Document.page_content/metadata, se conservó la colección B24, se versionó el prompt efectivo v3 sin desplegar v2, se agregó costo estimado y fuentes al resultado, se implementó actualización incremental y un interrupt de BC-01. El CI preliminar de 4811dad fue exitoso con Chroma real y modelos simulados. El CI corregido, instalación Windows limpia, corrida Gemini, cita contrastada y decisión interactiva están registrados en la sección de evidencia.

**Estado institucional:** U2.7 entregada el 26/11 y en revisión. Gate 2 todavía no enviado. La pantalla de actividad contiene el formulario de entrega, no un comprobante. Tras la evidencia final, presentar enlace GitHub de esta portada fijado a un commit, no el repositorio productivo.

**Tiempo efectivo de estudio:** no informado.

## 8. Hallazgo del CI y corrección (26/11/2026)

- [CI 811976c](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/45907565060): job general **314 tests OK**, sin omisiones reportadas, incluye 18 del núcleo Gate2, E2E Chroma e incremental. El job de los cuatro criterios oficiales detectó **3 fallos y 1 PASS** (supervisión). No se considera aprobado el Gate.
- Causa: el generador simulado dividía el mensaje por la primera mención textual de las etiquetas de contexto, que está en la instrucción, no por las líneas que delimitan el contexto real. Así no encontraba referencias [n].
- Corrección en commit `91e5d7e`: buscar las etiquetas de contexto en sus propias líneas. Conserva el formato de prompt del proyecto y la prueba oficial sin relajar afirmaciones. [CI de la corrección](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/45907697658): ambos jobs SUCCESS, incluidas las cuatro pruebas.

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
- Autoevaluación conservada: 81,0% (estimación propia, no nota oficial), cuatro criterios de aceptación PASS según evidencia anterior. Como comprobación adicional antes de presentar, ejecutar pregunta sobre precio/disponibilidad real fuera del corpus con `--supervision ninguna` y comprobar abstención o retención sin inventar datos. Esta prueba adicional de generación real todavía no consta. Gate 2 no enviado; nota institucional pendiente.
