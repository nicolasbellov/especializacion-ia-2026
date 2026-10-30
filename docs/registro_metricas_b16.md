# U2.2 · Bloque 16 — Métricas integradas sobre respuestas reales

**Fecha:** 29/10/2026 (Chile). **Lección:** «Métricas ya calculadas sobre las salidas de tu propio cliente».  
**Procedencia:** datos reales ya generados con el cliente Gemini del Módulo 2 en el [Bloque 15](../resultados_b15.json), publicados por el estudiante en el commit `bc4fdbe`. **Esta medición no realiza peticiones adicionales a la API**.

## 1. Método y componentes reutilizados

- [pipeline_texto.py](../pipeline_texto.py) contiene `procesar_texto`: minúsculas, eliminación de puntuación y tokenización.
- [metricas_texto.py](../metricas_texto.py) contiene `calcular_precision_cobertura_f1` sobre intersección de frecuencias (`Counter`).
- [evaluar_salidas_b16.py](../evaluar_salidas_b16.py) reúne ambas funciones con `calcular_metricas`, evalúa varias salidas reales previamente guardadas, calcula promedios simples por caso, ordena por F1 y escribe UTF-8.
- [resultados_metricas.json](../resultados_metricas.json) conserva **consulta, referencia, respuesta original, precisión, cobertura y F1**, sin inventar respuestas ni redondear los valores almacenados.
- [test_evaluar_salidas_b16.py](../test_evaluar_salidas_b16.py) prueba funcionalidad independiente de la red.

## 2. Datos efectivamente medidos

| Consulta resumida | Tokens ref. | Tokens generados | Coincidencias | Precisión | Cobertura | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Qué es Python | 6 | 21 | 6 | 28,6 % | 100,0 % | 44,4 % |
| Qué es una API | 7 | 23 | 5 | 21,7 % | 71,4 % | 33,3 % |
| Para qué sirve Git | 6 | 25 | 3 | 12,0 % | 50,0 % | 19,4 % |
| **Promedio simple por respuesta** | — | — | — | **20,8 %** | **73,8 %** | **32,4 %** |

Promedio F1 sin redondear: **0,3237753882915173**. El promedio cercano a 0,61 mostrado en la lección de Skillnest es **ilustrativo** y pertenece a una tabla de ejemplos distinta, no a este conjunto real.

**Prioridad de inspección automática:** Git → API → Python (F1 ascendente). Esta lista solo ordena por solapamiento léxico y **no** concluye cuáles respuestas son verdaderas o falsas.

## 3. Límites y decisiones

1. **Fuente de verdad:** conservar el archivo original `resultados_b15.json`, evitando volver a consultar Gemini y gastar cuota solo para repetir mediciones.
2. **Trazabilidad:** exportar cada respuesta junto a la consulta, su referencia y los tres indicadores. No registrar solo el promedio ni reemplazar texto original con respuestas de muestra del curso.
3. **Agregación:** el promedio es **macro** (media simple de métricas de cada caso), no micro ni F1 calculado a partir de promedios de P y R.
4. **Límite:** F1 no evalúa verdad factual, sinónimos, negación, ni seguridad; una respuesta razonable puede ser penalizada por ser más extensa que la referencia.
5. **Interpretación:** priorizar casos con F1 bajo para revisión humana es útil, pero revisar también valores altos porque pueden encubrir cambios de sentido.
6. **Formato:** guardar UTF-8 con `ensure_ascii=False` para preservar español, tildes y ñ en el archivo de evidencia público. Los ejemplos guardados aquí no contienen datos clínicos reales ni credenciales.

## 4. Validación y estado

- **Validación independiente:** se ejecutaron **8/8** pruebas nuevas en un entorno Python aislado, junto a la ejecución del script con datos históricos representativos de la fuente versionada. La salida reprodujo las tres métricas y el promedio F1 de 32,4 %.
- **Validación Windows del estudiante:** **pendiente** para la suite combinada (21 previas + 8 nuevas = 29 pruebas previstas). Una ejecución independiente no debe registrarse como ejecución del estudiante ni como calificación institucional.
- **Entrega formal en Skillnest:** no confirmada. El material compartido señala que la lección cierra la medición automática y que el próximo Bloque 17 se dedica a evaluación cualitativa.

**Próximo punto:** sincronizar `main`, confirmar pruebas y generación de JSON en Windows, luego revisar Bloque 17 «Cuando el número no basta: criterio cualitativo».
