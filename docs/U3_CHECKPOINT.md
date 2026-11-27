# Checkpoint acumulado — Módulo 3 / Booking Core AI

Fecha: 26/11/2026, America/Santiago. Rama: feature/modulo-3-booking-core-ai.
Base remota verificada: efe7ae3e5ef731a07776855250ed66e01082bad5.
Entrega Gate 2 preparada en ccd05d4bae11bf0e288c1309a5ee966096a5b924; tres commits posteriores exclusivamente documentales. U2.7 y Gate 2 entregados, evaluación pendiente. Autoevaluación 81%, 4/4 no compensables. No es nota oficial. Reutilizar [checkpoint Gate 2](U2_8_CHECKPOINT_20261126.md).

## U3.1 — B33/L1 y L2

Material oficial: páginas Skillnest 23504 y 23505, recibido como texto. L1 estudiada; L2 estudiada, ejercicio publicado y validado en Windows (8/8 PASS). Tiempo efectivo no informado.

- Perfil de trabajo: Backend / Integración de APIs (según contexto académico previo; confirmar ficha original si se requiere evidencia).
- Problema provisional: personal de barbería ficticia atiende manualmente 30 consultas semanales a 3 min cada una (90 min, supuestos, no mediciones). Objetivo: respuestas fundamentadas en menos de un minuto y abstención cuando falte información.
- MVP preliminar: RF-01 API JSON, RF-02 fuentes, RF-03 abstención, RF-04 disponibilidad simulada. RF-05 supervisión de cancelación ficticia deseable; si se incluye, aprobación obligatoria. RF-06 producción y RF-07 frontend propio excluidos. Docker obligatorio como trabajo T-DOCKER asociado a RNF-05.
- RNF propuestos (no verificados): 9/10 consultas bajo 20 s con índice cargado; 0 exposiciones de pregunta/documentos completos y credenciales en logs de 10 consultas; 9/10 respuestas documentales con fuente pertinente; 10/10 consultas válidas trazables; arranque reproducible bajo 15 min con Docker operativo y dependencias accesibles.
- L2: factor novedad 1,5; reserva 30%, imprevistos 20% del total. Ejemplo oficial 71 h solicitadas, neto 10 h, capas cubiertas. Sin contenedor: 68 h, capa faltante. Con 15 h: neto 7,5 h, 7 h seleccionadas, contenedor faltante. Los tres resultados esperados del material oficial fueron reproducidos y confirmados en Windows por el estudiante; ver evidencia abajo.
- Adaptación: RF-01 3 h, RF-02 2 h, RF-03 1 h, RF-04 2 h, T-DOCKER 3 h. Construcción obligatoria 11 h; mínimo teórico 22 h totales. Escenario provisional 24 h: neto 12, reserva 7,2, margen 4,8, holgura de construcción 1 h. Escenario 28 h: neto 14 h, permite considerar RF-05 (3 h). Estimaciones no medidas; disponibilidad efectiva del estudiante no confirmada. No implementar simulador complejo ni producto real.
- El algoritmo oficial puede admitir deseables aun faltando un imprescindible. Adaptación añade control de todos los IDs imprescindibles y las tres capas; devuelve 2 si el alcance no es viable. No sustituye decisión humana ni prueba de implementación.

## Artefactos y evidencia

- [Ejercicio oficial](../presupuesto/presupuesto_alcance.py), [sin contenedor](../presupuesto/variante_sin_contenedor.py), [15 horas](../presupuesto/variante_horas.py).
- [Adaptación](../presupuesto/presupuesto_booking_core.py), [pruebas](../presupuesto/test_presupuesto.py). Pruebas de adaptación y Windows confirmadas; ver evidencia abajo. Sin llamadas Gemini, cambios de índice, dependencias nuevas ni datos reales.
- Ejecutar desde raíz con el intérprete existente .venv-gate2/Scripts/python.exe: los tres scripts oficiales, presupuesto_booking_core.py --horas 20 (exit 2 esperado), --horas 24 (exit 0), --horas 28 (exit 0) y -m unittest discover -s presupuesto -p test_presupuesto.py -v.
- No crear aún docs/ficha_diseno_funcional.md: la actividad B33/L3 provee el generador oficial. Respetar los cinco títulos y dejar 4 y 5 pendientes hasta B34.

## Continuidad

Siguiente punto: confirmar horas reales disponibles, revisar el archivo local inesperado sin rastrear y recibir B33/L3 «Completa tu ficha de diseño funcional» (23506). Preservar verificar_tuning.py local sin rastrear, .env y vectorstore. No modificar Booking Core productivo. Rúbrica completa de Gate 3 aún no recibida. No hay entrega institucional del Módulo 3.

## Cierre técnico B33/L2 — evidencia Windows (26/11/2026)

- Estudiante confirmó fetch, switch a rama M3 con tracking y pull sin cambios; HEAD local/remoto `0e5b5cf719b8c7716894e751e820da3ee12beff6`. Python 3.12.8 con .venv-gate2 existente.
- Ejemplo oficial: 71 h / 10 h netas, 10 h seleccionadas, tres capas cubiertas. Variante sin contenedor: 68 h / 10 h, 10 h seleccionadas, alerta contenedor. Variante 15 h: 71 h / 7,5 h, 7 h seleccionadas, alerta contenedor. Los tres coinciden con resultados esperados.
- Booking Core AI 20 h: neto 10 h, selección 8 h, falta T-DOCKER y capa contenedor, exit 2 esperado. 24 h: neto 12 h, selección 11 h, RF-05 no incluido, exit 0. 28 h: neto 14 h, selección 14 h con RF-05, exit 0. Producción y frontend excluidos en los tres.
- Suite `python -m unittest discover -s presupuesto -p "test_presupuesto.py" -v`: 8/8 PASS, 0.011 s, OK, exit 0. Sin llamadas al proveedor IA ni nuevas dependencias. La viabilidad es de planificación, no implementación validada de API/Docker.
- Estado inicial: solo `verificar_tuning.py` no rastreado; estado final: también apareció `tatus --short` no rastreado, causa no confirmada. Inspeccionar localmente; no agregar, borrar ni publicar ninguno sin autorización. No se observan modificaciones de archivos rastreados.
- B33/L2 cerrada técnicamente. Avance de contenidos U3.1: 2/6 estudiados; sin entrega institucional de esta lección. Horas reales disponibles y tiempo efectivo no informados; escenario 24 h sigue provisional. Próximo: B33/L3, recibir consigna y generador oficial antes de crear ficha.

## B33/L3 — Ficha de diseño funcional (26/11/2026)

- Fuente oficial recibida: página Skillnest 23506. Requiere ficha Markdown con secciones 1–3, PNG con nombres y flujos coherentes, generador no destructivo, verificador, presupuesto y commit. Secciones 4 y 5 quedan pendientes.
- Sincronización de 94e4932 confirmada por estudiante; archivo accidental tatus --short inspeccionado (solo salida git log) y eliminado explícitamente. Estado final: solo verificar_tuning.py no rastreado.
- Publicación: [ficha](ficha_diseno_funcional.md), [PNG MVP](diagrama_arquitectura.png), [generador](../crear_ficha.py), [verificador oficial](../verificar_ficha.py), [6 pruebas de estructura](../tests/test_ficha_diseno_b33.py). Scripts conservan lógica oficial, las pruebas usan directorios temporales para no modificar la ficha real. El PNG U1.4 que ocupaba la ruta oficial se preserva con el mismo blob d9b1ab9a087da3b2631ab17b30136b9b6e58f6b0 en diagrama_arquitectura_u14.png; referencias de decision-arquitectura.md actualizadas solo en rama M3. Ramas anteriores intactas.
- 7 RF, 5 RNF, 4 imprescindibles, 1 deseable y 2 excluidos. Se reutiliza el script propio B33/L2, sin reemplazar el ejemplo oficial, ya validado 8/8 Windows. Escenario 24 h provisional; disponibilidad real no confirmada. RF-05 se considera deseable; si se incorpora requiere aprobación. No tocar Booking Core real, .env ni vectorstore.
- Verificación formal y suite nueva confirmadas en Windows; revisión visual de PNG realizada mediante capturas. El verificador revisa forma, no calidad ni funcionamiento del futuro servicio. Tiempo efectivo no informado. No se declara entrega institucional ni nota oficial; cierre técnico B33/L3 registrado abajo.
- Próximo: B34/L1 con contenido oficial y confirmación de horas reales disponibles.

## Cierre técnico B33/L3 — evidencia Windows (26/11/2026)

- HEAD local y remoto db3d9308e2686667d0a7d1bbce8d8ea3327a8a42 tras fast-forward de 94e4932; estudiante confirmó recepción de los ocho archivos modificados/agregados. Estado final sin modificaciones rastreadas; solo verificar_tuning.py no rastreado, preservado.
- `verificar_ficha.py`: «Ficha verificada: secciones 1 a 3 completas», sin avisos ni errores, exit 0. Suite `python -m unittest discover -s tests -p "test_ficha_diseno_b33.py" -v`: 6/6 PASS, 3.520 s, OK. Acumulado de suites específicas M3: 14/14 (8 B33/L2 + 6 B33/L3), no es una corrida global.
- Escenario provisional 24 h reconfirmado: 12 h netas, 11 h seleccionadas (RF-01 a RF-04 y T-DOCKER), 7,2 h de pruebas/docs/defensa, 4,8 h de imprevistos; RF-05 queda deseable, exit 0. No equivale a validación técnica de API, Docker ni RNF. Horas reales y tiempo efectivo no informados.
- Error de PowerShell por concatenación accidental de dos comandos ($LASTEXITCODE y operador &); corregido al ejecutarlos por separado. Sin defecto de código ni necesidad de parche.
- Capturas VS Code: ficha Markdown renderizada, PNG incrustado, nombres Gemini, Chroma, LangChain, FastAPI y Docker coinciden, frontera y secretos externos visibles, secciones 4 y 5 pendientes. Mejora visual pendiente antes de Gate 3: tipografía y etiquetas de flechas parcialmente recortadas (por ejemplo respuesta/vector); no afecta el verificador formal.
- B33/L3 cerrada técnicamente; B33 completo, U3.1 3/6 contenidos estudiados. Entrega Git realizada; sin constancia de entrega institucional ni nota. Próximo: B34/L1 «Criterios de aceptación verificables y plan por hitos» (23507). No se ha intervenido Booking Core productivo.
