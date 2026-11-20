# U2.6 · Bloque 30/L1 — Lo que cuesta personalizar

**Fuente académica:** Skillnest / Accenture / CChIA, «Lo que cuesta personalizar: datos, infraestructura, tiempo» (Bloque 30, lección 1, requisito «Ver»). Material compartido el 20/11/2026.

## 1. Qué enseña el curso

La lección compara **RAG** y **fine-tuning/PEFT** en tres dimensiones principales:

| Dimensión | RAG | Fine-tuning y PEFT (API gestionada, según el curso) |
| --- | --- | --- |
| Preparación de datos | Se pueden indexar documentos sin etiquetas de entrenamiento | Cada par entrada/salida necesita una salida correcta; trabajo de etiquetado humano |
| Infraestructura | El vector store debe mantenerse, respaldarse y actualizarse | La API gestiona cómputo de entrenamiento y alojamiento del modelo; en entornos autogestionados esto cambia |
| Cómputo y operación | Costos por consultas, embeddings y mantenimiento (véase B28) | Entrenamiento con costo de cómputo; la API puede exponer contadores reales del trabajo |
| Tiempo de iteración | Un cambio documental puede reflejarse sin reentrenar el LLM | Cada ciclo de ajuste puede tardar minutos u horas |
| Riesgos de calidad | Índice desactualizado; recuperación inadecuada | Etiquetas inconsistentes, desbalance y ejemplos recortados |

**Aclaración técnica:** «RAG no requiere etiquetas» se refiere a **indexar documentos**, no a medir la calidad del retrieval: en B27 sí usamos etiquetas humanas para precisión/recall. Los costos específicos y disponibilidad de tuning dependen del proveedor, modelo, región y cuenta; este ejercicio no prueba esas condiciones actuales.

## 2. Fórmula oficial y primeros ejemplos

La función del material es:

\`\`\`python
def estimar_costo_de_etiquetar(num_ejemplos, minutos_por_ejemplo, costo_por_hora):
    horas = (num_ejemplos * minutos_por_ejemplo) / 60
    costo = horas * costo_por_hora
    return horas, costo
\`\`\`

Con **5 minutos por ejemplo** y **USD 25 por hora**:

| Cantidad | Horas (estimadas) | Costo humano USD (estimado) |
| ---: | ---: | ---: |
| 8 ejemplos | 0,67 | 16,67 |
| 200 ejemplos | 16,67 | 416,67 |

El tiempo y el costo crecen **25x** al multiplicar por 25 la cantidad de casos y conservar la misma complejidad por ejemplo.

## 3. Mini-ejercicio oficial — 500 ejemplos

Supuestos de la consigna: 500 ejemplos; 4 minutos de etiquetado por ejemplo; tarifa USD 20/h; segundo revisor en 20 % de los casos (100), 2 minutos adicionales por caso.

| Etapa | Minutos totales | Horas | Costo USD |
| --- | ---: | ---: | ---: |
| Etiquetado inicial | 2.000 | 33,33 | 666,67 |
| Segunda revisión de 100 casos | 200 | 3,33 | 66,67 |
| **Total** | **2.200** | **36,67** | **733,33** |

**Jornadas de 8 horas:** 36,67 / 8 = **4,6 jornadas**, redondeadas a un decimal.

## 4. Extensión propia — Booking Core AI

El dataset **sintético** de B29 ([\`dataset_tuning.py\`](../dataset_tuning.py)) tiene 20 ejemplos equilibrados, cuatro para cada una de cinco intenciones. Se aplica exactamente el mismo supuesto **didáctico** del mini-ejercicio para comparar magnitudes: 4 minutos por ejemplo, 20 USD/h y revisión de 20 % (4 ejemplos) con 2 minutos cada uno.

| Etapa | Minutos totales | Horas | Costo USD |
| --- | ---: | ---: | ---: |
| Etiquetado inicial de 20 casos | 80 | 1,33 | 26,67 |
| Segunda revisión de 4 casos | 8 | 0,13 | 2,67 |
| **Total** | **88** | **1,47** | **29,33** |

**Importante:** esos USD 29,33 **no son costos incurridos**. Nadie reportó haber empleado cuatro minutos por caso, la tarifa no es una remuneración real y la segunda revisión aún no se realizó. Es un escenario hipotético para ilustrar la fórmula; los datos de estudio efectivo se registran por separado.

La distribución equilibrada no demuestra que un modelo entrenado con 20 ejemplos generalice adecuadamente. Antes de considerar PEFT en producción, hay que evaluar prompting estructurado como baseline, estimar el costo real del etiquetado y disponer de un conjunto independiente de evaluación.

## 5. Estadísticas reales del SDK de Gemini

El curso muestra \`client.tunings.get(name=nombre_trabajo)\` y, tras existir datos del entrenamiento, \`trabajo.tuning_data_stats.supervised_tuning_data_stats\`. Los campos expuestos en el material incluyen:

- \`tuning_dataset_example_count\`: ejemplos utilizados.
- \`total_truncated_example_count\`: ejemplos truncados.
- \`total_billable_token_count\` y \`total_billable_character_count\`: contadores facturables.
- \`tuning_step_count\`: pasos de entrenamiento.
- \`dropped_example_reasons\` y \`total_tuning_character_count\`: diagnóstico complementario.

Los valores **7 ejemplos / 1540 tokens / 35 pasos** de la lección son **ilustrativos**, no mediciones de Booking Core AI. **No tenemos un trabajo de tuning real ni un ID de job**, por lo que no llamamos a \`client.tunings.get\`; tampoco hicimos \`tune\` ni \`cancel\`.

## 6. Implementación y QA

- [\`costos_personalizacion.py\`](../costos_personalizacion.py): ejemplos oficiales 8/200, mini-ejercicio 500 y extensión ficticia con la cantidad del dataset B29.
- [\`tests/test_costos_personalizacion_b30.py\`](../tests/test_costos_personalizacion_b30.py): pruebas offline de la fórmula, revisión, totales, jornadas y valores fuera de rango.
- GitHub Actions incorpora \`python costos_personalizacion.py\` al job de ejercicios offline.

### Comandos para validar en Windows

\`\`\`powershell
git pull --ff-only origin main
.\.venv\Scripts\python.exe .\costos_personalizacion.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_costos_personalizacion_b30.py" -v
git status -sb
\`\`\`

**Estado:** código y tests publicados, resultados locales Windows aún por confirmar. No se realizan llamadas a la API ni se generan gastos de entrenamiento.

**Próxima lección:** U2.6 B30/L2 «Cómo comparar estrategias de personalización». Esperar su material oficial y elegir métricas antes de decidir entre prompting, RAG, PEFT y fine-tuning.
