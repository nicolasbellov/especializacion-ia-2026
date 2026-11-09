# U2.4 · B22/L1 — Herramienta personalizada con Pydantic

**Programa:** Especialización IA 2026 · Skillnest / Accenture / CChIA  
**Fecha:** 09/11/2026 (Chile)  
**Estado:** **validación técnica completada** en Windows: comprobaciones directas exitosas y traza de invocación real a Gemini verificada. Entrega/evaluación institucional no informada.

## Alcance del material de Skillnest

La lección enseña a describir herramientas con múltiples argumentos mediante `BaseModel`, `Field(description=...)` y `@tool(args_schema=...)`; especificar explícitamente el nombre de la herramienta; probar `.invoke({...})`; y observar errores `ValidationError` cuando los argumentos tienen tipos incompatibles. No establece una actividad core ni una entrega formal en esta lección.

## Adaptación propuesta para Booking Core AI

Archivo: [`src/herramienta_b22_booking_core.py`](../src/herramienta_b22_booking_core.py).

La herramienta **`consultar_disponibilidad_con_filtros`** amplía la consulta de agenda ficticia del Bloque 21:

| Campo | Tipo | Regla y descripción |
|---|---|---|
| `fecha` | `str` | Fecha `AAAA-MM-DD`; se valida patrón y calendario |
| `servicio` | `Literal` | `corte`, `barba` o `corte_barba` |
| `hora_desde` | `str | None` | Hora mínima opcional `HH:MM` (24 horas) |
| `incluir_duracion` | `bool` | Valor por defecto `False`; en `True` añade duración |

- El nombre explícito definido en el decorador es **`consultar_disponibilidad_con_filtros`**, diferente del nombre de la función Python `consultar_disponibilidad_detallada`.
- El catálogo y la agenda se reutilizan desde el código didáctico B21 para evitar valores contradictorios.
- Los horarios, precios y servicios son **simulados**. No se realiza ninguna consulta a Supabase o al backend de Booking Core.
- La función maneja fechas inexistentes y ausencia de información mediante un mensaje de texto. La validación de tipos de `args_schema` ocurre **antes** de ejecutar la función y puede lanzar `ValidationError`; esta excepción es capturada por el laboratorio de prueba, no por el cuerpo de la herramienta.
- Existe una integración opcional con Gemini y `AgentExecutor` para observar el uso de la herramienta en `intermediate_steps`; no es requisito para entender la validación directa.

## Pasos para Windows / PowerShell

Activación del entorno virtual con el procedimiento ya validado por el estudiante:

```powershell
cd C:\Users\nbello\dev\especializacion-ia-2026
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

La dependencia `pydantic` ya forma parte de `requirements.txt`; el estudiante puede verificar su versión con `python -m pip show pydantic`. No se requiere instalarla por duplicado.

Antes de descargar cambios remotos, verificar los archivos locales, ya que se trabaja en una rama de característica con historiales previamente divergentes:

```powershell
git status --short
git fetch origin
git merge --no-ff origin/main -m "merge: incorporar herramienta personalizada B22"
```

**No ejecutar el merge si `git status --short` tiene cambios no revisados**, y no aplicar el stash anterior automáticamente.

Después de integrar el archivo, probar la herramienta **sin gastar llamadas a Gemini**:

```powershell
python -m src.herramienta_b22_booking_core
```

La prueba directa revisa:

1. Nombre expuesto por el decorador.
2. Consulta sin filtro y con valores por defecto.
3. Consulta con `hora_desde="18:00"` y `incluir_duracion=True`.
4. Rechazo mediante `ValidationError` de `incluir_duracion="tal vez"`.

**Salida final observada en Windows:** `B22/L1: TRES COMPROBACIONES DIRECTAS CORRECTAS.`

Para ejecutar **además** una consulta real a Gemini, de forma optativa:

```powershell
python -m src.herramienta_b22_booking_core --agente
```

Este último modo **consume cuota/API** y permite examinar la traza del uso de `consultar_disponibilidad_con_filtros`.

## Estado y próximos pasos

- [x] Código propuesto y publicado.
- [x] Esquema explícito de Pydantic con descripciones de los parámetros.
- [x] `@tool` con nombre personalizado.
- [x] Pruebas directas preparadas (sin API).
- [x] Agente opcional preparado con `return_intermediate_steps=True`.
- [x] Resultados de pruebas directas recibidos y revisados del entorno Windows.
- [x] Traza de Gemini real verificada: nombre y cuatro parámetros correctos.
- [ ] Evaluación o entrega institucional: no solicitada explícitamente en esta lección.

**Siguiente tema oficial:** Bloque 22, «Que tu agente recuerde: memoria entre interacciones».

## Evidencia de ejecución · 09/11/2026 (Chile)

El participante compartió la salida de PowerShell de las siguientes ejecuciones, con `(.venv)` activo:

```powershell
python -m src.herramienta_b22_booking_core
python -m src.herramienta_b22_booking_core --agente
```

**Validación directa de herramienta (sin API):**

```text
Nombre expuesto al modelo: consultar_disponibilidad_con_filtros
CASO BASE:
AGENDA SIMULADA: Corte de cabello, fecha 2026-11-11, horarios: 10:00, 16:00, 18:30.
CASO FILTRADO:
AGENDA SIMULADA: Corte de cabello, fecha 2026-11-11, horarios: 18:30. Duración estimada: 40 minutos.
VALIDACIÓN PYDANTIC: rechazo correcto del booleano inválido
Campo: ('incluir_duracion',)
B22/L1: TRES COMPROBACIONES DIRECTAS CORRECTAS.
```

**Validación adicional con Gemini real:** el agente invocó la herramienta `consultar_disponibilidad_con_filtros` con los parámetros `{'hora_desde': '18:00', 'servicio': 'corte', 'fecha': '2026-11-11', 'incluir_duracion': True}`. La observación indicó solo **18:30** y **40 minutos**; respondió que se trataba de datos ficticios. `intermediate_steps` registró la acción y observación, y la terminal finalizó con `AGENTE: herramienta personalizada invocada correctamente.`

**Resultado:** implementación y verificación técnica de la lección completadas, sin errores de ejecución observados. Se omiten intencionalmente los campos `signature` del proveedor presentes en el log original aportado por el estudiante. **No se ha verificado conexión con una agenda real, ni se ha declarado aprobación institucional de Skillnest.**
