# B17 Core — Revisión cualitativa de respuestas reales

**Fuente:** resultados_core_b17.json; 20 respuestas reales (3 originales B15 y 17 nuevas B17 Core).
**Muestra:** cinco F1 menores y cinco F1 mayores, 10 casos únicos revisados con la rúbrica de Skillnest.
**Importante:** todos los juicios y notas siguientes se transcribieron desde revisión_manual_core_b17.json; no se generaron automáticamente.

| Caso | F1 | Corrección factual | Completitud | Contradicción | Fecha |
| ---: | ---: | --- | --- | --- | --- |
| 3 | 19.4% | si | si | no | 2026-10-29 |
| 14 | 27.0% | si | no | no | 2026-10-29 |
| 20 | 29.2% | si | si | no | 2026-10-29 |
| 2 | 33.3% | si | si | no | 2026-10-29 |
| 11 | 36.4% | si | parcialmente | no | 2026-10-29 |
| 12 | 54.5% | si | si | no | 2026-10-29 |
| 8 | 55.6% | si | parcialmente | no | 2026-10-29 |
| 9 | 57.9% | si | si | no | 2026-10-29 |
| 5 | 62.9% | si | si | no | 2026-10-29 |
| 16 | 64.0% | si | si | no | 2026-10-29 |

## Evidencia por caso

### Caso 3 — F1 19.4%

**Consulta:** ¿Para qué sirve Git? Responde en una sola oración breve.

**Referencia:** Git permite controlar versiones del código.

**Respuesta real:** Git sirve para **controlar y registrar los cambios en el código fuente** de un proyecto, facilitando el trabajo en equipo y el desarrollo de software.

**Rúbrica:** corrección factual si; completitud si; contradicción no.

**Justificación humana:** La respuesta describe correctamente el propósito de Git: controlar versiones y registrar cambios del código fuente. Incluye la información esencial de la referencia y añade su utilidad para el trabajo colaborativo. No contiene contradicciones. El F1 bajo refleja una diferencia léxica, no un error de significado.

### Caso 14 — F1 27.0%

**Consulta:** ¿Qué es una API REST? Responde en una sola oración breve.

**Referencia:** Una API REST expone recursos que se consultan y modifican mediante peticiones HTTP.

**Respuesta real:** Una API REST es una interfaz que permite la comunicación entre diferentes sistemas a través de internet usando los métodos estándar del protocolo HTTP.

**Rúbrica:** corrección factual si; completitud no; contradicción no.

**Justificación humana:** La respuesta describe correctamente la comunicación entre sistemas mediante HTTP, pero no explica que una API REST expone recursos que pueden consultarse y modificarse. Además, presenta el uso de internet como algo general, aunque REST también puede operar en redes privadas. No contradice directamente la referencia, pero resulta incompleta.

### Caso 20 — F1 29.2%

**Consulta:** ¿Qué es un token en procesamiento de texto? Responde en una sola oración breve.

**Referencia:** Un token es una unidad de texto obtenida al segmentar una entrada.

**Respuesta real:** Un token es la unidad básica de texto —que puede ser una palabra, parte de ella o un signo de puntuación— en la que se divide un documento para que un modelo de lenguaje pueda procesarlo.

**Rúbrica:** corrección factual si; completitud si; contradicción no.

**Justificación humana:** La respuesta define correctamente un token como una unidad de texto resultante de la segmentación y aporta ejemplos como palabras, fragmentos de palabras y signos de puntuación. Cubre el concepto esencial de la referencia y lo amplía con su aplicación en modelos de lenguaje. No presenta contradicciones. El F1 bajo se debe principalmente a diferencias léxicas y a la mayor extensión de la respuesta, no a un error conceptual.

### Caso 2 — F1 33.3%

**Consulta:** ¿Qué es una API? Responde en una sola oración breve.

**Referencia:** Una API permite la comunicación entre aplicaciones.

**Respuesta real:** Una API es un conjunto de reglas y protocolos que permite que diferentes aplicaciones de software se comuniquen e intercambien datos entre sí.

**Rúbrica:** corrección factual si; completitud si; contradicción no.

**Justificación humana:** La respuesta define correctamente una API como un conjunto de reglas y protocolos que facilita la comunicación e intercambio de datos entre aplicaciones. Cubre completamente el concepto expresado en la referencia y aporta información complementaria pertinente. No presenta contradicciones. El F1 de 33,3% refleja principalmente la diferencia de extensión y vocabulario respecto de la referencia, no una deficiencia conceptual.

### Caso 11 — F1 36.4%

**Consulta:** ¿Para qué sirve HTTP? Responde en una sola oración breve.

**Referencia:** HTTP es un protocolo para intercambiar solicitudes y respuestas entre clientes y servidores.

**Respuesta real:** HTTP sirve para transferir información y recursos (como páginas web e imágenes) entre un navegador y un servidor en internet.

**Rúbrica:** corrección factual si; completitud parcialmente; contradicción no.

**Justificación humana:** La respuesta describe correctamente que HTTP permite transferir información y recursos entre clientes y servidores, utilizando como ejemplo un navegador y un servidor web. Sin embargo, omite explicar que HTTP funciona mediante el intercambio de solicitudes y respuestas, elemento central de la referencia. Además, HTTP no se limita a navegadores ni a internet público, pues también puede utilizarse en otros clientes y redes privadas. No presenta contradicciones directas, pero su explicación es parcialmente completa.

### Caso 12 — F1 54.5%

**Consulta:** ¿Qué significa el código HTTP 404? Responde en una sola oración breve.

**Referencia:** HTTP 404 indica que el servidor no encontró el recurso solicitado.

**Respuesta real:** El código HTTP 404 significa que el servidor no pudo encontrar la página o el recurso solicitado en la dirección web proporcionada.

**Rúbrica:** corrección factual si; completitud si; contradicción no.

**Justificación humana:** La respuesta explica correctamente que HTTP 404 indica que el servidor no encontró el recurso solicitado. Cubre la información esencial de la referencia y añade contexto sobre páginas web y direcciones URL. No existen contradicciones ni errores factuales relevantes.

### Caso 8 — F1 55.6%

**Consulta:** ¿Qué es una función en Python? Responde en una sola oración breve.

**Referencia:** Una función es un bloque de código reutilizable que puede recibir argumentos y devolver resultados.

**Respuesta real:** En Python, una función es un bloque de código reutilizable que realiza una tarea específica y se ejecuta cuando es llamado.

**Rúbrica:** corrección factual si; completitud parcialmente; contradicción no.

**Justificación humana:** La respuesta define correctamente una función en Python como un bloque de código reutilizable que ejecuta una tarea específica cuando es llamado. Sin embargo, omite mencionar que las funciones pueden recibir argumentos y devolver resultados, dos características relevantes de la referencia. No presenta errores factuales ni contradicciones, pero su explicación es parcialmente completa.

### Caso 9 — F1 57.9%

**Consulta:** ¿Qué significa un error de sintaxis en Python? Responde en una sola oración breve.

**Referencia:** Un error de sintaxis aparece cuando el código no sigue las reglas del lenguaje.

**Respuesta real:** Un error de sintaxis en Python ocurre cuando el código viola las reglas gramaticales del lenguaje, impidiendo que el intérprete pueda leerlo y ejecutarlo.

**Rúbrica:** corrección factual si; completitud si; contradicción no.

**Justificación humana:** La respuesta explica correctamente que un error de sintaxis en Python se produce cuando el código incumple las reglas gramaticales del lenguaje. Cubre completamente el concepto de la referencia y añade una consecuencia relevante: el intérprete no puede procesar y ejecutar correctamente el código afectado. No contiene contradicciones ni errores conceptuales relevantes. El F1 de 57,9% refleja diferencias de vocabulario y extensión, no una pérdida de significado.

### Caso 5 — F1 62.9%

**Consulta:** ¿Qué es una lista en Python? Responde en una sola oración breve.

**Referencia:** Una lista de Python es una colección ordenada y modificable de elementos.

**Respuesta real:** Una lista en Python es una colección ordenada y mutable de elementos que pueden ser de diferentes tipos de datos, delimitada por corchetes `[]`.

**Rúbrica:** corrección factual si; completitud si; contradicción no.

**Justificación humana:** La respuesta define correctamente una lista de Python como una colección ordenada y modificable de elementos. Cubre todos los conceptos esenciales de la referencia y añade información válida: las listas pueden contener elementos de distintos tipos de datos y se representan mediante corchetes. No presenta contradicciones ni errores factuales relevantes. El F1 de 62,9% refleja coincidencias léxicas, pero no captura por completo la equivalencia entre «mutable» y «modificable».

### Caso 16 — F1 64.0%

**Consulta:** ¿Para qué sirve git clone? Responde en una sola oración breve.

**Referencia:** git clone crea una copia local de un repositorio.

**Respuesta real:** `git clone` sirve para descargar una copia exacta de un repositorio remoto en tu computadora local.

**Rúbrica:** corrección factual si; completitud si; contradicción no.

**Justificación humana:** La respuesta describe correctamente que git clone permite obtener una copia local de un repositorio remoto. Cubre completamente el propósito señalado en la referencia y no contiene contradicciones. La expresión «copia exacta» es una simplificación, ya que la clonación reproduce el repositorio Git, pero no necesariamente toda la información adicional de la plataforma que lo aloja. El F1 de 64,0% refleja coincidencia léxica, mientras que la revisión cualitativa confirma que la explicación es adecuada.

## Para documentar los hallazgos

Relacionar cada modo de falla observado con un caso y una nota concreta en el documento de límites. F1 por sí solo no demuestra corrección ni error.
