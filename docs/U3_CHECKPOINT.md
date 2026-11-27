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

## B34/L1 — Criterios verificables y plan por hitos (26/11/2026)

- Material oficial 23507 recibido y estudiado. Estudiante confirmó sincronización de f2c2b6e y restauración de una línea en blanco accidental en ficha; solo verificar_tuning.py no rastreado.
- Publicados [ejemplo oficial](../criterios/criterios_demo.py), [variante rota](../criterios/variante_rota.py) y [2 regresiones](../tests/test_criterios_demo_b34.py). Esperado 4/4 y 1/4 criterios cumplidos, respectivamente; variante falla CA-01, CA-02, CA-03 y pasa CA-05. Ambos scripts oficiales finalizan normalmente (no establecen exit distinto para criterios fallidos); pruebas Windows confirmadas; ver cierre abajo. No hay modelo, red, dependencias nuevas ni API.
- [Borrador de CA e hitos](U3_1_B34_L1_BORRADOR_CRITERIOS_HITOS.md): 11 CA propuestos, cubren los cuatro RF imprescindibles y cinco RNF; cinco hitos 18,2 h con presupuesto provisional 24 h, margen 4,8 h no asignado, 1 h holgura adicional de construcción. Casos negativos, fixture y contrato propuestos. Los 10 casos positivos del dataset B27/L3 servirán para latencia y calidad; falta prueba semántica real de generación, no inferir de recuperación.
- La ficha oficial no se modifica todavía (secciones 4 y 5 pendientes hasta Core). No se declara implementación ni aceptación de API/Docker. U3.1 4/6 contenidos estudiados, B34/L1 cerrada técnicamente con evidencia Windows. Tiempo efectivo y horas reales disponibles no informados. Próximo: recibir B34/L2 revisión cruzada (23508).

## Cierre técnico B34/L1 — evidencia Windows (26/11/2026)

- Estudiante sincronizó por fast-forward de f2c2b6e a 1c6f9b8a59411a822770d5b8d8cffbf545854f4d; HEAD local/remoto coinciden y estado final sin modificaciones rastreadas, solo verificar_tuning.py no rastreado (preservar).
- Ejemplo oficial: 4/4 criterios cumplidos, CA-01, CA-02, CA-03 y CA-05 pasan; latencia simulada 10/10 bajo 5 s; exit 0. Variante rota: CA-01 falla por ausencia de fuentes, CA-02/03 fallan con KeyError('fuentes'), CA-05 pasa; 1/4 cumplido, exit 0 esperado por ejecutor oficial. No es un benchmark del servicio real ni prueba de aceptación de Booking Core AI.
- Suite `python -m unittest discover -s tests -p "test_criterios_demo_b34.py" -v`: 2/2 PASS, 0.638 s, OK, exit 0. Acumulado de suites específicas M3: 16/16 (8 B33/L2 + 6 B33/L3 + 2 B34/L1), no corrida global. No nuevos errores inesperados.
- B34/L1 cerrada técnicamente. U3.1 4/6 contenidos completados. Borrador de 11 CA y cinco hitos se mantiene separado de ficha oficial hasta actividad Core; horas disponibles y tiempo efectivo todavía no informados, 24 h escenario provisional. Sin acceso a producción, sin llamadas Gemini ni modificación de índice. Próximo: B34/L2 revisión cruzada del alcance entre pares (23508).

## B34/L2 — Revisión cruzada del alcance entre pares (26/11/2026)

- Material oficial 23508 recibido. Método: presentación 5 min, lectura 15, devolución 10, decisión 10; máximo tres hallazgos y un acierto. Revisión formal propia corresponde a Core y requiere par real.
- Publicados ficha_datos.py, resumen_ficha.py y tests/test_revision_ficha_b34.py (4 pruebas). Dos patrones corruptos en texto recibido reparados para reconocer CA con paréntesis y H con NUMERO interpolado. Lógica de resumen del curso conservada; no es gate. Fixture oficial defectuoso y variante corregida se generan en directorios temporales, sin versionar practica_revision/ ni tocar ficha real. Ejecución Windows confirmada de los tres comandos; ver cierre abajo.
- [Pre-revisión interna IA](U3_1_B34_L2_PRE_REVISION.md): tres hallazgos propuestos (confirmar horas, CA negativo para horarios reales, pauta semántica) y un acierto; no se simula identidad de par ni decisiones del estudiante. No se crea revision_alcance.md hasta consigna Core. Ficha oficial intacta, secciones 4–5 pendientes; horas 24 provisionales, tiempo efectivo no informado. U3.1 5/6 completados; L2 cerrada técnicamente. Próximo: B34/L3 actividad Core (23509).

## Cierre técnico B34/L2 — evidencia Windows (26/11/2026)

- Estudiante sincronizó por fast-forward de 1c6f9b8 a 1a9e035 y luego a 762134fc17b34238cc4b459f48069edd522bd5c5; HEAD local/remoto coinciden. Estado final sin modificaciones rastreadas, solo verificar_tuning.py no rastreado (preservar).
- Práctica `python tests/test_revision_ficha_b34.py --demo`: ficha defectuosa 6 RF, 3 RNF, 6 CA, RF-03 sin criterio, 5 hitos y 18 h de 16 posibles, CA-06 huérfano, H4 sin criterio; ficha corregida 7 CA, 5 hitos y 16 h de 16 posibles, ninguna brecha listada. Exit 0 esperado en resumen descriptivo; no es gate. Coincide con resultados oficiales.
- Suite `python -m unittest discover -s tests -p "test_revision_ficha_b34.py" -v`: 4/4 PASS, 1.468 s, OK, exit 0. Acumulado específico M3: 20/20 (8+6+2+4), no corrida global. Sin errores inesperados.
- `python resumen_ficha.py` sobre ficha real: 7 RF, 5 RNF, 4 imprescindibles, 1 deseable, 2 excluidos, 0 CA, 0 hitos, 0 h planificadas, nueve requerimientos obligatorios sin CA incorporado, exit 0. Resultado esperado porque secciones 4 y 5 siguen pendientes hasta Core; no implica aceptación del diseño completo.
- L2 cerrada técnicamente. U3.1 5/6 contenidos completados. Revisión interna IA documentada; decisiones del autor todavía no comunicadas, disponibilidad efectiva de horas y revisión formal por un compañero pendientes. No se inventa revisor. Tiempo efectivo no informado; escenario 24 h provisional. Próximo: recibir consigna oficial B34/L3 actividad Core (23509) y completar ficha y revisión según sus reglas. Sin acceso a producción, Gemini ni modificación del índice.

## B34/L3 — Core U3.1: preparación de ficha completa (26/11/2026)

- Fuente oficial 23509 recibida; captura confirma formulario de entrega por enlace GitHub, no entrega registrada. HEAD de cierre L2 0039f5d sincronizado según captura.
- Secciones 4 y 5 incorporadas a ficha: 12 CA (incluye negativo de horarios reales y pauta semántica reforzada), cinco hitos, cobertura de nueve requerimientos obligatorios. Escenario 24 h aún provisional: 18,2 h planificadas de 19,2 posibles, 4,8 margen intacto, 1 h holgura construcción. No registrar disponibilidad real sin confirmación. Contratos/fixture pendientes de implementación.
- Publicados verificar_ficha_completa.py (lógica oficial con reparación de regex de Hallazgo para paréntesis opcionales), ocho pruebas de formato en tests/test_ficha_completa_b34.py, guía docs/U3_1_CORE_REVISION_PENDIENTE.md. Adaptada una regresión histórica B33 para verificar las marcas pendientes en el esqueleto temporal, no exigirlas en la ficha final. PNG existente preservado; mejora estética pendiente Gate 3. Sin cambios en código Gate2, índice ni producción.
- Falta revisión auténtica y prueba ciega: curso permite par, externo que no conozca el proyecto o autorrevisión si no hay nadie tras al menos un día de terminar ficha. No crear docs/revision_alcance.md con datos ficticios ni anticipar fecha. No se atribuyen decisiones al estudiante. Guía separada sin nombre ni hallazgos inventados. Verificador real debe devolver exit 1 por registro faltante; PASS temporal de formato no sustituye revisión. Validación Windows confirmada con bloqueo de revisión esperado; ver evidencia abajo. U3.1 6/6 estudiados, 5/6 cerrados; no entrega institucional, no nota, no cierre Core. Tiempo efectivo no informado.
- Próximo: confirmar horas y revisión real, aplicar decisiones, registrar revisión y repetir verificador completo antes de entregar enlace inmutable. U3.2 después de cierre o como estudio paralelo sin declarar Core aprobado.

## Validación técnica B34/L3 — evidencia Windows (26/11/2026)

- Estudiante sincronizó por fast-forward de 0039f5d a e8604b8b80f0dad09611255ccec0117459a2980d. HEAD local/remoto coinciden; estado final sin cambios rastreados, solo verificar_tuning.py no rastreado (preservar).
- Presupuesto propio --horas 24: 12 h construcción disponible, 11 h seleccionadas, 7,2 h QA/docs/defensa y 4,8 h imprevistos; RF-05 no cabe, RF-06/07 excluidos. Viable según estimaciones; horas efectivas no confirmadas.
- resumen_ficha.py: 7 RF, 5 RNF, 4 imprescindibles, 1 deseable, 2 excluidos, 12 CA, 5 hitos, 18,2 de 19,2 h posibles; ninguno obligatorio sin CA, ningún CA ni hito huérfano. verificar_ficha_completa.py: únicamente ERROR por falta de docs/revision_alcance.md, 1 problema, exit 1 esperado; ninguna advertencia ni otro error observado. Las capas anteriores pasan; no constituye aprobación final.
- Suite test_ficha_completa_b34.py: 8/8 PASS, 7.306 s, OK, exit 0. Regresión test_ficha_diseno_b33.py: 6/6 PASS, 3.519 s, OK, exit 0. Acumulado específico M3: 28/28 pruebas distintas (8+6+2+4+8); regresión B33 no se duplica. No corrida global. El fixture de revisión temporal no acredita revisión humana.
- Estado Core: ficha estructuralmente validada, pendiente confirmar horas reales, revisión auténtica/prueba ciega, decisiones del autor, registro y verificador final sin errores, y entrega institucional. No se crea registro ficticio; no se declara Core cerrado. U3.1 6/6 contenidos estudiados, 5/6 cerrados técnicamente. Tiempo efectivo de estudio no informado. No se ha intervenido producción ni índice ni consumido Gemini en esta actividad.
