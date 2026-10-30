# Estado académico — Especialización en Desarrollo con IA Generativa 2026

> **Actualizado:** 29/10/2026 (Chile). **Fuente:** material curricular compartido, conversación de estudio y evidencia versionada en este repositorio.  
> **Convención:** distinguir *evidencia técnica verificada*, *actividad completada en el entorno local*, *entrega publicada* y *aprobación formal informada por Skillnest*. No son equivalentes.

## Vista general

| Etapa | Alcance | Estado comprobable |
| --- | --- | --- |
| Módulo 1 — Fundamentos técnicos | 46 h curriculares; Gate 1 | Miniaplicación desarrollada; ensayo de instalación limpia y 19/19 pruebas documentados. **Aprobación formal del Gate 1: no confirmada aquí**. |
| **Módulo 2 — Construcción de componentes IA** | **88 h curriculares**; U2.1 a U2.8 | **En curso. U2.1: 7/9 lecciones técnicamente completadas; Bloque 14 actividad core aprobada con 13/13 pruebas pytest. Dos criterios de B13 requieren 429 real o aceptación de Skillnest**. |
| Módulo 3 — Desarrollo y despliegue end-to-end | 56 h curriculares; Gate 3 y proyecto integrador | Sin avance confirmado en este registro. |

**Total curricular del programa:** 190 h. Las horas curriculares no son horas efectivamente estudiadas; estas últimas se registran separadamente en [BITACORA_ESTUDIO.md](BITACORA_ESTUDIO.md).

## Módulo 1 — evidencia disponible

- Cliente Python/Gemini documentado en [README del proyecto](../README.md) y código en [src/consumir_gemini.py](../src/consumir_gemini.py).
- Ensayo del Gate 1: clonación desde GitHub, reconstrucción de entorno, petición real y **19/19 pruebas exitosas**, según [registro de ensayo](registro_ensayo_gate1.md), fechado el 21/10/2026.
- Evaluación institucional: **pendiente de confirmación del resultado formal**. La afirmación de «Gate 1 aprobado» en una lección posterior no sustituye una calificación o notificación del evaluador.

## Módulo 2 — recorrido

| Unidad | Tema | Seguimiento |
| --- | --- | --- |
| **U2.1** | Consumo avanzado de APIs de IA generativa | **En curso: Bloque 14 completo y actividad core verificada; 7/9 lecciones, dos lecciones de B13 no cerradas por HTTP 429 real**. |
| **U2.2** | Pipeline de texto, NLP básico y evaluación inicial | **En curso: 5/9 lecciones revisadas (55,6 %); Bloque 15 validado (9/9 pytest, 3/3 Gemini y JSON publicado); Bloque 16 L1 validada en Windows (17/17 pruebas B15+B16); Bloque 16 L2 validada en Windows: suite de 21/21 pruebas y cuatro ejemplos offline reproducidos. Entrega y evaluación institucional B15 pendientes.** |
| U2.3 | LangChain y orquestación de flujos | Pendiente |
| U2.4 | Agentes, herramientas externas y memoria | Pendiente |
| U2.5 | RAG y bases de datos vectoriales | Pendiente |
| U2.6 | Personalización: RAG, fine-tuning y soft-prompting | Pendiente |
| U2.7 | Observabilidad, seguridad y gobernanza técnica | Pendiente |
| U2.8 | Gate 2 — Integración y orquestación | Pendiente |

### U2.1 — control de lecciones

| Bloque | Lección/actividad | Estado | Evidencia |
| --- | --- | --- | --- |
| 12 | Autenticación y rate limits | Técnica validada | Respuesta real de Gemini; credencial inválida detectada como `ValueError` |
| 12 | Reintento ante error del proveedor | Técnica validada | Simulación: dos fallos, respuesta en tercer intento |
| 12 | Actividad: cliente modular con reintentos | **Implementada y publicada** | 4/4 pruebas simuladas, consulta real y commit [`f69c0f8`](https://github.com/nicolasbellov/especializacion-ia-2026/commit/f69c0f86bdef23bdac20a4be2f0d9975e6b94607) |
| 13 | Backoff y control de costo | **Completada técnicamente** | 5/5 pruebas B13 + 4/4 regresión B12 y consulta real a Gemini: 25 tokens, USD 0,000050 referenciales |
| 13 | Rate limit provocado | **Ensayo ejecutado; 429 real no observado** | 4/4 pruebas offline; 10/10 operaciones reales HTTP 200, 110 tokens, sin esperas de backoff; evidencia pendiente de 429 real |
| 13 | Límites y costos incorporados | **Revisión y pruebas integradas aprobadas; checklist global parcial** | Cuatro responsabilidades auditadas y cuatro pruebas integradas aprobadas en GitHub Actions; cierre Bloque 13 pendiente de HTTP 429 auténtico |
| 14 | Pruebas unitarias | **Completada técnicamente** | 3/3 pruebas pytest: HTTP 401, HTTP 429 simulado y HTTP 200; GitHub Actions aprobó además la regresión previa |
| 14 | Checklist del cliente modular | **Lección estudiada; matriz documentada** | [Cobertura de 12 comportamientos](checklist_cobertura_b14.md): tres pruebas pytest existentes, evidencias previas y brechas para la actividad final |
| 14 | Actividad core: escribir y verificar pruebas | **Completada técnicamente** | 13/13 pytest de los 12 criterios + metadata ausente; [GitHub Actions #40623902722](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40623902722) aprobó la suite y regresiones |

**Avance U2.1:** 7 de 9 lecciones, **77,8 % por cantidad de lecciones**, no por horas ni por ponderación oficial. La actividad práctica del Bloque 12 está publicada; no se cuenta como evaluación institucional aprobada.

### Entregable verificado de Bloque 12

- [`cliente_api.py`](../cliente_api.py): consumo HTTP y clasificación de errores.
- [`cliente_reintento.py`](../cliente_reintento.py): reintento acotado con espera fija.
- [`cliente.py`](../cliente.py): interfaz pública `consultar_modelo()`.
- [`pruebas_cliente_b12.py`](../pruebas_cliente_b12.py): cuatro escenarios probados.
- **Git:** rama `main`, commit `f69c0f8`, push confirmado y árbol limpio tras la entrega (según salida de PowerShell de la sesión).

### Próximo paso exacto

**Siguiente contenido: Bloque 16 / U2.2 — «Pon número a tus propias salidas generadas».** La actividad core del Bloque 14 está validada con pytest. En el seguimiento de U2.1 quedan sin cerrar dos lecciones del Bloque 13 que exigen observar un 429 auténtico o una aceptación explícita de Skillnest de la alternativa simulada.

### Primera lección del Bloque 13 completada · 27/10/2026

- **Origen de implementación:** rama `feature/u21-b13-backoff-costos`, preparada para integrar mediante PR #1 una vez documentada la validación.
- **Código publicado:** [commit `8b88a34`](https://github.com/nicolasbellov/especializacion-ia-2026/commit/8b88a342f6765587282f8e80624be6546bfd08db).
- **Validación Windows informada:** 5/5 pruebas B13 y 4/4 pruebas de regresión B12; ambos comandos terminaron con éxito.
- **Aspectos cubiertos:** espera exponencial 2→4 s, jitter y límite, `ValueError` no reintentable, total de tokens y costo referencial por operación, acumulación de sesión, ausencia de metadatos.
- **Importante:** costos = **simulación educativa de USD 0,002 por 1.000 tokens**, no costo real auditado ni facturación del proveedor.
- **Consulta real realizada en Windows con el cliente actualizado:** `consultar_modelo('Cual es la capital de Chile?')` devolvió Santiago; la consola informó **25 tokens**, **USD 0,000050 referenciales** y **USD 0,000050 acumulados**.
- **Lecciones contabilizadas como cerradas:** **4/9 (44,4 %)**. Cierre técnico verificado por ejecución del estudiante; no equivale a calificación institucional.

### Ensayo de rate limit · 27/10/2026

**Pruebas automatizadas adicionales:** [GitHub Actions - ejecución satisfactoria](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40620650829) con regresión Gate 1 + B12 + B13 + ensayo offline. **No** representa una observación de 429 real.

- **Pruebas offline:** 4/4 aprobadas. Incluyen `429 → 200`, tres `200`, error `401` y validación del tope de 10 operaciones.
- **Ensayo real con Gemini:** 10 operaciones exitosas, **10 respuestas HTTP 200**, **ningún HTTP 429**, sin reintentos ni backoff observados.
- **Tokens:** 11 por operación; 110 tokens informados en total.
- **Costo acumulado:** **USD 0,000220**, solo estimación didáctica a la tarifa del curso; no factura.
- **Interpretación:** los tests con mocks prueban el flujo de un 429, pero **no** demuestran que el proveedor devolvió un 429. El ensayo real tampoco lo provocó.
- **Evidencia:** [registro técnico](registro_ensayo_rate_limit_b13.md), [PR #2](https://github.com/nicolasbellov/especializacion-ia-2026/pull/2).
- **Avance académico:** permanece **4/9 lecciones**; la segunda lección del Bloque 13 conserva pendiente el criterio de observar un 429 auténtico.

### Lección 3 del Bloque 13 — repaso integral y checklist · 27/10/2026

- **Material revisado:** «Límites de uso y registro de costo, ya incorporados al cliente».
- **Cliente modular:** comunicación HTTP en cliente_api.py, reintentos en cliente_reintento.py, registro de costo e interfaz pública en cliente.py. Se conservaron los módulos existentes, sin duplicar el ejemplo monolítico.
- **Checklist:** [checklist_cierre_b13.md](checklist_cierre_b13.md), con criterios del curso, evidencias y límites documentados.
- **Pruebas integradas:** [pruebas_cierre_b13.py](../pruebas_cierre_b13.py), cuatro escenarios simulados (429 recuperado, 429 persistente, 401 y 500 recuperado), verificados por [GitHub Actions #40621224133](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40621224133) — **success**.
- **Pendiente académico:** el curso exige observar HTTP 429 real; no se ha conseguido. La tercera lección está revisada, pero **no se declara cerrado íntegramente el Bloque 13**.
- **Avance contabilizado sin sobredeclarar:** **4/9 lecciones (44,4 %)**, sin aprobación institucional inferida.

### Bloque 14 · Lección 1 — Pruebas unitarias · 27/10/2026

- **Fuente:** material Skillnest «Pruebas unitarias: la prueba de que tu cliente funciona».
- **Entregable:** [`test_cliente.py`](../test_cliente.py), con tres pruebas `test_enviar_peticion_*` para 401, 429 y 200 usando `pytest`, `Mock` y `patch`.
- **Adaptación al código real:** la función bajo prueba está en `cliente_api.py`, por lo que se parchea `cliente_api.requests.post`, no `cliente.requests.post`.
- **Instalación reproducible:** `pytest>=8,<10` agregado a `requirements.txt`, sin sobrescribir todo el archivo con un nuevo `pip freeze`.
- **Prueba CI confirmada:** [GitHub Actions #40622821093](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40622821093) `success`; pasó pytest y las baterías anteriores.
- **Límite:** los HTTP 401/429/200 de estas pruebas son **simulados**. No acreditan haber provocado un 429 auténtico.
- **Conteo:** 5/9 completadas en U2.1; el cierre global de B13 continúa con el criterio de 429 real pendiente.

### Bloque 14 · Lección 2 — Checklist del cliente modular · 27/10/2026

- **Material Skillnest revisado:** «Checklist de cliente modular: qué se revisa».
- **Resultado:** [matriz de doce comportamientos](checklist_cobertura_b14.md) en `enviar_peticion`, `con_reintento`, `registrar_costo` y `consultar_modelo`.
- **Cobertura actual:** tres pruebas `pytest` en `test_cliente.py` y pruebas adicionales en scripts B12/B13. Las pruebas fuera de `test_cliente.py` se mantienen como evidencia de regresión y **no** se presentan como suite final de la actividad.
- **Brechas:** 403, 500+ en prueba unitaria dedicada, propagación original de `TimeoutError` y consolidación de reintentos/costos/conversión de errores en `pytest`.
- **Punto siguiente:** actividad final del Bloque 14, escribir y comprobar la suite completa con GitHub Actions.
- **Avance:** 6/9 lecciones (66,7 %) por seguimiento interno; Bloque 13 mantiene pendiente el HTTP 429 auténtico.

### Bloque 14 · Actividad core — suite completa de pruebas unitarias · 27/10/2026

- **Fuente Skillnest:** «Escribe tus pruebas unitarias y verifica que pasen» (actividad core de Bloque 14).
- **Entrega:** [test_cliente.py](../test_cliente.py), 13 pruebas; los 12 escenarios del [checklist de cobertura](checklist_cobertura_b14.md) más respuesta sin metadata.
- **Aislamiento:** fixture autouse resetea el costo acumulado antes y después de cada prueba, mocks HTTP y sleep evitan red y esperas.
- **Dependencia:** pytest ya declarado en requirements.txt desde B14/L1; no se ha regenerado el archivo de dependencias.
- **Evidencia:** [GitHub Actions #40623902722](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40623902722) terminó con **success** en Python 3.12. Se ejecutaron pytest B14 y regresiones anteriores del Gate 1, B12 y B13.
- **Resultado académico interno:** actividad core aprobada técnicamente, U2.1 **7/9 (77,8 %)**. Esto NO equivale a cierre completo de U2.1: la evidencia de HTTP 429 auténtico en B13 aún falta.

### Entrega institucional B14 · 28/10/2026

- **Actividad:** «Bloque 14 - Escribe tus pruebas unitarias y verifica que pasen [Core]» (Skillnest LifeCycle).
- **Evidencia proporcionada:** captura de Skillnest con mensaje **«Entrega registrada»**, fecha visible **«Enviado el 28/10/2026»** y texto de que el instructor está revisando la actividad.
- **Estado institucional:** **entrega recibida; evaluación y calificación pendientes**. No atribuir aprobación institucional ni una nota hasta disponer del resultado del instructor.
- **Modalidad:** el estudiante trabajó mediante la opción «Enlace (Drive, etc.)» y se preparó una URL fija del repositorio GitHub. **La captura de confirmación no muestra el enlace finalmente registrado**, por lo que no certifica su valor exacto.
- **Código entregable validado previamente:** [commit `3dd1826`](https://github.com/nicolasbellov/especializacion-ia-2026/tree/3dd1826bac3f3d9fc09fcb8c64ca938ba1e5db5c), [13 pruebas en `test_cliente.py`](../test_cliente.py), [GitHub Actions aprobado](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40624041484).
- **Progreso académico interno:** se mantiene **U2.1 7/9 (77,8 %)**. El Bloque 13 sigue pendiente de evidencia de un HTTP 429 real o aceptación expresa del curso.

### U2.2 — Bloque 15 (29/10/2026)

- **Lecciones:** 1. «De texto crudo a vector»; 2. «Cuando la métrica engaña»; 3. actividad práctica «Construye tu pipeline de procesamiento de texto».
- **Evaluación formativa interna:** dos preguntas respondidas correctamente (2/2), no equivalente a calificación Skillnest.
- **Repositorio:** [pipeline_texto.py](../pipeline_texto.py), [test_pipeline_texto.py](../test_pipeline_texto.py); [PR #7](https://github.com/nicolasbellov/especializacion-ia-2026/pull/7) fusionada a main (`3273251`).
- **Ejecución local:** `pytest` 9/9 y tres consultas reales con `cliente.consultar_modelo`; las coincidencias crudas/procesadas fueron Python 83,3/100,0 %, API 57,1/71,4 %, Git 16,7/50,0 %.
- **Evidencia detallada:** [registro_pipeline_b15.md](registro_pipeline_b15.md). [resultados_b15.json](../resultados_b15.json) **publicado y verificado** mediante [commit `bc4fdbe`](https://github.com/nicolasbellov/especializacion-ia-2026/commit/bc4fdbe3eefba477b3c1e5724a09d02696f92569).
- **Interpretación:** la cobertura por palabras únicas no mide equivalencia semántica; no afirmar que 100 % significa una respuesta correcta.
- **Estado:** **Bloque 15 técnicamente validado**, no hay constancia de evaluación institucional ni de entrega de la actividad. **Avance U2.2: 3/9 (33,3 %)** por conteo de lecciones.
- **Continuidad:** Bloque 16, lección 1. Publicación del JSON ya comprobada; resta confirmar el envío/calificación institucional. No sumar horas no informadas.

### U2.2 — Bloque 16, lección 1 (29/10/2026)

- **Lección:** «Pon número a tus propias salidas generadas»: `Counter`, precisión, cobertura y F1 de tokens con repeticiones.
- **Código preparado:** [metricas_texto.py](../metricas_texto.py) y [test_metricas_texto.py](../test_metricas_texto.py). Se alimenta del [JSON original del Bloque 15](../resultados_b15.json) sin llamadas a Gemini.
- **Resultados calculados offline:** Python P/R/F1 = 28,6/100/44,4 %; API = 21,7/71,4/33,3 %; Git = 12,0/50,0/19,4 %.
- **Estado de verificación:** tras descargar el commit `9f4bec5`, el estudiante informó desde PowerShell **17 passed in 0.42s** para `test_metricas_texto.py` (8 pruebas) + `test_pipeline_texto.py` (9 pruebas). `metricas_texto.py` calculó los tres casos offline, con valores coincidentes; **sin nuevas llamadas a Gemini**. No se ha verificado aún una ejecución CI de esta suite.
- **Distinción técnica:** solapamiento de tokens no equivale a corrección factual ni semántica; valores bajos pueden penalizar reformulaciones acertadas.
- **Evaluación formativa (29/10/2026):** estudiante seleccionó P 40 %, R 80 %, F1 60 % para un caso de 4 coincidencias, 10 tokens generados y 5 de referencia. P y R correctos; F1 correcto **53,3 %** (fórmula armónica). **0/1 respuesta de opción múltiple completamente correcta; 2/3 cálculos parciales correctos**. Reforzar cálculo de F1. No es evaluación ni nota oficial.
- **Avance U2.2:** 4/9 lecciones **estudiadas** (44,4 %); código B16/L1 validado en Windows. Pendiente estudiar B16 L2 y completar la actividad oficial del bloque.
- **Punto siguiente:** Bloque 16 / «Por qué la métrica sola no basta».

### U2.2 — Bloque 16, lección 2 (29/10/2026)

- **Lección oficial:** «Sus límites: por qué la métrica sola no basta». Ejemplos sobre sinónimos, año diferente y negación omitida.
- **Material y cálculo:** F1 50 % en auto/vehículo, 80 % en 1991/1989, 90,9 % al quitar `no`, y 95,2 % al añadir `no` en el ejemplo legislativo. La coincidencia de tokens **no** determina corrección del significado.
- **Código complementario:** [ejemplos_limites_b16.py](../ejemplos_limites_b16.py) y [test_limitaciones_metricas_b16.py](../test_limitaciones_metricas_b16.py), basados en funciones existentes; no hay llamadas a la API ni modificaciones a `metricas_texto.py`.
- **Verificación en Windows aportada por el estudiante:** actualización a `38001b1`; suite conjunta de B15+B16 **21 passed in 0.46s** (9 + 8 + 4 pruebas). `ejemplos_limites_b16.py` reprodujo sinónimos 50,0 %, año distinto 80,0 %, negación omitida 90,9 % y negación añadida 95,2 % de F1. No se realizaron consultas a Gemini con este script; evidencia basada en consola local, no en ejecución CI.
- **Estado académico interno:** U2.2 **5/9 lecciones revisadas (55,6 %)**, sin cierre de todo el Bloque 16 ni calificación Skillnest.
- **Siguiente:** estudiar Bloque 16 L3 «Métricas ya calculadas sobre las salidas de tu propio cliente»; la validación local de B16 L2 ya fue confirmada.

## Cómo actualizar este archivo

1. Registrar cada lección solo después de estudiar su material y ejecutar la evidencia requerida.
2. Registrar la entrega en Git separadamente de la aprobación formal en Skillnest.
3. Registrar fechas límite solo cuando exista fuente oficial; **no hay fecha límite de U2.1 confirmada en este registro**.
4. Cada cambio técnico significativo debe enlazar su archivo, prueba y commit, y resumirse en [DECISIONES_TECNICAS.md](DECISIONES_TECNICAS.md).
5. No registrar datos personales sensibles, claves API ni contenido clínico real: este repositorio es **público**.
