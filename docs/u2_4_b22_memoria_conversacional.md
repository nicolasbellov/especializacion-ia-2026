# U2.4 · Bloque 22 / Lección 2 — Memoria entre interacciones

**Programa:** Skillnest · Accenture · CChIA — Especialización IA 2026  
**Fecha:** 09/11/2026 (Chile)  
**Estado:** **validación técnica completada en Windows**: memoria sin API y dos turnos reales con Gemini verificados; aprobación institucional no informada.

## 1. Material del curso

La lección muestra por qué un AgentExecutor sin memoria no conserva el contexto entre llamadas independientes a invoke(). Se introduce:

- InMemoryChatMessageHistory para conservar mensajes en RAM.
- RunnableWithMessageHistory para envolver el ejecutor existente.
- MessagesPlaceholder("chat_history") **antes** del mensaje humano actual, y MessagesPlaceholder("agent_scratchpad") **después**, con funciones diferentes.
- Una clave session_id dentro de config["configurable"] para mantener conversaciones separadas.
- Crecimiento del historial y su efecto sobre tokens/costo.
- Limpieza de sesiones con historiales.pop(session_id, None).

La lección advierte sobre un LangChainDeprecationWarning de RunnableWithMessageHistory y menciona LangGraph como opción futura. En esta fase se mantiene la API del curso, **sin reemplazar AgentExecutor**.

## 2. Adaptación propuesta para Booking Core AI

**Archivo:** [src/memoria_b22_booking_core.py](../src/memoria_b22_booking_core.py)

Reutiliza el catálogo y los horarios simulados del Bloque 21 y la herramienta personalizada del Bloque 22. No accede a Supabase, Booking Core real ni efectúa reservas.

Principales componentes:

- obtener_historial(session_id): crea/recupera historial de esa sesión.
- cerrar_sesion(session_id): elimina la sesión de la RAM de esta ejecución.
- crear_agente_con_memoria(): construye un AgentExecutor con herramientas, prompt e historial.
- envolver_con_memoria(ejecutor): utiliza RunnableWithMessageHistory con input_messages_key="entrada", history_messages_key="chat_history" y output_messages_key="output".
- _normalizar_respuesta(): transforma a texto las respuestas estructuradas de Gemini. Esto es una **adaptación adicional** al curso, motivada por la respuesta en bloques con signature observada en las lecciones anteriores. El historial conserva texto, no metadatos del proveedor.

### Dos turnos del mismo cliente

1. «¿Qué horarios SIMULADOS hay para un corte de cabello el 11 de noviembre de 2026?»
2. «¿Y después de las 18:00? Incluye cuánto dura.»

El **criterio de validación** del segundo turno no es únicamente el texto final: inspeccionamos intermediate_steps para encontrar una llamada a consultar_disponibilidad_con_filtros con:

- fecha = 2026-11-11, recuperada del turno anterior;
- servicio = corte, recuperado del turno anterior;
- hora_desde = 18:00, aportado en el segundo turno;
- incluir_duracion = True.

Con la agenda ficticia, la observación esperada corresponde a 18:30 y 40 minutos. El script verifica que el historial tenga **2 mensajes después del primer turno y 4 después del segundo**.

### Alcance y riesgos

El historial pertenece solo al proceso en RAM, desaparece al reiniciarlo y no equivale al estado real de las reservas. Un session_id debe asociarse a una identidad autenticada en una implementación real, nunca aceptar identificadores arbitrarios de otros clientes. El historial puede contener datos personales y crecer sin límite; para producción necesitaríamos controles de retención, privacidad, límites de contexto y persistencia.

RunnableWithMessageHistory aparece como API obsoleta en versiones recientes; el ejemplo permanece deliberadamente alineado con el material Skillnest. LangGraph con checkpointers sería una vía futura, fuera del alcance de esta lección.

## 3. Ejecución en Windows

**Activación de .venv (procedimiento validado previamente por el estudiante):**

```powershell
cd C:\Users\nbello\dev\especializacion-ia-2026
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Antes de sincronizar, verificar la situación de la rama local:

```powershell
git status --short
git fetch origin
git merge --no-ff origin/main -m "merge: incorporar memoria B22"
```

No ejecutar merge con cambios sin revisar o conflictos previos. No ejecutar reset --hard ni stash pop automáticamente.

**Primera prueba, SIN usar Gemini:**

```powershell
python -m src.memoria_b22_booking_core
```

Validaciones previstas: primer turno 2 mensajes, segundo turno 4 mensajes, segunda sesión vacía, normalización de respuesta y cierre de sesión. Salida observada en la consola del estudiante:

```text
B22/L2: PRUEBAS DE MEMORIA SIN API CORRECTAS.
```

**Segunda prueba, CON Gemini real:**

```powershell
python -m src.memoria_b22_booking_core --agente
```

Este modo consume cuota de la API y ejecuta dos turnos del mismo cliente. Debe mostrar el paso intermedio donde la herramienta utiliza la fecha y el servicio del primer turno, y terminar con:

```text
B22/L2: CONTEXTO ENTRE DOS INTERACCIONES VERIFICADO.
```

Las selecciones y redacción del modelo pueden variar; si el criterio falla, el resultado de terminal servirá para diagnosticar el caso.

## 4. Evidencias y cierre

- [x] Código publicado, sin reemplazar el agente validado del Bloque 21.
- [x] Historial por session_id y limpieza de sesiones implementados.
- [x] Pruebas offline preparadas para historial 2/4 y aislamiento de sesiones.
- [x] Ejemplo de dos turnos reales preparado, con traza y verificación de argumentos.
- [x] Ejecución offline confirmada por el estudiante: 2/4 mensajes, sesiones independientes, limpieza y normalización.
- [x] Dos turnos reales de Gemini confirmados por el estudiante; argumentos recuperados verificados en `intermediate_steps`.
- [x] Cierre técnico de la lección: **B22/L2 validada**.
- [ ] Entrega o calificación institucional (no afirmada).

**Siguiente lección de Skillnest:** Bloque 22 — «Tu herramienta personalizada, ya construida e integrada».

## 5. Evidencia observada en PowerShell · 09/11/2026

El estudiante sincronizó su rama local con `origin/main` mediante un merge sin conflictos y ejecutó ambos modos de `src.memoria_b22_booking_core` desde su entorno `(.venv)`.

### 5.1. Pruebas sin API

```text
SESIÓN A / TURNO 1: 2 mensajes guardados (usuario + asistente)
SESIÓN A / TURNO 2: 4 mensajes guardados
SESIÓN B: historial independiente, 0 mensajes
NORMALIZACIÓN: texto sin metadatos del proveedor
LIMPIEZA: sesiones eliminadas

B22/L2: PRUEBAS DE MEMORIA SIN API CORRECTAS.
```

**Interpretación:** el historial guardó y recuperó dos pares usuario/asistente, se comprobó que otra sesión comienza vacía, se probaron la transformación de salida y la limpieza. Esta ejecución no utilizó Gemini.

### 5.2. Invocaciones reales del agente con Gemini

**Turno 1.** Pregunta: «¿Qué horarios SIMULADOS hay para un corte de cabello el 11 de noviembre de 2026?».

```text
Invoking: consultar_disponibilidad_con_filtros
{'fecha': '2026-11-11', 'incluir_duracion': False, 'servicio': 'corte'}
Observación: 10:00, 16:00, 18:30 (agenda simulada)
MENSAJES GUARDADOS: 2
```

**Turno 2.** Pregunta: «¿Y después de las 18:00? Incluye cuánto dura.». La pregunta **no especifica** ni la fecha ni el servicio.

```text
Invoking: consultar_disponibilidad_con_filtros
{'servicio': 'corte', 'incluir_duracion': True,
 'hora_desde': '18:00', 'fecha': '2026-11-11'}
Observación: horario simulado 18:30; duración estimada 40 minutos
MENSAJES GUARDADOS: 4

B22/L2: CONTEXTO ENTRE DOS INTERACCIONES VERIFICADO.
```

**Interpretación técnica:** `intermediate_steps` acredita que el agente recuperó los parámetros `servicio='corte'` y `fecha='2026-11-11'` del contexto conversacional previo. `hora_desde='18:00'` e `incluir_duracion=True` corresponden a la consulta actual. No se observó creación de reservas ni acceso a datos reales.

### 5.3. Advertencias de obsolescencia

El terminal mostró `LangChainDeprecationWarning` por dos símbolos:

- `RunnableWithMessageHistory`, con recomendación de usar persistencia integrada de LangGraph.
- `InMemoryChatMessageHistory`, indicado como obsoleto desde LangChain 1.6.4 y con retiro previsto para 2.0.0 según el mensaje observado.

**No bloquearon la ejecución** ni invalidan la actividad académica. Para un servicio productivo se debe evaluar una alternativa vigente y persistente, además de controles de identidad, retención y costos. No se recomienda ocultar los warnings sin considerar la migración.

**Nota de trazabilidad:** los extractos anteriores sintetizan la salida que el estudiante compartió en la conversación, omitiendo los bloques `extras.signature` que Gemini emitió en modo `verbose=True`; no son un archivo de transcripción bruta.

### 5.4. Estado de cierre

**Lección 2 del Bloque 22: validada técnicamente.** Avance confirmado de U2.4: **5/9 lecciones**. La entrega o aprobación de Skillnest **no consta**.
