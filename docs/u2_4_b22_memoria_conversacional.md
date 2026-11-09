# U2.4 · Bloque 22 / Lección 2 — Memoria entre interacciones

**Programa:** Skillnest · Accenture · CChIA — Especialización IA 2026  
**Fecha:** 09/11/2026 (Chile)  
**Estado:** implementación publicada; pruebas en Windows y con Gemini **pendientes**.

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

El **criterio de validación** del segundo turno no es únicamente el texto final: inspectamos intermediate_steps para encontrar una llamada a consultar_disponibilidad_con_filtros con:

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

\`\`\`powershell
cd C:\Users\nbello\dev\especializacion-ia-2026
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
\`\`\`

Antes de sincronizar, verificar la situación de la rama local:

\`\`\`powershell
git status --short
git fetch origin
git merge --no-ff origin/main -m "merge: incorporar memoria B22"
\`\`\`

No ejecutar merge con cambios sin revisar o conflictos previos. No ejecutar reset --hard ni stash pop automáticamente.

**Primera prueba, SIN usar Gemini:**

\`\`\`powershell
python -m src.memoria_b22_booking_core
\`\`\`

Validaciones previstas: primer turno 2 mensajes, segundo turno 4 mensajes, segunda sesión vacía, normalización de respuesta y cierre de sesión. Salida esperada:

\`\`\`text
B22/L2: PRUEBAS DE MEMORIA SIN API CORRECTAS.
\`\`\`

**Segunda prueba, CON Gemini real:**

\`\`\`powershell
python -m src.memoria_b22_booking_core --agente
\`\`\`

Este modo consume cuota de la API y ejecuta dos turnos del mismo cliente. Debe mostrar el paso intermedio donde la herramienta utiliza la fecha y el servicio del primer turno, y terminar con:

\`\`\`text
B22/L2: CONTEXTO ENTRE DOS INTERACCIONES VERIFICADO.
\`\`\`

Las selecciones y redacción del modelo pueden variar; si el criterio falla, el resultado de terminal servirá para diagnosticar el caso.

## 4. Evidencias y cierre

- [x] Código publicado, sin reemplazar el agente validado del Bloque 21.
- [x] Historial por session_id y limpieza de sesiones implementados.
- [x] Pruebas offline preparadas para historial 2/4 y aislamiento de sesiones.
- [x] Ejemplo de dos turnos reales preparado, con traza y verificación de argumentos.
- [ ] Ejecución offline confirmada por el estudiante.
- [ ] Dos turnos reales de Gemini confirmados por el estudiante.
- [ ] Cierre técnico de la lección.
- [ ] Entrega o calificación institucional (no afirmada).

**Siguiente lección de Skillnest:** Bloque 22 — «Tu herramienta personalizada, ya construida e integrada».
