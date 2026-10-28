# Estado académico — Especialización en Desarrollo con IA Generativa 2026

> **Actualizado:** 27/10/2026 (Chile). **Fuente:** material curricular compartido, conversación de estudio y evidencia versionada en este repositorio.  
> **Convención:** distinguir *evidencia técnica verificada*, *actividad completada en el entorno local*, *entrega publicada* y *aprobación formal informada por Skillnest*. No son equivalentes.

## Vista general

| Etapa | Alcance | Estado comprobable |
| --- | --- | --- |
| Módulo 1 — Fundamentos técnicos | 46 h curriculares; Gate 1 | Miniaplicación desarrollada; ensayo de instalación limpia y 19/19 pruebas documentados. **Aprobación formal del Gate 1: no confirmada aquí**. |
| **Módulo 2 — Construcción de componentes IA** | **88 h curriculares**; U2.1 a U2.8 | **En curso. U2.1: 3/9 lecciones realizadas y actividad del Bloque 12 publicada**. |
| Módulo 3 — Desarrollo y despliegue end-to-end | 56 h curriculares; Gate 3 y proyecto integrador | Sin avance confirmado en este registro. |

**Total curricular del programa:** 190 h. Las horas curriculares no son horas efectivamente estudiadas; estas últimas se registran separadamente en [BITACORA_ESTUDIO.md](BITACORA_ESTUDIO.md).

## Módulo 1 — evidencia disponible

- Cliente Python/Gemini documentado en [README del proyecto](../README.md) y código en [src/consumir_gemini.py](../src/consumir_gemini.py).
- Ensayo del Gate 1: clonación desde GitHub, reconstrucción de entorno, petición real y **19/19 pruebas exitosas**, según [registro de ensayo](registro_ensayo_gate1.md), fechado el 21/10/2026.
- Evaluación institucional: **pendiente de confirmación del resultado formal**. La afirmación de «Gate 1 aprobado» en una lección posterior no sustituye una calificación o notificación del evaluador.

## Módulo 2 — recorrido

| Unidad | Tema | Seguimiento |
| --- | --- | --- |
| **U2.1** | Consumo avanzado de APIs de IA generativa | **En curso: Bloque 12 completado técnicamente y publicado; 3/9 lecciones**. |
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
| 13 | Backoff y control de costo | **Siguiente lección** | No iniciada en este registro |
| 13 | Rate limit provocado | Pendiente | — |
| 13 | Límites y costos incorporados | Pendiente | — |
| 14 | Pruebas unitarias | Pendiente | — |
| 14 | Checklist del cliente modular | Pendiente | — |
| 14 | Actividad core: escribir y verificar pruebas | Pendiente | — |

**Avance U2.1:** 3 de 9 lecciones, **33,3 % por cantidad de lecciones**, no por horas ni por ponderación oficial. La actividad práctica del Bloque 12 está publicada; no se cuenta como evaluación institucional aprobada.

### Entregable verificado de Bloque 12

- [`cliente_api.py`](../cliente_api.py): consumo HTTP y clasificación de errores.
- [`cliente_reintento.py`](../cliente_reintento.py): reintento acotado con espera fija.
- [`cliente.py`](../cliente.py): interfaz pública `consultar_modelo()`.
- [`pruebas_cliente_b12.py`](../pruebas_cliente_b12.py): cuatro escenarios probados.
- **Git:** rama `main`, commit `f69c0f8`, push confirmado y árbol limpio tras la entrega (según salida de PowerShell de la sesión).

### Próximo paso exacto

**U2.1, Bloque 13, lección «Backoff y control de costo, operación por operación».** Leer el material oficial antes de cambiar la lógica actual. Mantener pruebas del Bloque 12 como regresión; luego añadir backoff y registro de costo según los criterios del curso.

## Cómo actualizar este archivo

1. Registrar cada lección solo después de estudiar su material y ejecutar la evidencia requerida.
2. Registrar la entrega en Git separadamente de la aprobación formal en Skillnest.
3. Registrar fechas límite solo cuando exista fuente oficial; **no hay fecha límite de U2.1 confirmada en este registro**.
4. Cada cambio técnico significativo debe enlazar su archivo, prueba y commit, y resumirse en [DECISIONES_TECNICAS.md](DECISIONES_TECNICAS.md).
5. No registrar datos personales sensibles, claves API ni contenido clínico real: este repositorio es **público**.
