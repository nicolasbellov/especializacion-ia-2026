# Entrega CORE — U2.7 / Bloque 32 / Booking Core AI

**Actividad Skillnest:** Completa tu matriz de riesgos y el versionado de prompts [Core].
**Fecha:** 26/11/2026.
**Proyecto propio:** Booking Core AI, agente RAG de agenda para una barbería, especialización IA 2026.
**Rama académica:** feature/u2-7-b31-l2-mitigacion-booking-core.

**Alcance:** laboratorio académico. Los documentos, respuestas, aprobaciones y datos son ficticios. No usa Gemini, no despliega prompts, no modifica citas ni información de clientes reales.

## Los tres archivos que solicita la consigna

| Paso | Entregable | Función |
| --- | --- | --- |
| 1. Registro de prompts | [registro_prompts.py](../registro_prompts.py) | Dos versiones propias, SHA-256 abreviado, metadatos, última versión registrada y diff |
| 2. Supervisión humana | [grafo_supervision.py](../grafo_supervision.py) | StateGraph con interrupt, Command(resume=True/False), InMemorySaver y thread_id único |
| 3. Matriz de riesgos | [matriz_riesgos.py](../matriz_riesgos.py) | Seis riesgos propios, matriz 1–5, priorización, sensibilidad y revisión asociada |

Los scripts reutilizan estos datos del propio proyecto:

- [Prompt v1](../prompts/booking_core_ai/sistema_v1.txt) y [prompt v2 propuesto](../prompts/booking_core_ai/sistema_v2.txt).
- [Registro JSON de autor/fecha/motivo](../prompts/booking_core_ai/registro.json).
- [Matriz JSON con mitigaciones y supervisores](../data/matriz_riesgos_booking_core_b32.json).
- [Pruebas específicas de integración Core](../tests/test_entrega_core_b32.py).
- [Pruebas previas de versionado](../tests/test_versionado_supervision_b32.py) y [matriz](../tests/test_matriz_riesgos_b32.py).

## Paso 1 — Evidencia de versionado

Se recuperan las dos versiones reales del repositorio (no las cadenas genéricas de Skillnest).

- Versión **v1-b31-l2**: SHA-256/12 = **48cb9f82ec5e**. Corresponde al prompt utilizado en el laboratorio B31.
- Versión **v2-b32-l1**: SHA-256/12 = **efd33cc0add2**. Es una propuesta que refuerza las restricciones RAG y la autorización del backend.
- **ultima(...)** indica v2 por ser la última registrada, pero **la v2 no está desplegada ni activa en el pipeline B31/L3**.
- El diff muestra las palabras agregadas, y el registro conserva autor y motivo originales: asistente-ia-academico (autor del artefacto).

## Paso 2 — Evidencia de supervisión humana

La huella utilizada procede del registro del Paso 1.

- Primera invocación: **interrupt** real, sin ejecutar el nodo posterior; se puede inspeccionar con **get_state** y el identificador de hilo.
- **Command(resume=True)**: aprobación en estado **simulado** de la v2.
- Segundo hilo independiente y **Command(resume=False)**: rechazo y conservación de v1.
- Modo interactivo opcional: la persona introduce **s** o **n**.
- InMemorySaver no es persistente después de reiniciar y no autentica revisores. En esta actividad NO se activa ningún prompt productivo.

## Paso 3 — Seis riesgos propios

La escala es probabilidad × impacto, ambos entre 1 y 5; umbrales didácticos: CRITICO >=15, ALTO >=9, MEDIO >=4, BAJO el resto.

| ID | Riesgo propio | P | I | Puntaje | Categoría |
| --- | --- | ---: | ---: | ---: | --- |
| BC-01 | Alteración de cita sin autorización | 4 | 5 | 20 | CRITICO |
| BC-02 | Inyección de prompt mediante documentos RAG | 4 | 4 | 16 | CRITICO |
| BC-03 | Exposición de datos personales en logs | 3 | 5 | 15 | CRITICO |
| BC-04 | Acceso cruzado entre tenants | 3 | 4 | 12 | ALTO |
| BC-06 | Embeddings incompatibles u obsoletos | 2 | 4 | 8 | MEDIO |
| BC-05 | Documentación RAG no actualizada | 3 | 2 | 6 | MEDIO |

Todos poseen mitigación explícita. Al menos dos señalan controles efectivamente estudiados y construidos: **Bloque 31** (filtro y logs) y **Bloques 24/26** (corpus, citas e integridad). Los cuatro riesgos ALTO/CRITICO tienen punto de supervisión documentado, marcado **PROPUESTO_NO_IMPLEMENTADO**. Los puntajes son estimaciones académicas: NO provienen de auditoría ni incidentes productivos.

**Gap BC-02:** el flujo B31/L3 elimina documentos maliciosos y continúa con los legítimos; aún no está implementada la nueva recomendación de detenerse y exigir supervisión humana cuando se identifica una inyección.

## Comandos de validación local Windows

Desde la raíz del repositorio académico, en la rama U2.7 ya activa:

~~~powershell
cd C:\Users\nbello\dev\especializacion-ia-2026
git pull --ff-only

.\venv\Scripts\python.exe registro_prompts.py
.\venv\Scripts\python.exe grafo_supervision.py
.\venv\Scripts\python.exe matriz_riesgos.py

.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_entrega_core_b32.py" -v
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_versionado_supervision_b32.py" -v
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_matriz_riesgos_b32.py" -v
$LASTEXITCODE
git status --short
~~~

Opcional, decisión manual: ejecutar **python grafo_supervision.py --modo interactivo** y escribir **n** para probar rechazo.

El archivo local no rastreado **verificar_tuning.py** es anterior a esta entrega. Conservarlo; no usar git clean ni agregar archivos ajenos a la tarea.

## Evidencia acumulada anterior

- B31/L2: **9/9 PASS**, detector y demo verificados en Windows.
- B31/L3: **15/15 PASS**, logging, dos trace_id, consumo simulado y demo verificados.
- B32/L1: **16/16 PASS**, versionado, interrupt, aprobación/rechazo y rechazo manual interactivo.
- B32/L2: **16/16 PASS**, ranking y sensibilidad de riesgos y ejecución completa.

**Las nuevas pruebas de integración Core necesitan validación local en Windows**. Este documento no declara que la entrega haya sido enviada ni aprobada por Skillnest.

**Siguiente unidad:** U2.8 — Gate 2, según el curso; su rúbrica debe revisarse antes de iniciarla.
