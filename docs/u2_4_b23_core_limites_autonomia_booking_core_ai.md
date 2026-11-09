# Límites de autonomía de Booking Core AI
## Unidad 2.4 · Bloque 23 — Actividad Core

**Programa:** Especialización en Inteligencia Artificial 2026 · Skillnest / Accenture / CChIA  
**Proyecto:** Booking Core AI — agente conversacional didáctico para una barbería  
**Fecha:** 09 de noviembre de 2026  
**Estado del documento:** versión de entrega sustentada en código y ejecuciones de laboratorio; **sin integración productiva**.

### Alcance y criterio de evidencia

Este documento establece los límites de autonomía del **prototipo académico Booking Core AI** construido durante U2.4. Separa lo implementado y probado de cualquier capacidad futura.

En el repositorio existen **componentes de laboratorio separados**: el agente con memoria del Bloque 22 utiliza herramientas de lectura; el Bloque 23 demuestra cancelación supervisada y trazas persistidas mediante otros scripts. **No hay un único agente desplegado que combine ya memoria, cancelación, auditoría y base de datos reales.**

Todas las agendas, precios, reservas `DEMO-###` y respuestas de las pruebas son **ficticios**. El código no lee ni modifica reservas de Booking Core ni de Supabase. Las evidencias de consola fueron verificadas en Windows; los archivos JSONL locales están ignorados por Git para no publicar historiales.

## 1. Herramientas y nivel de riesgo

Clasificación según la actividad: **bajo** (solo lectura o cálculo), **medio** (escritura reversible) y **alto** (escritura con consecuencias significativas, posiblemente irreversibles o económicas).

| Herramienta expuesta al agente | Ubicación | Nivel | Justificación y consecuencia |
|---|---|---|---|
| `consultar_servicios` | [agente_b21_booking_core.py](../src/agente_b21_booking_core.py) | **Bajo** | Consulta el catálogo, precios y duración **simulados**. No modifica datos ni requiere autorización humana para esta información ficticia. |
| `consultar_disponibilidad` | [agente_b21_booking_core.py](../src/agente_b21_booking_core.py) | **Bajo** | Consulta la agenda **ficticia** del Bloque 21 por fecha y servicio; no crea reservas. Es la herramienta inicial, sustituida funcionalmente en el agente más reciente por una versión con filtros. |
| `consultar_disponibilidad_con_filtros` | [herramienta_b22_booking_core.py](../src/herramienta_b22_booking_core.py) | **Bajo** | Consulta horarios **simulados** con `fecha`, `servicio`, `hora_desde` e `incluir_duracion`. Pydantic valida tipos y formato. Una elección incorrecta afecta la respuesta, no la agenda. |
| `consultar_reserva_simulada` | [supervision_b23_booking_core.py](../src/supervision_b23_booking_core.py) | **Bajo en el laboratorio** | Lee el estado de `DEMO-001` y `DEMO-002` en memoria. **En producción, leer reservas identificadas implicaría autorización de acceso y privacidad**, aunque no sea escritura. |
| `cancelar_reserva_simulada` | [supervision_b23_booking_core.py](../src/supervision_b23_booking_core.py) | **Alto por el tipo de operación que representa** | Cambia el estado `confirmada → cancelada` **solo en RAM**. Una cancelación real podría afectar cupos, clientes e ingresos; por ello se obliga a aprobar antes de ejecutar, incluso en el ejercicio. |

**No hay herramientas de riesgo medio implementadas** en el agente actual. No se debe inventar una operación de escritura reversible solo para completar esa categoría.

**Operaciones no implementadas y no autorizadas:** crear o modificar reservas reales, cancelar reservas reales, procesar pagos o reembolsos, enviar comunicaciones a clientes y escribir en Supabase. Requerirían diseño, autenticación, autorizaciones y pruebas independientes antes de exponerse al modelo.

El agente conversacional de [memoria_b22_booking_core.py](../src/memoria_b22_booking_core.py) actualmente registra como herramientas `consultar_servicios` y `consultar_disponibilidad_con_filtros`. La lectura y cancelación de reservas DEMO se incorporan **solo en los ejercicios separados del Bloque 23**.

## 2. Herramientas que requieren aprobación humana

### `cancelar_reserva_simulada` — aprobación obligatoria

**Motivo:** es una operación de escritura que representa una cancelación con posibles consecuencias reales. No basta con que Gemini entienda la intención de cancelar: una autorización independiente debe preceder al cambio de estado.

**Comportamiento efectivamente implementado** en [supervision_b23_booking_core.py](../src/supervision_b23_booking_core.py):

1. El modelo puede proponer la llamada con `reserva_id` y `motivo`, validados mediante `ArgumentosCancelacion` (`DEMO-###`). **El modelo no dispone de un argumento `aprobado`.**
2. La herramienta comprueba que la reserva ficticia exista, esté `confirmada` y no tenga ya una solicitud de aprobación presentada en el proceso actual.
3. El canal aprobador se **inyecta desde fuera del LLM** mediante `crear_herramientas(entorno, aprobador=...)`. La consola muestra la reserva y el motivo.
4. `esperar_aprobacion_con_timeout` recibe `s` o `n`; en Windows utiliza `msvcrt` y `time.monotonic()`, no `select()` sobre la entrada estándar. El tiempo por defecto es **60 segundos** en el script de laboratorio, configurable entre más de 0 y 300 segundos.
5. Si se responde `s`, y la reserva sigue confirmada, la herramienta la marca `cancelada` **solo en el diccionario ficticio**. Si se responde `n`, expira el plazo, falta terminal/supervisor o falla el canal, **no ejecuta** la cancelación (*fail closed*).
6. `registro_aprobaciones` guarda `herramienta`, `argumentos`, `aprobado`, `decision`, `origen`, `ejecutada` y `momento_utc`. El registro es **temporal**; desaparece al terminar Python.

**Evidencia real obtenida en Windows:** [supervisión y resultados B23/L1](u2_4_b23_autonomia_supervision.md). Con Gemini seleccionando `cancelar_reserva_simulada`:

| Resultado de la consola | Decisión del supervisor | ¿Cambió `DEMO-001`? |
|---|---|---|
| Rechazo explícito | `n` | **No**: permanece `confirmada` |
| Sin respuesta antes del plazo | `timeout` | **No**: permanece `confirmada` |
| Aprobación explícita | `s` | **Sí**, exclusivamente en memoria: queda `cancelada` |

También se validaron denegación sin supervisor, rechazo por defecto y aprobación con un **doble automatizado de prueba**. Ese doble no constituye una aprobación humana real. La evidencia de `s` sí proviene de una respuesta de consola durante una invocación de Gemini.

**No necesitan aprobación para este laboratorio:** `consultar_servicios`, `consultar_disponibilidad`, `consultar_disponibilidad_con_filtros` y `consultar_reserva_simulada`, porque solo consultan datos ficticios. En un servicio real, cualquier consulta de datos privados exigiría controles de identidad y autorización, aun cuando no requiera confirmación manual.

## 3. Revisión de trazas: qué revisar y con qué frecuencia

### Qué registro existe

El código [trazas_b23_booking_core.py](../src/trazas_b23_booking_core.py) implementa `registrar_traza` y `revisar_trazas` sobre el archivo local **`trazas_agente_b23.jsonl`**, en UTF-8 y formato *append* (una interacción por línea). Guarda:

- Marca temporal UTC, `session_id`, pregunta o entrada y respuesta final.
- Cada acción de `intermediate_steps`: herramienta, argumentos y observación.
- Campo complementario `aprobaciones`, suministrado por el registro de la herramienta supervisada, **no inferido del texto de Gemini**.

`verbose=True` muestra información en consola, mientras que JSONL la conserva tras terminar el proceso. **El guardado JSONL es explícito en el script de trazas B23/L2:** no significa que todos los ejecutores de los Bloques 21 y 22 ya registren automáticamente cada conversación.

### Patrones y frecuencia recomendada

Esta es una **política propuesta de revisión**, no un proceso automático de monitoreo que ya se encuentre programado:

| Frecuencia propuesta | Qué revisar | Respuesta de revisión |
|---|---|---|
| **100 % de las interacciones de riesgo alto**, idealmente en la misma jornada | Invocaciones a `cancelar_reserva_simulada`, argumentos, decisión externa, ejecución y concordancia entre ellos | Escalar inmediatamente cualquier ejecución sin aprobación verificable o ausencia real de auditoría |
| **100 % de las alertas de integridad**, en cuanto se detecten | JSONL corrupto, acción sensible sin registro correlativo, `ejecutada=True` con `aprobado` distinto de `True` | Restringir la herramienta y conservar evidencia para investigación |
| **Muestra semanal de hasta 10 trazas de bajo riesgo**, más cualquier caso reportado | Llamadas consecutivas a una misma herramienta, errores de parámetros y respuestas sin respaldo en las observaciones | Distinguir comportamiento legítimo de repetición innecesaria o posible invención |
| **Después de cambiar prompt, schema o herramientas** | Pruebas dirigidas de consulta, memoria, rechazo, aprobación, timeout y registro | Solo dar por conforme el cambio con resultados observables y documentados |

La herramienta de análisis **marca candidatos**: que una herramienta aparezca dos veces consecutivas no demuestra un defecto si estaba consultando dos reservas distintas. Asimismo, comparar una respuesta final con sus observaciones exige juicio humano; el script no demuestra automáticamente que todas las respuestas sean correctas.

### Evidencia del archivo de trazas efectivamente ejecutado

El participante ejecutó [las pruebas de B23/L2](u2_4_b23_trazas_decision.md) en Windows: primero generó cinco registros y después anexó otros cinco de laboratorio y **una traza real de Gemini**. El último resumen fue:

| Indicador medido | Resultado |
|---|---:|
| Registros JSONL acumulados | **11** |
| Señales de repetición | **2** |
| Invocaciones clasificadas de riesgo alto | **5** |
| Alertas de auditoría ausente | **2** |
| Inconsistencias aprobación / ejecución detectadas | **0** |
| Líneas JSON inválidas | **0** |

Las **dos alertas de auditoría ausente son casos sintéticos deliberados**, uno por cada lote de pruebas; **no** evidencian cancelaciones no autorizadas. En la llamada real de Gemini, la herramienta de cancelación respondió `sin_supervisor`, con `ejecutada=False`, y la reserva ficticia permaneció confirmada. Las pruebas de aprobación con `s` y rechazo con `n` del Bloque 23/L1 se observaron en consola y su auditoría en memoria: **no se debe afirmar que ambas están archivadas dentro de ese JSONL**.

El archivo local JSONL está excluido con `trazas_agente*.jsonl` en [.gitignore](../.gitignore). El repositorio conserva código y resúmenes de evidencia, **no el historial bruto de conversaciones**.

## 4. Qué hacer ante un comportamiento inesperado

**Plan operativo concreto, en orden.** En este laboratorio las acciones son ficticias; al aplicar el patrón a un agente real se requerirían controles operativos equivalentes, además de autenticación y monitoreo.

1. **Detener la acción peligrosa:** si el agente propone una escritura no solicitada, invoca cancelaciones reiteradamente o falta evidencia de autorización, retirar temporalmente `cancelar_reserva_simulada` del conjunto de herramientas del ejecutor (eliminarla de `herramientas` en el script del agente) y mantener solo herramientas de lectura. **No pedir al modelo que se autocontenga como único control.**
2. **Denegar por defecto y no reintentar automáticamente:** sin supervisor autenticado, ante timeout o canal defectuoso, conservar el estado de la reserva y evitar nuevas solicitudes automáticas. Verificar el guardado de la decisión de rechazo.
3. **Conservar evidencias:** preservar la entrada, el `session_id`, `intermediate_steps`, los argumentos, observaciones, la respuesta, la decisión humana y el estado final; protegerlas y evitar registrar datos personales innecesarios.
4. **Reconstruir el incidente:** comparar lo solicitado por el usuario, lo propuesto por Gemini, lo aprobado realmente y el efecto producido. Distinguir selección incorrecta de herramienta, error del esquema, dato de agenda desactualizado, respuesta inventada, repetición o defecto del control de autorización.
5. **Corregir la causa concreta:** ajustar `Field(description=...)`, validaciones Pydantic, docstring, prompt o lógica de la herramienta, según corresponda. Los controles de autorización y permisos deben imponerse **en el backend**, no depender del prompt.
6. **Reprobar antes de habilitar:** ejecutar nuevamente los casos de lectura, validación, rechazo `n`, timeout, aprobación `s`, prevención de reintentos, trazas y aislamiento de sesiones. En producción se añadirían pruebas de concurrencia, idempotencia, permisos y recuperación ante fallos.
7. **Rehabilitar de forma controlada:** documentar resultado, responsable y autorización del cambio; volver a habilitar la herramienta solo cuando la condición de fallo esté resuelta y las pruebas pasen. Si hubiera efectos reales, resolverlos mediante el procedimiento operativo correspondiente, sin inventar un rollback.

## 5. Chequeos cruzados documento ↔ código ↔ traza

La actividad Core exige **verificar lo implementado**, no solamente documentar una intención. Estos comandos están adaptados a **PowerShell**, el terminal utilizado en el proyecto.

**5.1. Verificar el control de aprobación en el código:**

~~~powershell
Select-String -Path .srcsupervision_b23_booking_core.py -Pattern 'esperar_aprobacion_con_timeout','sin_supervisor','if decision.aprobado','registro_aprobaciones.append'
~~~

Las coincidencias se interpretan revisando `crear_herramientas`: que la aprobación se invoque desde el canal externo y que `cancelar_reserva` solo cambie el estado cuando `decision.aprobado` sea verdadero.

**5.2. Comprobar que existen trazas locales:**

~~~powershell
Test-Path .	razas_agente_b23.jsonl
(Get-Content -Encoding utf8 .	razas_agente_b23.jsonl | Measure-Object -Line).Lines
~~~

**5.3. Revisar las interacciones que contienen herramientas de alto riesgo:**

~~~powershell
$trazas = Get-Content -Encoding utf8 .	razas_agente_b23.jsonl |
    ForEach-Object { $_ | ConvertFrom-Json }
$trazas | Where-Object {
    $_.acciones.herramienta -contains 'cancelar_reserva_simulada'
} | Select-Object timestamp,session_id,acciones,aprobaciones
~~~

Esos comandos leen el JSONL y **no ejecutan nuevas cancelaciones**. Si se vuelven a correr los ejercicios, el archivo suma líneas adicionales: por eso el total de 11 corresponde al corte de prueba anterior, no a un límite del sistema.

### Evidencias de implementación y ejecución

- [Herramientas de catálogo y disponibilidad iniciales](../src/agente_b21_booking_core.py).
- [Herramienta estructurada de disponibilidad](../src/herramienta_b22_booking_core.py).
- [Agente con memoria por sesión](../src/memoria_b22_booking_core.py).
- [Herramienta de cancelación ficticia con aprobación externa](../src/supervision_b23_booking_core.py).
- [Registro y revisión de trazas JSONL](../src/trazas_b23_booking_core.py).
- [Resultados reales de supervisión y aprobación humana](u2_4_b23_autonomia_supervision.md).
- [Resultados reales de persistencia y análisis de trazas](u2_4_b23_trazas_decision.md).

## 6. Limitaciones explícitas

Este prototipo académico **no** es un sistema productivo ni demuestra seguridad multiusuario:

- No autentica identidad de cliente ni supervisor, ni verifica permisos de un titular sobre una reserva.
- No tiene persistencia real de reservas ni de aprobaciones: la cancelación modifica un diccionario en memoria y el registro de decisiones de B23/L1 también vive en RAM.
- El historial conversacional de B22 es temporal, basado en `session_id` y `InMemoryChatMessageHistory`; separar historiales no prueba aislamiento de acceso entre usuarios autenticados.
- El JSONL de B23/L2 se guarda solo en el laboratorio que llama explícitamente a `registrar_traza`, y no reemplaza una bitácora duradera y resistente a alteraciones.
- Las verificaciones actuales de trazas relacionan registros por herramienta e identificador de reserva; para producción harían falta identificadores de solicitud únicos, aprobación vinculada a los **argumentos completos**, idempotencia, transacciones y manejo de concurrencia.
- `RunnableWithMessageHistory` e `InMemoryChatMessageHistory` emitieron advertencias de obsolescencia; una evolución hacia persistencia moderna puede considerarse más adelante.
- Consultas sobre reservas reales también exigen control de acceso y protección de datos personales. Se debe definir minimización, permisos, plazo de retención y mecanismos de eliminación del historial.

**Criterio de cierre:** este documento clasifica todas las herramientas presentes en los agentes didácticos Booking Core AI, justifica la aprobación humana de la operación de mayor riesgo, fija una política de revisión de trazas y entrega un procedimiento concreto para incidentes, respaldado por **código y ejecuciones verificadas**. La calificación o aprobación de Skillnest y cualquier despliegue productivo quedan fuera de lo afirmado.
