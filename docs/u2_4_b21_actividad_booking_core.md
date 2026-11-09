# U2.4 · Bloque 21 · Actividad práctica: Booking Core AI

**Curso:** Skillnest / Accenture / CChIA — Especialización IA 2026  
**Fecha de preparación:** 2026-11-09  
**Fuente principal:** «Implementa tu agente con al menos dos herramientas [Actividad práctica]» (Bloque 21).  
**Estado:** código publicado; **pendiente de ejecución y validación manual con Gemini en Windows**.

## Objetivo y alcance

Crear un agente propio con al menos dos herramientas de dominio, comprobando a partir de `intermediate_steps` cuál escogió ante dos preguntas distintas. Se toma **Booking Core AI**, asistente conversacional de reservas de barbería, como dominio de aplicación.

**Importante:** todos los servicios, precios, fechas y horarios del ejercicio son **ficticios**. Este ejercicio no accede a Booking Core, Supabase, ni a calendarios o reservas reales. No crea, cancela ni modifica reservas.

## Implementación

Archivo: [`src/agente_b21_booking_core.py`](../src/agente_b21_booking_core.py).

- `consultar_servicios(servicio: str = "") -> str`: responde preguntas sobre catálogo, precio y duración; el docstring indica cuándo se usa.
- `consultar_disponibilidad(fecha: str, servicio: str) -> str`: consulta horas de la agenda ficticia, valida fecha ISO y servicio; informa errores como observaciones de texto.
- `crear_ejecutor()`: `ChatGoogleGenerativeAI` + `create_tool_calling_agent` + `AgentExecutor`, con `MessagesPlaceholder("agent_scratchpad")`, `return_intermediate_steps=True` y `max_iterations=4`.
- `ejecutar_caso()`: realiza una invocación **real** de Gemini, imprime la respuesta y el listado de herramientas empleadas y verifica que solo se haya usado la esperada.
- `_texto_visible()`: extrae el texto de la respuesta sin imprimir firmas o metadatos cuando Gemini devuelve bloques estructurados.

Se reutiliza `GEMINI_MODEL` desde `.env`, con valor predeterminado `gemini-3.5-flash-lite`, previamente probado en el proyecto.

## Preparación y ejecución (PowerShell en Windows)

Desde cualquier terminal de PowerShell:

```powershell
cd C:\Users\nbello\dev\especializacion-ia-2026
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

git status --short
git fetch origin
git merge --no-ff origin/main -m "merge: incorporar actividad B21 Booking Core AI"
python -m src.agente_b21_booking_core
```

Si hay archivos modificados o conflictos, resolver el estado local **antes** de ejecutar el merge. Evitar `git reset --hard` y no aplicar `stash pop` automáticamente; puede contener archivos ya incorporados desde `main`.

## Casos de validación manual requeridos

| Caso | Pregunta | Herramienta esperada | Estado |
|---|---|---|---|
| 1. Catálogo | «En esta barbería de prueba, ¿cuánto cuesta un corte de cabello?» | `consultar_servicios` | Pendiente de ejecución real |
| 2. Agenda | «¿Qué horarios simulados hay para un corte el 11 de noviembre de 2026?» | `consultar_disponibilidad` | Pendiente de ejecución real |

**No basta la respuesta final:** en cada caso, la selección de herramienta se verifica programáticamente mediante los pares de acción/observación en `resultado["intermediate_steps"]`. El programa imprime `VALIDACIÓN MANUAL: OK` para cada uno cuando cumple, y un mensaje final de cierre solo cuando ambas pasan. Si Gemini selecciona otra herramienta, el programa mostrará la traza y lanzará `AssertionError`.

Los resultados exactos de las herramientas están definidos por los datos simulados, pero la redacción del modelo y sus decisiones pueden variar.

## Evidencia y estado académico

- [x] Código fuente con dos herramientas propias y docstrings diferenciados.
- [x] Agente con `AgentExecutor`, prompt y `agent_scratchpad`.
- [x] Verificación programática de la elección de herramienta.
- [x] Código publicado en el repositorio.
- [ ] Caso 1 ejecutado y validado mediante Gemini real.
- [ ] Caso 2 ejecutado y validado mediante Gemini real.
- [ ] Salida de terminal adjunta al registro académico.
- [ ] Confirmación de entrega / aprobación en Skillnest.

**Criterio de cierre técnico:** deben pasar ambos casos reales y no observarse errores de ejecución. La publicación del código **no** equivale a haber ejecutado las pruebas ni a una aprobación institucional.
