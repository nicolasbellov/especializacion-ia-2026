# U2.5 · Bloque 26 / Lección 3 — Recuperación y prompt dinámico con citas (Booking Core AI)

**Fuente oficial:** Skillnest «Desarrolla tu recuperación y tu prompt dinámico [Actividad práctica]», recibida el 14/11/2026. La actividad exige código versionado y tres escenarios de validación (dos consultas, abstención y cita verificada). **No atribuir entrega en plataforma ni aprobación formal solo por commitear.**

## 1. Qué pide Skillnest

- Partir de **un corpus propio persistido** del Bloque 24, con embeddings REALES Gemini y metadata.fuente.
- Recuperar mediante as_retriever(...).invoke(...), con k recomendado de 3 a 4, y construir un prompt que contenga la pregunta original exacta, chunks enumerados [1]...[k] y un mapa n -> fuente.
- Instruir al modelo a responder solo con el contexto, citar cada afirmación y **abstenerse** si falta evidencia.
- Comprobar **dos preguntas diferentes** y que los contextos recuperados cambian; después una pregunta **sin respuesta en el corpus** y verificar manualmente la abstención del modelo; y finalmente comprobar **una cita [1] de una respuesta REAL** contra su documento de origen.
- Versionar el código y dependencias; no versionar bases Chroma, credenciales ni datos reales. El curso propone git add recuperacion.py requirements.txt, git commit y git push. Los cambios se publican desde el conector GitHub en la rama existente; las dependencias ya están declaradas en requirements.txt y requirements-rag.txt.

### Diferencia material con el texto genérico de la consigna

Skillnest presupone que el índice original B24 no tiene metadatos ni IDs y propone **borrar vectorstore/**, para reconstruir un corpus genérico de 5 textos. **Ese supuesto NO aplica a nuestro repositorio:** el propio script indexar_corpus.py (B24/L3) ya creó 10 chunks reales Gemini desde **5 archivos diferentes**, con metadata.fuente, metadata.titulo, metadata.origen=FICTICIO_ACADEMICO, metadata.indice_chunk, IDs SHA-256 estables y manifiesto de integridad.

**Decisión propia documentada:** no borrar, renombrar ni reindexar vectorstore/. La colección existente es booking_core_b24_l3. El nuevo script consulta sus documentos y comprueba la metadata del índice sin reescribir los embeddings. Así se satisface el objetivo de la lección con el **verdadero corpus propio** y se evitan costos, duplicados y pérdida de evidencia. La carpeta está ignorada por Git.

## 2. Diseño del script de entrega

**Código:** [recuperacion.py](../recuperacion.py).  
**Pruebas:** [tests/test_recuperacion_b26_l3.py](../tests/test_recuperacion_b26_l3.py).

El flujo implementa:

1. comprobar_fuentes → validar SIN API que Chroma SQLite/manifiesto ya existen, colección correcta, al menos 5 fuentes, IDs sin duplicados y metadata.fuente presente en **todos los chunks**, procedentes del corpus FICTICIO_ACADEMICO.
2. abrir_vectorstore → conectar mediante Chroma(collection_name="booking_core_b24_l3", persist_directory=RAIZ/"vectorstore", embedding_function=GoogleGenerativeAIEmbeddings(...)). No usa from_documents ni add_documents.
3. construir_resultado → retriever.as_retriever(search_kwargs={"k": k}).invoke(pregunta), formatear_contexto de la lección anterior, prompt oficial con restricciones y mapa citas local. Rechaza resultados sin fuente, pero no inventa números ni cambia la pregunta.
4. construir_prompt(pregunta, persist_directory, k=3) → interfaz solicitada por Skillnest: devuelve (prompt, citas).
5. respuesta_llm (optativa, solo al elegir el modo responder) → ChatGoogleGenerativeAI usando el modelo de conversación del proyecto, según GEMINI_MODEL o su valor por defecto; genera una respuesta REAL a partir del prompt. mostrar_citas_respuesta extrae números de cita y comprueba si existen en el mapa, pero NO certifica semánticamente sus afirmaciones.

**Nota técnica:** cuando el índice tiene menos de k chunks, Chroma devuelve hasta k, no exactamente k. Aquí tenemos 10 chunks y se recomienda k=3. Los números [n] son locales a cada consulta; nunca se asume que [1] identifica siempre el mismo documento.

## 3. Ejecución recomendada desde PowerShell

En la raíz del repositorio, con .venv activo y sin publicar la clave:

~~~powershell
git status --short
git pull --ff-only

# Validar integridad y metadatos locales SIN llamada Gemini
python recuperacion.py --modo inspeccionar

# Ejercitar unidad y contratos con mocks; NO usa API
python -m unittest discover -s tests -p "test_recuperacion_b26_l3.py" -v

# Escenario 1: dos preguntas diferentes + ambos prompts completos.
# Reutiliza el índice original; usa 2 llamadas a embeddings de pregunta
python recuperacion.py --modo comparar --k 3

# Escenario 2: pregunta que corpus NO puede resolver (consulta real + chat real)
python recuperacion.py --modo responder --pregunta "¿Cuál es el precio real de un corte hoy en AES Barber?"

# Escenario 3: respuesta real con citas, cotejar [1] con el chunk impreso
python recuperacion.py --modo responder --pregunta "¿Qué necesito para reprogramar una cita?"

git status --short
~~~

Opcional: para ver un único prompt y mapa sin llamar al chat, usar python recuperacion.py --modo recuperar --pregunta "¿Cómo cambiar una cita?". Repetir esa consulta sí genera otro embedding y consume cuota. **La prueba de salud de GEMINI_API_KEY/3072 sugerida por el curso es redundante** aquí: se verificó previamente en B24/B26/L1 que Gemini real funciona; los modos comparar/responder constituyen la validación de esta actividad. Si falla API key o aparece 429, revisar la guía de troubleshooting B25; no reindexar el corpus.

## 4. Condiciones para cierre técnico (NO suponer PASS de antemano)

| Escenario | Criterio de aceptación | Evidencia por recibir |
| --- | --- | --- |
| Preflight B24 | Fuente=5; chunks=10; metadata e IDs válidos; no escrituras al índice | Consola modo inspeccionar |
| Suite offline | Tests sobre corpus académico, prompts, mapa, cambio de consultas y ausencia de fuente | Resultado completo unittest |
| Dos preguntas | Dos embeddings reales; contextos distintos según pregunta de reprogramación vs privacidad; prompts numerados, mapa sin "desconocida" | Salida modo comparar |
| Fuera del corpus | Pregunta sobre **precio real** en AES Barber: el LLM debe reconocer que el corpus ficticio no ofrece datos reales; **no puede inventar un precio** | Respuesta real modo responder y evaluación manual |
| Cita real | Al menos una afirmación sustantiva sustentada por [1] (u otra cita) y contrastada con el chunk/documento correcto (ej. 03_reprogramacion.md) | Respuesta del LLM, mapa, texto de fuente y juicio manual |
| Integridad final | Índice no reindexado, git status limpio y ninguna clave o base vectorial publicada | Consola Git |

**Advertencia:** verificar que una referencia [1] exista en el mapa es un control de **trazabilidad sintáctica**; la comprobación de que esa fuente realmente respalda la afirmación exige una lectura o evaluación semántica aparte. Tampoco dos casos exitosos prueban precisión/recall o funcionamiento productivo: eso corresponde al Bloque 27.

## 5. Aplicación arquitectónica a Booking Core AI

Los cinco documentos son **políticas simuladas**: servicios, disponibilidad, reprogramación, cancelación y privacidad. Chroma no tiene agenda real, precios vigentes, horarios ni datos personales. Un asistente auténtico requiere APIs transaccionales autenticadas y autorizadas por tenant, revisión de acciones sensibles y auditoría. **No conectar este laboratorio a clientes reales ni hacer afirmaciones comerciales reales**.

El prompt pide al LLM que use las fuentes recuperadas y se abstenga si los documentos no lo respaldan; esa instrucción **reduce** el riesgo de alucinación, pero no garantiza ausencia de respuestas falsas. El corpus recuperado debe tratarse como datos no confiables, no instrucciones privilegiadas.

**CI actual:** [GitHub Actions #43557252216](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43557252216) completó ambos jobs, incluyendo **12/12 B26/L3 tests offline** con corpus propio, metadata y IDs existentes; regresiones **27/27 B24, 7/7 B25/L1, 11/11 B25/L2, 8/8 B25/L3, 9/9 B26/L1, 11/11 B26/L2**. Es una validación de código y mocks; **no** implica consultas Gemini reales ni que el modelo haya justificado o rechazado respuestas adecuadamente.

## 6. Estado académico y entrega

- **Previo comprobado:** B24 3/3, B25 3/3 y B26/L1-L2 2/3; U2.5 **8/15**.
- **Actividad B26/L3:** **validada técnicamente en Windows el 14/11/2026**, con los tres escenarios de la consigna y evidencia de las respuestas reales de Gemini. **12/12 tests Windows (`Ran 12 tests in 4.759s / OK`)**, comparación de dos contextos distintos, abstención ante un precio real inexistente en el corpus y comprobación manual de la cita `[1]` vinculada a `03_reprogramacion.md`. Se corrigió además el extractor de citas agrupadas `[1, 3]`; la CI de esa regresión se documenta por separado. **B26 3/3; U2.5 9/15**. La **entrega en Skillnest aún debe confirmarse**; la versión en GitHub no equivale a envío institucional.
- **Evidencia pública:** rama feature/u2-5-b24-rag-booking-core y PR #26, que permanece **draft, sin merge** a main.
- **Próximo bloque anunciado:** Bloque 27 — evaluación de recuperación RAG (precisión y exhaustividad), detalles pendientes de su lección oficial.

## 7. Validación definitiva Windows · 14/11/2026

**Entorno y Git:** `(.venv)` activo; `git status --short` vacío antes y después. `git pull --ff-only` sincronizó la rama mediante fast-forward **`3783f42..787dbcb`**. No se crearon ni subieron `.env`, `vectorstore/` ni índices de Chroma.

**Preflight SIN API:** `python recuperacion.py --modo inspeccionar` → colección **`booking_core_b24_l3`**, **5 fuentes**, **10 chunks**, todos con `metadata.fuente` e IDs existentes. Se reutilizó el índice Gemini creado en B24/L3, **sin borrar ni reindexar**.

**Suite Windows antes de la corrección de referencias agrupadas:** `python -m unittest discover -s tests -p "test_recuperacion_b26_l3.py" -v` → **12/12 OK**, `Ran 12 tests in 4.759s`. Tests con mocks, distintos de las consultas reales.

### Escenario 1: dos preguntas, dos recuperaciones Gemini reales

| Pregunta exacta | Fuentes devueltas (k=3) | Primer resultado |
| --- | --- | --- |
| «¿Cómo puedo cambiar mi cita para otro día?» | `03_reprogramacion.md`, `03_reprogramacion.md`, `04_cancelacion.md` | Reprogramación |
| «¿Cómo se separan los datos de clientes de distintas empresas?» | `05_privacidad.md`, `02_disponibilidad.md`, `05_privacidad.md` | Privacidad / aislamiento |

Ambas salidas incluyeron prompts dinámicos completos con **tres bloques [1]–[3] y las preguntas intactas**. La consola confirmó **`¿Cambió el contexto entre preguntas?: True`**. Es evidencia real de variación semántica para estas dos preguntas, no medición general de calidad.

### Escenario 2: información insuficiente y abstención del LLM

Pregunta: «¿Cuál es el precio real de un corte hoy en AES Barber?». El retriever devolvió `{1: "01_servicios.md", 2: "04_cancelacion.md", 3: "01_servicios.md"}`.

**Respuesta Gemini real observada:**

> El contexto no alcanza para responder, ya que las notas indican explícitamente que nunca se deben inventar precios reales [1, 3] y que el catálogo de demostración es un ejemplo ficticio que no establece los servicios ni precios disponibles [1].

**Interpretación:** **PASS de abstención**. Gemini no inventó precio ni simuló una consulta transaccional; los chunks [1] y [3] corresponden efectivamente al archivo ficticio `01_servicios.md`.

**Incidente de trazabilidad B26-CITE-001:** el parser previo de `mapear_citas` solamente reconocía referencias individuales como `[1]`, por lo que omitió la referencia **`[1, 3]`** y reportó solo la última `[1]`. Esto **no descalifica la respuesta** ni implica fuente inválida; sí es un defecto de extracción que requiere corrección para auditoría. Se corrigió en `citas_demo.py`, función compartida por B26/L2 y B26/L3, para reconocer números individuales y grupos separados por comas y espacios, respetando orden y repeticiones. Se añadieron tests de regresión tanto al test de B26/L2 como al de B26/L3. **La respuesta Gemini original se conserva como evidencia; no requiere consumir cuota nuevamente para arreglar el parser**.

### Escenario 3: trazabilidad y comprobación manual de la fuente

Pregunta: «¿Qué necesito para reprogramar una cita?». El mapa fue `{1: "03_reprogramacion.md", 2: "04_cancelacion.md", 3: "03_reprogramacion.md"}`.

**Respuesta Gemini real:**

> Para mostrar alternativas para cambiar una cita, haría falta verificar la identidad, la titularidad de la reserva y la disponibilidad actual a través del backend autorizado [1]. Después de presentar las opciones, cualquier operación de modificación requeriría una confirmación válida del usuario y una respuesta exitosa de la API transaccional [1].

**Contraste manual, PASS:** el contenido del chunk [1] impreso en la consola y el archivo original `data/corpus_b24_l3/03_reprogramacion.md` incluyen explícitamente esos requisitos. La referencia `[1]` fue extraída y mapeada a `03_reprogramacion.md` en ambas afirmaciones. Se verificó **respaldo textual**, no solo existencia de un número.

**Límite observado:** en algunos top-k aparecen dos chunks del mismo archivo y otro del tema de cancelación. Eso es razonable en este caso, pero será una cuestión medible en el **Bloque 27 (precision/recall)** y no debe interpretarse como ranking óptimo.

### Cierre técnico y entrega institucional

- **Bloque 26: 3/3 lecciones completadas técnicamente; U2.5: 9/15**.
- Código/versionado: `recuperacion.py`, tests, corpus ficticio y `requirements.txt` + `requirements-rag.txt` ya estaban en la rama y PR #26. El índice Chroma y las credenciales permanecen fuera de Git.
- **No consta entrega en Skillnest ni nota/aprobación oficial**. Usar el enlace público al script o PR al presentar el ejercicio y registrar el acuse de plataforma por separado.
- Horas de inicio/término y tiempo efectivo de estudio: **no informados**. Los 4.759 segundos son únicamente pruebas automatizadas.
- **Punto de continuación:** Bloque 27, evaluación de recuperación RAG, comenzando por la consigna oficial que comparta el estudiante.
