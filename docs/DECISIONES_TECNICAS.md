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

## Pendientes para futuras decisiones

- **Bloque 13:** política de backoff (espera progresiva, máximo, jitter, `Retry-After`) y registro de tokens/costos; documentar después de revisar el material oficial.
- **Bloque 14:** diseño de pruebas unitarias y criterios de aceptación de excepciones.
- **U2.3–U2.5:** selección de componentes LangChain, agentes y RAG fundamentada en tareas, complejidad y capacidad de evaluación.
- **Seguridad:** nunca guardar claves en código, logs o documentos; utilizar datos sintéticos para demostraciones de IA aplicada a salud.

## Procedimiento de actualización

1. Añadir decisión al índice con identificador `DT-00X`, fecha y estado.
2. Enlazar código, pruebas y commit; distinguir evidencia ejecutada de suposiciones.
3. Si cambia una decisión anterior, indicar revisión y motivo; conservar su contexto histórico.
4. Actualizar en paralelo [ESTADO_ACADEMICO.md](ESTADO_ACADEMICO.md) y [BITACORA_ESTUDIO.md](BITACORA_ESTUDIO.md) cuando corresponda.
