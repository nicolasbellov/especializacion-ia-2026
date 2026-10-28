# Estado académico — Especialización en Desarrollo con IA Generativa 2026

> **Actualizado:** 27/10/2026 (Chile). **Fuente:** material curricular compartido, conversación de estudio y evidencia versionada en este repositorio.  
> **Convención:** distinguir *evidencia técnica verificada*, *actividad completada en el entorno local*, *entrega publicada* y *aprobación formal informada por Skillnest*. No son equivalentes.

## Vista general

| Etapa | Alcance | Estado comprobable |
| --- | --- | --- |
| Módulo 1 — Fundamentos técnicos | 46 h curriculares; Gate 1 | Miniaplicación desarrollada; ensayo de instalación limpia y 19/19 pruebas documentados. **Aprobación formal del Gate 1: no confirmada aquí**. |
| **Módulo 2 — Construcción de componentes IA** | **88 h curriculares**; U2.1 a U2.8 | **En curso. U2.1: 6/9 lecciones revisadas/completadas según evidencia; Bloque 14 lección 2 (checklist) auditada. El criterio de 429 real de B13 sigue pendiente**. |
| Módulo 3 — Desarrollo y despliegue end-to-end | 56 h curriculares; Gate 3 y proyecto integrador | Sin avance confirmado en este registro. |

**Total curricular del programa:** 190 h. Las horas curriculares no son horas efectivamente estudiadas; estas últimas se registran separadamente en [BITACORA_ESTUDIO.md](BITACORA_ESTUDIO.md).

## Módulo 1 — evidencia disponible

- Cliente Python/Gemini documentado en [README del proyecto](../README.md) y código en [src/consumir_gemini.py](../src/consumir_gemini.py).
- Ensayo del Gate 1: clonación desde GitHub, reconstrucción de entorno, petición real y **19/19 pruebas exitosas**, según [registro de ensayo](registro_ensayo_gate1.md), fechado el 21/10/2026.
- Evaluación institucional: **pendiente de confirmación del resultado formal**. La afirmación de «Gate 1 aprobado» en una lección posterior no sustituye una calificación o notificación del evaluador.

## Módulo 2 — recorrido

| Unidad | Tema | Seguimiento |
| --- | --- | --- |
| **U2.1** | Consumo avanzado de APIs de IA generativa | **En curso: Bloque 14 lección 2 estudiada y checklist documentado; 6/9 lecciones, con criterio B13 pendiente de HTTP 429 real**. |
| U2.2 | Pipeline de texto, NLP básico y evaluación inicial | Pendiente |
| U2.3 | LangChain y orquestación de flujos | Pendiente |
| U2.4 | Agentes, herramientas externas y memoria | Pendiente |
| U2.5 | RAG y bases de datos vectoriales | Pendiente |
| U2.6 | Personalización: RAG, fine-tuning y soft-prompting | Pendiente |
| U2.7 | Observabilidad, seguridad y gobernanza técnica | Pendiente |
| U2.8 | Gate 2 — Integración y orquestación | Pendiente |

### U2.1 — control de lecciones

| Bloque | Lección/actividad | Estado | Evidencia |
| --- | --- | --- | --- |
| 12 | Autenticación y rate limits | Técnica validada | Respuesta real de Gemini; credencial inválida detectada como `ValueError` |
| 12 | Reintento ante error del proveedor | Técnica validada | Simulación: dos fallos, respuesta en tercer intento |
| 12 | Actividad: cliente modular con reintentos | **Implementada y publicada** | 4/4 pruebas simuladas, consulta real y commit [`f69c0f8`](https://github.com/nicolasbellov/especializacion-ia-2026/commit/f69c0f86bdef23bdac20a4be2f0d9975e6b94607) |
| 13 | Backoff y control de costo | **Completada técnicamente** | 5/5 pruebas B13 + 4/4 regresión B12 y consulta real a Gemini: 25 tokens, USD 0,000050 referenciales |
| 13 | Rate limit provocado | **Ensayo ejecutado; 429 real no observado** | 4/4 pruebas offline; 10/10 operaciones reales HTTP 200, 110 tokens, sin esperas de backoff; evidencia pendiente de 429 real |
| 13 | Límites y costos incorporados | **Revisión y pruebas integradas aprobadas; checklist global parcial** | Cuatro responsabilidades auditadas y cuatro pruebas integradas aprobadas en GitHub Actions; cierre Bloque 13 pendiente de HTTP 429 auténtico |
| 14 | Pruebas unitarias | **Completada técnicamente** | 3/3 pruebas pytest: HTTP 401, HTTP 429 simulado y HTTP 200; GitHub Actions aprobó además la regresión previa |
| 14 | Checklist del cliente modular | **Lección estudiada; matriz documentada** | [Cobertura de 12 comportamientos](checklist_cobertura_b14.md): tres pruebas pytest existentes, evidencias previas y brechas para la actividad final |
| 14 | Actividad core: escribir y verificar pruebas | Pendiente | — |

**Avance U2.1:** 6 de 9 lecciones, **66,7 % por cantidad de lecciones**, no por horas ni por ponderación oficial. La actividad práctica del Bloque 12 está publicada; no se cuenta como evaluación institucional aprobada.

### Entregable verificado de Bloque 12

- [`cliente_api.py`](../cliente_api.py): consumo HTTP y clasificación de errores.
- [`cliente_reintento.py`](../cliente_reintento.py): reintento acotado con espera fija.
- [`cliente.py`](../cliente.py): interfaz pública `consultar_modelo()`.
- [`pruebas_cliente_b12.py`](../pruebas_cliente_b12.py): cuatro escenarios probados.
- **Git:** rama `main`, commit `f69c0f8`, push confirmado y árbol limpio tras la entrega (según salida de PowerShell de la sesión).

### Próximo paso exacto

**Siguiente actividad: U2.1, Bloque 14, «Escribe tus pruebas unitarias y verifica que pasen».** El checklist de cobertura está [documentado](checklist_cobertura_b14.md), sin implementar anticipadamente la suite final. El criterio pendiente de Bloque 13 sigue siendo observar un HTTP 429 auténtico; no se confunde con las respuestas simuladas del test.

### Primera lección del Bloque 13 completada · 27/10/2026

- **Origen de implementación:** rama `feature/u21-b13-backoff-costos`, preparada para integrar mediante PR #1 una vez documentada la validación.
- **Código publicado:** [commit `8b88a34`](https://github.com/nicolasbellov/especializacion-ia-2026/commit/8b88a342f6765587282f8e80624be6546bfd08db).
- **Validación Windows informada:** 5/5 pruebas B13 y 4/4 pruebas de regresión B12; ambos comandos terminaron con éxito.
- **Aspectos cubiertos:** espera exponencial 2→4 s, jitter y límite, `ValueError` no reintentable, total de tokens y costo referencial por operación, acumulación de sesión, ausencia de metadatos.
- **Importante:** costos = **simulación educativa de USD 0,002 por 1.000 tokens**, no costo real auditado ni facturación del proveedor.
- **Consulta real realizada en Windows con el cliente actualizado:** `consultar_modelo('Cual es la capital de Chile?')` devolvió Santiago; la consola informó **25 tokens**, **USD 0,000050 referenciales** y **USD 0,000050 acumulados**.
- **Lecciones contabilizadas como cerradas:** **4/9 (44,4 %)**. Cierre técnico verificado por ejecución del estudiante; no equivale a calificación institucional.

### Ensayo de rate limit · 27/10/2026

**Pruebas automatizadas adicionales:** [GitHub Actions - ejecución satisfactoria](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40620650829) con regresión Gate 1 + B12 + B13 + ensayo offline. **No** representa una observación de 429 real.

- **Pruebas offline:** 4/4 aprobadas. Incluyen `429 → 200`, tres `200`, error `401` y validación del tope de 10 operaciones.
- **Ensayo real con Gemini:** 10 operaciones exitosas, **10 respuestas HTTP 200**, **ningún HTTP 429**, sin reintentos ni backoff observados.
- **Tokens:** 11 por operación; 110 tokens informados en total.
- **Costo acumulado:** **USD 0,000220**, solo estimación didáctica a la tarifa del curso; no factura.
- **Interpretación:** los tests con mocks prueban el flujo de un 429, pero **no** demuestran que el proveedor devolvió un 429. El ensayo real tampoco lo provocó.
- **Evidencia:** [registro técnico](registro_ensayo_rate_limit_b13.md), [PR #2](https://github.com/nicolasbellov/especializacion-ia-2026/pull/2).
- **Avance académico:** permanece **4/9 lecciones**; la segunda lección del Bloque 13 conserva pendiente el criterio de observar un 429 auténtico.

### Lección 3 del Bloque 13 — repaso integral y checklist · 27/10/2026

- **Material revisado:** «Límites de uso y registro de costo, ya incorporados al cliente».
- **Cliente modular:** comunicación HTTP en cliente_api.py, reintentos en cliente_reintento.py, registro de costo e interfaz pública en cliente.py. Se conservaron los módulos existentes, sin duplicar el ejemplo monolítico.
- **Checklist:** [checklist_cierre_b13.md](checklist_cierre_b13.md), con criterios del curso, evidencias y límites documentados.
- **Pruebas integradas:** [pruebas_cierre_b13.py](../pruebas_cierre_b13.py), cuatro escenarios simulados (429 recuperado, 429 persistente, 401 y 500 recuperado), verificados por [GitHub Actions #40621224133](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40621224133) — **success**.
- **Pendiente académico:** el curso exige observar HTTP 429 real; no se ha conseguido. La tercera lección está revisada, pero **no se declara cerrado íntegramente el Bloque 13**.
- **Avance contabilizado sin sobredeclarar:** **4/9 lecciones (44,4 %)**, sin aprobación institucional inferida.

### Bloque 14 · Lección 1 — Pruebas unitarias · 27/10/2026

- **Fuente:** material Skillnest «Pruebas unitarias: la prueba de que tu cliente funciona».
- **Entregable:** [`test_cliente.py`](../test_cliente.py), con tres pruebas `test_enviar_peticion_*` para 401, 429 y 200 usando `pytest`, `Mock` y `patch`.
- **Adaptación al código real:** la función bajo prueba está en `cliente_api.py`, por lo que se parchea `cliente_api.requests.post`, no `cliente.requests.post`.
- **Instalación reproducible:** `pytest>=8,<10` agregado a `requirements.txt`, sin sobrescribir todo el archivo con un nuevo `pip freeze`.
- **Prueba CI confirmada:** [GitHub Actions #40622821093](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40622821093) `success`; pasó pytest y las baterías anteriores.
- **Límite:** los HTTP 401/429/200 de estas pruebas son **simulados**. No acreditan haber provocado un 429 auténtico.
- **Conteo:** 5/9 completadas en U2.1; el cierre global de B13 continúa con el criterio de 429 real pendiente.

### Bloque 14 · Lección 2 — Checklist del cliente modular · 27/10/2026

- **Material Skillnest revisado:** «Checklist de cliente modular: qué se revisa».
- **Resultado:** [matriz de doce comportamientos](checklist_cobertura_b14.md) en `enviar_peticion`, `con_reintento`, `registrar_costo` y `consultar_modelo`.
- **Cobertura actual:** tres pruebas `pytest` en `test_cliente.py` y pruebas adicionales en scripts B12/B13. Las pruebas fuera de `test_cliente.py` se mantienen como evidencia de regresión y **no** se presentan como suite final de la actividad.
- **Brechas:** 403, 500+ en prueba unitaria dedicada, propagación original de `TimeoutError` y consolidación de reintentos/costos/conversión de errores en `pytest`.
- **Punto siguiente:** actividad final del Bloque 14, escribir y comprobar la suite completa con GitHub Actions.
- **Avance:** 6/9 lecciones (66,7 %) por seguimiento interno; Bloque 13 mantiene pendiente el HTTP 429 auténtico.

## Cómo actualizar este archivo

1. Registrar cada lección solo después de estudiar su material y ejecutar la evidencia requerida.
2. Registrar la entrega en Git separadamente de la aprobación formal en Skillnest.
3. Registrar fechas límite solo cuando exista fuente oficial; **no hay fecha límite de U2.1 confirmada en este registro**.
4. Cada cambio técnico significativo debe enlazar su archivo, prueba y commit, y resumirse en [DECISIONES_TECNICAS.md](DECISIONES_TECNICAS.md).
5. No registrar datos personales sensibles, claves API ni contenido clínico real: este repositorio es **público**.
