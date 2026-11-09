# U2.4 · B23 / Lección 2 — Qué revela la traza de decisión

**Especialización IA 2026 · Skillnest / Accenture / CChIA**  
**Fecha:** 09/11/2026, Chile  
**Estado:** **lección validada técnicamente** en Windows: generación y análisis JSONL, inspección de registros y traza real de Gemini persistida. No consta evaluación institucional.

## 1. Fuente del curso

El material introduce un registro durable de trazas del agente: timestamp UTC, session_id, entrada, acciones (herramienta, argumentos y observación) y respuesta_final. Se usa JSONL, agregando una línea de JSON por interacción, con codificación UTF-8.

Aprendizajes centrales:

- verbose=True muestra la traza en terminal; guardar el JSONL permite revisarla después.
- resultado.get("intermediate_steps", []) evita errores si no se registraron pasos.
- Una misma herramienta invocada consecutivamente es un candidato a revisión, **no** necesariamente un defecto.
- Toda acción de riesgo alto debe revisarse, especialmente si falta registro de aprobación.
- Una respuesta final que no coincide con las observaciones necesita inspección humana.
- Muestra periódica para operaciones comunes y revisión de todas las acciones de riesgo alto.

La traza registra comportamiento observable del agente, **no es acceso al razonamiento privado del modelo**. No reemplaza los controles preventivos.

## 2. Adaptación para Booking Core AI

**Código:** [src/trazas_b23_booking_core.py](../src/trazas_b23_booking_core.py)

El ejemplo de Skillnest usa trazas_agente.jsonl; nuestra implementación usa trazas_agente_b23.jsonl para separar este laboratorio. Incluye una columna adicional: aprobaciones, tomada del registro independiente del supervisor creado en B23/L1. Gemini no puede crear esa evidencia escribiendo argumentos de herramienta.

El revisor detecta:

- Herramientas de igual nombre usadas consecutivamente dentro de una interacción, aun con argumentos diferentes (señal para revisión manual).
- Todas las invocaciones de cancelar_reserva_simulada (riesgo alto).
- Acciones sensibles sin un registro de supervisión correlacionado por herramienta e identificador DEMO.
- Inconsistencia entre ejecutada=True y aprobado diferente de True.
- Líneas con JSON inválido, mostrando el número de línea.

La respuesta final de Gemini se normaliza a texto, omitiendo bloques y firmas de metadatos del proveedor.

### Cinco escenarios sin API

1. Consulta ficticia de DEMO-001; herramienta de solo lectura.
2. Cancelación ficticia denegada por un doble de prueba (no una persona). Se guarda el registro independiente de rechazo.
3. Dos consultas consecutivas de reservas ficticias distintas; se detecta repetición como posible señal, no un error demostrado.
4. Registro sin intermediate_steps; se conserva acciones=[] sin fallar.
5. Caso sintético SIN auditoría; se genera una alerta intencional, **sin cancelar ninguna reserva**.

Estos registros son muestras de laboratorio. Cada ejecución anexa cinco líneas más al archivo.

### Caso opcional con Gemini

El modo --agente pide a Gemini cancelar DEMO-001, pero crea las herramientas **sin un aprobador**. Por defecto se deniega la cancelación y se registra la acción real del agente con decision=sin_supervisor y ejecutada=False. Se conservará el log JSONL para inspección posterior.

No hay conexión a Supabase, Booking Core real, correos ni pasarelas de pago.

## 3. Ejecución en Windows PowerShell

Activar el entorno:

~~~powershell
cd C:\Users\nbello\dev\especializacion-ia-2026
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
~~~

Revisar estado local e integrar cambios de main solamente si Git está limpio:

~~~powershell
git status --short
git fetch origin
git merge --no-ff origin/main -m "merge: incorporar registro de trazas Bloque 23"
~~~

No ejecutar reset --hard, stash pop ni push sin revisar la rama local divergente.

**Prueba A — sin utilizar Gemini**

~~~powershell
python -m src.trazas_b23_booking_core
~~~

Salida final observada en PowerShell:

~~~text
B23/L2: REGISTRO Y ANALISIS DE TRAZAS SIN API VERIFICADOS.
~~~

Inspeccionar las últimas tres líneas del archivo:

~~~powershell
Get-Content -Encoding utf8 .\trazas_agente_b23.jsonl | Select-Object -Last 3
~~~

El archivo se añadió a .gitignore mediante el patrón trazas_agente*.jsonl para evitar que la traza local se publique accidentalmente.

**Prueba B — opcional con Gemini real**

~~~powershell
python -m src.trazas_b23_booking_core --agente
~~~

Debe finalizar, si Gemini selecciona la herramienta de cancelación simulada, con:

~~~text
GEMINI: herramienta registrada y cancelacion bloqueada sin supervisor.
B23/L2: TRAZA REAL DE GEMINI PERSISTIDA.
~~~

Este modo consume cuota de API. Ningún modo crea, modifica ni cancela reservas reales.

## 4. Limitaciones y diagnóstico

- Archivo inexistente: ejecutar la prueba A en la raíz del repositorio.
- JSONDecodeError: una línea corrupta se informa y se continúa con las demás.
- Repetición consecutiva puede ser legítima si los argumentos difieren.
- FALTA AUDITORIA del quinto registro es intencional, no una prueba de cancelación indebida.
- La traza no valida permisos, identidad del supervisor ni autenticidad de eventos del backend.
- En producción habría que minimizar datos personales, proteger el log, usar permisos, retención e integridad. .gitignore no es una medida de protección suficiente para información privada.

## 5. Checklist

- [x] Código de registro y revisión preparado.
- [x] Campo adicional de auditoría del supervisor independiente del LLM.
- [x] Formato JSONL UTF-8 y tolerancia a pasos ausentes.
- [x] Logs de demostración excluidos mediante .gitignore.
- [x] Pruebas sin API ejecutadas en Windows: cinco trazas iniciales, alertas esperadas y cero inconsistencias.
- [x] Prueba real con Gemini ejecutada y guardada, con cancelación ficticia bloqueada por ausencia de supervisor.
- [x] Cierre técnico de la lección confirmado: B23/L2 completada; U2.4 alcanza 8/9 lecciones.
- [ ] Entrega o nota institucional confirmada.

**Siguiente lección:** Bloque 23 — Documenta los límites de autonomía de tu agente [Core].

## 6. Evidencia observada del estudiante — 09/11/2026

### 6.1 Sincronización y validación sin API

El estudiante integró `origin/main` en su rama local mediante merge exitoso. Luego ejecutó:

```powershell
python -m src.trazas_b23_booking_core
```

Salida observada:

```text
REVISAR ALTO RIESGO: linea 2, sesion cliente_demo_denegado
REVISAR REPETICION: linea 3, sesion cliente_demo_repeticion
REVISAR ALTO RIESGO: linea 5, sesion cliente_demo_sin_auditoria
  FALTA AUDITORIA: no hay una decision correlativa.
RESUMEN DE REVISION:
{'registros': 5, 'repeticiones': 1, 'alto_riesgo': 2,
 'sin_registro_aprobacion': 1, 'inconsistencias': 0, 'lineas_invalidas': 0}
B23/L2: REGISTRO Y ANALISIS DE TRAZAS SIN API VERIFICADOS.
```

Archivo creado en el proyecto local: `trazas_agente_b23.jsonl`. El estudiante leyó las últimas tres líneas con `Get-Content -Encoding utf8`, comprobando:

- Una interacción con dos llamadas consecutivas a `consultar_reserva_simulada` para distintas reservas DEMO.
- Una interacción con `acciones=[]` sin errores.
- Una **traza sintética** de cancelación sin auditoría, explícitamente etiquetada `NO ejecutado`. La alerta correspondiente es **intencional**, no evidencia de un problema real.

### 6.2 Ejecución con Gemini y archivo acumulado

Posteriormente se ejecutó:

```powershell
python -m src.trazas_b23_booking_core --agente
```

El comando añadió otros **cinco registros sintéticos** antes de usar Gemini, por lo que el conteo pasó de **5 a 10**. Gemini invocó realmente `cancelar_reserva_simulada` con `reserva_id="DEMO-001"` y `motivo="Cambio de planes"`; al estar ausente un canal aprobador, el control externo devolvió `sin_supervisor` y la cancelación **no se ejecutó**.

```text
GEMINI: herramienta registrada y cancelacion bloqueada sin supervisor.
B23/L2: TRAZA REAL DE GEMINI PERSISTIDA.
```

El revisor, aplicado a las **11 líneas acumuladas**, produjo:

```text
{'registros': 11, 'repeticiones': 2, 'alto_riesgo': 5,
 'sin_registro_aprobacion': 2, 'inconsistencias': 0, 'lineas_invalidas': 0}
```

**Lectura:** las dos alertas de auditoría ausente pertenecen a los dos casos sintéticos fabricados deliberadamente en los lotes de prueba. La traza real de Gemini corresponde a una operación denegada y auditable. Las repeticiones marcadas son candidatos de revisión, no errores confirmados.

**Conclusión académica:** segunda lección del Bloque 23 validada técnicamente. Avance U2.4: **8/9 lecciones** (B21 3/3, B22 3/3, B23 2/3). Siguiente lección: **«Documenta los límites de autonomía de tu agente [Core]»**.

**Limitación:** no se ha verificado almacenamiento transaccional, identidad de supervisor, integridad criptográfica de auditoría o capacidad de reserva real. No hay evidencia de entrega o calificación institucional.
