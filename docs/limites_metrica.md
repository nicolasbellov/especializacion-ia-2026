# Límites de la métrica de evaluación del pipeline de texto

**Última actualización:** 29/10/2026 (Chile) · **Alcance:** U2.2, Bloques 15–17 · **Estado:** hallazgos propios incorporados desde revisión humana completada según consola; publicación de los JSON e informe originales aún pendiente.

## Qué mide

**Precisión, cobertura y F1 miden coincidencia exacta de tokens normalizados entre una respuesta generada y una referencia, contando repeticiones.** El pipeline convierte a minúsculas, elimina puntuación, tokeniza y compara frecuencias con `Counter`. Un F1 alto **no significa** que una respuesta sea verdadera, segura o semánticamente correcta.

## Modos de falla conocidos (demostrados con ejemplos oficiales de Skillnest)

- **Sinónimos y paráfrasis:** «El auto es veloz.» / «El vehículo es rápido.» → **F1 50,0 %** pese a expresar una idea equivalente.
- **Cifras o fechas diferentes:** «Python fue creado en 1991.» / «Python fue creado en 1989.» → **F1 80,0 %** aunque el año contradice el dato **de la referencia**. La métrica no comprueba cuál año corresponde a la historia real.
- **Negación omitida:** «Python no es un lenguaje compilado.» / «Python es un lenguaje compilado.» → **F1 90,9 %** aunque las afirmaciones tienen sentidos opuestos.
- **Negación añadida:** «El congreso aprobó la ley por 45 votos a favor.» / «El congreso no aprobó la ley por 45 votos a favor.» → **F1 95,2 %**, también con sentido invertido.
- **Información importante omitida (ejemplo oficial B17):** la respuesta «El equipo ganó el partido en su estadio local.» omite «3 goles a 1» frente a su referencia: **F1 78,3 %** pese a incompletitud sustantiva.

Estos ejemplos pertenecen al **material del curso**: no son hallazgos obtenidos al revisar humanamente nuestras salidas de Gemini.

## Modos de falla observados en nuestra revisión (Bloque 17 Core)

Los siguientes resultados **sí proceden de las diez anotaciones humanas del estudiante** sobre respuestas reales de Gemini, según la consola; no son ejemplos inventados ni un resumen de todas las respuestas no revisadas.

- **F1 bajo a pesar de una respuesta adecuada — caso 3, Git:** **F1 19,4 %**, factual **sí**, completitud **sí**, contradicción **no**. La respuesta sobre control de cambios y colaboración preserva el significado de «controlar versiones del código» con vocabulario distinto.
- **F1 bajo y omisión sustantiva — caso 14, API REST:** **F1 27,0 %**, factual **sí**, completitud **no**, contradicción **no**. Habla de comunicación mediante HTTP, pero no de recursos que se consultan y modifican, núcleo de la referencia.
- **Respuesta correcta, parcialmente completa — caso 11, HTTP:** **F1 36,4 %**, factual **sí**, completitud **parcialmente**. Omite el intercambio explícito de solicitudes y respuestas. **Caso 8, funciones Python, F1 55,6 %**, también **parcialmente**: omite argumentos y retorno.
- **Sinónimos técnicos — caso 5, lista Python:** **F1 62,9 %**, factual y completitud **sí**, contradicción **no**. La referencia dice «modificable» y Gemini dice «mutable»; la métrica no reconoce la equivalencia.
- **Respuesta explicativa penalizada — caso 20, tokenización:** **F1 29,2 %**, factual y completitud **sí**. Se amplía con tipos de tokens (palabra, fragmento, puntuación), pero el aumento de longitud reduce precisión léxica.

**Resumen:** 10/10 respuestas fueron clasificadas como factualmente correctas por el estudiante, pero **3/10** resultaron incompletas total o parcialmente. No se identificaron contradicciones **en esta muestra corregida**. No generalizar estos resultados a respuestas no revisadas ni al comportamiento global del modelo. [Ver análisis de la revisión humana y justificaciones de origen](analisis_revision_b17_core.md).

## Muestra revisada

- **Universo propio:** **20 respuestas reales** generadas por `consultar_modelo` (3 históricas del B15 y 17 nuevas durante el Core, con sus métricas), según el registro de ejecución local.
- **Muestra:** **10/20 casos revisados manualmente**, escogidos como **cinco menores F1** (casos 3, 14, 20, 2, 11) y **cinco mayores F1** (12, 8, 9, 5, 16), sin duplicados. La revisión y su corrección se informaron en la sesión de **29/10/2026**.
- **Rangos:** de **19,4 %** (Git) a **64,0 %** (`git clone`). Los cinco «mayores» lo son solo en el conjunto de 20, no necesariamente representan F1 altos absolutos.
- **Rúbrica:** corrección factual: **10 sí**; completitud: **7 sí, 2 parcialmente, 1 no**; contradicción: **10 no** después de corregir una anotación del caso 16.
- **Trazabilidad:** el estudiante ejecutó `--validar` (20/20 y 10/10) y regeneró el informe `docs/revision_manual_core_b17.md` después de corregir el caso 16. **Los archivos originales `resultados_core_b17.json`, `revision_manual_core_b17.json` y el informe Markdown todavía no han sido inspeccionados ni publicados en GitHub**. Este documento recoge hallazgos **sustentados por la transcripción**, sujetos a una auditoría final al recibir esos artefactos.
- **Historial:** en B17 L1 la muestra inicial contenía solo 3 casos seleccionados y **0/3 evaluados**; esta ronda Core la amplió a 20 y revisó 10. Mantener el historial al incorporar nuevas rondas.

## Recomendación de uso

**Usar F1 para ordenar inspecciones, nunca para aprobar respuestas automáticamente.** En nuestro corpus, Git (19,4 %) fue considerado completo, pero API REST (27,0 %), HTTP (36,4 %) y funciones Python (55,6 %) omitieron información importante. Revisar siempre los requisitos semánticos de la referencia —sobre todo recursos de una API, solicitudes/respuestas HTTP, argumentos y retorno de funciones— y cualquier cifra, fecha, nombre o negación; inspeccionar tanto los F1 inferiores como los superiores. La rúbrica requiere una justificación escrita y una comprobación de coherencia entre nota y etiqueta.

## Trazabilidad y mantenimiento

- Cálculo: [pipeline_texto.py](../pipeline_texto.py), [metricas_texto.py](../metricas_texto.py) y [evaluar_salidas_b16.py](../evaluar_salidas_b16.py).
- Rúbrica y selección: [revision_cualitativa_b17.py](../revision_cualitativa_b17.py) y [registro_revision_cualitativa_b17.md](registro_revision_cualitativa_b17.md).
- Core: [análisis de juicios humanos registrados por consola](analisis_revision_b17_core.md), [guía de actividad](guia_entrega_b17_core.md).
- Revisar este documento si cambian el preprocesamiento, el conteo o las referencias, y tras cada ronda nueva de revisión humana. Mantenerlo bajo control de versiones.
- En un repositorio público no incluir credenciales ni datos clínicos reales. Las métricas textuales por sí solas no deben autorizar decisiones clínicas ni de otra índole crítica.
