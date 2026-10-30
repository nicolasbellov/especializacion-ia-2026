# Bitácora de estudio — Especialización IA 2026

## Propósito y reglas

Registro incremental de sesiones, aprendizaje, evidencias, errores y punto de reanudación. Se actualiza cuando existan datos verificables. **Nunca inferir tiempo efectivo a partir de la duración de un chat o de timestamps de Git**; registrar pausas, inicio y término explícitos cuando estén disponibles.

**Campos por sesión:** fecha Chile · módulo/unidad · actividad · inicio · término · tiempo efectivo · avance acumulado · contenidos · ejecución/evidencia · incidentes y solución · pendientes · punto exacto de continuidad.

## Registro acumulado

| Fecha (Chile) | Sesión | Actividad | Inicio | Término | Tiempo efectivo | Resultado |
| --- | --- | --- | --- | --- | --- | --- |
| 21/10/2026 | Antecedente M1 | Ensayo de instalación limpia del Gate 1, documentado en el repositorio | No registrado | No registrado | No registrado | 19/19 pruebas; Gemini real; reproducción local validada |
| **27/10/2026** | **M2-001** | **U2.1, Bloque 12: tres lecciones** | No cronometrado | No cronometrado | **Pendiente de informar** | **Cliente modular integrado; 4/4 pruebas, consulta real y push exitoso** |

> La fila de M1 recupera evidencia del repositorio; **no** significa que la calificación institucional del Gate 1 haya sido recibida.

## Detalle de la sesión M2-001 · 27/10/2026

**Programa:** Skillnest / Accenture / CChIA. **Etapa activa:** Módulo 2, U2.1 — Consumo avanzado de APIs. **Bloque:** 12.

### Contenidos desarrollados

1. Clasificación HTTP: `401/403` → autenticación/permisos sin reintento; `429` y fallas potencialmente transitorias → candidato a reintento; caso de `400 API_KEY_INVALID` observado en la práctica del cliente.
2. Manejo de `requests.post(..., timeout=10)`, variables de entorno con `python-dotenv` y protección de `.env`.
3. Reintentos mediante `con_reintento()`: máximo tres intentos, espera fija de dos segundos entre fallos, captura selectiva de `TimeoutError`.
4. Interfaz pública `consultar_modelo(pregunta, system_instruction="")`, encapsulación del envío, reintentos y extracción de texto.
5. Pruebas con `unittest.mock.patch` para evitar consumo innecesario de cuota; separación entre pruebas simuladas y llamada real.

### Evidencia verificada

- `cliente_api.py` creado, Gemini respondió correctamente a la prueba «Di hola».
- Prueba con credencial inválida en memoria: `ValueError` esperado; la clave real no se modificó en el archivo de entorno.
- `cliente_reintento.py`: dos errores simulados seguidos de respuesta exitosa en tercer intento.
- `pruebas_cliente_b12.py`: **4/4 escenarios correctos**: consulta normal, autenticación sin reintentos, recuperación y agotamiento con `RuntimeError`.
- `cliente.py`: consulta real «¿Cuál es la capital de Chile?» respondida por Gemini con Santiago.
- `git status`: `.env` ignorado; cambios duplicados en `requirements.txt` revertidos antes del commit.
- Commit **[`f69c0f8`](https://github.com/nicolasbellov/especializacion-ia-2026/commit/f69c0f86bdef23bdac20a4be2f0d9975e6b94607)** en `main`, push a `origin/main` confirmado y repositorio sin cambios pendientes después de publicarlo.

### Hallazgos / resoluciones

- **Archivo faltante:** `cliente_api.py` no existía inicialmente en la raíz; se creó mediante PowerShell.
- **Carga del entorno:** se añadió `load_dotenv()` para que `.env` se lea explícitamente.
- **API key inválida:** el proveedor puede responder `400 API_KEY_INVALID`; se incorporó clasificación adicional para no confundirlo con un error genérico.
- **Resultado inicialmente exitoso con clave supuestamente inválida:** se evitó asumir qué versión de `.env` estaba guardada; se probó el caso reemplazando el header **solo en memoria**.
- **Dependencias duplicadas:** se detectaron líneas extra de `requests` y `python-dotenv`; se restituyó `requirements.txt` a la versión original.
- **Avisos LF/CRLF:** Git advirtió conversión de finales de línea; no impidieron validación, commit ni ejecución.

### Limitaciones que quedan abiertas

- Los fallos `429` y los reintentos fueron verificados **por simulación**; no se reporta una medición de rate limit real.
- No hay todavía backoff exponencial, `Retry-After`, métricas por operación ni control de presupuesto.
- El código del Módulo 2 está en archivos independientes en la raíz; revisar futura integración con `src/consumir_gemini.py` para reducir duplicaciones.
- Tiempo efectivo de esta sesión: **no registrado**; completar solo con dato facilitado por el estudiante.

### Avance y punto de continuidad

- **U2.1: 3/9 lecciones = 33,3 % por conteo.**
- **Bloque 12: completado técnicamente y publicado.**
- **Próximo:** leer **Bloque 13 / «Backoff y control de costo, operación por operación»**, preservar las cuatro pruebas ya aprobadas y extender gradualmente el cliente.
- **Pendiente administrativo:** confirmar estado/calificación oficial del Gate 1 cuando se disponga de ese dato.

## Sesión M2-002 · 27/10/2026 — Bloque 13, primera lección

- **Actividad:** «Backoff y control de costo, operación por operación»; uso de material oficial compartido.
- **Inicio/término/tiempo efectivo:** no cronometrados; no inferir duraciones.
- **Implementación:** en rama `feature/u21-b13-backoff-costos`, [commit `8b88a34`](https://github.com/nicolasbellov/especializacion-ia-2026/commit/8b88a342f6765587282f8e80624be6546bfd08db): `cliente_reintento.py` (backoff exponencial, jitter, techo), `cliente.py` (costeo referencial y acumulado) y `pruebas_cliente_b13.py`.
- **Evidencia local informada:** **5/5 pruebas B13 aprobadas** y **4/4 de regresión B12 aprobadas**, desde PowerShell en Windows. Las pruebas simulan respuestas; no consumen cuota de Gemini.
- **Valores de prueba:** backoff sin jitter 2 s y 4 s; con jitter y techo de 3 s, 2,2 s y 3,0 s; costos referenciales de 42 y 57 tokens por USD 0,000084 y 0,000114, acumulado USD 0,000198.
- **Error 1:** un generador de código por sustitución de texto utilizó offsets calculados antes de insertar una importación, dando `SyntaxError: unmatched ')'`. Falló la validación *antes* de modificar los archivos.
- **Error 2:** un segundo script dependía de la variable `$script` no disponible en la sesión de PowerShell. Produjo mensajes de éxito falsos; `git status` seguía limpio y B12 seguía aprobando.
- **Error 3:** archivo adjunto `actualizar_b13.py` no disponible mediante descarga. Solución: se preparó el cambio directamente en una rama de GitHub accesible por `git fetch`/`git switch`, sin descargas manuales.
- **Advertencia de entorno:** la ejecución de `Activate.ps1` está restringida por PowerShell; usar directamente `.\\venv\\Scripts\\python.exe`, sin cambiar políticas de ejecución.
- **Consulta real confirmada:** después de `git pull --ff-only`, `consultar_modelo('Cual es la capital de Chile?')` devolvió Santiago; el cliente imprimió `Operacion: 25 tokens | USD referencial: 0.000050 | Acumulado: 0.000050`. Es una estimación didáctica y **no prueba un cargo real de USD 0,000050**. No se provocó ningún HTTP 429 en esta sesión.
- **Próximo punto exacto:** revisar la lección oficial B13 «Provocamos un rate limit a propósito», planificar la prueba de forma controlada y conservar evidencia de 9/9 pruebas y de la consulta real. Integrar la rama vía PR #1 luego del cierre documental.

### Cierre técnico de la sesión M2-002

- **Estado:** primera lección del Bloque 13 validada, con **9/9 pruebas automatizadas** aprobadas y petición real funcionando.
- **Progreso académico:** **U2.1 4/9 lecciones (44,4 %)**. Pendiente la evaluación institucional correspondiente, si la hubiera.
- **Nota de regresión:** en las pruebas del Bloque 12 el aviso «costo no estimable» es esperado, pues los mocks no traen `usageMetadata`.
- **Evidencia de integración:** PR #1 del repositorio; histórico de la rama `feature/u21-b13-backoff-costos`.

## Sesión M2-003 · 27/10/2026 — Bloque 13, segunda lección

- **Tema oficial:** «Provocamos un rate limit a propósito, para aprender a manejarlo».
- **Horas de inicio/término y tiempo efectivo:** no registrados; no inferir desde la consola.
- **Rama:** `feature/u21-b13-ensayo-rate-limit`. Ensayo independiente de `cliente.py`, con máximo 10 operaciones y observación de códigos HTTP mediante instrumentación temporal.
- **Pruebas simuladas:** **4/4 aprobadas**, con un `429` simulado seguido de `200` y recuperación; escenario sin `429`; error `401` sin reintento; verificación del máximo permitido.
- **Ensayo real:** 10 operaciones, 10 llamadas HTTP, **10 respuestas 200**, ninguna 429, ninguna espera de backoff, 10 respuestas `OK`.
- **Consumo informado:** 11 tokens por operación, **110 tokens** en total. Costo acumulado **USD 0,000220**, conforme a la tarifa **referencial académica** (no se ha comprobado facturación real).
- **Hallazgo:** el texto «HTTP 429 REAL OBSERVADO» aparecía en una prueba con `requests.post` simulado. No era evidencia de rate limit del proveedor. Se corrigió el ensayo para identificar explícitamente su modo **simulado** o **real**.
- **Conclusión:** validación positiva del procesamiento simulado de `429` y de diez respuestas reales exitosas, pero **no** se ha demostrado un `429` auténtico de Gemini; la lección queda **parcialmente validada**.
- **Seguridad:** no repetir en ráfagas ni incrementar automáticamente llamadas solo para alcanzar cuotas; conservar `.env` sin versionar.
- **Próximo punto exacto:** decidir una forma autorizada/acotada de verificar un `429` auténtico si se exige como evidencia; entretanto, los resultados reales y simulados permanecen claramente separados. Avance U2.1: **4/9**.

### Validación independiente en GitHub Actions

- [Workflow de pruebas offline](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40620650829): ejecución satisfactoria en Python 3.12 después de corregir los mensajes `real/simulado`.
- Etapas en verde: pruebas Gate 1, cliente Bloque 12, cliente Bloque 13 y ensayo de rate limit simulado.
- PR #2 fusionado a `main`, con el ensayo documentado como **sin 429 real observado**. No se incrementa el avance académico de 4/9 por esta integración.

### Confirmación local final tras integrar PR #2

- **Pruebas tras corregir la terminología real/simulado:** ejecución de `pruebas_ensayo_rate_limit_b13.py` reportada desde Windows, **4/4 aprobadas**, con marca `Tipo de ensayo: SIMULADO` y `HTTP 429 SIMULADO OBSERVADO` cuando correspondía.
- **Sin consultas adicionales a Gemini** durante esta validación offline. El ensayo real anterior sigue documentado como **10 HTTP 200, cero HTTP 429**.
- **Repositorio local:** `git switch main`, `git pull --ff-only` hasta el commit `dcb5884` y `git status -sb` produjo `## main...origin/main` (sin modificaciones pendientes).
- **CI adicional:** [ejecución GitHub Actions #40620774412](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40620774412) finalizada con resultado `success`.
- **Seguimiento:** se mantiene **4/9 lecciones**; está completa la documentación del ensayo, pero observar un rate limit auténtico permanece pendiente si el curso lo exige como criterio obligatorio.
- **Próximo contenido para estudiar:** Bloque 13, tercera lección «Límites de uso y registro de costo».

## Sesión M2-004 · 27/10/2026 — Bloque 13, tercera lección

- **Material oficial:** «Límites de uso y registro de costo, ya incorporados al cliente».
- **Inicio/término/tiempo efectivo:** no documentados, sin duraciones inferidas.
- **Actividad:** repaso del cliente modular completo y verificación de cuatro funciones/responsabilidades: enviar_peticion, con_reintento, registrar_costo y consultar_modelo.
- **Decisión:** mantener la separación modular existente y no reemplazar los archivos por el ejemplo monolítico del curso. Se conserva .env fuera del repositorio público.
- **Evidencia nueva:** [checklist técnico](checklist_cierre_b13.md), cuatro pruebas integradas simuladas de error/recuperación y costo único ([archivo de pruebas](../pruebas_cierre_b13.py)).
- **Validación CI:** [GitHub Actions #40621224133](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40621224133) **success** en Python 3.12, sin clave real ni llamadas de red.
- **Limitación principal:** se revisó el criterio de un 429 real, pero la única ejecución real anterior tuvo 10 respuestas HTTP 200. No declarar cumplido ese criterio ni atribuir éxito a un mock.
- **Progreso:** continúa U2.1 **4/9 (44,4 %)** por evidencia íntegra; la tercera lección está **revisada/auditada**, con checklist global parcial.
- **Punto exacto de continuidad:** obtener el contenido de la primera lección del Bloque 14, «Pruebas unitarias». Mantener pendiente la evidencia del HTTP 429 real o la aceptación de la simulación por Skillnest.

## Sesión M2-005 · 27/10/2026 — Bloque 14, primera lección

- **Material oficial:** «Pruebas unitarias: la prueba de que tu cliente funciona» (Skillnest).
- **Inicio, término, tiempo efectivo:** no registrados; no inferidos.
- **Conceptos:** prueba unitaria, aserciones (`assert`), excepción esperada (`pytest.raises`), mock HTTP (`unittest.mock.Mock` y `patch`), convención `test_` y ejecución aislada de una prueba.
- **Adaptación técnica:** usar `from cliente_api import enviar_peticion` y `patch("cliente_api.requests.post")`, ya que esa función no está definida directamente en `cliente.py`.
- **Código:** `test_cliente.py`, con tres escenarios: 401 -> `ValueError`, 429 -> `TimeoutError`, 200 -> diccionario JSON esperado.
- **Dependencias:** `pytest>=8,<10` añadido directamente al `requirements.txt` existente, sin reemplazar las versiones de las demás librerías.
- **Pruebas:** [GitHub Actions #40622821093](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40622821093) completado con `success`: nueva etapa `python -m pytest test_cliente.py -v` aprobada y sin regresiones en Gate 1, B12, B13 ni ensayo offline.
- **Seguridad y costo:** clave ficticia en CI, `requests.post` simulado en cada caso; sin solicitudes reales ni consumo de tokens.
- **Precisión:** el 429 es un valor de prueba simulado. El requisito de un 429 auténtico del Bloque 13 sigue sin acreditarse.
- **Avance U2.1:** de 4/9 a **5/9 (55,6 %)** tras evidencia CI de las tres pruebas. No representa aprobación institucional.
- **Próximo punto exacto:** Bloque 14, lección 2 «Checklist de cliente modular: qué se revisa».

## Sesión M2-006 · 27/10/2026 — Bloque 14, segunda lección

- **Lección:** «Checklist de cliente modular: qué se revisa» (Skillnest).
- **Inicio, término y tiempo efectivo:** no registrados; no inferir desde la conversación ni commits.
- **Trabajo realizado:** auditoría de cobertura de las cuatro funciones del cliente; distinción entre comportamiento implementado, prueba en `test_cliente.py` y evidencia de scripts anteriores.
- **Entregable:** [docs/checklist_cobertura_b14.md](checklist_cobertura_b14.md), con doce criterios, mapeo de las pruebas existentes y brechas concretas.
- **Hallazgos:** en nuestro repositorio el patch correcto para esperas es `cliente_reintento.time.sleep`, no `cliente.time.sleep`; el HTTP se simula en `cliente_api.requests.post`. Las pruebas de costo requieren restablecer el estado global entre casos.
- **Decisión:** no adelantarse a la actividad final escribiendo toda la suite en una lección cuyo objetivo es diseñar su checklist. Conservar B12/B13 y las tres pruebas pytest existentes.
- **Progreso:** U2.1, de 5/9 a **6/9 lecciones (66,7 %)** en el registro interno. No se acredita un 429 real ni evaluación institucional.
- **Próximo punto exacto:** compartir la actividad final de Bloque 14 «Escribe tus pruebas unitarias y verifica que pasen» y desarrollar en `test_cliente.py` la cobertura faltante antes de pasar a otra unidad.

## Sesión M2-007 · 27/10/2026 — Bloque 14, actividad core

- **Lección:** Skillnest, «Escribe tus pruebas unitarias y verifica que pasen».
- **Hora de inicio, término y tiempo efectivo:** no registrados; no inferir duraciones.
- **Implementación:** se completó [test_cliente.py](../test_cliente.py) con **13 pruebas pytest** sobre las cuatro funciones del cliente. Doce corresponden a los criterios del checklist y una a metadata ausente.
- **Fixture:** reiniciar_costo_total con autouse=True restablece el acumulado antes/después de cada caso; red y time.sleep están mockeados.
- **Verificación de calidad:** se comprueba también la identidad de errores originales donde corresponde y que el costo no se acumule al fallar consultar_modelo.
- **Validación remota:** [GitHub Actions #40623902722](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40623902722) completado con success; 13/13 pruebas B14 y etapas de regresión Gate 1, B12 y B13 sin errores.
- **Dependencias:** pytest ya consta en requirements.txt, por lo que no se volvió a instalar ni fijar en Git.
- **Resultado:** actividad core completada técnicamente; avance U2.1 de 6/9 a **7/9 (77,8 %)**.
- **Pendiente B13:** los 429 en pytest fueron simulados; faltan la observación auténtica del proveedor y el cierre global de B13, sin generar tráfico indiscriminado.
- **Continuidad:** sincronizar main tras merge del PR #6; leer el primer contenido de Bloque 15 / U2.2.

## Hito institucional · 28/10/2026 — Entrega core B14 registrada

- **Actividad:** «Escribe tus pruebas unitarias y verifica que pasen [Core]» del Bloque 14.
- **Prueba del envío:** captura proporcionada por el estudiante con el mensaje «Entrega registrada» y fecha visible «Enviado el 28/10/2026». La pantalla indica que la entrega está siendo revisada por el instructor.
- **Calificación:** **pendiente**. La aceptación de la plataforma no acredita aprobación académica ni nota.
- **Entregable técnico relacionado:** repo público en GitHub, commit `3dd1826` con `test_cliente.py` (13 pruebas) y [ejecución GitHub Actions satisfactoria](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40624041484).
- **Enlace de envío:** se utilizó la sección de URL de Skillnest; la captura de confirmación no deja visible cuál fue la URL registrada.
- **Inicio/término/tiempo efectivo de estudio:** no registrados; no inferir a partir de la fecha de entrega.
- **Avance:** **U2.1 7/9 (77,8 %)** según evidencia técnica, sin declarar 9/9 ni cierre total de la unidad por el requisito del HTTP 429 real de B13.
- **Pendientes:** esperar calificación institucional y revisar retroalimentación; mantener documentación del 429 real sin volver a forzar cargas sobre Gemini.
- **Punto exacto de continuidad:** iniciar estudio de **Unidad 2.2 · Bloque 15 — limpieza, tokenización y métricas**. Consultar evaluación de la entrega B14 cuando aparezca en Skillnest.

## Sesión M2-008 · 29/10/2026 — U2.2, Bloque 15 (lecciones 1–3)

- **Actividad:** «De texto crudo a vector», «Cuando la métrica engaña» y «Construye tu pipeline de procesamiento de texto [Actividad práctica]».
- **Inicio/término/tiempo efectivo:** no facilitados; no se estiman a partir del chat ni de Git.
- **Comprensión:** 2/2 respuestas correctas en evaluaciones formativas internas de las lecciones 1 y 2 (no son calificaciones oficiales).
- **Implementación:** [pipeline_texto.py](../pipeline_texto.py) y [test_pipeline_texto.py](../test_pipeline_texto.py), integrados a `main` mediante [PR #7](https://github.com/nicolasbellov/especializacion-ia-2026/pull/7), commit `3273251`.
- **Incidencias de entorno:** `pytest` ausente en `venv` y pipeline inexistente en el `main` local antes de fusionar PR #7. Solución: merge, `git pull --ff-only origin main` e instalación local de pytest 9.2.0.
- **Pruebas:** `9 passed in 0.14s`, ejecutadas con Python 3.12 desde PowerShell del estudiante.
- **API real:** tres consultas Gemini respondidas y comparadas: Python 83,3→100,0 %; API 57,1→71,4 %; Git 16,7→50,0 % (crudo→procesado).
- **Registro del cliente:** 127 tokens y USD 0,000254 acumulados, **costo referencial didáctico**; no confundir con facturación.
- **Evidencia:** [registro de ejecución y límites](registro_pipeline_b15.md). El script generó `resultados_b15.json` localmente; **publicación posterior confirmada** en [commit `bc4fdbe`](https://github.com/nicolasbellov/especializacion-ia-2026/commit/bc4fdbe3eefba477b3c1e5724a09d02696f92569), con contenido contrastado con los resultados de PowerShell.
- **Resultado:** Bloque 15 técnicamente validado; U2.2 **3/9 lecciones revisadas y actividad implementada (33,3 % por conteo)**, sin afirmar envío ni aprobación institucional.
- **Pendientes:** comprobar el estado de entrega y evaluación de esta actividad en Skillnest. JSON original ya publicado y verificado; tiempo efectivo no informado.
- **Punto exacto para continuar:** Bloque 16 · «Pon número a tus propias salidas generadas».

## Sesión M2-009 · 29/10/2026 — U2.2, Bloque 16, lección 1

- **Material oficial:** «Pon número a tus propias salidas generadas» (Bloque 16): `Counter`, intersección multiconjunto, precisión, cobertura/recall y F1 armónico.
- **Tiempo efectivo, inicio y término:** no informados; no inferir.
- **Implementación preparada:** [metricas_texto.py](../metricas_texto.py) reutiliza `procesar_texto` y el [JSON real del Bloque 15](../resultados_b15.json), sin consumir la API; [test_metricas_texto.py](../test_metricas_texto.py) incluye ocho pruebas offline.
- **Cálculo independiente de referencia:** Python, 6 coincidencias / 6 tokens de referencia / 21 generados: P 28,6 %, R 100 %, F1 44,4 %. API, 5 / 7 / 23: P 21,7 %, R 71,4 %, F1 33,3 %. Git, 3 / 6 / 25: P 12 %, R 50 %, F1 19,4 %.
- **Contraste con el Bloque 15:** los porcentajes de cobertura coinciden con la métrica previa en estos tres casos, pero ya no se asume que esto sucederá cuando existan repeticiones.
- **Límite:** son métricas de **solapamiento léxico**, no validan hechos, orden ni equivalencia semántica. F1 bajo no implica por sí solo una respuesta incorrecta.
- **Observación sobre la fuente:** `procesar_texto(None)` en la implementación existente lanza `TypeError`, no produce lista vacía; si la API devuelve `None`, debe validarse antes de llamar al pipeline.
- **Evaluación formativa en conversación (29/10/2026):** ante 10 tokens generados, 5 de referencia y 4 coincidencias, respuesta elegida: P = 40 %, R = 80 %, F1 = 60 %. **Corrección:** P = 40 % y R = 80 % acertados, F1 correcto = **53,3 %** (media armónica). Resultado de selección múltiple: **0/1 alternativa completamente correcta**; **2/3 componentes numéricos acertados**. Refuerzo pendiente: distinguir media aritmética de armónica. Esta evaluación no es calificación institucional.
- **Validación posterior en Windows (29/10/2026):** tras `git pull --ff-only origin main` hasta `9f4bec5`, se ejecutó `python -m pytest -q .\\test_metricas_texto.py .\\test_pipeline_texto.py` mediante el intérprete `venv`: **17 passed in 0.42s** (8 B16 + 9 B15). El script `metricas_texto.py` leyó el JSON de B15 y presentó P/R/F1 para los tres casos: Python 28,6/100,0/44,4 %; API 21,7/71,4/33,3 %; Git 12,0/50,0/19,4 %. **Sin nuevas llamadas a Gemini** durante el cálculo offline. Esta evidencia es salida de PowerShell enviada por el estudiante, no ejecución CI.
- **Estado:** lección 1 del Bloque 16 **técnicamente validada localmente**; U2.2: **4/9 lecciones** por material estudiado (44,4 %), sin aprobación institucional ni cierre del Bloque 16.
- **Continuidad:** estudiar Bloque 16 / lección 2 «Por qué la métrica sola no basta». Posteriormente desarrollar y publicar la actividad oficial del Bloque 16; no repetir llamadas a Gemini sin necesidad.

## Sesión M2-010 · 29/10/2026 — U2.2, Bloque 16, lección 2

- **Material oficial:** «Sus límites: por qué la métrica sola no basta». Tres fallos de la coincidencia léxica: castiga sinónimos válidos, no detecta hechos numéricos cambiados y puede premiar afirmaciones con negación omitida.
- **Inicio/término/tiempo efectivo:** no informados; no inventar minutos estudiados.
- **Implementación complementaria:** [ejemplos_limites_b16.py](../ejemplos_limites_b16.py) reutiliza `procesar_texto` y `calcular_precision_cobertura_f1` sin modificar las funciones centrales ni hacer llamadas API. [test_limitaciones_metricas_b16.py](../test_limitaciones_metricas_b16.py) incluye cuatro casos parametrizados; tres reproducen el curso y el cuarto reproduce la pregunta de comprensión del material.
- **Cálculos:** sinónimos P/R/F1 = 50/50/50 %; fecha diferente 80/80/80 %; negación omitida 100/83,3/90,9 %; negación añadida en ejemplo legislativo 90,9/100/95,2 %.
- **Verificación técnica posterior en Windows (29/10/2026):** el estudiante sincronizó `main` hasta `38001b1` mediante `git pull --ff-only origin main`. Ejecutó `python -m pytest -q .\test_pipeline_texto.py .\test_metricas_texto.py .\test_limitaciones_metricas_b16.py` con el intérprete `venv`: **21 passed in 0.46s** (9 B15 + 8 B16 L1 + 4 B16 L2). También ejecutó `ejemplos_limites_b16.py`: sinónimos F1 50,0 %, año diferente 80,0 %, negación omitida 90,9 %, negación agregada 95,2 %. El script es offline, sin llamadas a Gemini. Evidencia: salida textual de PowerShell facilitada por el estudiante; no se afirma verificación CI.
- **Criterio técnico:** F1 mide solapamiento de tokens. No establece equivalencia semántica, exactitud factual, seguridad ni validez de números/fechas o negaciones; en textos clínicos sintéticos, revisar negación explícitamente antes de adoptar resultados.
- **Avance:** U2.2 **5/9 lecciones revisadas (55,6 %)** por conteo. Bloque 16 L2 estudiada; actividad final B16 y calificación institucional aún pendientes.
- **Punto exacto de continuidad:** estudiar «Métricas ya calculadas sobre las salidas de tu propio cliente» (Bloque 16, lección 3). No repetir las pruebas B16 L2 ni generar nuevas llamadas a Gemini sin necesidad.

## Sesión M2-011 · 29/10/2026 — U2.2, Bloque 16, lección 3

- **Material oficial:** «Métricas ya calculadas sobre las salidas de tu propio cliente». Función `calcular_metricas` de extremo a extremo, aplicación a varias salidas reales, JSON UTF-8 con respuesta y referencia, promedios y orden de revisión por F1.
- **Inicio/término/tiempo efectivo:** no informados; no inferidos desde Git ni desde el chat.
- **Implementación:** [evaluar_salidas_b16.py](../evaluar_salidas_b16.py) integra el procesamiento B15 con precisión/cobertura/F1 B16. Reutiliza las **tres respuestas originales** de [resultados_b15.json](../resultados_b15.json); no genera nuevas solicitudes ni consume cuota. [test_evaluar_salidas_b16.py](../test_evaluar_salidas_b16.py) incorpora **8 pruebas offline**.
- **Evidencia reproducible:** [resultados_metricas.json](../resultados_metricas.json), que conserva consulta, referencia, respuesta real, precisión, cobertura y F1. [Registro interpretativo](registro_metricas_b16.md) con fórmulas, límites y decisiones.
- **Resultados:** Python P/R/F1 28,6/100,0/44,4 %; API 21,7/71,4/33,3 %; Git 12,0/50,0/19,4 %. Promedios simples: P **20,8 %**, R **73,8 %**, F1 **32,4 %**. Prioridad de lectura por F1: Git → API → Python; esto no ordena calidad factual.
- **Contraste con el material:** el F1 medio cercano a 0,61 del ejemplo oficial corresponde a valores ilustrativos distintos, no a nuestras salidas reales.
- **Verificación:** 8/8 pruebas nuevas aprobadas y script ejecutado en entorno Python independiente; **ejecución Windows del estudiante pendiente** (29 pruebas esperadas: 21 anteriores + 8 nuevas).
- **Estado:** B16 lecciones 1–3 revisadas y nuevas funciones publicadas en repositorio; U2.2 **6/9 lecciones revisadas (66,7 %)**, sin atribuir calificación institucional.
- **Punto exacto de continuación:** sincronizar y verificar `evaluar_salidas_b16.py` en Windows; luego Bloque 17 L1 «Cuando el número no basta: criterio cualitativo».

## Plantilla para próximas sesiones

```markdown
### AAAA-MM-DD · Sesión M2-00X
- Módulo / unidad / bloque / lección:
- Inicio (hora Chile):
- Término (hora Chile):
- Pausas:
- Tiempo efectivo:
- Avance anterior → nuevo:
- Conceptos aprendidos:
- Código / archivos modificados:
- Pruebas y resultados:
- Errores y resolución:
- Evidencia (commit, enlace, salida):
- Pendientes:
- Punto exacto de reanudación:
```
