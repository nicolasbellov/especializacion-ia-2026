# Checkpoint acumulado — Módulo 3 / Booking Core AI

Fecha: 26/11/2026, America/Santiago. Rama: feature/modulo-3-booking-core-ai.
Base remota verificada: efe7ae3e5ef731a07776855250ed66e01082bad5.
Entrega Gate 2 preparada en ccd05d4bae11bf0e288c1309a5ee966096a5b924; tres commits posteriores exclusivamente documentales. U2.7 y Gate 2 entregados, evaluación pendiente. Autoevaluación 81%, 4/4 no compensables. No es nota oficial. Reutilizar [checkpoint Gate 2](U2_8_CHECKPOINT_20261126.md).

## U3.1 — B33/L1 y L2

Material oficial: páginas Skillnest 23504 y 23505, recibido como texto. L1 estudiada; L2 estudiada y ejercicio publicado, validación Windows pendiente. Tiempo efectivo no informado.

- Perfil de trabajo: Backend / Integración de APIs (según contexto académico previo; confirmar ficha original si se requiere evidencia).
- Problema provisional: personal de barbería ficticia atiende manualmente 30 consultas semanales a 3 min cada una (90 min, supuestos, no mediciones). Objetivo: respuestas fundamentadas en menos de un minuto y abstención cuando falte información.
- MVP preliminar: RF-01 API JSON, RF-02 fuentes, RF-03 abstención, RF-04 disponibilidad simulada. RF-05 supervisión de cancelación ficticia deseable; si se incluye, aprobación obligatoria. RF-06 producción y RF-07 frontend propio excluidos. Docker obligatorio como trabajo T-DOCKER asociado a RNF-05.
- RNF propuestos (no verificados): 9/10 consultas bajo 20 s con índice cargado; 0 exposiciones de pregunta/documentos completos y credenciales en logs de 10 consultas; 9/10 respuestas documentales con fuente pertinente; 10/10 consultas válidas trazables; arranque reproducible bajo 15 min con Docker operativo y dependencias accesibles.
- L2: factor novedad 1,5; reserva 30%, imprevistos 20% del total. Ejemplo oficial 71 h solicitadas, neto 10 h, capas cubiertas. Sin contenedor: 68 h, capa faltante. Con 15 h: neto 7,5 h, 7 h seleccionadas, contenedor faltante. Se reprodujeron estos tres escenarios con Python en entorno del asistente a partir del material oficial; no es evidencia Windows.
- Adaptación: RF-01 3 h, RF-02 2 h, RF-03 1 h, RF-04 2 h, T-DOCKER 3 h. Construcción obligatoria 11 h; mínimo teórico 22 h totales. Escenario provisional 24 h: neto 12, reserva 7,2, margen 4,8, holgura de construcción 1 h. Escenario 28 h: neto 14 h, permite considerar RF-05 (3 h). Estimaciones no medidas; disponibilidad efectiva del estudiante no confirmada. No implementar simulador complejo ni producto real.
- El algoritmo oficial puede admitir deseables aun faltando un imprescindible. Adaptación añade control de todos los IDs imprescindibles y las tres capas; devuelve 2 si el alcance no es viable. No sustituye decisión humana ni prueba de implementación.

## Artefactos y evidencia

- [Ejercicio oficial](../presupuesto/presupuesto_alcance.py), [sin contenedor](../presupuesto/variante_sin_contenedor.py), [15 horas](../presupuesto/variante_horas.py).
- [Adaptación](../presupuesto/presupuesto_booking_core.py), [pruebas](../presupuesto/test_presupuesto.py). Pruebas de adaptación y Windows aún pendientes de evidencia. Sin llamadas Gemini, cambios de índice, dependencias nuevas ni datos reales.
- Ejecutar desde raíz con el intérprete existente .venv-gate2/Scripts/python.exe: los tres scripts oficiales, presupuesto_booking_core.py --horas 20 (exit 2 esperado), --horas 24 (exit 0), --horas 28 (exit 0) y -m unittest discover -s presupuesto -p test_presupuesto.py -v.
- No crear aún docs/ficha_diseno_funcional.md: la actividad B33/L3 provee el generador oficial. Respetar los cinco títulos y dejar 4 y 5 pendientes hasta B34.

## Continuidad

Siguiente punto: verificar ejecución Windows, confirmar horas reales disponibles, recibir B33/L3 «Completa tu ficha de diseño funcional» (23506). Preservar verificar_tuning.py local sin rastrear, .env y vectorstore. No modificar Booking Core productivo. Rúbrica completa de Gate 3 aún no recibida. No hay entrega institucional del Módulo 3.
