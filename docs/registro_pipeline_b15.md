# U2.2 · Bloque 15 — Registro de validación del pipeline de texto

**Fecha de ejecución informada:** 29/10/2026 (Chile)  
**Fuente de resultados:** salida íntegra de PowerShell proporcionada por el estudiante en la conversación; no se reconstruyen ejecuciones no observadas.  
**Estado:** validación técnica local satisfactoria; publicación del JSON original y eventual entrega/evaluación institucional aún por confirmar.

## 1. Entregables de código

- [pipeline_texto.py](../pipeline_texto.py): `limpiar_texto`, `tokenizar`, `procesar_texto`, `coincidencia_palabras`, ejecución de tres consultas reales con `cliente.consultar_modelo()`.
- [test_pipeline_texto.py](../test_pipeline_texto.py): nueve pruebas automatizadas.
- Integración inicial de ambos archivos a `main`: [PR #7](https://github.com/nicolasbellov/especializacion-ia-2026/pull/7), commit squash `3273251`.
- Dependencia `pytest>=8,<10` ya declarada en `requirements.txt`; faltaba instalarla en el entorno virtual local.

## 2. Incidencias y solución

1. Primera ejecución: `No module named pytest`. Se resolvió con `.\\venv\\Scripts\\python.exe -m pip install "pytest>=8,<10"`; versión instalada: **pytest 9.2.0**.
2. Primera ejecución: `pipeline_texto.py` inexistente en el directorio local porque PR #7 aún no había sido fusionada en `main`.
3. Se fusionó PR #7 y se ejecutó `git pull --ff-only origin main`: avance local a `3273251`, con ambos archivos descargados por Git, sin descarga manual de ZIP.

## 3. Pruebas automatizadas en Windows

Comando: `.\\venv\\Scripts\\python.exe -m pytest -q .\\test_pipeline_texto.py`  
Salida informada: **9 passed in 0.14s**.

## 4. Ejecución real de Gemini

Comando: `.\\venv\\Scripts\\python.exe .\\pipeline_texto.py`. El cliente reportó las siguientes respuestas y métricas:

| Caso | Tema | Coincidencia cruda | Coincidencia procesada | Diferencia |
| --- | --- | ---: | ---: | ---: |
| 1 | Python | 83,3 % | 100,0 % | +16,7 puntos porcentuales |
| 2 | API | 57,1 % | 71,4 % | +14,3 puntos porcentuales |
| 3 | Git | 16,7 % | 50,0 % | +33,3 puntos porcentuales |

**Respuestas reales informadas:**

1. Python: «Python es un lenguaje de programación de alto nivel, interpretado y de propósito general, conocido por su sintaxis clara y legible.»
2. API: «Una API es un conjunto de reglas y protocolos que permite que diferentes aplicaciones de software se comuniquen e intercambien datos entre sí.»
3. Git: «Git sirve para **controlar y registrar los cambios en el código fuente** de un proyecto, facilitando el trabajo en equipo y el desarrollo de software.»

El archivo original [resultados_b15.json](../resultados_b15.json), generado en el entorno local del estudiante, fue **publicado y verificado en GitHub**, commit [`bc4fdbe`](https://github.com/nicolasbellov/especializacion-ia-2026/commit/bc4fdbe3eefba477b3c1e5724a09d02696f92569). Las tres respuestas y los seis valores de coincidencia coinciden con la consola aportada.

**Uso registrado:** 40 + 41 + 46 = **127 tokens**; `USD 0.000254` de costo **referencial didáctico**, no facturación real de Gemini.

## 5. Interpretación y límites

- Las tres coincidencias aumentaron tras normalizar; el caso 1 pasó a 100 % porque se corrigieron diferencias de mayúsculas y puntuación.
- El caso 2 mantuvo una coincidencia parcial porque una respuesta válida puede expresar el concepto con palabras distintas de la referencia.
- El caso 3 contiene formato Markdown (`**`) que la limpieza trata como puntuación; 50 % no implica que la respuesta sea mitad correcta.
- La métrica es cobertura de palabras **únicas** de la referencia: ignora orden, repeticiones, relaciones semánticas y posibles errores factuales.
- La normalización `[^\\w\\s]` elimina signos y puede alterar información importante en dominios sensibles; no utilizarla sin revisión en datos clínicos reales.
- La evaluación de comprensión del Bloque 15, Lecciones 1 y 2, fue **2/2 correcta**, evaluación formativa interna de conversación, no nota institucional.

## 6. Cierre y próximos pasos

**Cumplimiento técnico:** funciones solicitadas, 3/3 consultas reales, comparaciones antes/después y 9/9 pruebas locales **verificadas por salida del estudiante**.  
**Trazabilidad completada:** archivo JSON original versionado y disponible públicamente; se inspeccionó el contenido de los tres casos y no se observan credenciales ni datos personales sensibles. Esta revisión del contenido no reemplaza una auditoría de privacidad.  
**Pendiente institucional:** no hay constancia de envío, revisión ni calificación de Skillnest para esta actividad.

**Punto de continuación:** U2.2 · Bloque 16 · «Pon número a tus propias salidas generadas».
