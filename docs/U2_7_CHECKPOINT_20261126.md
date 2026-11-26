# Checkpoint · Especialización IA 2026 · U2.7 / Booking Core AI

**Fecha:** 2026-11-26.
**Objetivo del proyecto:** Booking Core AI, agente académico para la agenda de AES Barber. No conectar ni alterar reservas reales sin autorización explícita y controles del backend.
**Repositorio:** nicolasbellov/especializacion-ia-2026.
**Rama académica actual:** feature/u2-7-b31-l2-mitigacion-booking-core.
**Método acordado:** publicar GitHub -> git pull local -> pruebas Windows -> evidencia -> actualizar checkpoint. Conservar el archivo local no rastreado verificar_tuning.py.

## Evidencia acumulada y estado

| Etapa | Fuente Skillnest | Código | Evidencia local | Estado |
| --- | --- | --- | --- | --- |
| B31/L1 Logging y trazabilidad | Recibida y estudiada | Ejemplos discutidos | No consta ejecución individual | Revisión de contenido |
| B31/L2 Inyección indirecta | Recibida y estudiada | src/mitigacion_inyeccion_b31_booking_core.py | **9/9 unittest PASS**, demo PASS, exit code 0 | Cierre técnico offline |
| B31/L3 Instrumentación, consumo y filtro | Recibida y estudiada | logging_rag.py | **15/15 unittest PASS** (0.548s), demo dos consultas PASS, exit code 0 | Cierre técnico offline |
| B32/L1 Versionado de prompts y HITL | Recibida y estudiada | src/versionado_supervision_b32.py, 2 prompts, registro.json | **16/16 Windows PASS** (0.517s), demo PASS, exit 0; modo interactivo aguardando respuesta | Cierre técnico offline |
| B32/L2 Matriz de riesgos | Aún no recibida en este chat | No se inició | Ninguna | Siguiente lección después de cerrar B32/L1 |

## Hallazgos específicos

### B31/L2 y L3

- Dependencia langchain-core inicialmente ausente en venv: se resolvió con pip install -r requirements.txt; pip check confirmó ausencia de conflictos.
- B31/L2 filtró 1 documento malicioso de 2 con 3 patrones y conservó el documento legítimo.
- B31/L3 trazas de la demo: trace-eca46fef6836 y trace-7cbb92e94969, correctamente distintas; 2 documentos por consulta, 1 descartado por consulta, 3 coincidencias en el malicioso.
- Consumo de demo por consulta: 210 input, 18 output, 228 total, **simulado=true**; no es consumo real Gemini ni costo facturado.
- El último git status aportado mostró solamente verificar_tuning.py no rastreado: preservarlo, no hacer git clean ni git add -A.
- La actividad Skillnest y el Gate 2 no constan como formalmente entregados/aprobados.

### B32/L1 — validado offline en Windows

- Dos versiones inmutables en Git: prompts/booking_core_ai/sistema_v1.txt y sistema_v2.txt; registro.json guarda autor, fecha, motivo, modelo probado = null.
- v1 coincide con la constante PROMPT_SISTEMA de B31/L2 (verificado al publicar); v2 es una **propuesta** con reglas adicionales, **no está activa** en logging_rag.py.
- RegistroDePrompts + SHA-256 de 12 caracteres + difflib; LangGraph StateGraph con InMemorySaver, interrupt y Command(resume=...).
- Revisor debe comparar versión y huella; hilo único por solicitud, bloqueo de doble reanudación y rechazo que conserva la versión previa.
- El nodo final modifica **solo estado simulado**: no publica, no instala, no reserva, no reprograma, no cancela ni usa Gemini. La demo automática NO es aprobación humana real; el modo interactivo pide s/n pero tampoco autentica a un operador.
- El checkpointer InMemorySaver no es durable; SQLite y comprobaciones de identidad/autorización quedan fuera de esta lección.

## Próximo checkpoint operativo

Desde PowerShell, en la carpeta académica y misma rama:

~~~powershell
cd C:\Users\nbello\dev\especializacion-ia-2026
git status --short
git pull --ff-only
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_versionado_supervision_b32.py" -v
.\venv\Scripts\python.exe -m src.versionado_supervision_b32 --modo demo
$LASTEXITCODE
git status --short
~~~

**Cierre técnico B32/L1 confirmado con evidencia Windows:** 16/16 PASS, demo con aprobación y rechazo simulados PASS, `$LASTEXITCODE`=0. El modo interactivo también se completó: el estudiante escribió `n`; el sistema devolvió `rechazado_en_simulacion`, conservó `v1-b31-l2` y mostró PASS. Después revisar la lección oficial B32/L2 y diseñar la matriz de riesgos del agente de reservas.

**Tiempo efectivo y horarios de estudio:** no informados, no inferir. **Siguiente lección:** U2.7/B32/L2 (matriz de riesgos), aún sin fuente oficial aportada en este punto de la conversación.

## Evidencia recibida posterior al checkpoint

- Fecha: 26/11/2026. Git fast-forward `6ef8ad2..3a3cdaf` incorporó B32/L1.
- 16 pruebas de `tests/test_versionado_supervision_b32.py` pasaron en 0.517s (`OK`).
- Demo: prompt v1 SHA-256 12 chars `48cb9f82ec5e`; prompt v2 propuesto `efd33cc0add2`. `interrupt()` pausó, `get_state` mostró el hilo, y `Command(resume=...)` aprobó/rechazó en simulación; PASS y exit code 0.
- Modo interactivo: se recibió entrada manual **`n`** en el hilo `revision-booking-core-c5997a5adc5c44b991b7dcfccfadc029`; salida `resultado: rechazado_en_simulacion | version simulada: v1-b31-l2`, PASS y `Sin despliegues, sin reservas reales, sin API Gemini.`
- Archivo local no rastreado `verificar_tuning.py` preservado.
- Documentación detallada en `docs/u2_7_b32_l1_versionado_supervision_booking_core.md`.
- La v2 **no está activa en el pipeline B31/L3**, no hay despliegue productivo ni reservas cambiadas. Sin entrega Skillnest confirmada.
