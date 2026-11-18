# U2.5 · B27/L3 — La recuperación de tu flujo RAG, evaluada con métricas

**Fuente Skillnest:** «La recuperación de tu flujo RAG, ya evaluada con métricas», Bloque 27, lección 3 (material recibido el 18/11/2026). Actividad de tipo «Ver» con **ejecución real** del retriever y **entrega en GitHub** de `evaluacion_recuperacion.py` y `resultados_evaluacion.txt`.

## 1. Requisitos oficiales

1. Crear **8–15 preguntas propias** sobre el corpus indexado; leer los chunks y etiquetar los **IDs relevantes antes de consultar el retriever**. Una pregunta puede tener varios relevantes o ninguno.
2. Recuperar con **embeddings Gemini reales**, la colección Chroma correcta, y k=3. Por pregunta, informar precisión@k, recall@k y promedios.
3. Guardar `resultados_evaluacion.txt` con fecha, `k`, `chunk_size`, `chunk_overlap`, resultados y promedios.
4. Ejecutar la evaluación **dos veces sin modificar el índice** y comprobar resultados idénticos. Cambiar a k=5 y repetir. Guardar las corridas para comparar futuras modificaciones.
5. Versionar el script y el **registro real** en GitHub. El siguiente bloque es **B28: costo y latencia de un RAG completo**.

En el ejemplo de Skillnest aparecen `doc0...doc4` y chunking `200/30`; **estos valores NO corresponden a nuestro índice**. El índice existente B24/L3 es `booking_core_b24_l3`, con **5 documentos, 10 chunks**, chunk_size **550**, overlap **80** y **IDs SHA-256**. No borrar ni reconstruir el vectorstore para imitar la guía genérica.

## 2. Dataset congelado antes del retrieval

**Archivo:** [data/etiquetas_b27_l3_booking_core.json](../data/etiquetas_b27_l3_booking_core.json), versionado ANTES del script que consulta Gemini. Las doce preguntas (dentro del rango oficial 8–15) cubren las cinco fuentes. Se leyó el texto original y la segmentación de la indexación B24/L3 antes de definir qué chunks contienen evidencia. Los identificadores son SHA-256 de la cadena `fuente|indice_chunk` tal como define `indexar_corpus.ids_estables`, no son IDs inventados o `doc0...doc4`.

| Etiqueta | Asunto | Fuentes/chunks relevantes |
| --- | --- | --- |
| SERV-01 | Servicios de barbería mencionados en la demo | `01_servicios.md#0` |
| SERV-02 | Prohibición de inventar precios, duración y profesionales | `01_servicios.md#0`, `#1` |
| DISP-01 | Servicio/fecha al consultar horarios | `02_disponibilidad.md#0` |
| DISP-02 | Validación final de una franja disputada | `02_disponibilidad.md#1` |
| REPRO-01 | Requisitos y confirmación para modificar cita | `03_reprogramacion.md#0` |
| REPRO-02 | Imposibilidad de mover citas sin integración | `03_reprogramacion.md#1` |
| CANC-01 | Supervisión humana en cancelación simulada | `04_cancelacion.md#0` |
| CANC-02 | No anunciar cancelación a partir de texto | `04_cancelacion.md#1` |
| PRIV-01 | Autorización multiempresa validada en backend | `05_privacidad.md#0` |
| PRIV-02 | Memoria/trazas no son un control de acceso | `05_privacidad.md#1` |
| SIN-01 | Precio vigente real de AES Barber | **Ninguno** |
| SIN-02 | Número de teléfono comercial actual | **Ninguno** |

Los **10 positivos** cubren el contenido fuente y **2 casos sin respuesta factual** permiten validar recall `None`/`n/a`. Los razonamientos individuales están congelados junto con los IDs. Esta es una **etiquetación inicial de criterio humano**, no una medición automática ni una garantía de relevancia perfecta; no retocar después de ver los rankings para elevar las métricas.

## 3. Script de evaluación real

**Código:** [evaluacion_recuperacion.py](../evaluacion_recuperacion.py) · **Pruebas:** [tests/test_evaluacion_recuperacion_b27_l3.py](../tests/test_evaluacion_recuperacion_b27_l3.py).

**Tres modos, cada uno con un propósito:**

- `--modo etiquetas`: lee los doce casos ya fijados; **sin Gemini ni Chroma**, útil para auditar el set de referencia.
- `--modo inventario`: verifica el **manifiesto, huella de corpus, contenido exacto, IDs y metadata** de los diez chunks; muestra el texto completo de cada chunk desde el Chroma local, **sin Gemini**. Si el índice difiere, aborta en lugar de crear uno vacío.
- `--modo evaluar --k 3` o `--k 5`: reabre la misma colección con embeddings Gemini reales y recupera los IDs de Document.id. Usa **dos corridas por configuración** (12 preguntas × 2 repeticiones = **24 consultas de embedding de pregunta**, y ninguna llamada a un LLM generador). Conserva la pregunta original, contrasta los IDs con el inventario y calcula métricas por caso. **La comparación de repetibilidad exige mismas secuencias ordenadas de IDs y mismas métricas**, no solo promedio idéntico.

**Registro:** la primera evaluación real exitosa crea `resultados_evaluacion.txt`, con fecha real del Windows, parámetros **550/80**, huella, 12 preguntas, 2 corridas, precisión/recall (`n/a` sin relevantes), promedios y las secuencias de IDs. La siguiente evaluación (por ejemplo k=5) usa un archivo fechado para **no sobrescribir** el registro anterior. Se pueden entregar ambos. **No existe todavía archivo real porque no se ha ejecutado Gemini en Windows para esta lección**; no generar números ficticios ni plantillas que parezcan mediciones.

**Matiz sobre el curso:** para un ranking fijo, recall@5 es mayor o igual que recall@3, pero precisión@5 **no tiene que ser siempre menor**: puede aumentar si el cuarto/quinto chunk también es relevante. Por ello informaremos lo observado, sin forzar que cumpla una tendencia no universal.

## 4. Comandos de Windows para completar la actividad

Ejecutar desde `C:\Users\nbello\dev\especializacion-ia-2026` (con `.venv` activo y `GEMINI_API_KEY` en `.env`, nunca subir ese archivo). Usar comandos separados para evitar repetir la entrada concatenada `shortgit` de PowerShell.

~~~powershell
git status --short
git pull --ff-only

# Paso A: 12 etiquetas fijas, sin API
python evaluacion_recuperacion.py --modo etiquetas

# Paso B: 10 chunks e IDs reales y huella, sin API
python evaluacion_recuperacion.py --modo inventario

# Paso C: tests con mocks offline, sin API
python -m unittest discover -s tests -p "test_evaluacion_recuperacion_b27_l3.py" -v

# Paso D: 2 corridas reales k=3, 24 llamadas Gemini de embeddings de pregunta
python evaluacion_recuperacion.py --modo evaluar --k 3

# Paso E: 2 corridas reales k=5, 24 llamadas Gemini de embeddings de pregunta
python evaluacion_recuperacion.py --modo evaluar --k 5

git status --short
~~~

**Antes de ejecutar D/E:** verifica la cuota de tu cuenta; son **48 consultas de embedding de pregunta en total**, distribuidas entre los dos comandos (sin recrear embeddings de documentos). Si surge 429, detener sin borrar/reindexar; la ejecución no debe fabricar PASS ni un registro de resultado incompleto. No ejecutar ambos si el primero falla.

**Qué revisar:** el preflight debe mostrar **5 documentos y 10 chunks**; tests offline todos PASS; para cada k deben aparecer **12 preguntas en dos corridas**, con **`Repetibilidad ... PASS`**; dos archivos con parámetros reales y métricas. Para comparar k, cotejar valores en ambos registros. **No** inferir métricas exactas de los ejemplos Skillnest `0.25/0.75`: corresponden al dataset simulado B27/L2.

## 5. Seguridad y estado académico

Todo el corpus es ficticio. Nunca enviar a GitHub `.env`, token privado, pacientes, clientes, sesiones reales ni `vectorstore/`. Los registros de estas pruebas solo contienen preguntas académicas, IDs de documentos ficticios y métricas. La generación no es parte de estas métricas: un buen recall no demuestra respuestas generadas correctas.

**Estado al preparar la actividad:** 12 etiquetas congeladas en GitHub, script creado, tests y CI offline; la evaluación real Gemini y los reportes **pendientes de ejecución Windows**. **U2.5 permanece 11/15, B27 2/3** hasta completar la prueba real; no equiparar pruebas con mocks a actividad completada. PR #26 **draft, sin merge**. B26/L3 sigue sin constancia de entrega/calificación Skillnest. Tiempo de estudio no informado.

**Punto exacto de continuación:** recibir consola `--modo inventario`, `--modo evaluar --k 3` y `--k 5`; verificar IDs/rankings, promedios, repetibilidad y publicar `resultados_evaluacion.txt` real antes de marcar B27 3/3 y U2.5 12/15. Después, comenzar B28 solo con el contenido oficial.
