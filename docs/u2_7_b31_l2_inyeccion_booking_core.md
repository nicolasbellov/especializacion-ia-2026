# U2.7 · Bloque 31 / Lección 2 — Prompt injection indirecta en Booking Core AI

**Fuente principal:** Skillnest, «Inyección de prompt en vivo: el ataque y su mitigación», contenido entregado por el estudiante el 26/11/2026.  
**Alcance:** laboratorio educativo, sin acceso a API de Booking Core, sin Gemini y sin escritura de reservas.  
**Estado:** **cierre técnico validado en Windows el 26/11/2026**: 9/9 unittest PASS, demostración completa PASS y código de salida 0. La entrega institucional en Skillnest no está confirmada.

## 1. Qué indica la lección

Una inyección indirecta aparece cuando un documento recuperado por RAG intenta convertirse en instrucción del asistente. La lección presenta tres mitigaciones *complementarias*:

1. **Separar roles reales:** SystemMessage y HumanMessage.
2. **Delimitar el contexto:** marcar el texto recuperado como datos no confiables.
3. **Filtrar patrones sospechosos:** expresiones regulares antes de ensamblar mensajes.

El texto del curso advierte que ninguna medida, ni siquiera las tres juntas, constituye una protección infalible. El detector por firmas puede omitir ataques y bloquear textos legítimos. Este laboratorio **no** ejecuta pruebas adversariales con un LLM real.

## 2. Adaptación propia al proyecto integrador

La tienda ficticia del ejemplo original se reemplaza por **Booking Core AI**, el agente académico que evolucionará hacia la agenda de la barbería **AES Barber**. Los dos documentos del ejemplo se construyen dentro del script y son *ficticios*: uno describe un proceso autorizado de reprogramación y otro simula una instrucción maliciosa insertada en documentación de agenda.

Se mantienen las tres capas de Skillnest, sin crear conexiones al producto real. El mensaje de sistema especifica que una respuesta RAG no acredita precios, disponibilidad ni confirmaciones de reservas. La autoridad transaccional sigue siendo el backend de Booking Core, con autenticación y control de tenant, cuando una integración futura sea aprobada.

Archivos:
- [src/mitigacion_inyeccion_b31_booking_core.py](../src/mitigacion_inyeccion_b31_booking_core.py): simulación y ensamblado de mensajes.
- [tests/test_mitigacion_inyeccion_b31.py](../tests/test_mitigacion_inyeccion_b31.py): 9 pruebas unitarias sin red.

## 3. Sincronización del repositorio (Windows / PowerShell)

La rama de U2.5 quedó por detrás de main, así que esta unidad utiliza **una rama independiente creada desde main**, para evitar cambios accidentales en el trabajo de U2.5.

Desde la carpeta académica local. **Antes de cambiar de rama, revisar el estado de Git:** el estudiante tenía `verificar_tuning.py` sin seguimiento; conservarlo y no borrarlo por error:

~~~powershell
cd C:\Users\nbello\dev\especializacion-ia-2026
git status --short
git fetch origin
git switch --track origin/feature/u2-7-b31-l2-mitigacion-booking-core
git pull --ff-only

.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_mitigacion_inyeccion_b31.py" -v
.\venv\Scripts\python.exe -m src.mitigacion_inyeccion_b31_booking_core

git status --short
~~~

Si esa rama **ya existe localmente**, utilizar el comando siguiente en lugar de switch --track:

~~~powershell
git switch feature/u2-7-b31-l2-mitigacion-booking-core
~~~

LangChain Core está incluido como dependencia de LangChain en el proyecto; no hace falta una API key para esta lección. Si falta, revisar el entorno virtual y las dependencias declaradas en requirements.txt antes de instalar paquetes sueltos.

## 4. Evidencia esperada y límites

- **Pruebas offline:** nueve casos, incluyendo documento legítimo, tres firmas del curso, inglés, roles, delimitadores, ausencia de documento inyectado, entrada vacía, tipo inválido y restricción académica.
- **Script demo:** dos documentos recibidos, uno descartado, tres coincidencias; mensajes system/human y salida final PASS.
- **Seguridad:** se imprime únicamente un resumen JSON, sin volcar los textos de los documentos al log. El script devuelve documentos descartados en memoria para fines didácticos; no deben registrarse completos en sistemas productivos.
- **No demostrado:** resistencia frente a ataques no previstos, seguridad multi-tenant, autorización de herramientas, consumo de tokens, ni funcionamiento con LLM real.
- **Siguiente actividad:** Bloque 31 / Lección 3, integración de logging estructurado, consumo e inyección de prompt en el flujo RAG de Booking Core AI.

## 5. Bitácora

- Fecha de material: 26/11/2026.
- Fuente oficial recibida y analizada: sí.
- Artefactos GitHub: preparados en rama de U2.7.
- Validación local Windows: **9/9 unittest PASS (0,015 s) el 26/11/2026** en Python 3.12. Demostración posterior PASS, `$LASTEXITCODE = 0`.
- Tiempo efectivo / entrega Skillnest: no informados.

## 6. Evidencia Windows recibida el 26/11/2026

Transcripción aportada por el estudiante, sin secretos publicados:

- **Git:** `git fetch origin` descargó la rama `feature/u2-7-b31-l2-mitigacion-booking-core`, `git switch --track` la activó correctamente y `git pull --ff-only` informó `Already up to date.`.
- **Archivo ajeno al commit:** `git status --short` mostró `?? verificar_tuning.py`; es material local sin seguimiento que debe conservarse.
- **Primer fallo:** `ModuleNotFoundError: No module named 'langchain_core'` tanto en unittest como en el script.
- **Resolución:** ejecutar `venv\\Scripts\\python.exe -m pip install -r requirements.txt`. Se instaló `langchain-core 1.8.5` como dependencia; `python -m pip check` informó `No broken requirements found.`.
- **Validación real:** `python -m unittest discover -s tests -p "test_mitigacion_inyeccion_b31.py" -v` → **Ran 9 tests in 0.015s / OK**.
- **Validación posterior confirmada por salida de PowerShell:** `python -m src.mitigacion_inyeccion_b31_booking_core` imprimió JSON con `documentos_recibidos=2`, `documentos_descartados=1`, `patrones_detectados=3`; `Roles: system, human`; `PASS: tres mitigaciones aplicadas al ejemplo ficticio.`; `$LASTEXITCODE` devolvió `0`. Un intento anterior falló por comandos accidentalmente concatenados (`...booking_coregit`) y no representa un defecto de implementación.
- **Regresión general:** no ejecutada ni documentada tras actualizar dependencias; solo queda confirmada la suite focalizada B31/L2.

**Cierre técnico B31/L2:** confirmado en Windows. `git status --short` mostró solo `?? verificar_tuning.py` (archivo local preexistente, conservar); la rama publicada contiene los artefactos de la lección. No se ejecutó una regresión general ni se acreditó entrega institucional. **Siguiente:** recibir la consigna B31/L3 e instrumentar logging y consumo de Booking Core AI respetando la separación del backend productivo.
