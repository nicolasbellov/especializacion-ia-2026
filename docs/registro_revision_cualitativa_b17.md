# U2.2 — Bloque 17, lección 1: rúbrica cualitativa

**Fecha:** 29/10/2026 (Chile). **Fuente principal:** lección Skillnest «Cuando el número no basta: criterio cualitativo», aportada por el estudiante.  
**Evidencia real:** [resultados_metricas.json](../resultados_metricas.json), calculada en B16 a partir de respuestas Gemini generadas originalmente en B15.

## 1. Qué enseña la lección de Skillnest

La revisión cualitativa lee una respuesta junto con su referencia y aplica **los mismos criterios a cada caso**, en vez de inferir verdad o calidad a partir de precisión, cobertura y F1.

| Dimensión | Pregunta según la rúbrica | Valores |
| --- | --- | --- |
| Corrección factual | ¿Los datos verificables coinciden con la referencia? | Sí, no, parcialmente |
| Completitud | ¿Se cubre la información importante de la referencia? | Sí, no, parcialmente |
| Contradicción | ¿Se afirma lo contrario de la referencia? | Sí, no |

Toda evaluación debe explicar el **porqué**. Cuando haya dudas, usar `parcialmente` con una nota es preferible a forzar un sí/no. «Contradicción» sigue siendo sí/no como indica la definición del curso.

**Señales para revisión:** F1 bajo pese a una paráfrasis plausible, F1 alto con información dudosa y **cualquier número, fecha o nombre propio**, aun si el F1 es alto.

**Ejemplo oficial (partido):** al omitir `3 goles a 1` en una respuesta, P 100 %, R 64,3 % y F1 78,3 % no evitan una evaluación de **factual: sí; completitud: no; contradicción: no**. La omisión del marcador es importante.

## 2. Aplicación a los tres casos reales propios

| Caso | Consulta resumida | F1 | Estado cualitativo |
| --- | --- | ---: | --- |
| 3 | ¿Para qué sirve Git? | 19,4 % | **Pendiente de revisión humana** |
| 2 | ¿Qué es una API? | 33,3 % | **Pendiente de revisión humana** |
| 1 | ¿Qué es Python? | 44,4 % | **Pendiente de revisión humana** |

La [plantilla JSON](../revision_cualitativa_b17.json) guarda `null` para las tres evaluaciones y una justificación vacía: **no son calificaciones**, sino campos a completar tras leer los textos. Contiene los pares originales de referencia y respuesta, sin regenerar contenido de Gemini.

## 3. Decisiones técnicas complementarias (no exigidas literalmente por la lección)

- [revision_cualitativa_b17.py](../revision_cualitativa_b17.py) lee resultados B16 y selecciona extremos por F1. Si hay hasta 10 casos para 5 por extremo, **selecciona cada caso una sola vez** en lugar de duplicarlo; con tres datos se revisan los tres.
- La plantilla **no se sobrescribe** al volver a ejecutar el script, para proteger notas humanas ya elaboradas.
- [test_revision_cualitativa_b17.py](../test_revision_cualitativa_b17.py) verifica selección, deduplicación, campos pendientes, valores válidos y protección ante sobreescritura.
- Como el repositorio es público, solo usar respuestas de ejemplo no sensibles. En contextos de salud, evitar publicar información clínica real.
- Una lectura manual tampoco convierte automáticamente una respuesta en verdadera: si se quiere corroborar una afirmación factual no respaldada por la referencia, se necesita una fuente adecuada. Por ahora la rúbrica se aplica al par de textos disponible.

## 4. Estado de evidencia

- **Lección revisada:** B17 L1; U2.2 llega a **7/9 (77,8 %)** por número de lecciones estudiadas.
- **Criterios humanos de los tres casos reales:** **sin completar**; no inventar evaluación del estudiante ni aprobación del curso.
- **Validación del nuevo código:** pendiente confirmar ejecución de pruebas en el Windows del estudiante; las 29 pruebas previas de B15+B16 ya estaban confirmadas.
- **Punto exacto para continuar:** ejecutar nueva suite, aplicar rúbrica al caso Git y luego API/Python; estudiar B17 L2 «Qué documentar como límite de tu pipeline».
