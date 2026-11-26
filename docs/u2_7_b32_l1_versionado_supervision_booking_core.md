# U2.7 · Bloque 32 / Lección 1 — Versionado de prompts y supervisión humana

**Fuente primaria:** lección oficial Skillnest «Versionado de prompts y puntos de supervisión humana», proporcionada el **26/11/2026**.
**Proyecto integrador:** Booking Core AI (agente de agenda para AES Barber).
**Estado:** cierre técnico offline en Windows el **26/11/2026**: **16/16 pruebas PASS**, demo automática PASS y exit code 0. Prueba interactiva iniciada, decisión s/n aún no compartida. Entrega institucional Skillnest NO confirmada.

## 1. Qué enseña el curso

- Registrar cada prompt como artefacto versionable con **texto exacto, SHA-256 abreviado, autor, fecha y nota**. Complementar con el modelo y parámetros sobre los que se haya ensayado, sin inventar verificaciones.
- Usar difflib.unified_diff para identificar cambios entre versiones.
- Añadir puntos de supervisión humana con **LangGraph interrupt(...)** y reanudar solo mediante **Command(resume=...)**, identificando cada aprobación con thread_id.
- Consultar app.get_state(config) y snapshot.interrupts para inspeccionar la solicitud pendiente antes de reanudar.
- Diferenciar aprobación (True) y rechazo (False), conservando la versión anterior cuando se rechaza.
- InMemorySaver sirve para pruebas y **NO** conserva estados tras reiniciar procesos. Un entorno real necesita un checkpoint durable y autenticación/autorización del aprobador. El paquete SQLite es **opcional** en la lección.

## 2. Decisiones propias para Booking Core AI

Se mantiene el **repositorio académico**, sin tocar nicolasbellov/booking-core ni reservas reales.

Archivos:
- [src/versionado_supervision_b32.py](../src/versionado_supervision_b32.py): RegistroDePrompts, huella, diferencias, grafo LangGraph y doble demostración sin red.
- [prompts/booking_core_ai/sistema_v1.txt](../prompts/booking_core_ai/sistema_v1.txt): fotografía textual del prompt B31/L2 (se lee sin el salto final, conservando el texto exacto de la constante previa).
- [prompts/booking_core_ai/sistema_v2.txt](../prompts/booking_core_ai/sistema_v2.txt): versión **PROPUESTA**, añade reglas de autorización y confirmación para operaciones sensibles.
- [prompts/booking_core_ai/registro.json](../prompts/booking_core_ai/registro.json): metadatos: versiones, autor, fecha, motivo, modelo/parametrización null (no probados con LLM real).
- [tests/test_versionado_supervision_b32.py](../tests/test_versionado_supervision_b32.py): 16 pruebas offline para registro, huellas, diff, pausas, aprobación, rechazo, versión distinta, doble aprobación y separación por thread_id.

**La v2 NO está activa** en el pipeline logging_rag.py: el laboratorio B31/L3 conserva el prompt v1 importado desde src/mitigacion_inyeccion_b31_booking_core.py. Publicar archivos en Git no cambia el comportamiento del agente ni despliega prompts a Booking Core.

El nodo aplicar_simulacion solo modifica el **estado del grafo en memoria**; no guarda una nueva versión activa real, no contacta el backend y no realiza cancelaciones ni reprogramaciones. La opción --modo demo usa decisiones automáticas simuladas **para enseñar la API**; NO es aprobación humana real. Para probar la intervención de una persona en el laboratorio existe --modo interactivo, que pide s o n en consola y luego llama a resolver_solicitud.

Se exige revisar **versión y huella** antes de reanudar, se rechaza una aprobación duplicada y cada propuesta recibe un nuevo thread_id UUID. No se implementan controles de identidad/rol del aprobador; esa es una obligación pendiente para producción.

## 3. Ejecución Windows con nuestra metodología GitHub -> pull -> tests -> checkpoint

LangGraph fue instalado previamente mediante requirements.txt (en la ejecución Windows de B31/L2 se instaló langgraph 1.2.24, compatible con la lección). **No instalar** langgraph-checkpoint-sqlite para esta práctica: el ejemplo utiliza InMemorySaver y no crea base SQLite.

En PowerShell, desde la raíz del repositorio y **en la misma rama U2.7**:

~~~powershell
cd C:\Users\nbello\dev\especializacion-ia-2026
git branch --show-current
git status --short
git pull --ff-only

# 16 pruebas OFFLINE de B32/L1
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_versionado_supervision_b32.py" -v

# Ejemplo reproducible: historial, diff, interrupt, aprobación y rechazo SIMULADOS
.\venv\Scripts\python.exe -m src.versionado_supervision_b32 --modo demo
$LASTEXITCODE

# Regresiones focalizadas, opcionales pero recomendadas
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_logging_rag_b31.py" -v
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_mitigacion_inyeccion_b31.py" -v

git status --short
~~~

**Opcional**: demo con una decisión introducida manualmente, SIN efectos externos:

~~~powershell
.\venv\Scripts\python.exe -m src.versionado_supervision_b32 --modo interactivo
~~~

El programa presenta el diff, versión y huella, deja el grafo interrumpido y solicita s o n. Su aprobación solamente cambia el estado de una **simulación en memoria**. En este chat no se autoriza ninguna acción sobre Booking Core real.

**Conservar** el archivo local no rastreado verificar_tuning.py. No usar git clean ni git add -A.

## 4. Criterios de aceptación (validados offline en Windows)

- Dos versiones con SHA-256 distintos; v1 coincide exactamente con el prompt del Bloque 31.
- registro.json documenta autor, fecha y motivo; los modelos no probados permanecen como null.
- diff_prompts permite visualizar el agregado de reglas de backend y supervisión.
- interrupt detiene el grafo, get_state muestra la solicitud y Command(resume=True) simula su aprobación; False simula el rechazo y mantiene v1.
- Solicitudes nuevas reciben thread_id distintos. Versión o huella diferente y doble aprobación: **bloqueadas**.
- 16 pruebas unitarias pasan y la demo termina con PASS; código de salida 0.
- Sin llamadas a Gemini, sin SQLite, sin cambio real de versión de prompt en B31/L3 y sin operaciones de reservas.

## 5. Limitaciones y siguiente etapa

Una huella SHA-256 truncada es suficiente para aprender y comparar versiones, pero **no sustituye** verificaciones de integridad más sólidas o firmas en un despliegue productivo. Los prompts aquí son ficticios, no secretos. La lista de metadatos de versiones está en Git; un sistema real necesita control de acceso y auditoría de cambios.

Para una agenda real, supervisión humana no debe confundirse con **autenticación, control de tenant, confirmación del cliente o permisos del operador**, que son controles independientes del backend. Aprobación manual por cada respuesta RAG ordinaria no escala.

**Próximo contenido oficial:** Bloque 32 / Lección 2: «Cómo completar una matriz de riesgos de IA generativa». Allí priorizaremos riesgos como alteración no autorizada de citas, cambios de prompts, aislamiento de tenants, inyección indirecta, manejo de datos personales y registro de acciones, sin afirmar mitigaciones productivas ya operativas.

## 6. Bitácora

- Fecha del material: 26/11/2026.
- Etapa: U2.7/B32/L1, revisión del material oficial y preparación de código versionado.
- Código publicado en GitHub y sincronizado por fast-forward hasta el commit 3a3cdaf. Suite 16/16 PASS en Windows y demostración automática PASS.
- Pruebas B32/L1: 16/16 PASS en 0.517 s; demo automática PASS; `$LASTEXITCODE` = 0. Horas de estudio y entrega en plataforma: no informadas.
- Punto exacto siguiente: responder `s` o `n` en el modo interactivo y compartir su resultado; después seguir a B32/L2, matriz de riesgos.

## 7. Evidencia real de Windows · 26/11/2026

Transcripción de PowerShell aportada por el estudiante:

- Git: fast-forward exitoso `6ef8ad2..3a3cdaf` con los siete archivos B32/L1.
- Pruebas: `python -m unittest discover -s tests -p "test_versionado_supervision_b32.py" -v` → **Ran 16 tests in 0.517s / OK**. No fallos ni errores.
- Versiones exactas: `v1-b31-l2` → SHA-256 abreviado `48cb9f82ec5e`; `v2-b32-l1` → `efd33cc0add2`; modelo probado `None` (no probado con Gemini).
- La demo mostró el diff, la interrupción pendiente con `thread_id` propio, una aprobación **simulada** que activó v2 solo en memoria y un rechazo **simulado** que conservó v1.
- Resultado del script: `PASS: registro, diff, interrupt, estado pendiente y decision.` seguido de `Sin despliegues, sin reservas reales, sin API Gemini.`; `$LASTEXITCODE` → **0**.
- Estado de Git después de las pruebas: solo `?? verificar_tuning.py`, archivo local sin seguimiento que se preserva sin subir ni borrar.
- **Modo interactivo:** se ejecutó `python -m src.versionado_supervision_b32 --modo interactivo`, se mostró la propuesta y el interrupt `revision-booking-core-c5997a5adc5c44b991b7dcfccfadc029`, pero la transcripción termina en `¿Aprobar propuesta ficticia? [s/n]:`. No se dispone todavía de una decisión ni resultado final interactivo.
- **Alcance:** el resultado verifica las APIs de supervisión en memoria, no autenticación humana real, persistencia durable, publicación efectiva de prompts ni modificación de reservas.

**Cierre técnico de B32/L1 por pruebas obligatorias:** confirmado; ejecución interactiva opcional pendiente de respuesta. No inferir entrega institucional.
