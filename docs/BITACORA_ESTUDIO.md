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
- **Validación Windows (29/10/2026):** estudiante ejecutó el conjunto B15+B16 de **29/29 pruebas aprobadas en 0,97 s** y `evaluar_salidas_b16.py` sin llamadas a Gemini. Se reprodujeron P/R/F1 de las tres consultas, los promedios P 20,8 %, R 73,8 %, F1 32,4 % y el orden Git → API → Python. Evidencia: salida PowerShell aportada por el estudiante; no equivale a ejecución CI.
- **Estado:** B16 lecciones 1–3 revisadas y nuevas funciones publicadas en repositorio; U2.2 **6/9 lecciones revisadas (66,7 %)**, sin atribuir calificación institucional.
- **Incidente de reproducibilidad JSON:** `git status -sb` mostró únicamente `M resultados_metricas.json` luego de ejecutar el script. La versión generada por Python escribe `"cobertura": 1.0` para el caso Python (división `6/6`), mientras la primera versión del archivo subida a GitHub contenía `"cobertura": 1`; son numéricamente equivalentes, pero producen diferencias textuales en Git. Se corrigió en el repositorio la representación a `1.0` para respetar el serializador Python y evitar cambios espurios al regenerar evidencia. **Cierre confirmado por salida PowerShell:** `git diff` identificó exactamente esa línea; el estudiante ejecutó `git restore -- resultados_metricas.json`, `git pull --ff-only origin main` hasta `85dc97c`, regeneró el JSON con `evaluar_salidas_b16.py` y `git status -sb` devolvió `## main...origin/main`, sin cambios pendientes.
- **Punto exacto de continuación:** Bloque 17 L1 «Cuando el número no basta: criterio cualitativo». Bloque 16 validado localmente y evidencia JSON reproducible, sin aprobación institucional atribuida.

## Sesión M2-012 · 29/10/2026 — U2.2, Bloque 17, lección 1

- **Material oficial estudiado:** «Cuando el número no basta: criterio cualitativo»: señales de revisión manual, rúbrica uniforme de corrección factual (sí/no/parcial), completitud (sí/no/parcial) y contradicción (sí/no), con justificaciones; selección de F1 bajos y altos.
- **Inicio/término/tiempo efectivo:** no informados; no atribuir minutos al usuario.
- **Ejemplo del curso (partido):** al omitir «3 goles a 1», precisión 100 %, cobertura 64,3 % y F1 78,3 %, pero la valoración cualitativa oficial es factual «sí», completitud «no», contradicción «no».
- **Implementación complementaria:** [revision_cualitativa_b17.py](../revision_cualitativa_b17.py) selecciona extremos sin duplicados; [test_revision_cualitativa_b17.py](../test_revision_cualitativa_b17.py) contiene 11 pruebas offline; [revision_cualitativa_b17.json](../revision_cualitativa_b17.json) conserva tres pares reales, orden Git→API→Python, con valores cualitativos nulos **pendientes de evaluación humana**. No consulta Gemini ni escribe juicios por cuenta del estudiante.
- **Documentación:** [registro_revision_cualitativa_b17.md](registro_revision_cualitativa_b17.md) separa contenido del curso, adaptación técnica a muestra pequeña y límites.
- **Validación en Windows (29/10/2026):** el estudiante sincronizó `main` hasta `7b82c96` mediante `git pull --ff-only origin main`; ejecutó `pytest` sobre las cinco suites B15+B16+B17 con **40 passed in 0.72s** (29 previas + 11 nuevas). `revision_cualitativa_b17.py` seleccionó los tres casos Git (19,4 %), API (33,3 %) y Python (44,4 %) sin duplicados y confirmó `Archivo existente preservado sin cambios`, sin llamadas a Gemini. `git status -sb` devolvió `## main...origin/main`, árbol limpio. Evidencia: salida PowerShell aportada por el estudiante; no CI.
- **Avance:** U2.2 **7/9 lecciones revisadas (77,8 %)**. B17 L1 estudiada y técnicamente validada en Windows; **siguen pendientes los juicios humanos para Git, API y Python**, sin calificación institucional atribuida.
- **Punto exacto de continuación:** revisar humanamente el caso real Git con la rúbrica (corrección factual, completitud, contradicción y justificación), luego API y Python. A continuación B17 L2 «Qué documentar como límite de tu pipeline». No repetir pruebas ni API sin necesidad.

## Sesión M2-013 · 29/10/2026 — U2.2, Bloque 17, lección 2

- **Material oficial:** «Qué documentar como límite de tu pipeline». Cuatro partes del documento: definición de la métrica, fallos con ejemplos, tamaño y criterio de muestra realmente revisada, y recomendación de uso. Versionar el archivo en Git y añadir fechas/hallazgos sin borrar antecedentes.
- **Inicio/término/tiempo efectivo:** no informados; no inferirlos de los cambios en el repositorio.
- **Documento creado:** [limites_metrica.md](limites_metrica.md), junto al código y la rúbrica. Distingue ejemplos oficiales de los resultados de Gemini y de evaluaciones humanas aún no realizadas.
- **Modos de falla conocidos:** sinónimos (F1 50 %), fecha diferente (80 %), negación omitida (90,9 %), negación añadida (95,2 %) e información relevante omitida (78,3 %), todos como **ejemplos del material Skillnest**, no hallazgos de revisión propia.
- **Muestra propia:** 3 respuestas reales de B15 (Git, API, Python), seleccionadas sin duplicados por extremos de F1; **0/3 revisiones cualitativas humanas terminadas** al registrar esta lección. No se inventaron calificaciones, fechas de revisión individual ni hallazgos de errores propios.
- **Verificación técnica:** cambio solo documental; código y suite previa de **40/40 pruebas** no modificados. No se ha recibido una nueva ejecución, y no se requiere API.
- **Avance:** U2.2 **8/9 lecciones revisadas (88,9 %)**. B17 L2 documentada; falta completar la revisión humana y la actividad **B17 Core «Interpreta tus resultados y documenta sus límites»**, además de cualquier envío/evaluación institucional.
- **Punto exacto de continuación:** aplicar rúbrica con justificación a las respuestas Git, API y Python, incorporando hallazgos a [limites_metrica.md](limites_metrica.md) solo si la evidencia lo sostiene; después abordar la actividad Core del B17.

## Sesión M2-014 · 29/10/2026 — U2.2, Bloque 17, actividad Core (preparación)

- **Fuente oficial:** «Interpreta tus resultados y documenta sus límites [Actividad core]», más captura de entrega por enlace Skillnest. **Requisitos verificables:** 20 respuestas reales obtenidas con `consultar_modelo` y sus métricas; 10 revisiones manuales (5 F1 bajos + 5 altos) con rúbrica/nota; documento de límites basado en hallazgos propios; evidencia publicada en Git y enlace presentado en Skillnest.
- **Estado previo:** **3/20 respuestas** reales versionadas (B15), **0/10 revisiones humanas Core**, `docs/limites_metrica.md` inicial con ejemplos del curso, sin hallazgos de revisión humana propia. La suite acumulada B15+B16+B17 L1 **40/40** aprobada en Windows en sesión anterior.
- **Preparación de software, no ejecución real:** [core_b17_generar.py](../core_b17_generar.py) agrega 17 consultas técnicas con referencias explícitas y llamadas posteriores a `cliente.consultar_modelo` en el entorno local. Guárdalas incrementalmente y reanuda tras errores sin consultas duplicadas. `--plan` no hace peticiones ni escribe archivos; `--generar` sí puede consumir cuota o generar cargos.
- **Revisión humana, aún no realizada:** [core_b17_revisar.py](../core_b17_revisar.py) selecciona 5 + 5 extremos sin duplicados a partir de 20 respuestas, presenta las parejas y exige que el estudiante registre factual, completitud, contradicción y justificación. Guarda tras cada revisión y permite exportar [informe Core pendiente](revision_manual_core_b17.md) solo cuando se hayan completado las diez.
- **Pruebas preparadas:** [test_core_b17.py](../test_core_b17.py) agrega **15 pruebas offline con simulaciones exclusivamente de prueba**, que no se cuentan como respuestas reales. Total esperado de suite conjunta: **55**; ejecución local de estas pruebas **pendiente**.
- **Guía y trazabilidad:** [guia_entrega_b17_core.md](guia_entrega_b17_core.md) registra comandos PowerShell, entregables exactos y criterios de no enviar antes de cumplir 20/10 y ajustar límites propios.
- **Inicio/término/tiempo efectivo:** no informados; no inferir tiempos.
- **Avance curricular:** U2.2 se mantiene en **8/9 (88,9 %)** lecciones revisadas: actividad Core examinada y herramientas preparadas, **todavía no completada, enviada ni aprobada por Skillnest**.
- **Punto exacto para continuar:** sincronizar `main`, validar las 55 pruebas esperadas, ejecutar `core_b17_generar.py --plan`; tras confirmación, ejecutar `--generar --max-nuevas 17` con clave local para obtener 20/20. Luego documentar 10 juicios humanos y actualizar límites a partir de evidencia propia.

## Sesión M2-015 · 29/10/2026 — U2.2, Bloque 17 Core: ejecución y rúbrica

- **Evidencia aportada:** transcripción completa de PowerShell del estudiante, con comandos y resultados locales. No se han recibido aún los archivos completos `resultados_core_b17.json` y `revision_manual_core_b17.json` para inspección ni están publicados en GitHub.
- **Pruebas técnicas:** actualización a `8e2432e`, conjunto B15+B16+B17+Core **55 passed in 1.50s**. `core_b17_generar.py --plan` confirmó 3/20 reales, 17 pendientes y cero llamadas de ese modo.
- **Generación real:** ejecución `--generar --max-nuevas 17` con cliente conectado; los 17 casos nuevos se guardaron progresivamente hasta **20/20 reales**. Caso 20 requirió dos reintentos y acabó guardado; el log **no identifica el HTTP concreto**, por lo que no afirmar 429 real. Costo estimado exclusivamente **didáctico** para el lote nuevo: **USD 0,001588 referenciales**, no facturación verificada.
- **Selección y revisión:** `--preparar` seleccionó exactamente **10 casos** de los extremos F1: 3, 14, 20, 2, 11, 12, 8, 9, 5 y 16. `--revisar` registró diez valoraciones manuales con notas. Interrupciones en casos 12 y 9 fueron recuperadas sin perder los casos previos. `--validar` informó **20/20 y 10/10**, y `--informe` creó localmente `docs/revision_manual_core_b17.md`.
- **Control de calidad crítico:** el **caso 16 (`git clone`) quedó grabado con `contradiccion: "si"`**, mientras su justificación afirma «no contiene contradicciones». Es una discrepancia semántica no detectable por el validador estructural. El estudiante **aún no ha confirmado la corrección**. Casos 12 y 9 se retomaron y fueron guardados correctamente con contradicción «no», según el log.
- **Entrega:** no atribuida como completa. Falta corregir caso 16, volver a validar y regenerar informe, inspeccionar los dos JSON locales, **actualizar `docs/limites_metrica.md` con hallazgos realmente documentados** y publicar los artefactos finales vía PR/merge. Tampoco existe evidencia de envío ni calificación Skillnest.
- **Avance curricular:** U2.2 **8/9 lecciones revisadas (88,9 %)**; Core en ejecución avanzada con 20/20 y 10/10 **según salida local**, sujeto a QA semántico y publicación final.
- **Inicio/término/tiempo efectivo:** no informados; no inventar horas.
- **Punto exacto de continuación:** corregir únicamente `contradiccion` del caso 16 a `no` si el estudiante confirma esa valoración; ejecutar `core_b17_revisar.py --validar` y `--informe`, recibir y auditar JSON e informe, redactar hallazgos propios, publicar la entrega y recién después evaluar envío a Skillnest.
- **Actualización y cierre del incidente con evidencia posterior:** el estudiante ejecutó `Copy-Item` para respaldar el JSON, corrigió solo `contradiccion` del caso 16 de `si` a `no` (con `assert` de identificación única y valor anterior) y obtuvo `Caso 16 corregido: contradiccion = no`. Volvió a ejecutar `--validar`: **20/20 y 10/10, VÁLIDO**; regeneró `docs/revision_manual_core_b17.md`. Los diez registros de la consola quedan con corrección factual **10 sí**, completitud **7 sí, 2 parcialmente y 1 no**, contradicción **10 no**.
- **Límites y QA:** [limites_metrica.md](limites_metrica.md) actualizado con ejemplos **propios** (Git, API REST, HTTP, funciones Python, listas y tokenización) y [análisis de la transcripción](analisis_revision_b17_core.md) publicado. La evidencia original completa sigue **local y no recibida**; esta documentación basada en la consola **no reemplaza** el corpus y la revisión JSON del Core.
- **Punto exacto actualizado:** recibir `resultados_core_b17.json`, `revision_manual_core_b17.json` y `docs/revision_manual_core_b17.md`, auditarlos y publicarlos mediante PR/merge; confirmar después el enlace de entrega a Skillnest. La Unidad 2.2 permanece 8/9 hasta ese cierre.

## Cierre M2-015 · 29/10/2026 — Bloque 17 Core

- Se recibieron y auditaron los tres artefactos originales: [corpus](../resultados_core_b17.json), [rúbrica](../revision_manual_core_b17.json) e [informe](revision_manual_core_b17.md).
- Auditoría: 20 casos únicos; 60/60 métricas reproducidas; muestra de cinco F1 inferiores y cinco superiores; diez valoraciones y justificaciones fieles al informe; caso 16 corregido a contradicción `no`.
- Se documentaron los hallazgos concretos en [limites_metrica.md](limites_metrica.md). Las pruebas 55/55 y llamadas Gemini constan en el registro local compartido por el estudiante.
- **U2.2: 9/9 lecciones (100 %) técnicamente completadas.** No consta entrega ni aprobación institucional en Skillnest.
- Horas efectivas no informadas. Punto exacto para continuar: sincronizar las evidencias en local sin perder las copias originales, enviar el enlace GitHub en Skillnest y registrar comprobante.

## Hito M2-016 · 29/10/2026 — Envío de actividad Core B17 a Skillnest

- **Acción declarada:** el estudiante confirmó explícitamente en el chat: **«Entregado»** después de incorporar el enlace de GitHub en la pantalla de envío de Skillnest.
- **Referencia de entrega:** [guía e índice de evidencias](guia_entrega_b17_core.md), con 20 respuestas reales, 10 evaluaciones cualitativas, informe y límites basados en casos revisados.
- **Estado:** **envío institucional confirmado por declaración del estudiante**, sin acuse de recibo ni nota visibles en esta conversación. No afirmar aprobación o calificación.
- **Avance técnico:** U2.2 **9/9 lecciones (100 %)**. **Pendiente:** eventual retroalimentación/aprobación de Skillnest. **Punto exacto desde donde continuar:** U2.3, Bloque 18: LangChain y plantillas parametrizables; usar como base los aprendizajes de evaluación de texto de U2.2.
- **Tiempo efectivo:** hora de inicio/término y duración no informados.

## Sesión M2-U2.4-B21 · 09/11/2026 — Primer agente y actividad Booking Core AI

- **Unidad / bloque:** U2.4 · Bloque 21.
- **Lección 1:** «Chain vs agente» revisada a partir del material de Skillnest. Conceptos: autonomía de selección de herramientas, ReAct, costo variable y trazabilidad.
- **Lección 2:** laboratorio de dos herramientas **ejecutado por el estudiante** en Windows con Gemini. Traza observada: `buscar_en_documentacion({'consulta': 'reintentos'})` → **3 reintentos**; `calcular({'expresion': '3 * 2'})` → **6**. Respuesta correcta y `intermediate_steps` disponibles. `src/agente_b21_demo.py` y `langchain-classic==1.0.8` publicados. En una ejecución Gemini devolvió bloques de texto con metadatos; se considera un formato de salida, no fallo funcional.
- **Incidente Git local resuelto:** la rama local `feature/u2-3-b20-core-verificacion` divergía de `origin/main`. El estudiante respaldó archivos con `git stash push -u` y completó `git merge --no-ff origin/main` sin conflictos. **No** ejecutar `stash pop` automáticamente porque contiene rutas ya publicadas en main.
- **Lección 3 (actividad práctica):** código propio de dominio **Booking Core AI** publicado en [`src/agente_b21_booking_core.py`](../src/agente_b21_booking_core.py) con dos herramientas de solo lectura (`consultar_servicios` y `consultar_disponibilidad`), datos simulados, `AgentExecutor`, `return_intermediate_steps=True`, límites y extracción de texto. [Protocolo y checklist](u2_4_b21_actividad_booking_core.md).
- **Validación de lección 3:** **pendiente** de dos invocaciones reales con Gemini en Windows, una por herramienta; la publicación de código no equivale a ejecución aprobada.
- **Hora de inicio / término y tiempo efectivo:** no informados; no calcular horas ni atribuir calificación.
- **Avance verificable:** lecciones 1 y 2 revisadas; lección 2 validada con Gemini. Lección 3 implementada pero no cerrada técnicamente. Sin aprobación institucional informada.
- **Próximo paso exacto:** en la rama local sincronizar `origin/main` sin descartar el respaldo; ejecutar `python -m src.agente_b21_booking_core`; comprobar los dos `intermediate_steps` y documentar la salida. Luego continuar al Bloque 22.

## Cierre M2-U2.4-B21 · 09/11/2026 — Actividad propia con dos herramientas

- **Evidencia recibida:** salida de PowerShell compartida por el estudiante tras ejecutar `python -m src.agente_b21_booking_core` con `(.venv)` activo.
- **Caso 1 (servicios):** `consultar_servicios({'servicio': 'corte'})` elegido correctamente; respuesta: corte de cabello ficticio **$15.000 CLP**, **40 minutos**; terminal informó `VALIDACIÓN MANUAL: OK (herramienta: consultar_servicios)`.
- **Caso 2 (agenda):** `consultar_disponibilidad({'servicio': 'corte', 'fecha': '2026-11-11'})` elegido correctamente; horarios simulados **10:00, 16:00 y 18:30**; terminal informó `VALIDACIÓN MANUAL: OK (herramienta: consultar_disponibilidad)`.
- **Cierre de ejecución:** `ACTIVIDAD B21: DOS VALIDACIONES MANUALES CORRECTAS.` **2/2 casos correctos**, sin excepciones observadas. Las decisiones se validaron leyendo `intermediate_steps`, no solo la respuesta textual.
- **Documento de evidencia:** [U2.4 B21 Booking Core AI](u2_4_b21_actividad_booking_core.md), actualizado con traza depurada (sin metadatos/firmas).
- **Estado académico:** las tres lecciones del Bloque 21 están revisadas; lecciones 2 y 3 verificadas técnicamente con Gemini real. **Bloque 21 cerrado técnicamente (3/3 lecciones).** Entrega en Skillnest y aprobación **no confirmadas**.
- **Tiempo efectivo y horas de término/inicio:** no informados; evitar suposiciones.
- **Código:** en `main` de GitHub, `src/agente_b21_booking_core.py`. **Estado local:** ejecución funcional, pero no se dispone del estado Git posterior; la rama anterior era `feature/u2-3-b20-core-verificacion`, con `stash` aún por conciliar. No hacer `stash pop` o `reset --hard` sin revisar.
- **Punto exacto de reanudación:** revisar envío de actividad si corresponde, y avanzar a **U2.4 / Bloque 22 — Cómo construir una herramienta personalizada para tu agente**, ampliando Booking Core AI con pruebas, mejor separación de datos y memoria entre interacciones.

## Inicio M2-U2.4-B22 · 09/11/2026 — Herramienta personalizada con args_schema

- **Lección:** «Cómo construir una herramienta personalizada para tu agente» (Bloque 22, lección 4/9 de U2.4).
- **Conceptos del curso:** `BaseModel`, `Field(description=...)`, `@tool(args_schema=...)`, nombre explícito de herramienta, `invoke` y `ValidationError`.
- **Aplicación a Booking Core AI (propuesta complementaria):** [`src/herramienta_b22_booking_core.py`](../src/herramienta_b22_booking_core.py), basada en los datos ficticios B21. Herramienta `consultar_disponibilidad_con_filtros` con cuatro parámetros: `fecha`, `servicio`, `hora_desde` e `incluir_duracion`. Se conservó la posibilidad de ejecutar tests directos sin API y un modo opcional `--agente`.
- **Documento de actividad:** [guía de B22/L1](u2_4_b22_herramienta_personalizada.md).
- **Evidencia y estado:** implementación publicada en GitHub. **Pendiente** de ejecución de pruebas locales en Windows y de validación real de Gemini. No declarar lección validada técnicamente aún.
- **Inicio/término y tiempo efectivo:** no informados.
- **Estado Git local:** rama anterior `feature/u2-3-b20-core-verificacion`; se debe comprobar `git status --short` y conciliar los cambios remotos. Existe stash histórico local que no debe aplicarse a ciegas.
- **Punto exacto siguiente:** ejecutar `python -m src.herramienta_b22_booking_core`, revisar resultados y, opcionalmente, `--agente`; luego estudiar «Que tu agente recuerde: memoria entre interacciones».

## Cierre M2-U2.4-B22/L1 · 09/11/2026 — Pydantic y Gemini reales

- **Fuente de evidencia:** consola PowerShell compartida por el estudiante, entorno `(.venv)`; dos ejecuciones: `python -m src.herramienta_b22_booking_core` y `python -m src.herramienta_b22_booking_core --agente`.
- **Pruebas directas:** nombre expuesto `consultar_disponibilidad_con_filtros`; consulta base devolvió horas ficticias **10:00, 16:00, 18:30**; consulta filtrada desde **18:00** devolvió **18:30** y duración **40 min**; `incluir_duracion="tal vez"` produjo el `ValidationError` esperado, identificado en el campo `('incluir_duracion',)`. Terminal: `B22/L1: TRES COMPROBACIONES DIRECTAS CORRECTAS.`
- **Prueba real Gemini:** invocó `consultar_disponibilidad_con_filtros` con `{'hora_desde': '18:00', 'servicio': 'corte', 'fecha': '2026-11-11', 'incluir_duracion': True}`, recibió una observación simulada de **18:30** y **40 min**; `intermediate_steps` registró acción y observación. Terminal: `AGENTE: herramienta personalizada invocada correctamente.`
- **Conclusión:** **Bloque 22, lección 1 validada técnicamente**, con datos simulados, sin errores de ejecución observados. Avance U2.4 **4/9 lecciones** revisadas y validadas técnicamente; Bloque 21 3/3 y Bloque 22 1/3. Este avance no representa aprobación institucional.
- **Evidencia documentada:** [U2.4 B22/L1](u2_4_b22_herramienta_personalizada.md).
- **Incidente Git resuelto en Windows:** se respaldó `docs/BITACORA_ESTUDIO.md` fuera del repositorio; se resolvió un conflicto `UU` con la versión entrante, commit local `554102c`; después se completó un merge de `origin/main` que incorporó el código B22. La rama local `feature/u2-3-b20-core-verificacion` había divergido previamente de su rama remota; se desconoce el estado posterior de sincronización. Evitar `git stash pop` automático.
- **Horas de inicio/término y tiempo efectivo:** no informados, no inferir.
- **Punto exacto de continuación:** Bloque 22, lección 2, «Que tu agente recuerde: memoria entre interacciones». Mantener Booking Core AI como ejercicio progresivo.

## Inicio M2-U2.4-B22/L2 · 09/11/2026 — Memoria conversacional por sesión

- **Lección:** «Que tu agente recuerde: memoria entre interacciones» (quinta lección de U2.4, segunda del Bloque 22).
- **Fuente Skillnest:** `RunnableWithMessageHistory`, `InMemoryChatMessageHistory`, `session_id`, `MessagesPlaceholder("chat_history")` y separación respecto de `agent_scratchpad`; memoria temporal, aumento de tokens y cierre de sesión.
- **Aplicación incremental Booking Core AI:** [`src/memoria_b22_booking_core.py`](../src/memoria_b22_booking_core.py). Conserva AgentExecutor y las herramientas simuladas anteriores. Usa dos turnos: consulta de corte el 11/11/2026 seguida de «¿Y después de las 18:00? Incluye cuánto dura». Evalúa que la segunda llamada incorpore servicio y fecha del historial.
- **Adaptación técnica complementaria:** normalización de salida por bloques de Gemini a texto antes de almacenar la respuesta en `RunnableWithMessageHistory` (motivada por la traza real B21/B22). `output_messages_key="output"` explícito.
- **Evidencia publicada:** [guía y checklist del ejercicio](u2_4_b22_memoria_conversacional.md).
- **Pruebas preparadas:** simulación sin consumo API para comprobar 2/4 mensajes, sesiones independientes, eliminación y normalización; modo opcional `--agente` para verificar dos turnos reales con Gemini.
- **Estado:** código/documentación en GitHub; **no** hay ejecuciones aportadas de esta nueva lección; por tanto, **4/9 lecciones validadas técnicamente** y lección 5 en curso. No declarar cierre ni aprobación institucional.
- **Inicio, término, tiempo efectivo:** no informados.
- **Próximo paso:** sincronizar Git en rama local con precaución, ejecutar primero `python -m src.memoria_b22_booking_core`, luego `python -m src.memoria_b22_booking_core --agente`; revisar trazas, registrar resultados y avanzar a «Tu herramienta personalizada, ya construida e integrada».

## Cierre M2-U2.4-B22/L2 · 09/11/2026 — Memoria conversacional validada

- **Fuente de evidencia:** ejecución PowerShell aportada por el estudiante de `python -m src.memoria_b22_booking_core` y `python -m src.memoria_b22_booking_core --agente`, con entorno `(.venv)` activo, después de integrar `origin/main` en su rama local sin conflictos.
- **Pruebas sin API:** sesión A con 2 mensajes después del primer turno y 4 después del segundo; sesión B independiente con 0; normalización de bloques Gemini a texto y eliminación de las sesiones correctas. Salida final: `B22/L2: PRUEBAS DE MEMORIA SIN API CORRECTAS.`
- **Gemini, turno 1:** usuario consulta horarios simulados para corte el 11/11/2026; herramienta `consultar_disponibilidad_con_filtros` invocada con fecha `2026-11-11`, servicio `corte`, `incluir_duracion=False`; datos ficticios **10:00, 16:00 y 18:30**; historial con **2** mensajes.
- **Gemini, turno 2:** usuario dice solo «¿Y después de las 18:00? Incluye cuánto dura.»; `intermediate_steps` registró `consultar_disponibilidad_con_filtros` con **servicio=`corte` y fecha=`2026-11-11` recuperados del historial**, más `hora_desde=`18:00`` e `incluir_duracion=True`. Observación: horario ficticio **18:30**, duración **40 minutos**; historial con **4** mensajes. Salida final: `B22/L2: CONTEXTO ENTRE DOS INTERACCIONES VERIFICADO.`
- **Advertencias no bloqueantes:** `LangChainDeprecationWarning` por `RunnableWithMessageHistory` y `InMemoryChatMessageHistory`, señalando persistencia de LangGraph y futuro retiro. Son advertencias reales, no errores; planificar migración cuando corresponda.
- **Conclusión académica:** Bloque 22, lección 2 **completada técnicamente**. Avance U2.4 **5/9 lecciones** (Bloque 21 3/3 y Bloque 22 2/3); sin evidencia de entrega, aprobación ni calificación institucional.
- **Documento de evidencia:** [memoria conversacional B22/L2](u2_4_b22_memoria_conversacional.md), con extractos depurados de consola.
- **Tiempo de estudio:** inicio, término y tiempo efectivo no proporcionados; sin inferencias.
- **Git:** nuevo registro publicado en `main`. Rama local `feature/u2-3-b20-core-verificacion` tenía historial divergente de su remoto antes de esta sesión; evitar `push` o `stash pop` sin revisar.
- **Punto exacto de reanudación:** Bloque 22, lección 3, «Tu herramienta personalizada, ya construida e integrada»; reutilizar herramienta con `args_schema`, memoria por sesión y `intermediate_steps` como evidencia.

## Inicio M2-U2.4-B22/L3 · 09/11/2026 — Integración final y separación de clientes

- **Lección oficial:** «Tu herramienta personalizada, ya construida e integrada» — cierre del Bloque 22.
- **Fuente Skillnest:** integración de tres capas (herramienta Pydantic con `args_schema`; `AgentExecutor` con `chat_history` y `agent_scratchpad`; `RunnableWithMessageHistory` por `session_id`). Checklist: argumentos documentados, orden del prompt, dos turnos vinculados y dos sesiones independientes.
- **Aplicación complementaria:** [`src/integracion_b22_booking_core.py`](../src/integracion_b22_booking_core.py), que **reutiliza** el código ya probado de [herramienta B22/L1](../src/herramienta_b22_booking_core.py) y [agente/memoria B22/L2](../src/memoria_b22_booking_core.py), sin duplicar modelos y herramientas. Datos ficticios; ninguna reserva real.
- **Pruebas preparadas sin API:** esquema y validación, dos turnos en A (4 mensajes), uno en B (2 mensajes), ausencia cruzada de contenido textual y limpieza de ambos historiales.
- **Pruebas preparadas con Gemini:** dos turnos relacionados en A + primer turno independiente en B, con comprobación de `intermediate_steps` y aislamiento de las sesiones.
- **Documentación y checklist:** [integración final de B22](u2_4_b22_integracion_final.md).
- **Estado académico:** Bloque 22 con **2/3 lecciones validadas técnicamente**; lección 3 preparada y pendiente de pruebas en Windows. U2.4 sigue **5/9 lecciones confirmadas**, no 6/9. Sin entrega ni aprobación institucional informadas.
- **Registro horario:** inicio, término y tiempo efectivo no informados.
- **Punto exacto siguiente:** en la rama local comprobar `git status --short`, integrar `origin/main` con precaución, ejecutar `python -m src.integracion_b22_booking_core`; si pasa, ejecutar `python -m src.integracion_b22_booking_core --agente`, registrar salidas y cerrar técnicamente Bloque 22. Después continuar con Bloque 23, límites de autonomía y supervisión.

## Cierre M2-U2.4-B22/L3 · 09/11/2026 — Agente integrado con sesiones independientes

- **Evidencia recibida:** el estudiante ejecutó desde PowerShell, con `(.venv)` activo y merge exitoso de `origin/main`: `python -m src.integracion_b22_booking_core` y `python -m src.integracion_b22_booking_core --agente`.
- **Prueba offline de integración:** validación de la herramienta `args_schema`; sesión A con 2 turnos y 4 mensajes; sesión B independiente con 1 turno y 2 mensajes; ausencia cruzada de contenido textual y limpieza de sesiones. Terminal: `B22/L3: INTEGRACIÓN SIN API VERIFICADA.`
- **Gemini / cliente A, primer turno:** consultó horarios simulados de corte para 11/11/2026; herramienta `consultar_disponibilidad_con_filtros` invocada con `servicio=corte`, `fecha=2026-11-11`, `incluir_duracion=False`; respuesta 10:00, 16:00 y 18:30, ficticios.
- **Gemini / cliente A, segundo turno:** dijo únicamente «¿Y después de las 18:00? Incluye cuánto dura.». Traza `intermediate_steps`: `consultar_disponibilidad_con_filtros` con `hora_desde=18:00`, `fecha=2026-11-11`, `servicio=corte`, `incluir_duracion=True`. Resultado ficticio **18:30**, duración **40 min**.
- **Gemini / cliente B, primera interacción:** ante la pregunta por servicio y fecha previos en **su** conversación, respondió que no se habían mencionado; **sin invocaciones de herramienta** y sin recuperar información del cliente A. Terminal final: `B22/L3: AGENTE INTEGRADO Y SESIONES AISLADAS VERIFICADOS.`
- **Advertencias:** `LangChainDeprecationWarning` de `RunnableWithMessageHistory` y `InMemoryChatMessageHistory`; no hubo errores de ejecución. Persistencia moderna y autenticación multiusuario siguen fuera del alcance de estos ejercicios.
- **Resultado académico:** **Bloque 22 cerrado técnicamente 3/3 lecciones**; avance U2.4 confirmado **6/9 lecciones** (Bloque 21 3/3, Bloque 22 3/3). No atribuir entrega, nota ni aprobación institucional de Skillnest.
- **Documentación:** [evidencia de integración final B22](u2_4_b22_integracion_final.md). Código funcional: [integracion_b22_booking_core.py](../src/integracion_b22_booking_core.py).
- **Git:** la rama local de estudio incorporó `origin/main` mediante merge sin conflicto antes de las pruebas. Esta nueva anotación se publicó en `main`; no hacer push/rebase sobre la rama local divergente sin revisar su estado y sus respaldos.
- **Horas de inicio, término, tiempo efectivo y pausas:** no informadas; no inferirlas.
- **Punto exacto de continuación:** Bloque 23, lección 1, «Límites de autonomía y supervisión humana del agente». Introducir decisiones de seguridad y aprobación para acciones con efectos reales (reservar, cancelar, modificar) sin exponer aún Booking Core productivo.

## Inicio M2-U2.4-B23/L1 · 09/11/2026 — Supervisión humana y riesgo

- **Material oficial:** «Límites de autonomía y supervisión humana del agente». Clasificación bajo/medio/alto, aprobación humana previa a operaciones riesgosas, límite de espera, rechazo por defecto y registro de decisiones. El curso aclara que `select.select()` sobre stdin no funciona en Windows.
- **Adaptación para Booking Core AI:** [`src/supervision_b23_booking_core.py`](../src/supervision_b23_booking_core.py) con consulta de reservas de prueba y cancelación ficticia `DEMO-###`, autorización inyectada por canal **independiente del LLM**, bitácora en memoria, prevención de aprobación repetida y esquema Pydantic sin un argumento `aprobado`.
- **Estrategia Windows:** teclado con `msvcrt` y reloj `time.monotonic()` para timeout; equivalente del curso con `select` solo para plataformas POSIX. Sin terminal, sin respuesta, ante error o rechazo, no se modifica ninguna reserva.
- **Tests preparados:** modo directo automatizado para aprobación/rechazo simulados (no humanos), timeout, ausencia de canal, esquema Pydantic y auditoría; modo `--interactivo` para autorización humana de una cancelación ficticia; modo `--agente` que permite a Gemini solicitar la herramienta, nunca aprobarla.
- **Documentación:** [guía y checklist B23/L1](u2_4_b23_autonomia_supervision.md).
- **Estado:** publicado en `main`; **no hay pruebas ejecutadas en Windows todavía**. Avance técnico U2.4 sigue **6/9 lecciones validadas** (B21 3/3, B22 3/3); B23/L1 implementada pero pendiente de ejecución. Entrega/calificación de Skillnest no confirmadas.
- **Horarios y tiempo efectivo:** no proporcionados; no inferir.
- **Continuación:** verificar Git local limpio, integrar `origin/main`, ejecutar `python -m src.supervision_b23_booking_core`, después probar rechazo y aprobación con `--interactivo`, y si interesa el agente, `--agente`. Revisar salida antes de cerrar la lección y avanzar a «Qué revela la traza de decisión de un agente».

## Cierre M2-U2.4-B23/L1 · 09/11/2026 — Supervisión humana con Gemini

- **Evidencia real:** PowerShell del estudiante con `python -m src.supervision_b23_booking_core`, `--interactivo --timeout 60` y tres ejecuciones de `--agente --timeout 60`, tras integrar `origin/main` sin conflictos.
- **Pruebas automáticas sin Gemini:** rechazo y prevención de reintento, denegación ante ausencia de canal o timeout, aceptación programada con doble de prueba, validación Pydantic de ID `DEMO-###` y auditoría. Terminal: `B23/L1: CONTROLES DE APROBACION SIMULADA VERIFICADOS.` El doble de prueba con `aprobado=True` **no es aprobación humana**.
- **Rechazo humano sin Gemini:** respuesta `n`; `DEMO-001` permaneció `confirmada` y se registró `aprobado=False`, `ejecutada=False`, `origen=consola_demo`.
- **Gemini + timeout:** invocó `cancelar_reserva_simulada` para `DEMO-001`; no hubo autorización antes de 60 segundos; `aprobado=False`, `decision=timeout`, `ejecutada=False` y estado `confirmada`.
- **Gemini + rechazo:** operador respondió `n`; `decision=rechazado`, `aprobado=False`, `ejecutada=False` y estado `confirmada`.
- **Gemini + aprobación:** operador respondió explícitamente `s`; `intermediate_steps` mostró `cancelar_reserva_simulada` con `reserva_id=DEMO-001` y `motivo=cambio de planes`. Auditoría `aprobado=True`, `decision=aprobado`, `origen=consola_demo`, `ejecutada=True`, `momento_utc=2026-11-09T21:27:15.881541+00:00`. Estado final ficticio `cancelada`; terminal: `B23/L1: SUPERVISION DEL AGENTE VERIFICADA.`
- **Conclusión:** **B23/L1 completada técnicamente** mediante pruebas de denegación por defecto, rechazo y autorización explícita, con auditoría. El aprobador es una consola didáctica, **sin autenticación ni efectos sobre Booking Core/Supabase**. No representa control de producción ni aprobación institucional.
- **Avance académico:** U2.4 **7/9 lecciones** (B21 3/3, B22 3/3, B23 1/3). No constan entrega, calificación o aprobación de Skillnest.
- **Documentación:** [B23/L1 supervisión](u2_4_b23_autonomia_supervision.md); código en [supervision_b23_booking_core.py](../src/supervision_b23_booking_core.py).
- **Inicio, término, pausas y tiempo efectivo:** no informados; no estimarlos a partir de marcas UTC de auditoría.
- **Próximo paso exacto:** estudiar la segunda lección de Bloque 23, «Qué revela la traza de decisión de un agente». Mantener diseño de herramientas de lectura y escritura separadas y aprobación independiente; no conectar producción.
- **Git:** documento actualizado en `main`; la rama local de estudio `feature/u2-3-b20-core-verificacion` requiere sincronización futura con precaución por antecedentes de divergencia respecto de su rama remota. Evitar `git stash pop` o `git push` automático.

## Inicio M2-U2.4-B23/L2 · 09/11/2026 — Persistencia y revisión de trazas

- **Lección fuente Skillnest:** «Qué revela la traza de decisión de un agente». Persistencia de `intermediate_steps` en JSONL con `timestamp`, `session_id`, `entrada`, acciones con herramienta/argumentos/observación y respuesta final. Registro UTF-8, pasos ausentes tolerados, detección de herramientas repetidas consecutivamente, alertas sobre acciones sensibles sin aprobación y revisión humana selectiva.
- **Aplicación Booking Core AI:** [`src/trazas_b23_booking_core.py`](../src/trazas_b23_booking_core.py). Crea `trazas_agente_b23.jsonl` y analiza repeticiones, operaciones de riesgo alto, ausencia de un registro de autorización vinculado por ID y decisiones incompatibles con una ejecución.
- **Ampliación técnica propia:** registro `aprobaciones` originado en el control externo de supervisión del Bloque 23/L1, separado de las acciones de Gemini; normalización de salida del modelo a texto sin firmas de proveedor. Un registro de ejemplo sin aprobación se genera intencionalmente como **sintético**, sin ejecutar cancelación.
- **Protección básica del ejercicio:** `.gitignore` actualizado con `trazas_agente*.jsonl` para evitar subir accidentalmente históricos locales. No es suficiente como seguridad para datos personales reales.
- **Pruebas preparadas:** cinco escenarios sin consumir Gemini: consulta, rechazo auditable, repetición consecutiva, omisión de `intermediate_steps`, ausencia sintética de auditoría. Modo opcional `--agente` registra una interacción real con Gemini y denegación automática de cancelación por falta de supervisor.
- **Material de apoyo:** [B23/L2 trazas de decisión](u2_4_b23_trazas_decision.md).
- **Estado:** publicada implementación y documentación en GitHub; pruebas del B23/L2 **pendientes de ejecución real**. Avance técnicamente validado sigue **7 de 9 lecciones** de U2.4. Bloque 21 3/3; Bloque 22 3/3; Bloque 23 1/3. No atribuir aprobación institucional.
- **Inicio/término/tiempo efectivo:** no proporcionados; no inferir.
- **Próxima acción exacta:** comprobar `git status --short` y sincronizar cambios desde `origin/main` con cautela; ejecutar `python -m src.trazas_b23_booking_core`, inspeccionar el archivo JSONL y, si interesa, ejecutar `python -m src.trazas_b23_booking_core --agente`. Revisar evidencias y luego abordar la lección Core: «Documenta los límites de autonomía de tu agente».

## Cierre M2-U2.4-B23/L2 · 09/11/2026 — Persistencia y auditoría de trazas

- **Fuente verificada:** consola PowerShell del estudiante, tras merge exitoso de `origin/main`. Se ejecutaron `python -m src.trazas_b23_booking_core`, `Get-Content -Encoding utf8 .\trazas_agente_b23.jsonl | Select-Object -Last 3` y `python -m src.trazas_b23_booking_core --agente`.
- **Primera prueba, sin Gemini:** se escribieron **5** registros JSONL; resumen `registros=5`, `repeticiones=1`, `alto_riesgo=2`, `sin_registro_aprobacion=1`, `inconsistencias=0`, `lineas_invalidas=0`. Terminal: `B23/L2: REGISTRO Y ANALISIS DE TRAZAS SIN API VERIFICADOS.`
- **Inspección de JSONL:** el estudiante mostró un registro de consulta repetida con diferentes reservas ficticias, otro sin `intermediate_steps` (`acciones=[]`) y uno sintético que señalaba auditoría ausente sin ejecutar cancelación.
- **Prueba con Gemini real:** el comando `--agente` agregó otros **5** casos de prueba y **1** traza de Gemini. El modelo invocó `cancelar_reserva_simulada` para `DEMO-001`; sin supervisor, `decision=sin_supervisor` y la cancelación fue **bloqueada**. Terminal: `B23/L2: TRAZA REAL DE GEMINI PERSISTIDA.`
- **Resumen final de las 11 líneas acumuladas:** `registros=11`, `repeticiones=2`, `alto_riesgo=5`, `sin_registro_aprobacion=2`, `inconsistencias=0`, `lineas_invalidas=0`. Las dos alertas de auditoría ausente son los casos **sintéticos intencionales**, no violaciones detectadas de autorización.
- **Hallazgos y límites:** JSONL en UTF-8 persiste trazas observables de herramientas, argumentos y observaciones, con aprobaciones externas cuando existen. El registro no revela razonamiento privado del LLM ni representa auditoría durable, protegida o vinculada a identidad real. Todo el experimento utiliza datos ficticios sin tocar Booking Core ni Supabase.
- **Estado:** **B23/L2 validada técnicamente**. Avance acumulado U2.4 **8/9 lecciones** (B21 3/3, B22 3/3, B23 2/3), sin evidencia de evaluación/entrega o calificación institucional.
- **Documentación:** [u2_4_b23_trazas_decision.md](u2_4_b23_trazas_decision.md); código [trazas_b23_booking_core.py](../src/trazas_b23_booking_core.py); archivo local `trazas_agente_b23.jsonl` excluido de Git.
- **Inicio, término, pausas y tiempo efectivo:** no informados; no inferir.
- **Punto exacto para continuar:** Bloque 23, última lección Core, **«Documenta los límites de autonomía de tu agente»**. Preparar la entrega únicamente al recibir y revisar la consigna específica de Skillnest.

## Preparación de entrega M2-U2.4-B23/Core · 09/11/2026 — Documento de límites de autonomía

- **Actividad oficial Skillnest:** «Documenta los límites de autonomía de tu agente [Core]» — última lección de U2.4. Consigna fuente revisada, junto con captura del formulario que permite adjuntar un enlace (GitHub/Drive).
- **Documento entregable creado en GitHub (rama `main`):** [Límites de autonomía de Booking Core AI](u2_4_b23_core_limites_autonomia_booking_core_ai.md). Repositorio verificado **público**; enlace directo: https://github.com/nicolasbellov/especializacion-ia-2026/blob/main/docs/u2_4_b23_core_limites_autonomia_booking_core_ai.md
- **Contenido conforme a las cuatro secciones solicitadas:** clasificación de todas las herramientas propias del laboratorio por nivel de riesgo (bajo, medio, alto); exigencia de aprobación humana y justificación; revisión de trazas con frecuencia y señales de alerta; plan operativo concreto y secuencial ante conducta inesperada.
- **Contraste contra código actual:** B21 consulta de servicios y disponibilidad; B22 consulta estructurada y memoria temporal por sesión; B23 consulta de reservas ficticias, cancelación supervisada (`DecisionSupervisor`, `esperar_aprobacion_con_timeout`, fail closed, registro en RAM) y `registrar_traza` / `revisar_trazas` en JSONL.
- **Evidencia verificada previamente y referenciada:** rechazo humano, timeout y aprobación humana `s` en consola durante las pruebas B23/L1; en B23/L2, **11 registros JSONL** acumulados, 2 repeticiones, 5 invocaciones de riesgo alto, 2 alertas de auditoría ausente fabricadas sintéticamente, 0 inconsistencias y 0 líneas inválidas. Gemini real intentó la cancelación, bloqueada por `sin_supervisor`.
- **Limitación reconocida:** los agentes de memoria, supervisión y trazabilidad son **componentes de laboratorio separados**, no un servicio productivo unificado; no hay conexión con Booking Core ni Supabase real. No afirmar que el registro JSONL contiene las decisiones `s` y `n` observadas en consola de otra prueba.
- **Verificación del documento:** archivo y sus cuatro secciones localizados mediante la conexión GitHub, con código y referencias verificables. No fue necesario crear herramientas nuevas ni modificar los scripts ya probados.
- **Avance:** U2.4 tiene **9/9 contenidos abordados y documento Core listo para enviar**. **8/9 lecciones anteriores validadas mediante ejecución**; la novena es un documento ya confeccionado y contrastado con la evidencia. **Envío del formulario y aprobación/calificación institucional aún NO confirmados.**
- **Inicio, término, pausas y tiempo efectivo:** no informados; no inferir.
- **Punto exacto para continuar:** copiar el enlace público del Markdown a la sección **«Enlace (Drive, etc.)»** de la tarea Core en Skillnest y pulsar «Enviar entrega» personalmente; registrar después el resultado o captura de confirmación. Al confirmar la entrega, pasar a **U2.5 / Bloque 24: «RAG por dentro»**.

## Confirmación de entrega U2.4/B23 Core · 09/11/2026 — Registrada en Skillnest

- **Evidencia institucional compartida:** captura de Skillnest LifeCycle desde la actividad «Bloque 23 - Documenta los límites de autonomía de tu agente [Core]». En pantalla consta el texto **«Entrega registrada»**, indica que la tarea fue **registrada exitosamente y está siendo revisada por el instructor**, y muestra **«Enviado el 09/11/2026»**.
- **Estado administrativo confirmado:** **entrega Core registrada en Skillnest el 09/11/2026; evaluación/calificación del instructor pendiente**. No confundir confirmación de recepción con aprobación o nota.
- **Artefacto enviado/preparado:** [documento Core «Límites de autonomía de Booking Core AI»](u2_4_b23_core_limites_autonomia_booking_core_ai.md), publicado en `main` de GitHub. El contenido exacto del enlace que quedó registrado dentro del formulario no es visible en esta captura; no afirmar comprobación independiente de ese campo.
- **Avance académico:** **Unidad 2.4: 9 de 9 lecciones abordadas y documentadas; ocho lecciones comprobadas mediante ejecución y última actividad Core confeccionada y entrega confirmada.** Bloques 21 (3/3), 22 (3/3) y 23 (3/3) completados a nivel de trabajo académico. **Calificación institucional aún no informada.**
- **Aprendizajes integrados:** herramientas de LangChain con `args_schema`/Pydantic, Gemini con `intermediate_steps`, memoria por `session_id`, control humano previo a cancelaciones ficticias, denegación por defecto, auditoría y trazas JSONL.
- **Tiempo de estudio / inicio / término:** no informados por el estudiante; sin estimaciones.
- **Pendientes:** consultar evaluación del instructor cuando aparezca y conservar retroalimentación/correcciones si son requeridas; no se han programado avisos automáticos.
- **Punto exacto para continuar:** Unidad 2.5, **Bloque 24 «RAG por dentro»**. Mantener el caso Booking Core AI como hilo conductor, sin acceso a datos de clientes reales ni servicios de producción sin autorización expresa.

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


## Sesión U2.5 / Bloque 24 / Lección 1 · 13/11/2026 — RAG para Booking Core AI

- **Fuente principal:** contenido oficial de Skillnest «RAG por dentro: chunking, embeddings y vector stores» facilitado por el estudiante; lección conceptual **sin entrega obligatoria**.
- **Objetivo del capstone que no cambia:** agente conectado a la agenda de la barbería mediante Booking Core (AES Barber piloto), no un chatbot documental independiente.
- **Conceptos estudiados:** diccionario hardcodeado versus similitud semántica, chunking, embeddings con `models/gemini-embedding-001`, Chroma local, indexación separada de consulta, limitaciones de calidad y costo.
- **Consola recibida:** `python -m pip install langchain langchain-google-genai python-dotenv` terminó con `Successfully installed`. Versiones observadas en esa ejecución: `langchain==1.5.0` y `langchain-google-genai==4.5.0`; `python-dotenv==1.2.4` ya estaba instalado. Las rutas mostradas apuntan a Python 3.12 global, **no acreditan instalación en el `.venv` del repositorio**.
- **Artefactos creados en rama `feature/u2-5-b24-rag-booking-core`:** `src/rag_b24_booking_core.py`, `data/rag_demo_booking_core.md`, `tests/test_rag_b24_booking_core.py`, `requirements-rag.txt`, `docs/u2_5_b24_rag_booking_core.md`, ajuste de `.gitignore`.
- **Alcance de seguridad:** el corpus y las consultas del laboratorio son ficticios; no consulta Booking Core, no accede a Supabase real y no crea, modifica o cancela reservas. RAG para FAQs; agenda viva mediante API autorizada a implementar en etapa posterior.
- **Pruebas automáticas verificadas en GitHub Actions:** [workflow #43526194476](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43526194476) aprobado: **11/11 pruebas B24** con Chroma real, vectores ficticios, persistencia y búsqueda; `pip check` e importaciones RAG aprobadas; además, el job de regresión histórica aprobó. **No es una llamada real a Gemini**. En el PC del estudiante siguen pendientes la instalación dentro de `.venv`, el embedding real de 3072 dimensiones y la prueba manual de indexación.
- **Instante de inicio, término, pausas y tiempo efectivo:** no informados; no inferir.
- **Avance:** la lectura de Lección 1 y el material oficial están disponibles; **no declarar lección técnicamente completada hasta revisar al menos la demostración y las pruebas**.
- **Punto exacto para continuar:** en Windows, revisar estado Git antes de cambiar de rama, activar `.venv`, instalar `requirements-rag.txt`, ejecutar tests offline, probar `--modo embedding` con `GEMINI_API_KEY` local y corroborar 3072 dimensiones. Luego Lección 2: comparación de chunking.

## Validación Windows U2.5/B24-L1 · 13/11/2026 — Embeddings Gemini y corrección Chroma

- **Evidencia de consola real del estudiante:** `.venv` activado en Windows; `requirements-rag.txt` instalado (incluidos `chromadb==1.5.9` y `langchain-chroma==1.1.0`); `pip check` informó **No broken requirements found**.
- **Primera llamada real de Gemini Embeddings:** `python -m src.rag_b24_booking_core --modo embedding` → **3072 dimensiones**; primeros cinco valores observados `[-0.001601775, 0.02089852, 0.01956536, -0.065919146, -0.0064969533]`. **Validación real exitosa**, no simulada.
- **Tests locales:** **10/11**; `test_chroma_local_real_sin_red_si_instalado` falló con `PermissionError: [WinError 32]` durante limpieza de `tempfile.TemporaryDirectory` por handle abierto de Chroma (`data_level0.bin`).
- **Diagnóstico técnico:** falla de liberación de archivos de índice bajo Windows, no de generación de embeddings ni de búsqueda. CI Linux anterior había mostrado 11/11.
- **Acción en GitHub:** corrección de la prueba para indexar en un proceso Python independiente, abrir y recuperar en otro y limpiar la carpeta únicamente después de que ambos procesos terminen. Permite medir persistencia entre procesos sin conexión a Gemini o Booking Core.
- **GitHub Actions de la corrección:** [ejecución #43527127870](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43527127870) aprobó ambos jobs; **11/11 pruebas RAG**, incluida persistencia entre procesos, y `pip check` sin conflictos. **Resultado Windows posterior a la corrección:** aún pendiente; no elevar 10/11 locales a 11/11 sin nueva consola.
- **Arquitectura y seguridad:** se mantiene corpus ficticio, agente sin conexión a reserva real y Booking Core sin modificaciones. Se requiere API autenticada para agenda viva.
- **Inicio/término/tiempo efectivo:** no informados; no estimar a partir de timestamps.
- **Próximo paso exacto:** verificar Git limpio, `git pull --ff-only` en `feature/u2-5-b24-rag-booking-core`, repetir los 11 tests y compartir salida; luego indexar corpus ficticio usando `--modo indexar` y consultar con `--modo buscar`, registrando las fuentes recuperadas.

## Validación Windows posterior al fix B24-WIN-001 · 13/11/2026

- **Fuente de evidencia:** salida PowerShell proporcionada por el estudiante desde `C:\\Users\\nbello\\dev\\especializacion-ia-2026` con `(.venv)` activo.
- **Sincronización:** `git status --short` sin cambios; `git pull --ff-only` correcto, `7474ec3..96b64d3`; actualizó la prueba y documentación sin conflictos.
- **Prueba:** `python -m unittest discover -s tests -p "test_rag_b24_booking_core.py" -v` terminó con **Ran 11 tests in 10.604s / OK**.
- **Incidente resuelto (en la ejecución observada):** `test_chroma_local_real_sin_red_si_instalado` pasó en Windows, con indexación y recuperación entre subprocesos y sin `PermissionError / WinError 32`.
- **Gemini real:** `python -m src.rag_b24_booking_core --modo embedding` produjo **3072 dimensiones**, con muestra `[-0.001601775, 0.02089852, 0.01956536, -0.065919146, -0.0064969533]`. Esta ejecución confirma conexión efectiva al proveedor para generar embeddings.
- **Alcance de validación:** las 11 pruebas son offline con embeddings ficticios cuando validan Chroma; la prueba de embedding fue real. **Todavía no se ha observado indexación del corpus de cinco documentos mediante Gemini ni una búsqueda semántica real contra ese índice**.
- **Próximo paso exacto:** mantener rama `feature/u2-5-b24-rag-booking-core`, sincronizar con `git pull --ff-only` si está limpio, ejecutar `python -m src.rag_b24_booking_core --modo indexar` y después `python -m src.rag_b24_booking_core --modo buscar --pregunta "¿Cómo puedo cambiar una cita?"`; registrar ambos resultados antes de dar por cerrado el laboratorio.
- **Objetivo integrador permanente:** agente conectado a agenda Booking Core (AES Barber piloto); ningún acceso, escritura o reserva real en este ejercicio.
- **Inicio/término de estudio y tiempo efectivo:** no informados; 10,604 s mide exclusivamente ejecución automatizada de pruebas.

## Cierre técnico U2.5/Bloque 24/Lección 1 · 13/11/2026 — Indexación y recuperación Gemini/Chroma

- **Evidencia:** salida PowerShell compartida por el estudiante con `(.venv)` activo en `C:\\Users\\nbello\\dev\\especializacion-ia-2026`.
- **Sincronización Git:** `git status --short` sin cambios; `git pull --ff-only` correcto, fast-forward `96b64d3..f70a9e8` en `feature/u2-5-b24-rag-booking-core`. Los cambios del pull se limitaron a dos documentos.
- **Indexación real:** `python -m src.rag_b24_booking_core --modo indexar` → **`Chunks indexados: 5`**. Se almacenaron embeddings generados mediante Gemini en Chroma persistente en `.local/chroma_b24` (directorio local ignorado por Git).
- **Consulta semántica real:** `python -m src.rag_b24_booking_core --modo buscar --pregunta "¿Cómo puedo cambiar una cita?"` → **3 fragmentos recuperados** (`k=3`, valor predeterminado). Orden observado:
  1. `rag_demo_booking_core.md / Cambios de una cita ficticia` — fragmento directamente pertinente: consultar disponibilidad actualizada en Booking Core antes de proponer alternativas, no afirmar modificación sin confirmación del backend.
  2. `rag_demo_booking_core.md / Cancelación de una cita ficticia` — información relacionada, pero no respuesta principal para cambiar cita.
  3. `rag_demo_booking_core.md / Preguntas frecuentes y horarios` — contexto sobre disponibilidad actual y API transaccional.
- **Interpretación:** se verificó que la primera posición corresponde a la sección más directamente relacionada con la pregunta del laboratorio. No se midieron aún métricas de precisión/exhaustividad (Bloque 27), scores de similitud ni calidad de respuesta final de un LLM; este script imprime documentos recuperados, **no genera todavía una respuesta final con citas**.
- **Seguridad y alcance:** todos los fragmentos del corpus son `FICTICIO_ACADEMICO`. No se conectó ni modificó Booking Core, Supabase, clientes o reservas reales. RAG se reserva para FAQs/documentos; disponibilidad y cambios de citas deben validarse por API autenticada del backend con controles multi-tenant.
- **Estado de aprendizaje:** **U2.5/B24/L1 completada técnicamente**: conceptos y flujo de indexación/recuperación validados, 11/11 tests Windows previamente aprobados, embedding real de 3072 dimensiones y persistencia Chroma demostrada. **La lección no exige entrega**; no equivale a nota institucional.
- **Avance verificable de U2.5:** **1 de 15 actividades/lecciones del temario identificadas**, primera lección del Bloque 24 completada; 2 restantes del Bloque 24 aún sin verificar.
- **Tiempo efectivo:** no informado. No confundir segundos de ejecución de tests con estudio efectivo.
- **Punto exacto de continuación:** Bloque 24, **segunda lección «Dos estrategias de chunking, comparadas en vivo»**, enlace del curso https://learning-pro.skillnest.com/mod/page/view.php?id=20452. Comparar estrategias sin alterar ni reindexar todavía el corpus actual hasta revisar material oficial y diseño de experimento.

## Inicio U2.5 / Bloque 24 / Lección 2 · 13/11/2026 — Comparativa chunking

- **Material oficial recibido:** «Dos estrategias de chunking, comparadas en vivo» de Skillnest, con texto de tres párrafos y ejemplos para `CharacterTextSplitter(separator="", chunk_size=110, chunk_overlap=0)` y `RecursiveCharacterTextSplitter(chunk_size=110, chunk_overlap=20)`.
- **Explicación del curso:** fijo produce 3 fragmentos (110/110/93) con división de `Los er/rores`; recursivo produce 3 (102/108/99) preservando cada párrafo. El overlap configurado no genera solapamiento en ese caso; no existe tamaño óptimo universal.
- **Implementación preparada:** `test_chunking.py` contiene script continuo oficial; `src/comparar_chunking_b24_booking_core.py` compara ambas estrategias en el corpus académico de cinco secciones manteniendo metadatos por fuente, sección y origen; `tests/test_chunking_b24_booking_core.py` contiene pruebas offline. Se actualizó CI para ejecutar tests B24/L1+L2 y se añadió `docs/u2_5_b24_chunking_comparativo.md`.
- **Seguridad y límites:** ejercicio en memoria, sin API, sin embeddings, sin reindexar el Chroma de L1 y sin tocar la agenda de Booking Core, AES Barber o Supabase.
- **CI verificado (Linux, sin API):** [workflow #43529545967](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43529545967) aprobó ambos jobs; en el job RAG **18/18 pruebas B24** (11 L1 + 7 L2), `pip check` correcto y scripts de comparación ejecutados. El ejemplo del curso reprodujo las longitudes **fijo 110/110/93** y **recursivo 102/108/99**.
- **Resultado Booking Core AI en CI:** sobre 5 secciones ficticias, fijo `chunk_size=110, overlap=0` → **20 chunks** (4 por sección); recursivo `chunk_size=110, overlap=20` → **25 chunks** (5 por sección). Fijo: tamaño 12–110; recursivo: 31–109. Hallazgo: el recursivo originó un chunk solo con el encabezado `## Servicios de la barbería ficticia`, de 36 caracteres; más chunks no prueba recuperación más precisa.
- **Pruebas en Windows:** **pendientes de ejecución/verificación local**; no marcar completada la lección con solo publicar código y aprobar CI.
- **Avance formal:** U2.5 **1/15 completada técnicamente**, L2 **en estudio / práctica preparada**; sin nota ni entrega nueva.
- **Tiempo efectivo / horas de inicio y término:** no informados; no inventar.
- **Punto exacto de continuidad:** en Windows sincronizar rama `feature/u2-5-b24-rag-booking-core`, verificar import de `langchain_text_splitters`, ejecutar `python test_chunking.py`, `python -m src.comparar_chunking_b24_booking_core` y `python -m unittest discover -s tests -p "test_chunking_b24_booking_core.py" -v`; contrastar longitudes y registrar resultados.

## Cierre técnico U2.5/Bloque 24/Lección 2 · 13/11/2026 — Comparativa reproducida en Windows

- **Origen de evidencia:** salida PowerShell compartida por el estudiante desde el entorno virtual `(.venv)` en Windows. La instalación de `langchain_text_splitters` se verificó con salida **OK**.
- **Git:** `git status --short` limpio; `git pull --ff-only` exitoso, fast-forward `f70a9e8..0c700ca` sobre `feature/u2-5-b24-rag-booking-core`. Se recibieron scripts, tests, documentos y configuración de CI sin conflictos.
- **Ejercicio oficial (`python test_chunking.py`):** fijo con tamaño 110, overlap 0 → **3 chunks, longitudes [110, 110, 93]**, partió `Los er/rores` y `El cos/to`. Recursivo con tamaño 110, overlap 20 → **3 chunks, [102, 108, 99]**, un párrafo y una idea por chunk, sin overlap visible en esta configuración. Resultados concordantes con el material de Skillnest.
- **Extensión Booking Core AI (`python -m src.comparar_chunking_b24_booking_core`):** corpus de **5 secciones ficticias**. Fijo → **20 chunks (4 por sección)**, longitudes observadas [110, 110, 109, 12, 110, 109, 110, 17, 110, 110, 109, 50, 110, 110, 109, 23, 110, 109, 110, 23]. Recursivo → **25 chunks (5 por sección)**, longitudes [36, 78, 76, 80, 68, 31, 80, 75, 79, 78, 35, 79, 75, 78, 109, 34, 78, 82, 81, 74, 38, 76, 77, 81, 77].
- **Hallazgo:** el fijo puede cortar palabras e ideas; el recursivo con 110 caracteres genera al menos un chunk con solo el título `## Servicios de la barbería ficticia` (36 caracteres). No se puede concluir aún cuál recupera mejor ni decidir `chunk_size` óptimo por la sola cantidad de fragmentos.
- **Pruebas locales específicas de L2:** `python -m unittest discover -s tests -p "test_chunking_b24_booking_core.py" -v` → **Ran 7 tests in 3.023s / OK**. `18/18` en CI anterior pertenece a la suma L1+L2 del job GitHub Actions, no a esta ejecución Windows.
- **Seguridad y alcance:** comparación 100 % local, sin Gemini/tokens, sin modificar el índice Chroma persistente ya existente, sin reservas reales ni acceso a Booking Core o Supabase.
- **Estado:** **U2.5/B24/L2 completada técnicamente**; avance **2/15 lecciones de U2.5**, Bloque 24 **2/3**. No se observó entrega ni calificación institucional.
- **Tiempo académico:** hora de inicio/término y tiempo efectivo no informados; 3,023 s corresponde solo a duración automática de pruebas.
- **Próximo punto exacto:** recibir y estudiar la consigna oficial de **Bloque 24/L3: «Indexa tu corpus y persiste los embeddings en un vector store [Actividad práctica]»**. Proponer chunking recursivo con ajuste de tamaño y tratamiento de encabezados, validar fragmentos y persistir un nuevo índice **separado** de `.local/chroma_b24`. No elegir como definitivo sin contrastar resultados y consigna.

## Preparación U2.5/B24-L3 · 13/11/2026 — Indexar corpus y persistir embeddings

- **Consigna oficial recibida:** «Indexa tu corpus y persiste los embeddings en un vector store [Actividad práctica]». Exige ≥5 documentos relacionados, chunking previo, GoogleGenerativeAIEmbeddings reales, Chroma persistente en disco, apertura desde un script diferente y exclusión del índice del repositorio.
- **Selección de corpus:** cinco documentos Markdown independientes, **creados específicamente para el caso académico Booking Core AI** (servicios, disponibilidad, reprogramación, cancelación y privacidad), todos con aviso `EJEMPLO FICTICIO`; no describen políticas comerciales vigentes de AES Barber ni usan datos reales.
- **Chunking elegido:** `RecursiveCharacterTextSplitter(chunk_size=550, chunk_overlap=80)`. Los títulos se unen con su contenido y permanecen también en metadatos para evitar encabezados aislados detectados en L2. Split por documento antes de Gemini; no se decidió la calidad de recuperación por conteos.
- **Archivos preparados:** `indexar_corpus.py`, `verificar_vectorstore_b24.py`, `data/corpus_b24_l3/01_servicios.md` a `05_privacidad.md`, `tests/test_indexacion_b24_booking_core.py`, `docs/u2_5_b24_l3_indexacion_booking_core.md` y exclusión `vectorstore/` en `.gitignore`.
- **Arquitectura:** nuevo `vectorstore/` con colección `booking_core_b24_l3`; el índice de L1 `.local/chroma_b24` permanece sin modificaciones. Se usa `Chroma.from_documents` únicamente para la primera indexación y un manifiesto con huella/IDs. El verificador abre `Chroma(..., embedding_function=None)` y compara metadatos/IDs sin volver a consultar Gemini.
- **Estado de pruebas CI:** [GitHub Actions #43530916089](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43530916089) aprobó ambos jobs, **26/26 pruebas B24**, incluida B24/L3 con Chroma persistido entre procesos y embeddings de prueba. **Todavía no hay evidencia de Gemini real ni persistencia Windows para esta actividad**. Los embeddings falsos se usan exclusivamente en tests offline.
- **Avance:** U2.5 **2/15 lecciones completadas técnicamente**; B24/L3 **en desarrollo**, no cerrada ni entregada a Skillnest.
- **Tiempo de estudio real, inicio y término:** no informados; sin inventar.
- **Continuación exacta:** recibir resultado CI y ejecutar en Windows `python -m unittest discover -s tests -p "test_indexacion_b24_booking_core.py" -v`, `python indexar_corpus.py`, `python verificar_vectorstore_b24.py` y una segunda `python indexar_corpus.py` para demostrar que se evita el re-embedding.

## Ejecución real B24/L3 + incidente de codificación Windows · 13/11/2026

- **Entorno:** Windows PowerShell, `(.venv)`, Python 3.12.8 y comprobación explícita «Entorno virtual activo»; `git status --short` limpio y `git pull --ff-only` correcto, `0c700ca..6b467b7`. No hubo cambios locales pendientes tras la actividad.
- **Criterio central cumplido con Gemini real:** `python indexar_corpus.py` → **«Estado: creado con embeddings», 5 documentos fuente, 10 chunks indexados** en `vectorstore/`. Se utilizó `RecursiveCharacterTextSplitter(550,80)` y `Chroma.from_documents`, no embeddings de prueba.
- **Persistencia verificada en otro proceso:** `python verificar_vectorstore_b24.py` → **«Persistencia confirmada: Chroma reabierto sin reindexación ni Gemini», 5 fuentes y 10 chunks**. Las fuentes mostradas coinciden con `01_servicios.md`, `02_disponibilidad.md`, `03_reprogramacion.md`, `04_cancelacion.md`, `05_privacidad.md`.
- **Idempotencia de la reutilización:** segunda ejecución de `python indexar_corpus.py` → **«Estado: existente; sin re-embedding»**, 5 documentos y 10 chunks, sin nuevos embeddings. El índice de L1 `.local/chroma_b24` permanece sin cambios según la salida de la implementación.
- **Higiene Git:** `git status --short` limpio; `git check-ignore -v vectorstore/chroma.sqlite3` → `.gitignore:31:vectorstore/`. Índice y secretos excluidos del repositorio público.
- **Incidente B24-WIN-002:** primera suite local de L3 **7/8**: `UnicodeDecodeError` al leer como UTF-8 stdout de subproceso Windows que emitió `0xf3` (posible `ó` CP1252). `subprocess.run` dejó `stdout=None`, provocando `TypeError` en `assertIn`. **Error del transporte de salida de la prueba, no de Gemini ni Chroma**, demostrado por la indexación y verificación reales satisfactorias inmediatamente después.
- **Corrección GitHub:** `tests/test_indexacion_b24_booking_core.py` usa `PYTHONIOENCODING=utf-8`, `PYTHONUTF8=1` y decodificación tolerante para los tres procesos hijos, con nueva prueba de regresión Unicode. No se modifica el índice ni el módulo funcional. **CI posterior al fix: [GitHub Actions #43531505453](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43531505453) aprobó ambos jobs; `pip check` correcto, 27/27 pruebas B24 (11+7+9) y test de acentos incluido.** Nueva suite **Windows aún pendiente**.
- **Estado académico:** **criterios funcionales oficiales de B24/L3 cumplidos técnicamente**, pendiente cierre del control de calidad local (esperamos **9/9 tests** tras nueva prueba) y entrega/nota institucional si correspondiera. Por rigor, U2.5 se mantiene **2/15 cerradas** hasta completar la suite corregida.
- **Tiempo efectivo, inicio/término:** sin datos aportados; `14.317s` solo mide ejecución automatizada de pruebas.
- **Continuación exacta:** con la rama limpia, `git pull --ff-only` y `python -m unittest discover -s tests -p "test_indexacion_b24_booking_core.py" -v`. **No volver a ejecutar `python indexar_corpus.py`**: los 10 chunks reales ya están persistidos y verificados.

## Cierre B24/L3 y del Bloque 24 completo — validación Windows 13/11/2026

- **Evidencia aportada:** consola PowerShell en `(.venv)`, tras `git status --short` limpio y `git pull --ff-only` fast-forward **`6b467b7..367d1e3`** en `feature/u2-5-b24-rag-booking-core`.
- **Regresión Windows B24-WIN-002 resuelta:** `python -m unittest discover -s tests -p "test_indexacion_b24_booking_core.py" -v` → **`Ran 9 tests in 13.680s / OK`**. Pasaron tanto `test_chroma_persistente_otro_proceso_no_reindexa` como `test_subproceso_utf8_con_acentos`; desaparecieron el `UnicodeDecodeError` y el `TypeError` de la primera ejecución.
- **Evidencia funcional previa, conservada:** `python indexar_corpus.py` generó **10 embeddings/chunks con Gemini real a partir de 5 documentos propios ficticios**; `verificar_vectorstore_b24.py` abrió otro proceso y comprobó la persistencia de los mismos 10 chunks; segunda ejecución → **`Estado: existente; sin re-embedding`**; `vectorstore/` permanece excluido de Git. No se repitieron las llamadas reales a Gemini para corregir los tests.
- **CI de referencia:** [GitHub Actions #43531505453](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43531505453) → **27/27 pruebas B24** (11 L1 + 7 L2 + 9 L3), ambos jobs correctos, incluidas pruebas offline de Chroma y UTF-8.
- **Estado académico cerrado técnicamente:** B24/L1, B24/L2 y B24/L3 **3/3**; unidad U2.5 **3/15 lecciones completadas técnicamente**. **No hay constancia de entrega ni nota institucional para B24/L3**. El PR académico **#26** permanece en borrador y sin merge.
- **Aprendizajes transferibles:** chunking recursivo según estructura, embeddings Gemini, indexación Chroma con metadatos e IDs, persistencia y recarga sin reindexar, control de secretos, casos límite de codificación Windows. El RAG sigue siendo documental, sin conexión ni modificación de la agenda de Booking Core/AES Barber.
- **Tiempo de estudio efectivo / horas de inicio y fin:** no informados; los **13.680 s** representan duración de ejecución automatizada, no tiempo de estudio.
- **Punto exacto para retomar:** **Unidad U2.5, Bloque 25, primera lección** (indexación de un corpus de ejemplo diferente y troubleshooting según avance presentado por el curso). Obtener el material oficial antes de desarrollar o dar por realizadas nuevas actividades. Preservar índice local `vectorstore/` ya validado.

## Inicio U2.5/B25/L1 · 13/11/2026 — Receta reutilizable de indexación

- **Material oficial recibido:** «Réplica guiada de indexación sobre corpus de ejemplo / Cómo indexar y persistir un corpus en un vector store». Es una síntesis técnica de B24 y anticipa B25/L2 «Guía de troubleshooting» y B25/L3 réplica práctica sobre corpus distinto.
- **Cinco pasos del curso:** reunir corpus; chunking por documento; embeddings Gemini reales `models/gemini-embedding-001`; persistir con `Chroma.from_documents`; recargar en otro proceso sin recalcular embeddings.
- **Ejemplo oficial:** 3 textos (reintentos TimeoutError, costo `totalTokenCount`, tests con mocks), `RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)`; salida esperada 3 chunks y `count()=3`.
- **Aprendizajes:** tamaño/overlap son trade-offs; IDs explícitos permiten altas/bajas incrementales; cambios de modelo y chunking requieren reembeddings coherentes; no confundir sumar documentos nuevos con actualizar una colección sin IDs. El snippet simple del curso no protege contra duplicaciones si se reejecuta en el mismo vectorstore.
- **Implementación preparada:** `src/receta_indexacion_b25.py` expone `preparar_chunks`, `indexar_corpus`, `cargar_vectorstore`, `verificar_indice` y CLI `--modo preparar|indexar|verificar`. Replicará el corpus oficial en un índice separado `.local/chroma_b25_receta/` (ignorado por Git), con IDs estables y guardas de reejecución. **No modifica** `vectorstore/` (10 chunks Gemini reales de B24/L3) ni `.local/chroma_b24/`.
- **Pruebas:** `tests/test_receta_b25.py` contiene 7 casos. [GitHub Actions #43532526769](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43532526769) aprobó ambos jobs: **27/27 B24 + 7/7 B25**, preparación offline con 3 chunks y persistencia Chroma entre procesos mediante embeddings ficticios. **Windows B25 y Gemini real de este ejemplo todavía por confirmar.**
- **Estado:** B24 3/3 completado técnicamente; B25/L1 en estudio/replicación preparada, **U2.5 se mantiene 3/15** hasta la evidencia local. No consta calificación ni entrega para esta lección.
- **Inicio/término y tiempo efectivo:** no proporcionados, no estimar.
- **Punto exacto:** sincronizar GitHub si está limpio, ejecutar `python -m src.receta_indexacion_b25 --modo preparar`, suite B25 offline, `--modo indexar` solo para el nuevo índice, `--modo verificar` en otro proceso, y segunda indexación para constatar reutilización; luego registrar resultados antes del cierre.

## Cierre técnico U2.5/B25/L1 · 13/11/2026 — Receta Gemini/Chroma reutilizable en Windows

- **Evidencia:** consola PowerShell compartida desde `(.venv)` en Windows. `git status --short` limpio; `git pull --ff-only` ejecutó fast-forward **`367d1e3..a44a963`** sobre la rama `feature/u2-5-b24-rag-booking-core`, sin conflictos. `git status --short` final sin cambios.
- **Preparación puramente local:** `python -m src.receta_indexacion_b25 --modo preparar` → **3 textos y 3 chunks de [78, 64, 77] caracteres**, sin llamar a Gemini ni escribir en disco.
- **Pruebas específicas Windows:** `python -m unittest discover -s tests -p "test_receta_b25.py" -v` → **7/7 casos `OK`, `Ran 7 tests in 28.677s`**. Incluyó Chroma persistente entre procesos con vectores ficticios, firma/IDs, corpus y validación de rutas aisladas. El tiempo de 28.677 s corresponde a tests, no al tiempo efectivo de estudio.
- **Indexación real Gemini:** `python -m src.receta_indexacion_b25 --modo indexar` → **«Estado: indexado con embeddings», 3 chunks** creados en el directorio **`.local/chroma_b25_receta/`**. Modelo del script: `models/gemini-embedding-001`.
- **Persistencia independiente:** `python -m src.receta_indexacion_b25 --modo verificar` → **«Índice recargado sin re-embedding: 3 chunks»** en otro proceso.
- **Idempotencia:** segunda llamada a `--modo indexar` → **«Estado: reutilizado sin re-embedding», 3 chunks**. No se requirió volver a calcular embeddings de los documentos del ejemplo.
- **Aislamiento:** la CLI indicó que `vectorstore/` (10 chunks Gemini de B24/L3) y `.local/chroma_b24/` **no fueron modificados** por estos comandos. El índice nuevo bajo `.local/` está ignorado por Git.
- **CI previa:** [GitHub Actions #43532526769](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43532526769), **27/27 B24 y 7/7 B25** con embeddings ficticios para tests offline; evidencia distinta de Gemini real en Windows.
- **Lección completada técnicamente:** **B25/L1 1/3**, avance **U2.5 4/15**. No se confirma calificación ni entrega institucional para B25/L1. El PR #26 se mantiene como borrador y sin merge a `main`.
- **Tiempo efectivo / inicio y término:** no informados; no inferirlos de la terminal ni del workflow.
- **Punto exacto de continuación:** **Bloque 25, Lección 2 «Guía de troubleshooting»**, contenido oficial aún no compartido. Revisar el material antes de crear nuevas pruebas o interpretar errores. Conservar ambos índices de B24 y el índice B25 actual; no reindexarlos innecesariamente.

## Estudio U2.5/B25/L2 · 13/11/2026 — Guía de troubleshooting de vector stores

- **Material oficial recibido:** «Réplica guiada de indexación sobre corpus de ejemplo / Guía de troubleshooting de vector stores». Lección de referencia tipo **«Ver»**; consolida errores por etapa: instalación SQLite/paquetes, API key ausente versus inválida, 429/cuotas, permisos/ruta de persistencia, inconsistencias de dimensión/modelo, resultados irrelevantes, y nombres/colecciones fantasma.
- **Configuración de referencia del curso:** ruta absoluta y **`collection_name` explícito**, idénticos en indexación y lectura. La colección nueva comienza con `count()=0`; que devuelva cero después de indexar exige revisar ruta y colección, además de la existencia del índice.
- **Reintentos oficiales:** `con_reintentos(operacion, max_intentos=4, espera_inicial=5)` reintenta exclusivamente síntomas `429`/`RESOURCE_EXHAUSTED`, con esperas 5/10/20 segundos y excepción propagada si falla el último intento; no reintenta `401`, clave inválida ni permisos.
- **Ampliación recomendada:** retry solo para operaciones **idempotentes**. Repetir `Chroma.from_documents` tras un fallo parcial puede duplicar fragmentos con IDs aleatorios; no conectar reintentos genéricos a los índices persistentes existentes sin controles de progreso/IDs/backup.
- **Herramienta de lectura local preparada:** `src/diagnosticar_chroma_b25.py`, opciones `--indice todos|b24_l1|b24_l3|b25_receta`, inspección de Python/SQLite/imports/variable de entorno sin revelar claves, rutas y `PRAGMA quick_check` con SQLite `mode=ro`. No importa Chroma, no instancia Gemini, no crea colecciones, no borra nada ni reindexa. El conteo de manifiesto se distingue del conteo real de Chroma.
- **Pruebas complementarias:** `tests/test_troubleshooting_b25.py`, **11 tests offline**, incluyen simulación 429 5/10/20 sin esperar, propagación, rechazo de errores no reintentables, nombres/rutas explícitas y control de lectura SQLite sin cambios. [GitHub Actions #43533641828](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43533641828) verificó **11/11 pruebas B25/L2 (`Ran 11 tests in 0.036s / OK`)**, **7/7 B25/L1** y **27/27 B24**, ambos jobs exitosos, dependencias presentes, CLI sin API ejecutada.
- **Incidentes propios integrados como anexo:** B24-WIN-001 `WinError 32` por conexiones a SQLite no liberadas y B24-WIN-002 `UnicodeDecodeError` UTF-8/CP1252 en pipes Windows, resueltos en sesiones previas. Diferenciados de material de Skillnest.
- **Artefacto permanente:** `docs/u2_5_b25_troubleshooting_vectorstores.md` con mapa de fallos oficial, diagnóstico contextualizado para Booking Core AI y procedimientos seguros sin sobrescribir los índices Gemini ya validados.
- **Estado y alcance:** **B25/L2 completada como lección de referencia** («Ver»), con estudio del material y guía versionada; **CI 11/11 complementaria en verde**. El contenido oficial no exige llamadas reales de Gemini ni ejecutar el diagnóstico en Windows, por lo que su validación local es **opcional**. **U2.5 5/15 lecciones estudiadas/completadas según requisitos; B25 2/3**. No se observó entrega ni calificación institucional.
- **Tiempo efectivo / horas de inicio y término:** no informados; no inferir de las marcas del repositorio.
- **Siguiente punto exacto:** pasar a B25/L3 «Indexación y persistencia de tu corpus» (consigna oficial detallada pendiente); opcionalmente ejecutar en Windows el diagnóstico read-only y la suite de 11 tests sin API para practicar troubleshooting. Preservar `vectorstore/`, `.local/chroma_b24/` y `.local/chroma_b25_receta/`.

## Validación complementaria B25/L2 · 13/11/2026 — Windows y diagnóstico de tres índices

- **Evidencia recibida:** consola PowerShell desde `(.venv)`, `git status --short` sin cambios antes del pull, `git pull --ff-only` fast-forward `a44a963..4e7647d` sobre `feature/u2-5-b24-rag-booking-core`. No hubo conflictos ni modificaciones manuales en los índices.
- **Suite específica de troubleshooting:** `python -m unittest discover -s tests -p "test_troubleshooting_b25.py" -v` → **11/11 PASS**, `Ran 11 tests in 0.932s / OK`. Incluye 429/backoff 5-10-20 simulado, propagación de errores, distinción 401/403, validación de manifiestos y protección contra lectura de secretos.
- **Herramienta de diagnóstico read-only ejecutada realmente en Windows:** `python -m src.diagnosticar_chroma_b25 --indice todos` → Python **3.12.8**, venv **True**, SQLite **3.45.3**; importaciones de `langchain-google-genai`, `langchain-text-splitters`, `langchain-chroma`, `chromadb` y `python-dotenv` todas **OK**.
- **Resultados de índices:** `b24_l1` (`.local/chroma_b24`): carpeta y `chroma.sqlite3` existentes, `PRAGMA quick_check=ok`, manifiesto no requerido. `b24_l3` (`vectorstore`): carpeta/SQLite existentes, `quick_check=ok`, manifiesto coincide con la colección declarada y contiene **10 IDs/chunks declarados**. `b25_receta` (`.local/chroma_b25_receta`): carpeta/SQLite existentes, `quick_check=ok`, manifiesto coincide y declara **3 IDs/chunks**. Esos conteos de manifiesto no reemplazan el `count()` real de Chroma, verificado en sesiones previas.
- **Clave Gemini:** `GEMINI_API_KEY presente en el proceso: False` **no es un fallo**; la herramienta no lee `.env` deliberadamente. Indexaciones Gemini reales ya habían funcionado. No imprimir ni registrar secretos.
- **Límites de la validación:** SQLite `quick_check=ok` muestra integridad interna, no relevancia semántica de retrieval ni compatibilidad del modelo de embeddings. La herramienta informó «Diagnóstico local completado. Sin API, sin cambios en los índices».
- **Estado:** **B25/L2 ya estaba cerrada como lección de consulta**; esta ejecución añade evidencia local opcional satisfactoria. **B25 2/3; U2.5 5/15**, sin afirmar evaluación institucional.
- **Tiempo efectivo e inicio/término:** no informados. `0.932s` es duración automática de pruebas, no tiempo real de estudio.
- **Continuación exacta:** recibir material oficial **B25/L3: «Indexación y persistencia de tu corpus»** antes de crear la siguiente réplica, manteniendo intactos los tres índices existentes.

## Inicio U2.5/B25/L3 · 13/11/2026 — Réplica de tienda ficticia en GitHub

- **Fuente:** lección oficial «Indexación y persistencia de tu corpus de ejemplo» (Bloque 25). La instrucción original señala explícitamente que **no se entrega ni se commitea**. **Excepción voluntaria del estudiante:** ante su solicitud «pero usa el github», se versionó solo **código/documentación/tests** para mantener el flujo académico centralizado en GitHub; nunca el índice real ni credenciales.
- **Corpus oficial:** cinco documentos de una tienda ficticia (cancelación, devoluciones, reembolso, liquidación y envío de devoluciones), longitudes esperadas **[106,103,99,85,97]**, **490 caracteres totales**, sin vacíos ni duplicados. Splitter recursivo **(150,20)**; un chunk por documento.
- **Código:** \`replica_ejemplo.py\` en la raíz del repositorio. CLI \`--modo preparar|indexar|verificar\`; usa Gemini \`models/gemini-embedding-001\` para la primera indexación, colección única \`tienda_ficticia_b25_replica\`, índice en \`.local/chroma_b25_tienda_ejemplo/\`. Protección adicional mediante hash/IDs/manifest, reindexación no duplicada y bloqueo de índices parciales.
- **Pruebas verificadas:** `tests/test_replica_ejemplo_b25.py`: **8/8 OK en [GitHub Actions #43536897395](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43536897395)**, incluida persistencia Chroma entre procesos con embeddings simulados exclusivamente para CI. Se mantuvieron **27/27 B24, 7/7 B25/L1 y 11/11 B25/L2**, y el preflight mostró **5 chunks, 490 caracteres**. La prueba local con Gemini real está **pendiente** hasta recibir consola Windows.
- **Aislamiento:** índice nuevo dentro de \`.local/\` (ignorado en Git); **no modificar** \`vectorstore/\` del Bloque 24, \`.local/chroma_b24/\` ni \`.local/chroma_b25_receta/\`.
- **Progreso académico:** B25/L3 **en preparación/ejecución**, B25 **2/3 cerradas**, U2.5 **5/15** hasta confirmar la indexación real con Gemini y la recarga de 5 chunks. No es una entrega a Skillnest ni se atribuye nota.
- **Horas de inicio, término y tiempo efectivo:** no comunicados.
- **Siguiente paso:** en Windows, con venv activo y rama limpia, \`git pull --ff-only\`, ejecutar \`python replica_ejemplo.py --modo preparar\`, suite \`test_replica_ejemplo_b25.py\`, indexar con \`--modo indexar\`, verificar y reindexar nuevamente comprobando reutilización. El siguiente contenido del curso corresponde al Bloque 26, todavía sin material detallado recibido.

## Cierre técnico U2.5/B25/L3 y Bloque 25 · 14/11/2026 (Chile)

- **Evidencia aportada:** consola de Windows PowerShell desde `(.venv)`, en `C:\Users\nbello\dev\especializacion-ia-2026`. El `git status --short` inicial y final estuvo **limpio**. `git pull --ff-only` sincronizó correctamente la rama `feature/u2-5-b24-rag-booking-core` mediante fast-forward **`4e7647d..96ec7e1`**.
- **Preflight oficial (sin red):** `python replica_ejemplo.py --modo preparar` → **5 chunks**, tamaños `[106, 103, 99, 85, 97]`, `chunks vacios: []`, `hay duplicados: False`, **490 caracteres** en los chunks y **490 en corpus original**; `PREFLIGHT OK`.
- **Pruebas Windows:** `python -m unittest discover -s tests -p "test_replica_ejemplo_b25.py" -v` → **8/8 OK**, `Ran 8 tests in 24.535s`. El test de Chroma con vectores simulados entre procesos pasó, junto con tests de integridad, huellas/IDs, rutas y claves. Duración de pruebas ≠ tiempo de estudio.
- **Gemini real:** `python replica_ejemplo.py --modo indexar` → **«Estado: indexado con Gemini real. Chunks: 5»**, en `.local/chroma_b25_tienda_ejemplo/`, modelo `models/gemini-embedding-001` definido por script. Esta ejecución **sí** usó embeddings reales, a diferencia de las pruebas CI.
- **Persistencia en proceso separado, sin Gemini:** `python replica_ejemplo.py --modo verificar` → **«Índice recargado sin Gemini, chunks: 5»**; contraste de conteo e IDs con manifiesto.
- **Idempotencia:** segunda ejecución de `python replica_ejemplo.py --modo indexar` → **«Estado: reutilizado sin re-embedding. Chunks: 5»**. No se volvieron a calcular embeddings y no se insertaron duplicados.
- **Aislamiento:** la carpeta de la réplica está bajo `.local/`, excluida por `.gitignore`. No se ejecutaron modificaciones de los índices B24/L1 `.local/chroma_b24/`, B24/L3 `vectorstore/` ni B25/L1 `.local/chroma_b25_receta/`. No se hizo commit del índice ni de `.env`.
- **CI previa:** [GitHub Actions #43536897395](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43536897395) → **8/8 pruebas B25/L3** offline y regresiones **27/27 B24, 7/7 B25/L1, 11/11 B25/L2**. Pruebas complementarias distintas de la validación Windows con Gemini real.
- **Cierre académico:** **Bloque 25 3/3 lecciones completadas**; U2.5 **6/15** (B24 3/3 + B25 3/3). La lección B25/L3 **no requiere entrega ni commit según Skillnest**; código y documentación versionados en GitHub **a petición del estudiante**, sin declarar evaluación/calificación institucional. El PR **#26 permanece en borrador y sin merge**.
- **Tiempo de estudio efectivo e inicio/término:** no informados; no estimar a partir de `24.535s` ni de la hora de la carga.
- **Punto exacto de continuación:** **Bloque 26 / Lección 1 «Buscar por significado, no por palabra»**, según el curso; recibir el material oficial antes de implementar recuperación semántica y prompts. Conservar los cuatro índices académicos sin reindexarlos innecesariamente.

## Inicio U2.5/B26/L1 · 14/11/2026 — Recuperación semántica y Retriever

- **Material oficial recibido:** «Buscar por significado, no por palabra: recuperación semántica» (Bloque 26, primera lección, requisito «Ver»). Tras terminar la indexación/persistencia de B24 y B25, se estudia el uso de `similarity_search` (documentos y metadatos), `similarity_search_with_score` (distancia, **menor = más próximo**) y `as_retriever(search_kwargs={"k":2}).invoke(...)` (interfaz encadenable). La siguiente lección anunciada es **B26/L2 «Por qué la respuesta debe citar su fuente»**.
- **Ejemplo semántico oficial:** «¿qué pasa si mi conexión tarda demasiado?» debe relacionarse con «El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente», aun cuando las palabras no coincidan. **El orden en embeddings reales es una hipótesis por validar, no un hecho ya observado**.
- **Ejemplo sin red del curso:** 5 textos (TimeoutError, ValueError, costo `totalTokenCount`, herramientas de agente U2.4, tests con mocks), fuente `doc0.md` a `doc4.md`; `DeterministicFakeEmbedding(size=16)` genera vectores por hash sin comprensión semántica. La salida de scores de esta prueba **no** prueba relevancia; scores de Chroma son distancias, no porcentajes.
- **Código académico preparado:** `src/recuperacion_semantica_b26.py` (modos `fake|real|real-search|real-retriever`). El modo `fake` crea una colección efímera aislada y muestra las tres interfaces; el modo `real` **reabre** el índice Gemini **B25/L1** `.local/chroma_b25_receta/` con `receta_b25_ejemplo`, verifica manifiesto/3 IDs/chunks, y calcula **solo el embedding de la pregunta**. No inserta, modifica ni reindexa los documentos ni otros índices.
- **Pruebas complementarias:** `tests/test_recuperacion_semantica_b26.py` cubre 9 casos de la mecánica offline, distancias ordenadas, `k` mayor que colección, retriever y guardas de índice ausente. **[CI GitHub Actions #43553593077](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43553593077): ambos jobs PASS, B26/L1 9/9 OK (`Ran 9 tests in 2.403s`)**, más regresiones RAG **27/27 B24, 7/7 B25/L1, 11/11 B25/L2, 8/8 B25/L3**. **Gemini real y calidad semántica del nuevo retrieval aún pendientes de salida Windows**.
- **Incidente CI corregido (B26-CI-001):** al incluir nuevas pruebas en `unittest discover -s tests -p "test_*.py"`, el job base (solo `requirements.txt`) falló por `ModuleNotFoundError: langchain_chroma`; no fue fallo de retrieval ni de Gemini. La suite fue marcada `skipUnless` si no está instalado `langchain-chroma` y se ejecuta completa en el job RAG con `requirements-rag.txt`. La CI posterior pasó ambos jobs, sin añadir Chroma a dependencias del job base.
- **Apunte permanente:** `docs/u2_5_b26_l1_recuperacion_semantica.md`, diferenciando lo indicado por Skillnest, adaptación a índice ya existente, limitaciones del fake y controles de cuota.
- **Estado académico:** B24 **3/3** y B25 **3/3**, U2.5 **6/15** completadas. B26/L1 **en estudio y prueba**, sin calificación/entrega institucional confirmada. La lección oficial es de tipo «Ver»; los tests son material adicional.
- **Tiempo efectivo / hora inicio y término:** no informados, no estimar.
- **Punto exacto de continuación:** verificar CI; Windows: `git pull --ff-only`, `python -m src.recuperacion_semantica_b26 --modo fake`, 9 tests offline y `--modo real` (una solicitud Gemini para embebido de la consulta). Revisar **ranking, distancias y metadata.fuente** antes de dar por demostrada la recuperación semántica real. Mantener intactos los cuatro índices previos.

## Cierre técnico U2.5/B26/L1 · 14/11/2026 — Recuperación semántica real comprobada en Windows

- **Evidencia aportada:** consola PowerShell con `(.venv)` activo. `git status --short` **limpio al principio y al final**. `git pull --ff-only` realizó fast-forward **`96ec7e1..c914d0e`** de la rama académica, sin conflictos.
- **Demostración oficial sin API:** `python -m src.recuperacion_semantica_b26 --modo fake` → colección efímera de **5 chunks**, recupera `k=3` con `similarity_search`: **1.º doc2.md (costos), 2.º doc4.md (mocks), 3.º doc0.md (TimeoutError)**. `similarity_search_with_score` devolvió las mismas fuentes en ese orden, distancias **19.9059, 20.8040, 24.8037**. `as_retriever.invoke` (`k=2`) devolvió **doc2.md** y **doc4.md**. **Estos valores comparan vectores falsos basados en hash: no prueban relevancia semántica.** Coinciden con el resultado de referencia del curso.
- **Tests específicos Windows:** `python -m unittest discover -s tests -p "test_recuperacion_semantica_b26.py" -v` → **9/9 OK**, `Ran 9 tests in 5.082s`. Son pruebas offline; no se enviaron consultas Gemini durante la suite.
- **Consulta real:** `python -m src.recuperacion_semantica_b26 --modo real` sobre el índice B25/L1 **`.local/chroma_b25_receta/`**, colección **`receta_b25_ejemplo`**, modelo **`models/gemini-embedding-001`**, con **3 chunks originales**. Pregunta: «que pasa si la conexion tarda demasiado». Se calculó el embedding de la consulta (no del corpus).
- **Ranking/distancias reales observado:** **(1)** `ejemplo_skillnest_1`, «El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente», **0.5494**; **(2)** `ejemplo_skillnest_3`, «Las pruebas unitarias del cliente usan mocks y corren en menos de un segundo», **0.7277**; **(3)** `ejemplo_skillnest_2`, «El costo de cada llamada se calcula a partir de totalTokenCount», **0.7557**. El resultado semánticamente esperado **ocupó el primer lugar**, pese a no compartir palabras literales con la pregunta.
- **Interpretación:** los scores de Chroma son **distancias (menor es más cercano)**, no porcentajes. **No comparar magnitudes fake vs Gemini**: los embeddings y espacios son distintos. La prueba ofrece una confirmación **de relevancia para esta consulta específica**, no una métrica de precisión/recall generalizable.
- **Seguridad/alcance:** no hubo nueva indexación, no se añadieron documentos, no se alteraron índices; no se conectó la agenda transaccional de Booking Core. Metadatos de origen presentes en cada resultado. PR #26 en borrador, sin merge.
- **Estado académico actualizado:** **B26/L1 completada técnicamente**. U2.5 **7/15 lecciones**; B24 **3/3**, B25 **3/3**, B26 **1 lección completada**. No constan envío, aprobación institucional ni nota para esta lección (tipo «Ver»).
- **Tiempo efectivo / hora inicio/término:** no proporcionados. `5.082s` son segundos de pruebas, **no** duración del estudio.
- **Punto exacto de continuación:** **B26/L2 «Por qué la respuesta debe citar su fuente»**, según Skillnest. Recibir el contenido oficial antes de desarrollar extracción de fuentes, respuestas y citas; preservar los índices existentes y reutilizar la metadata `fuente` en el siguiente ejercicio.

## Estudio B26/L2 · 14/11/2026 — Por qué la respuesta debe citar su fuente

- **Material oficial:** lección «Ver» del Bloque 26: trazabilidad de evidencia frente a alucinaciones, herencia de metadatos al partir documentos, contexto numerado y mapa de citas por número de chunk, prompt con restricción a contexto y abstención si este no basta. No hay llamadas reales a Gemini/Chroma ni entrega exigida.
- **Corpus exacto del curso:** dos documentos de prueba (reintentos/errores de autenticación y costo por tokens), con fuentes `manual_cliente.md` y `manual_costos.md`. Splitter recursivo tamaño **90**, overlap **10**; salida de referencia **4 chunks**, dos por cada documento, y mapa **{1: manual_cliente.md, 2: manual_cliente.md, 3: manual_costos.md, 4: manual_costos.md}**.
- **Semántica de numeración:** los índices [1] a [4] corresponden **al orden local del contexto**, no a ID global de Chroma. En un contexto reordenado, cambian los números; las metadatas permiten recuperar la fuente original.
- **Prompts y citas inválidas:** la consigna exige «SOLO el contexto» y declarar insuficiencia en vez de inventar. Regex `\\[(\\d+)\\]` mapea referencias [n]; [99] debe devolver **«Cita invalida / no encontrada»** sin KeyError. La verificación de existencia de [1] NO prueba veracidad de la afirmación: solo demuestra trazabilidad.
- **Código creado en GitHub:** `citas_demo.py`, que replica el ejemplo oficial sin API, incluye `crear_chunks`, `formatear_contexto`, `construir_prompt` y `mapear_citas`; este último y la validación de longitudes de metadatos son **ampliaciones propias**, no exigencias adicionales del curso. Los archivos vectoriales y secretos permanecen intactos.
- **Pruebas verificadas en CI:** `tests/test_citas_demo_b26.py` cubre **11 casos offline**, incluido chunking/meta, mapa, numeración local, fuente ausente, prompt con abstención, respuestas [1] y [99], metadatos incompletos, CLI sin API. **[GitHub Actions #43555914394](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43555914394): ambos jobs PASS, 11/11 pruebas B26/L2 (`Ran 11 tests in 0.488s / OK`)**, además de regresiones **27/27 B24, 7/7 B25/L1, 11/11 B25/L2, 8/8 B25/L3, 9/9 B26/L1**. El script `python citas_demo.py` se ejecutó en CI y reprodujo el mapa y la marca de [99] inválida. Prueba Windows opcional aún no aportada.
- **Apunte versionado:** `docs/u2_5_b26_l2_citas_fuentes.md`.
- **Cierre de la lección de consulta («Ver»):** B26/L2 **estudiada, documentada y verificada offline en CI**. **U2.5 8/15 lecciones; Bloque 26 2/3**. Como Skillnest no pide una ejecución con Gemini ni entrega de este contenido, la comprobación Windows queda **opcional**. El script solo genera un prompt y mapea citas en una respuesta simulada; **no** afirma haber consultado un LLM ni demostrado que todas sus afirmaciones son verdaderas.
- **Horas de inicio, término y tiempo efectivo:** no informados, no inferir tiempos de CI.
- **Siguiente punto exacto:** B26/L3 «Desarrolla tu recuperación y tu prompt dinámico» sobre corpus propio, a la espera de su consigna oficial. Si se desea práctica local adicional, ejecutar en Windows `python citas_demo.py` y la suite de 11 pruebas; no se requiere clave, red ni índices.

## Evidencia complementaria Windows B26/L2 · 14/11/2026 (Chile) — 11/11 OK

- **Sincronización y limpieza Git:** `git status --short` inicialmente y al término **sin salida** (árbol limpio); `git pull --ff-only` fast-forward `c914d0e..3783f42` en `feature/u2-5-b24-rag-booking-core`. Ningún conflicto ni archivo nuevo sin seguimiento.
- **Ejecución real en equipo del estudiante, completamente offline:** `python citas_demo.py` produjo **4 chunks** de los dos documentos oficiales: dos con `{'fuente': 'manual_cliente.md'}` y dos con `{'fuente': 'manual_costos.md'}`. El contexto numerado presentó **[1]...[4]**; el mapa exacto fue `{1: 'manual_cliente.md', 2: 'manual_cliente.md', 3: 'manual_costos.md', 4: 'manual_costos.md'}`.
- **Prompt y trazabilidad:** el prompt contiene la pregunta `Que hace el cliente si hay un TimeoutError?`, la instrucción de responder **SOLO** con el contexto y de reconocer evidencia insuficiente. `La cita [1] corresponde a: manual_cliente.md`. En citas múltiples, [1], [2] y [3] se mapearon correctamente; `Cita [99]: Cita invalida / no encontrada` sin error.
- **Suite Windows:** `python -m unittest discover -s tests -p "test_citas_demo_b26.py" -v` → **11/11 PASS**, `Ran 11 tests in 1.651s / OK`. No hubo test omitido. Los segundos corresponden a ejecución automatizada, **no** al tiempo de estudio.
- **Aislamiento:** `Modo local: sin Gemini, Chroma ni solicitud de API`; los índices B24/B25 y el corpus de Booking Core no se tocaron. Es una respuesta de muestra, **no** una respuesta generada por un LLM ni validación factual automática.
- **Estado:** B26/L2 ya estaba marcada como lección «Ver» completada con CI **11/11**; esta salida agrega evidencia independiente de Windows. **U2.5 sigue 8/15; B26 sigue 2/3**, sin contar dos veces la misma lección ni afirmar evaluación institucional.
- **Horas de inicio/término y tiempo efectivo:** no comunicados.
- **Próximo punto exacto:** B26/L3 «Desarrolla tu recuperación y tu prompt dinámico»; esperar su consigna oficial para combinar recuperación Gemini con contexto numerado y citas sobre un corpus ficticio.

## Inicio U2.5/B26/L3 · 14/11/2026 (Chile) — Recuperación y prompt sobre corpus propio (entregable)

- **Material oficial recibido:** «Desarrolla tu recuperación y tu prompt dinámico [Actividad práctica]», Bloque 26/L3. Se exige indexación real previa, recuperación de k chunks, contexto numerado, citas fuente, prompt con abstención; validar **dos preguntas** y cambio de contexto, **una pregunta sin respuesta** que el LLM no debe inventar, y **una cita de respuesta REAL** contrastada contra el documento de origen; versionar el código y dependencias en GitHub. Siguiente Bloque 27, evaluación de precisión/exhaustividad.
- **Decisión técnica fundamental (diferencia con supuesto del curso):** Skillnest aconseja borrar vectorstore/ y reindexar porque su ejemplo B24 no tenía metadata ni IDs. **Nuestra implementación B24/L3 YA los tiene**: script indexar_corpus.py, colección booking_core_b24_l3, cinco archivos en data/corpus_b24_l3, diez chunks Gemini reales validados Windows, metadata fuente/titulo/origen/indice_chunk y IDs SHA-256 deterministas; manifiesto guardado. **NO borrar, no sobrescribir ni reindexar vectorstore/**: reutilizarlo por lectura y evitar cuota/duplicación; se documentó esta diferencia sin alterar archivos históricos.
- **Script de entrega:** recuperacion.py. Modos inspeccionar (comprobar índice, IDs, fuentes y origen FICTICIO_ACADEMICO **sin Gemini**), comparar (dos preguntas con **dos embeddings Gemini**, prompts enteros y comparación de contextos), recuperar (un prompt/citas, una consulta Gemini) y responder (consulta Gemini + llamada ChatGoogleGenerativeAI). Usa as_retriever(...).invoke, formatear_contexto de citas_demo.py y PROMPT_TEMPLATE oficial; construir_prompt(...) devuelve (prompt,citas) según consigna.
- **Trazabilidad y seguridad:** rechaza índice ausente, incompleto o con fuentes/IDs inválidos; rechaza documentos recuperados sin metadata.fuente. Usa rutas absolutas y colección explícita. No contiene operaciones from_documents/add_documents/delete ni accesos Booking Core o Supabase. Las citas numeradas son locales al contexto, no IDs del documento; comprobar cita existente **no prueba** la verdad de lo afirmado.
- **Pruebas verificadas:** tests/test_recuperacion_b26_l3.py, **12/12 pruebas offline PASS** en [GitHub Actions #43557252216](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43557252216) (`Ran 12 tests in 0.977s / OK`), con retriever simulado y corpus B24 original en disco (solo lectura). **Ambos jobs CI PASS** y regresiones correctas: 27/27 B24, 7/7 B25/L1, 11/11 B25/L2, 8/8 B25/L3, 9/9 B26/L1 y 11/11 B26/L2. **No equivale a Gemini real**, validación con proveedor pendiente de Windows.
- **Documentación:** docs/u2_5_b26_l3_recuperacion_prompt.md contiene objetivos oficiales, evidencia de que el índice ya tiene metadatos/IDs, comandos y criterios de aceptación de los tres escenarios. Dependencias ya versionadas en requirements.txt + requirements-rag.txt; no introducir nuevas dependencias.
- **Criterios de cierre por verificar:** inspeccionar el índice B24 (5 fuentes/10 chunks), 12/12 tests locales, comparar dos prompts recuperados y distintos, probar abstención del LLM ante pregunta sobre **precio real de AES Barber**, validar la cita de al menos una afirmación en respuesta real sobre reprogramación (mapa ↔ chunk ↔ fichero de origen). Evitar inventar outputs.
- **Estado académico:** B24 **3/3**, B25 **3/3**, B26/L1-L2 **2/3**, U2.5 **8/15**. B26/L3 **código preparado en rama/PR #26, evaluación real y entrega institucional pendientes**. El PR continúa **draft y sin merge**.
- **Horas de estudio efectivo/inicio/término:** no informados; no usar duración de tests para suplantarlas.
- **Punto de continuación:** revisar CI, pedir ejecución Windows de modos inspeccionar/comparar/responder, evaluar citas y abstención, después preparar entrega formal a Skillnest con URL del código. No pasar a B27 como finalizado antes de validar B26/L3.
