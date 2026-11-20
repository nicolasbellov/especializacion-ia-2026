# Decisión fundamentada de personalización — Booking Core AI

## 1. El problema
Booking Core AI debe responder consultas sobre procedimientos de servicios, reprogramación, cancelación y privacidad con respaldo documental identificable, sin inventar condiciones comerciales ni ejecutar reservas por el solo hecho de generar una respuesta.

## 2. Resultado del método de decisión
Se aplicó la rúbrica de B30 Core al componente documental.

- **RAG: 2 puntos**
- **PEFT: 1 punto**
- **Fine-tuning completo: 0 puntos**

**Candidatas mejor puntuadas:** RAG.

**Evidencia por criterio (True/False):**

- **informacion_cambia_seguido = False.** Las cinco fuentes ficticias fueron creadas el 13/11/2026 y no registran cambios posteriores hasta el 20/11. La historia disponible no acredita al menos una actualización mensual durante tres meses; no se afirma que las futuras políticas comerciales sean estáticas.
- **problema_de_formato_o_tono = False.** No se dispone de una auditoría de 20 respuestas reales de este componente con al menos tres fallos. Los 20 pares de dataset_tuning.py son ejemplos etiquetados, NO salidas observadas del modelo. False indica umbral sin demostrar, no tasa observada de fallos cero.
- **dataset_grande_y_de_calidad = False.** Existen 20 ejemplos sintéticos para el clasificador de intención, menos de los 200 del umbral y sin auditoría aleatoria de etiquetas. RAG no necesita ejemplos de entrenamiento para indexar documentos.
- **presupuesto_limitado_o_iterar_rapido = True.** El piloto académico ADOPTA como condición de diseño poder observar cambios de contenido en menos de un día; es coherente con las iteraciones dentro del mismo día ya registradas en GitHub y Windows. No equivale a un SLA de producción ni a un límite de dinero aprobado.
- **necesita_multiples_variantes = False.** La implementación académica evalúa un asistente Booking Core AI, sin requerimiento documentado de dos o más variantes ajustadas.

**Prueba de sensibilidad:** se invirtió SOLO `presupuesto_limitado_o_iterar_rapido` de True a False. Resultado: RAG 0, fine-tuning completo 0, PEFT 0; **empate entre RAG, Fine-tuning completo, PEFT**. En ese caso la heurística deja de decidir: RAG seguiría siendo una opción cualitativa para datos documentales, pero no una ganadora por puntaje. Hay que ratificar el objetivo de iteración menor a un día antes de una decisión productiva.

## 3. Técnica elegida y por qué
Elijo **RAG para el componente documental**, con contexto numerado, citas verificables y abstención cuando falta evidencia. El método lo sitúa primero bajo los supuestos explícitos (2 puntos frente a 1 de PEFT y 0 de fine-tuning completo). RAG permite actualizar documentos sin entrenar otro modelo y aprovecha el corpus/vectorstore ya preparado. No elijo PEFT ni fine-tuning para este problema: no está acreditada una falla sistemática de formato en 20 respuestas reales, y tampoco tenemos 200 ejemplos revisados. Para el **clasificador de intenciones** del Bloque 29 (20 ejemplos sintéticos), evaluaría primero prompting estructurado/JSON Schema; PEFT solo si un baseline medido falla. La puntuación del curso no incluye prompting ni soft-prompting. RAG no sustituye el backend: identidad, tenant, disponibilidad y operaciones de agenda requieren APIs autorizadas.

## 4. Qué necesitarías para ejecutarla
Para la demostración ya existen **5 de 5 documentos ficticios** en data/corpus_b24_l3 y un índice Chroma local de **10 chunks**: **faltan 0 documentos para reproducir el alcance académico actual**. En B27 se prepararon **12 preguntas** (10 con relevancia etiquetada y 2 sin respuesta factual) y se obtuvieron dos corridas reproducibles para k=3: precisión media **0,306** y recall medio **1,000** en los casos evaluables. Son métricas de recuperación de un corpus sintético, no resultados de producción ni verificación del texto final. Para uso real falta inventariar las fuentes oficiales de políticas y servicios de AES Barber; **todavía no existe una cifra verificable** de documentos faltantes para producción. También se requieren actualización/versionado del índice, controles de tenant, citas validadas, pruebas de abstención y acceso al backend autorizado. La disponibilidad y los precios vigentes nunca se extraerán de notas ficticias. Como alternativa futura, el clasificador tiene **20 ejemplos**, le faltan **180 para llegar a 200** según el umbral orientativo del curso, además de etiquetas revisadas y evaluación con respuestas reales: 200 no garantiza un tuning útil.
