# Decisiones técnicas — Registro y continuidad

> **Actualizado:** 27/10/2026 (Chile). Documento índice para recuperar los fundamentos de cada decisión. No sustituye los ADR detallados ni acredita por sí solo pruebas o aprobaciones.

## Criterio de registro

Cada decisión incluye contexto, elección, razón, evidencia, límites y condición de revisión. Diferenciar lo **implementado y observado** de lo **propuesto**; conservar enlaces a archivos y commits. Se evita almacenar secretos: el repositorio es público.

## Decisiones registradas

### DT-001 · Selección de modelo para prototipo (M1)

- **Referencia principal:** [ADR-001: decisión de arquitectura](decision-arquitectura.md).
- **Fecha original:** 20/10/2026; implementación y ensayos posteriores registrados el 21/10/2026.
- **Elección:** `gemini-3.5-flash-lite` como modelo de referencia configurable mediante `GEMINI_MODEL`, según evaluación académica.
- **Razón:** en el experimento documentado mostró calidad semántica suficiente para escenarios simulados de reserva y menor latencia/costo estimado que la alternativa, con limitaciones de formato JSON anotadas.
- **Límite:** no es certificación productiva ni autorización para crear reservas reales. Las tarifas y resultados históricos no deben extrapolarse sin verificar.

### DT-002 · Clasificar errores antes de reintentar (M2 / Bloque 12)

- **Fecha:** 27/10/2026.
- **Implementado en:** [`cliente_api.py`](../cliente_api.py).
- **Elección:** `ValueError` para autenticación/permiso (`401/403` y detección `400 API_KEY_INVALID` de Gemini); `TimeoutError` como **simplificación del curso** para `429`, `5xx` y fallos transitorios de conexión o lectura.
- **Motivo:** impedir reintentos inútiles con credenciales incorrectas y entregar una señal distinguible al mecanismo de recuperación.
- **Evidencia:** prueba de clave inválida y pruebas de cliente sin segundo envío tras error de autenticación.
- **Límite:** `TimeoutError` no es una taxonomía de errores ideal en sistemas de producción; considerar excepciones propias y otros errores HTTP en una evolución futura.

### DT-003 · Reintentos genéricos, acotados y encapsulados (M2 / Bloque 12)

- **Fecha:** 27/10/2026.
- **Archivos:** [`cliente_reintento.py`](../cliente_reintento.py), [`cliente.py`](../cliente.py), [`pruebas_cliente_b12.py`](../pruebas_cliente_b12.py).
- **Elección:** `con_reintento(funcion, intentos=3, espera_segundos=2)`, solo captura `TimeoutError`; `consultar_modelo()` devuelve el texto final y traduce agotamiento en `RuntimeError`. `ValueError` se propaga sin reintento.
- **Motivo:** separar responsabilidades y simplificar la interfaz pública sin ocultar errores permanentes ni repetir infinitamente.
- **Evidencia:** cuatro pruebas simuladas aprobadas, consulta real a Gemini y commit [`f69c0f8`](https://github.com/nicolasbellov/especializacion-ia-2026/commit/f69c0f86bdef23bdac20a4be2f0d9975e6b94607).
- **Límites:** espera **fija**, no backoff exponencial; todavía sin tratamiento de `Retry-After`, cuotas sostenidas, observabilidad o costo por operación. La función simulada de la segunda lección permanece en el módulo de demostración y no debe confundirse con el cliente real.

### DT-004 · Preservar Gate 1 y construir M2 de forma incremental

- **Fecha:** 27/10/2026.
- **Elección:** añadir los módulos nuevos en la raíz sin reemplazar `src/consumir_gemini.py` del Módulo 1, para conservar evidencias y facilitar la práctica de Skillnest.
- **Consecuencia:** `cliente.py` contiene `armar_peticion()` y `extraer_texto()` propios, potencialmente duplicados respecto del módulo del Gate 1. No afirmar reutilización total del código heredado.
- **Próxima revisión:** antes de Gate 2, evaluar una única implementación compartida, conservando compatibilidad y pruebas del Gate 1. **No refactorizar solo por estilo durante la actividad del Bloque 13.**

### DT-005 · Backoff con jitter acotado y costos referenciales (M2 / Bloque 13)

- **Fecha:** 27/10/2026. **Estado:** implementado y probado en Windows con simulaciones y con una consulta real a Gemini.
- **Código:** `cliente_reintento.py` y `cliente.py`, commit [`8b88a34`](https://github.com/nicolasbellov/especializacion-ia-2026/commit/8b88a342f6765587282f8e80624be6546bfd08db).
- **Elección:** 3 intentos totales; backoff de base 2 segundos, duplicando por fallo y con máximo de 30 s; jitter aleatorio positivo hasta 10 %, con recorte final al techo. Se conserva la captura selectiva de `TimeoutError` y la propagación de `ValueError`.
- **Costos:** leer `usageMetadata.totalTokenCount` de respuestas exitosas y sumar un **costo referencial** con la constante educativa del curso (USD 0,002/1.000 tokens). Si faltan metadatos, informar «no estimable», en vez de inventar costo cero. El acumulado solo vive durante el proceso Python.
- **Evidencia:** cinco pruebas B13 y cuatro B12 ejecutadas y aprobadas en Windows, con mocks para evitar gasto en esas pruebas; después, una **consulta real** reportó 25 tokens y un costo **didáctico** estimado de USD 0,000050, devolviendo «Santiago». No hubo validación de rate limit HTTP 429 real.
- **Limitaciones:** no usa aún `Retry-After`; la tarifa única **no representa costos reales del modelo** (entrada/salida/razonamiento tienen posibles tarifas distintas); no hay persistencia, concurrencia ni métricas de facturación.
- **Observación:** el ejemplo docente aplica jitter después del tope, pero esta implementación recorta también el valor final para garantizar que no se exceda el máximo de espera.

### DT-006 · Evidencia separada de 429 simulado y real (M2 / Bloque 13)

- **Fecha:** 27/10/2026. **Estado:** ensayo de diez llamadas reales ejecutado; objetivo de 429 real **no observado**.
- **Elección:** limitar el ensayo a 10 operaciones, sin ampliar automáticamente el número de peticiones. Registrar los códigos HTTP observados y cortar tras el primer 429 si llega a ocurrir.
- **Evidencia:** 4/4 pruebas con respuestas simuladas; un caso `429 → 200` funcionó con backoff. En las llamadas reales a Gemini: **10/10 HTTP 200**, **cero 429**, 110 tokens y costo referencial USD 0,000220.
- **Corrección de trazabilidad:** distinguir el modo de ensayo (`simulado` o `real_gemini`), de forma que los logs de los mocks nunca acrediten falsamente un 429 de Gemini.
- **Límite técnico:** ni un mock ni diez respuestas 200 demuestran cuál es la cuota máxima de la cuenta; tampoco corresponde a una medición de cargos realmente facturados.
- **Próxima revisión:** cuando exista evidencia de un HTTP 429 auténtico, documentar tipo de cuota, esperas y recuperación de forma controlada.

### DT-007 · Conservar cliente modular y automatizar la integración del cierre B13

- **Fecha:** 27/10/2026. **Estado:** implementado y probado con simulaciones.
- **Elección:** el ejemplo monolítico de la tercera lección B13 es una **recapitulación conceptual**, no una orden de reemplazar el cliente ya separado en módulos.
- **Mejora:** [pruebas_cierre_b13.py](../pruebas_cierre_b13.py) añade pruebas completas de 429→200, 429 persistente→RuntimeError, 401 sin reintento y 500→200, con verificaciones de costo único y system_instruction.
- **Evidencia:** [GitHub Actions #40621224133](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40621224133) terminó correctamente, sin clave real.
- **Limitaciones:** todas las respuestas 429 y 500 del test son simuladas; un HTTP 429 real sigue pendiente. La tarifa académica no es una factura, y un costo ausente tras error en el contador local no garantiza ausencia de consumo facturable del proveedor.
- **Checklist:** [docs/checklist_cierre_b13.md](checklist_cierre_b13.md).

### DT-008 · Unit tests con pytest sin alterar el cliente académico

- **Fecha:** 27/10/2026. **Estado:** pruebas automatizadas publicadas en rama y verificadas por GitHub Actions.
- **Decisión:** seguir el patrón del Bloque 14 de Skillnest con `test_cliente.py`, `pytest.raises`, `Mock` y `patch`, apuntando a `cliente_api.requests.post` porque allí se resuelve el símbolo `requests` de `enviar_peticion`.
- **Razón:** las pruebas son deterministas, veloces, reproducibles y no consumen cuota API; cubren tanto errores 401/429 como respuesta 200.
- **Dependencia:** agregar `pytest>=8,<10` al `requirements.txt` existente, sin regenerar innecesariamente todas las dependencias del entorno de estudio.
- **Evidencia:** [GitHub Actions #40622821093](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40622821093) con resultados correctos para pytest y todas las regresiones anteriores.
- **Límites:** el test simula un 429 y no sustituye la observación real requerida por B13. Próxima lección: ampliar el checklist de pruebas de cliente modular.

### DT-009 · Matriz de cobertura antes de completar el archivo pytest (B14)

- **Fecha:** 27/10/2026. **Estado:** matriz revisada y documentada; la implementación de la suite completa queda para la actividad final del bloque.
- **Decisión:** trazar cada comportamiento del checklist de Skillnest hasta una prueba específica, distinguiendo los tres unit tests `pytest` del historial de tests B12/B13.
- **Justificación:** el número de pruebas no equivale a su cobertura. También evita duplicar pruebas sin necesidad o sustituir el código de producción por ejemplos monolíticos.
- **Fuente y evidencia:** [checklist_cobertura_b14.md](checklist_cobertura_b14.md) y pruebas existentes `test_cliente.py`, `pruebas_cliente_b12.py`, `pruebas_cliente_b13.py`, `pruebas_cierre_b13.py`.
- **Punto relevante:** patch `cliente_api.requests.post` para HTTP y `cliente_reintento.time.sleep` para esperas; controlar/restablecer estado global en costos. No introducir llamadas reales a la API dentro de pytest.
- **Limitación:** esta lección prepara el checklist; no declara terminada la suite de la actividad siguiente ni resuelve el 429 real pendiente del Bloque 13.

### DT-010 · Suite pytest completa y fixture para aislamiento de costos (Bloque 14)

- **Fecha:** 27/10/2026. **Estado:** implementado y verificado por CI.
- **Decisión:** concentrar los doce criterios del checklist B14 en el test_cliente.py existente y añadir un caso para ausencia de metadata. Conservar los ejercicios heredados como regresión.
- **Estrategia:** fixture autouse de pytest que resetea el acumulado de cada prueba, mocks de cliente_api.requests.post y cliente_reintento.time.sleep, pytest.raises y nombres descriptivos por escenario.
- **Razón:** los tests no dependen de la disponibilidad de Gemini, no consumen tokens, no tienen esperas reales ni comparten estado de costo entre pruebas.
- **Evidencia:** [GitHub Actions #40623902722](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40623902722) success para pytest B14 y regresiones previas.
- **Límites:** la tarifa de costo continúa siendo referencial. Un HTTP 429 simulado no acredita un rate limit auténtico, criterio pendiente del Bloque 13. Las pruebas no sustituyen la aprobación formal de Skillnest.

## Pendientes para futuras decisiones

- **Bloque 13:** primera lección validada con Gemini real; los temas `Retry-After`, tarifas reales por tipo de tokens y prueba acotada de rate limit provocado siguen pendientes en próximas lecciones.
- **Bloque 14:** diseño de pruebas unitarias y criterios de aceptación de excepciones.
- **U2.3–U2.5:** selección de componentes LangChain, agentes y RAG fundamentada en tareas, complejidad y capacidad de evaluación.
- **Seguridad:** nunca guardar claves en código, logs o documentos; utilizar datos sintéticos para demostraciones de IA aplicada a salud.

## Procedimiento de actualización

1. Añadir decisión al índice con identificador `DT-00X`, fecha y estado.
2. Enlazar código, pruebas y commit; distinguir evidencia ejecutada de suposiciones.
3. Si cambia una decisión anterior, indicar revisión y motivo; conservar su contexto histórico.
4. Actualizar en paralelo [ESTADO_ACADEMICO.md](ESTADO_ACADEMICO.md) y [BITACORA_ESTUDIO.md](BITACORA_ESTUDIO.md) cuando corresponda.
