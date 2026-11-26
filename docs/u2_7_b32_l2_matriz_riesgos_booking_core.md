# U2.7 · Bloque 32 / Lección 2 — Matriz de riesgos de IA generativa

**Fuente:** lección oficial Skillnest «Cómo completar una matriz de riesgos de IA generativa», aportada el 26/11/2026.
**Caso de estudio:** Booking Core AI, agente académico de agenda de barbería. **No se conecta ni modifica Booking Core productivo**.
**Estado:** **cierre técnico offline validado en Windows el 26/11/2026**: 16/16 tests PASS, ejecución del script completa y código de salida 0. Entrega en Skillnest NO confirmada.

## 1. Contenido del curso

El curso define probabilidad e impacto en una escala 1–5, puntaje = probabilidad × impacto y categorías **CRITICO (15–25), ALTO (9–14), MEDIO (4–8), BAJO (1–3)**. Son umbrales pedagógicos, no un estándar universal.

Se deben describir riesgo concreto, mitigación y punto de supervisión cuando corresponda. La prueba de sensibilidad cambia exactamente un eje un punto dentro de 1–5 para comprobar si la categoría varía.

Los cinco ejemplos oficiales tienen los siguientes puntajes y categorías, mantenidos sin alterar en matriz_riesgos.py:

| Ejemplo oficial | Puntaje | Nivel |
| --- | ---: | --- |
| Inyección vía documentos RAG | 16 | CRITICO |
| Filtración PII en logs | 15 | CRITICO |
| Dataset tuning desbalanceado | 9 | ALTO |
| Modelo embeddings deprecado | 8 | MEDIO |
| Chunk desactualizado | 6 | MEDIO |

**Los cinco están AL LIMITE** frente al cambio de un punto. El control 1×1=1 BAJO no lo está. El curso exige un punto humano de supervisión asociado a cada riesgo ALTO o CRITICO.

## 2. Extensión propia: matriz Booking Core AI

La matriz preliminar está separada en [data/matriz_riesgos_booking_core_b32.json](../data/matriz_riesgos_booking_core_b32.json). **Las probabilidades son estimaciones iniciales de diseño, no mediciones o incidentes verificados en producción.**

| ID | Riesgo Booking Core AI | P | I | Puntaje | Nivel |
| --- | --- | ---: | ---: | ---: | --- |
| BC-01 | Alta, modificación o cancelación sin autorización | 4 | 5 | 20 | CRITICO |
| BC-02 | Inyección indirecta en RAG | 4 | 4 | 16 | CRITICO |
| BC-03 | Filtración de datos personales en logs | 3 | 5 | 15 | CRITICO |
| BC-04 | Acceso cruzado entre tenants | 3 | 4 | 12 | ALTO |
| BC-06 | Obsolescencia de modelo de embeddings | 2 | 4 | 8 | MEDIO |
| BC-05 | Políticas desactualizadas por índice RAG | 3 | 2 | 6 | MEDIO |

Cada riesgo incluye justificación, mitigación existente, mitigación pendiente, estado y punto de supervisión. Los cuatro riesgos ALTO/CRITICO están señalados como PROPUESTO_NO_IMPLEMENTADO. La matriz NO afirma que los puntos de aprobación estén operativos.

### Hallazgos de arquitectura

**BC-01:** el laboratorio no tiene acceso a APIs de escritura de Booking Core; falta validar identidad, tenant, permisos, confirmación del usuario y gates para operaciones sensibles.

**BC-02:** las prácticas B31/L2 y B31/L3 filtran patrones y delimitan contexto; sin embargo, al detectar una inyección, el flujo actual elimina el documento sospechoso **y continúa**. El curso ahora recomienda frenar la respuesta automática y derivarla a revisión. Esa modificación sigue **PENDIENTE**.

**BC-03:** la demo B31/L3 no registra preguntas ni respuestas completas, pero el control real de acceso a registros y política de retención son pendientes.

**BC-04:** aislamiento multi-tenant real del backend no ha sido examinado con esta práctica.

**BC-05 y BC-06:** corpus académico versionado y con integridad, pero mantenimiento de políticas reales y migración de embeddings no se han implementado.

La supervisión interactiva B32/L1 está validada para **aprobar o rechazar una versión ficticia de prompt en memoria**: no autoriza operaciones reales ni sustituye autenticación y permisos del backend.

## 3. Archivos de la lección

- [matriz_riesgos.py](../matriz_riesgos.py): ejemplo oficial del curso, sensibilidad y evaluación de la extensión propia, solo librería estándar.
- [data/matriz_riesgos_booking_core_b32.json](../data/matriz_riesgos_booking_core_b32.json): seis riesgos preliminares, controles existentes/propuestos y fuentes.
- [tests/test_matriz_riesgos_b32.py](../tests/test_matriz_riesgos_b32.py): 16 pruebas offline de reglas, valores, sensibilidad y validación de supervisión propuesta.

## 4. Sincronización y validación Windows

Desde la **misma rama U2.7**:

~~~powershell
cd C:\Users\nbello\dev\especializacion-ia-2026
git status --short
git pull --ff-only

.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_matriz_riesgos_b32.py" -v

.\venv\Scripts\python.exe matriz_riesgos.py
$LASTEXITCODE

git status --short
~~~

No instalar dependencias nuevas ni usar una API. **Conservar verificar_tuning.py**, archivo local no rastreado de un ejercicio anterior. No hacer limpieza ni subirlo automáticamente.

## 5. Criterios de cierre técnico (verificados en Windows el 26/11/2026)

- Cinco riesgos oficiales con puntajes 16,15,9,8,6; sus cinco alertas [AL LIMITE]; contraste 1×1 no al límite.
- Seis riesgos de Booking Core AI con puntajes 20,16,15,12,8,6, claramente rotulados como estimaciones preliminares.
- Los cuatro riesgos altos/críticos muestran supervisiones **propuestas, no implementadas**.
- Suite de 16 tests PASS, script ejecutado y código de salida 0; cero intervenciones en reservas reales.

## 6. Bitácora y continuación

- Fecha: 26/11/2026.
- Fuente oficial B32/L2: recibida y analizada.
- Script, datos y pruebas: publicados en GitHub y validados localmente en Windows: **16/16 PASS (0.929 s)**, script completo, `$LASTEXITCODE=0`.
- Tiempo efectivo y entrega institucional: no informados.
- Próximo punto: **B32/L3: Completa tu matriz de riesgos y el versionado de prompts**, última actividad de U2.7. Leer primero la consigna oficial, todavía no recibida.

## 7. Evidencia local Windows recibida (26/11/2026)

- `git pull --ff-only`: fast-forward exitoso `79cd2d0..97c169a`, 5 archivos actualizados/creados.
- `python -m unittest discover -s tests -p "test_matriz_riesgos_b32.py" -v`: **Ran 16 tests in 0.929s / OK**, sin errores ni fallos.
- `python matriz_riesgos.py`: imprimió puntajes y categorías del ejemplo Skillnest (16/15/9/8/6), las cinco advertencias `[AL LIMITE]` y el contraste `1x1 no al limite | puntaje 1 BAJO`.
- La matriz propuesta Booking Core AI imprimió **BC-01=20 (CRITICO), BC-02=16 (CRITICO), BC-03=15 (CRITICO), BC-04=12 (ALTO), BC-06=8 (MEDIO), BC-05=6 (MEDIO)**. Las cinco últimas filas estuvieron `[AL LIMITE]`; BC-01 no. Son **estimaciones académicas**, no cifras de incidentes.
- Los cuatro riesgos críticos/altos registraron `supervision PROPUESTO_NO_IMPLEMENTADO` junto a un punto humano definido, sin declarar protección operativa.
- `$LASTEXITCODE` posterior al script: **0**. `git status --short`: únicamente `?? verificar_tuning.py` (archivo local preexistente; conservarlo).
- La salida del script indicó: `ningun punto de supervision productivo se ha implementado` y `No se consulto Gemini ni se altero la agenda real de Booking Core.`

**Veredicto:** B32/L2 completada técnicamente en el laboratorio offline; no demuestra controles productivos ni constituye entrega en Skillnest. **Siguiente:** consigna de la actividad B32/L3.
