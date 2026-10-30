# Análisis de la revisión humana — U2.2 / Bloque 17 Core

**Fecha de la sesión informada:** 29/10/2026, Chile. **Fuente primaria:** transcripción de PowerShell aportada por el estudiante después de ejecutar `core_b17_generar.py` y `core_b17_revisar.py`.  
**Alcance probatorio:** la consola acredita la generación de **20/20 respuestas reales**, **10/10 evaluaciones introducidas manualmente** y el resultado satisfactorio de `--validar` y `--informe`. **Actualización posterior:** archivos fuente incorporados en el repositorio; las notas originales se conservan.

## Selección y resultados de la rúbrica

La muestra contiene los **cinco F1 más bajos y cinco más altos de las 20 respuestas disponibles**, sin duplicaciones. Los cinco superiores son altos *relativamente a este corpus*, no cercanos a 100%.

| Grupo | Caso | Concepto | F1 | Corrección factual | Completitud | Contradicción |
| --- | ---: | --- | ---: | --- | --- | --- |
| F1 inferiores | 3 | Git | 19,4 % | sí | sí | no |
| F1 inferiores | 14 | API REST | 27,0 % | sí | no | no |
| F1 inferiores | 20 | Tokenización | 29,2 % | sí | sí | no |
| F1 inferiores | 2 | API | 33,3 % | sí | sí | no |
| F1 inferiores | 11 | HTTP | 36,4 % | sí | parcialmente | no |
| F1 superiores | 12 | HTTP 404 | 54,5 % | sí | sí | no |
| F1 superiores | 8 | Funciones de Python | 55,6 % | sí | parcialmente | no |
| F1 superiores | 9 | Error de sintaxis | 57,9 % | sí | sí | no |
| F1 superiores | 5 | Listas de Python | 62,9 % | sí | sí | no |
| F1 superiores | 16 | `git clone` | 64,0 % | sí | sí | no |

**Conteos de evaluaciones consignadas:** corrección factual **10 sí**; completitud **7 sí, 2 parcialmente, 1 no**; contradicción **10 no**. Esto describe únicamente **esta muestra pequeña**, no una tasa de calidad general de Gemini.

## Modos de falla y hallazgos propios, con trazabilidad

1. **Falsos negativos léxicos por reformulación y respuesta más extensa:** **caso 3, Git, F1 19,4 %**. Referencia: «Git permite controlar versiones del código». La respuesta explica controlar/registrar cambios del código y trabajo en equipo. El estudiante la valoró factual **sí**, completa **sí**, contradictoria **no**. El bajo F1 **no equivale a un error factual**. También **casos 20 (29,2 %) y 2 (33,3 %)**, valorados sí/sí/no, ilustran paráfrasis o explicaciones más largas que la referencia.
2. **Omisión del concepto central pese a que la respuesta afirma algo razonable:** **caso 14, API REST, F1 27,0 %**, factual **sí**, completitud **no**, contradicción **no**. La respuesta describe comunicación por HTTP pero omite que la API REST expone recursos para consulta/modificación. La nota humana advierte que no se limita a internet público.
3. **Omisiones parciales en respuestas factualmente correctas:** **caso 11, HTTP, F1 36,4 %**, factual **sí**, completitud **parcialmente**, contradicción **no**: no explica explícitamente el patrón de solicitudes y respuestas. **Caso 8, funciones de Python, F1 55,6 %**, factual **sí**, completitud **parcialmente**, contradicción **no**: omite que pueden recibir argumentos y devolver resultados.
4. **Sinónimos no reconocidos por el conteo exacto:** **caso 5, listas Python, F1 62,9 %**, factual **sí**, completitud **sí**, contradicción **no**: la referencia utiliza «modificable» y la respuesta «mutable», equivalentes en este contexto. La métrica cuenta ambas como palabras distintas.
5. **Coincidencia parcial entre F1 relativamente superior y revisión humana favorable:** los casos **12 (HTTP 404, 54,5 %), 9 (sintaxis, 57,9 %) y 16 (`git clone`, 64,0 %)** fueron valorados factual **sí**, completitud **sí**, contradicción **no**. Estos datos **no demuestran** que un F1 alto garantice validez, especialmente porque el máximo observado es 64,0 %.

## Control de calidad de la anotación

- El **caso 12** se interrumpió antes de guardarlo con un valor equivocado; al reanudarlo se guardó explícitamente `contradiccion=no`.
- El **caso 9** se interrumpió antes de guardarlo y al reanudarlo quedó `contradiccion=no`.
- El **caso 16** inicialmente se guardó con `contradiccion=si`, pero la justificación escrita decía «no contiene contradicciones». El estudiante **corrigió solo ese valor a `no`** utilizando un respaldo del JSON. La consola registró `Caso 16 corregido: contradiccion = no` y repitió **`VÁLIDO: 20 respuestas reales y 10 revisiones humanas justificadas.`** Después volvió a generar `docs/revision_manual_core_b17.md`.
- **Lección del QA:** el validador comprobaba que el valor perteneciera a `si/no`, pero no si era coherente con la justificación. La auditoría semántica sigue siendo necesaria. Las correcciones fueron del estudiante, no juicios realizados automáticamente.

## Estado de la actividad y siguiente acción

**Avance local corroborado por consola:** `55 passed in 1.50s` en la suite, 20/20 respuestas, 10/10 revisiones, informe regenerado. Las 17 nuevas consultas incluyeron dos reintentos exitosos en el caso 20; el código HTTP del error **no está identificado**. Costo mostrado `USD 0.001588` es una **estimación didáctica**, no facturación verificada.

**Archivos originales recibidos y publicados:** [corpus](../resultados_core_b17.json), [rúbrica](../revision_manual_core_b17.json) e [informe](revision_manual_core_b17.md). Las 60 métricas fueron recalculadas con resultado consistente y las diez valoraciones coinciden con el informe. **Pendiente:** enviar el enlace en Skillnest y registrar la aprobación institucional.
