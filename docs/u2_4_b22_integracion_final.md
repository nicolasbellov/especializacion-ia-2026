# U2.4 · Bloque 22 / Lección 3 — Agente completo e integrado

**Programa:** Especialización IA 2026 — Skillnest, Accenture y CChIA  
**Fecha:** 09/11/2026 (Chile)  
**Estado:** **validado técnicamente en Windows** mediante pruebas sin API y tres turnos reales de Gemini, con aislamiento de sesiones confirmado. Entrega/aprobación institucional no informada.

## Fuente principal: qué exige la lección

La lección «Tu herramienta personalizada, ya construida e integrada» reúne en un agente completo tres bloques:

1. **Herramienta personalizada:** `@tool(args_schema=...)` con descripciones de campos.
2. **Agente y ejecutor:** `create_tool_calling_agent` y `AgentExecutor` con `MessagesPlaceholder("chat_history")` antes de `("human", "{entrada}")`, y `MessagesPlaceholder("agent_scratchpad")` después.
3. **Memoria por sesión:** `RunnableWithMessageHistory`, `InMemoryChatMessageHistory`, `session_id` independiente por cliente.

Criterios de cierre del curso: argumentos estructurados, orden correcto del prompt, seguimiento entre dos turnos y aislamiento de historiales de clientes distintos.

El ejemplo original del curso utiliza envíos; aquí mantenemos el caso **Booking Core AI**.

## Aplicación a nuestro proyecto

**Archivo de pruebas de aceptación:** [`src/integracion_b22_booking_core.py`](../src/integracion_b22_booking_core.py).

No duplicamos todo el código del curso ni las herramientas: el proyecto ya tiene implementaciones probadas y separadas. La integración reutiliza:

| Capa | Código reutilizado | Responsabilidad |
|---|---|---|
| Herramienta | [`herramienta_b22_booking_core.py`](../src/herramienta_b22_booking_core.py) | `ArgumentosDisponibilidad` con Pydantic y `consultar_disponibilidad_con_filtros` |
| Agente | [`memoria_b22_booking_core.py`](../src/memoria_b22_booking_core.py) | Construcción de AgentExecutor con las herramientas y placeholders |
| Memoria | [`memoria_b22_booking_core.py`](../src/memoria_b22_booking_core.py) | Historiales por sesión, normalización de salida y limpieza |
| Criterios de aceptación | [`integracion_b22_booking_core.py`](../src/integracion_b22_booking_core.py) | Pruebas offline y con Gemini, más aislamiento entre dos clientes |

### Pruebas sin consumir API

Se comprueba que la herramienta tiene nombre propio, `args_schema`, cuatro descripciones de campos y funcionamiento correcto del filtro. Se rechaza `incluir_duracion="tal vez"` con `ValidationError`.

Con un ejecutor simulado se crean **dos sesiones diferentes**:

- **Cliente A:** «Quiero corte el 11 de noviembre de 2026» y «¿Y después de las 18:00?» → historial esperado de **4 mensajes**.
- **Cliente B:** «Quiero perfilado de barba el 12 de noviembre de 2026» → historial esperado de **2 mensajes**.

Se comprueba que la memoria de B no incluye el contenido textual del cliente A, y viceversa. Ambos historiales se limpian al terminar.

### Prueba con Gemini real

El modo `--agente` hace **tres llamadas conversacionales** (el número interno de llamadas al modelo puede ser mayor por las herramientas):

1. A solicita disponibilidad ficticia para `corte` el `2026-11-11`.
2. A pregunta «¿Y después de las 18:00? Incluye cuánto dura.». En `intermediate_steps` se debe comprobar el uso de `consultar_disponibilidad_con_filtros` con los cuatro argumentos (fecha, servicio, hora, duración).
3. B inicia una sesión nueva y pregunta qué servicio y fecha se mencionaron antes. No debe recibir el historial de A. Se verifica aislamiento del almacén y que las acciones de B no reutilicen simultáneamente `fecha=2026-11-11` y `servicio=corte`.

**Limitación:** estas pruebas demuestran separación de los objetos de historial en este laboratorio, pero no sustituyen pruebas de autorización, privacidad y aislamiento multiusuario del backend real.

## Instrucciones para Windows

Activar el entorno virtual:

```powershell
cd C:\Users\nbello\dev\especializacion-ia-2026
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Revisar el estado local, sincronizar y **solo si está limpio y no hay merges pendientes**, incorporar los commits de `main`:

```powershell
git status --short
git fetch origin
git merge --no-ff origin/main -m "merge: integrar cierre del Bloque 22"
```

El repositorio local tiene antecedentes de divergencia entre la rama de funcionalidad y su rama remota; **no usar** `git reset --hard`, `git stash pop` o `git push` sin revisar el estado.

**Primera prueba, sin utilizar Gemini:**

```powershell
python -m src.integracion_b22_booking_core
```

Salida final observada en PowerShell:

```text
BLOQUE 1 OK: herramienta con args_schema, nombre y validación.
BLOQUE 2 OK: conversación A de 2 turnos (4 mensajes).
BLOQUE 3 OK: conversación B independiente (2 mensajes).
LIMPIEZA OK: sesiones eliminadas.

B22/L3: INTEGRACIÓN SIN API VERIFICADA.
```

**Segunda prueba, con Gemini real:**

```powershell
python -m src.integracion_b22_booking_core --agente
```

Salida final observada con Gemini:

```text
B22/L3: AGENTE INTEGRADO Y SESIONES AISLADAS VERIFICADOS.
```

La traza de las herramientas y el historial observado son evidencias más fiables que una respuesta textual aparentemente correcta. Si falla alguna aserción, conservar el resultado de consola para diagnosticarlo; la conducta del modelo no es completamente determinista.

## Advertencias y próximos pasos

- Todos los servicios, precios y horarios son **simulados**. No se consulta ni modifica Supabase o Booking Core real.
- `RunnableWithMessageHistory` e `InMemoryChatMessageHistory` mostraron en B22/L2 avisos de deprecación: no se cambia de librería a mitad del ejercicio de Skillnest, pero una migración a persistencia moderna será necesaria para producción.
- Almacenamiento de contexto **volátil**: se pierde al reiniciar Python. Sesiones reales requerirán autenticación, separación por cliente, retención y control de tokens.
- La herramienta solo consulta: **no crea reservas** ni autoriza cambios de estado.
- Bloque 23 abordará los límites de autonomía y la supervisión humana.

### Lista de verificación académica

- [x] Herramienta con args_schema y campos documentados creada y validada previamente.
- [x] Prompt de agente con chat_history y agent_scratchpad en orden correcto implementado y probado en B22/L2.
- [x] Memoria entre turnos validada con Gemini real en B22/L2.
- [x] Pruebas nuevas de aislamiento entre dos sesiones preparadas.
- [x] Pruebas nuevas sin API ejecutadas y verificadas en el PC del estudiante.
- [x] Integración real de 2 sesiones con Gemini ejecutada y verificada (tres turnos conversacionales).
- [x] Cierre técnico del Bloque 22: **3/3 lecciones validadas**.
- [ ] Entrega y aprobación institucional, si corresponde (no confirmadas).

## Evidencia de ejecución real · 09/11/2026

Fuente: salida de PowerShell compartida por el estudiante después de integrar `origin/main` en su rama local sin conflictos. Se ejecutaron ambos comandos:

```powershell
python -m src.integracion_b22_booking_core
python -m src.integracion_b22_booking_core --agente
```

### Prueba A — Integración sin Gemini

```text
BLOQUE 1 OK: herramienta con args_schema, nombre y validación.
BLOQUE 2 OK: conversación A de 2 turnos (4 mensajes).
BLOQUE 3 OK: conversación B independiente (2 mensajes).
LIMPIEZA OK: sesiones eliminadas.

B22/L3: INTEGRACIÓN SIN API VERIFICADA.
```

Se confirmaron el nombre y esquema Pydantic, validación del booleano, historial de cuatro mensajes para A, historial de dos mensajes para B, ausencia cruzada de texto y limpieza de las sesiones.

### Prueba B — Agente integrado con Gemini real

**Cliente A / turno 1:** consultó corte de cabello el 11/11/2026. El agente invocó `consultar_disponibilidad_con_filtros` con `{'servicio':'corte', 'incluir_duracion':False, 'fecha':'2026-11-11'}` y obtuvo horarios ficticios 10:00, 16:00 y 18:30.

**Cliente A / turno 2:** preguntó «¿Y después de las 18:00? Incluye cuánto dura.», sin repetir servicio ni fecha. La traza de `intermediate_steps` confirmó:

```text
consultar_disponibilidad_con_filtros
{'hora_desde': '18:00', 'fecha': '2026-11-11',
 'servicio': 'corte', 'incluir_duracion': True}
→ AGENDA SIMULADA: Corte de cabello, fecha 2026-11-11,
  horarios: 18:30. Duración estimada: 40 minutos.
```

**Cliente B / primer turno:** preguntó qué servicio y fecha había mencionado anteriormente **en su propia conversación**. El agente respondió correctamente que no había proporcionado esos datos y **no invocó ninguna herramienta**. La separación de los historiales A y B se verificó en el código de prueba.

```text
B22/L3: AGENTE INTEGRADO Y SESIONES AISLADAS VERIFICADOS.
```

Se observaron avisos `LangChainDeprecationWarning` para `RunnableWithMessageHistory` e `InMemoryChatMessageHistory`, **no bloqueantes**. El uso de estas API corresponde a la lección del curso, pero no es una recomendación de producción.

**Resultado académico:** Bloque 22 cerrado **técnicamente** (3/3 lecciones); U2.4 alcanza **6/9 lecciones técnicamente validadas**. No consta entrega formal, nota ni aprobación institucional de Skillnest.

**Limitaciones:** el ensayo verifica memoria temporal e independencia de objetos por `session_id`, no autorización de usuarios ni aislamiento multi-tenant en un sistema real. Todos los horarios y servicios son ficticios. Los extractos omiten las firmas `extras.signature` del proveedor presentes en la salida de consola.
