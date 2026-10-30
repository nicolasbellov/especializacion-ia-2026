# Límites de la métrica de evaluación del pipeline de texto

**Última actualización:** 29/10/2026 (Chile) · **Alcance:** U2.2, Bloques 15–17 · **Estado:** documento inicial; revisión cualitativa propia pendiente.

## Qué mide

**Precisión, cobertura y F1 miden coincidencia exacta de tokens normalizados entre una respuesta generada y una referencia, contando repeticiones.** El pipeline convierte a minúsculas, elimina puntuación, tokeniza y compara frecuencias con `Counter`. Un F1 alto **no significa** que una respuesta sea verdadera, segura o semánticamente correcta.

## Modos de falla conocidos (demostrados con ejemplos oficiales de Skillnest)

- **Sinónimos y paráfrasis:** «El auto es veloz.» / «El vehículo es rápido.» → **F1 50,0 %** pese a expresar una idea equivalente.
- **Cifras o fechas diferentes:** «Python fue creado en 1991.» / «Python fue creado en 1989.» → **F1 80,0 %** aunque el año contradice el dato **de la referencia**. La métrica no comprueba cuál año corresponde a la historia real.
- **Negación omitida:** «Python no es un lenguaje compilado.» / «Python es un lenguaje compilado.» → **F1 90,9 %** aunque las afirmaciones tienen sentidos opuestos.
- **Negación añadida:** «El congreso aprobó la ley por 45 votos a favor.» / «El congreso no aprobó la ley por 45 votos a favor.» → **F1 95,2 %**, también con sentido invertido.
- **Información importante omitida (ejemplo oficial B17):** la respuesta «El equipo ganó el partido en su estadio local.» omite «3 goles a 1» frente a su referencia: **F1 78,3 %** pese a incompletitud sustantiva.

Estos ejemplos pertenecen al **material del curso**: no son hallazgos obtenidos al revisar humanamente nuestras salidas de Gemini.

## Muestra propia: origen, selección y estado

- **Fecha de las respuestas de origen:** 29/10/2026; generadas en el Bloque 15, conservadas en [resultados_b15.json](../resultados_b15.json). Métricas calculadas offline y versionadas en [resultados_metricas.json](../resultados_metricas.json).
- **Universo:** **3 respuestas reales** (Git, API y Python), no 40. **Seleccionadas para evaluación:** **3 casos únicos**, todos disponibles: Git F1 **19,4 %**, API **33,3 %**, Python **44,4 %**, en orden ascendente.
- **Criterio de muestreo:** tomar extremos de F1 (valores menores y mayores) **sin duplicados**. Con solo 3 respuestas, ambos extremos se solapan: por eso se seleccionaron **las 3 una sola vez**; Python es el mayor F1 *relativo a esta muestra*, no un F1 alto en sentido absoluto.
- **Revisión cualitativa humana terminada:** **0/3 al 29/10/2026**. En [revision_cualitativa_b17.json](../revision_cualitativa_b17.json), corrección factual, completitud y contradicción permanecen en `null`, sin justificaciones consignadas. **Todavía no hay modos de falla propios confirmados mediante rúbrica**.

Cuando se revise un caso, registrar **fecha de revisión**, los tres criterios (**factual:** sí/no/parcialmente; **completitud:** sí/no/parcialmente; **contradicción:** sí/no), justificación y evidencia. Incorporar aquí cada hallazgo propio **solo después** de obtenerlo; no confundir «seleccionado» con «revisado». En nuevas rondas, agregar fecha y tamaño de muestra sin borrar el historial.

## Recomendación de uso

**Usar F1 como indicador rápido de coincidencia léxica y para priorizar inspecciones, nunca como aprobación automática de la exactitud de una respuesta.** Revisar manualmente respuestas con cifras, fechas, nombres propios, negaciones, omisiones importantes o consecuencias relevantes; incluir además una muestra con F1 alto para detectar falsos positivos.

## Trazabilidad y mantenimiento

- Cálculo: [pipeline_texto.py](../pipeline_texto.py), [metricas_texto.py](../metricas_texto.py) y [evaluar_salidas_b16.py](../evaluar_salidas_b16.py).
- Rúbrica y selección: [revision_cualitativa_b17.py](../revision_cualitativa_b17.py) y [registro_revision_cualitativa_b17.md](registro_revision_cualitativa_b17.md).
- Revisar este documento si cambian el preprocesamiento, el conteo o las referencias, y tras cada ronda nueva de revisión humana. Mantenerlo bajo control de versiones.
- En un repositorio público no incluir credenciales ni datos clínicos reales. Las métricas textuales por sí solas no deben autorizar decisiones clínicas ni de otra índole crítica.
