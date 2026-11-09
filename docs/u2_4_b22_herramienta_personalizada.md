# U2.4 · B22/L1 — Herramienta personalizada con Pydantic

**Programa:** Especialización IA 2026 · Skillnest / Accenture / CChIA  
**Fecha:** 09/11/2026 (Chile)  
**Estado:** código publicado y pendiente de ejecución local. Sin llamadas reales a Gemini verificadas en esta lección.

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

**Salida final esperada (pendiente de validación real):** `B22/L1: TRES COMPROBACIONES DIRECTAS CORRECTAS.`

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
- [ ] Resultados de pruebas directas recibidos del entorno Windows.
- [ ] Traza opcional Gemini verificada, si se ejecuta.
- [ ] Evaluación o entrega institucional: no solicitada explícitamente en esta lección.

**Siguiente tema oficial:** Bloque 22, «Que tu agente recuerde: memoria entre interacciones».
