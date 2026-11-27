# Ficha de Diseño Funcional

Proyecto: **Booking Core AI** · Especialización IA 2026 · Perfil de referencia: Backend / Integración de APIs.

## 1. Problema de negocio
El personal encargado de atender clientes de una barbería ficticia responde manualmente consultas recurrentes sobre servicios, disponibilidad de horarios y políticas de reserva, cancelación y reprogramación. Debe revisar las políticas y la agenda, lo que interrumpe su trabajo y puede producir respuestas inconsistentes. Se considera un volumen de 30 consultas semanales y 3 minutos por consulta (estimación académica, no datos reales), equivalente a 90 minutos semanales de atención repetitiva. Se espera obtener respuestas fundamentadas y consistentes en menos de un minuto por consulta, identificando explícitamente los casos en que no existe información suficiente.

## 2. Requerimientos y alcance (MVP)
### Requerimientos funcionales
- RF-01: Responder preguntas de texto mediante POST /consulta, con la pregunta en el cuerpo JSON y salida estructurada en JSON.
- RF-02: Incluir al menos una referencia al documento pertinente en cada respuesta documental fundamentada.
- RF-03: Abstenerse de afirmar información cuando no exista evidencia suficiente, incluyendo precios y horarios reales desconocidos.
- RF-04: Consultar horarios disponibles de una agenda ficticia mediante datos transaccionales simulados, identificándolos explícitamente como ficticios.
- RF-05: Gestionar la aprobación o rechazo humano previo a una cancelación ficticia, sin efectuar operaciones reales.
- RF-06: Consultar información transaccional de Booking Core productivo.
- RF-07: Mostrar el historial conversacional en una interfaz web propia.
### Requerimientos no funcionales
- RNF-01: Al menos 9 de 10 consultas documentales del conjunto de prueba con Gemini real responden en menos de 20 segundos, medidos de extremo a extremo por HTTP con el índice previamente cargado.
- RNF-02: En los logs de aplicación, acceso y error ASGI, y stdout/stderr del contenedor cuando corresponda, de 10 consultas de prueba, 0 líneas contienen la pregunta completa, documentos completos o credenciales; se verificará con entradas y secretos ficticios controlados.
- RNF-03: Al menos 9 de 10 respuestas del conjunto documental etiquetado citan una fuente pertinente cuyo contenido respalda la afirmación, contrastada con el corpus original.
- RNF-04: Las 10 de 10 consultas válidas del conjunto de prueba tienen un trace_id único y correlacionable entre la respuesta HTTP y el registro de aplicación.
- RNF-05: En 1 instalación limpia de referencia con Docker operativo y acceso a dependencias, el servicio se construye e inicia hasta responder una comprobación de salud en menos de 15 minutos siguiendo el README.
### Alcance
Imprescindible: RF-01, RF-02, RF-03, RF-04

Deseable: RF-05 (solo con presupuesto adicional; si se incluye, la aprobación es obligatoria antes de cancelar).

Fuera de alcance: RF-06 (requiere sistemas y datos reales), RF-07 (frontend propio no necesario para demostrar el servicio).

**Presupuesto confirmado por el autor (26/11/2026):** 24 horas totales estimadas disponibles para laboratorio y evidencia; 12 h construcción, 7,2 h pruebas/documentación/defensa y 4,8 h imprevistos. Los imprescindibles y T-DOCKER (trabajo asociado a RNF-05) suman 11 h ajustadas; queda 1 h de holgura de construcción. RF-05 añade 3 h y solo cabe a partir de un escenario de 28 h totales. Se reutiliza [el presupuesto validado en Windows](../presupuesto/presupuesto_booking_core.py), con factor 1,5 para novedad. Los RNF son objetivos pendientes de medición, no resultados alcanzados. Si cambia la disponibilidad, recalcular el presupuesto y revisar el alcance sin consumir el margen de imprevistos.

## 3. Arquitectura de la solución
Diagrama: docs/diagrama_arquitectura.png

![Arquitectura objetivo de Booking Core AI](diagrama_arquitectura.png)

- Modelo: Gemini mediante API externa para generación y embeddings compatibles con el índice Gate 2; la clave se suministra desde .env local al entorno de ejecución, nunca se incorpora a la imagen.
- Vector store: Chroma con índice académico persistente (5 documentos ficticios, 10 chunks en Gate 2, k=3), montado como volumen de Docker y reutilizado sin reindexar en cada consulta.
- Orquestación: LangChain reutiliza recuperación, filtro de inyección, generación con citas y trazabilidad de Gate 2; el enrutamiento a Agenda simulada será determinista para datos transaccionales ficticios, sin inventar disponibilidad ni consultar producción.
- Exposición: FastAPI con Pydantic recibe consultas de Cliente HTTP (Swagger UI o cliente de pruebas) mediante `POST /consulta` con cuerpo JSON (`pregunta`); devuelve JSON validado, incluyendo estado, fuentes cuando corresponda y trace_id. Las preguntas no se reciben por parámetros de URL y las credenciales no se transmiten por URL.
- Empaquetado: Docker delimita el servicio académico y monta el índice persistente, con configuración y secretos externos; permite construir y ejecutar el servicio de manera reproducible.

**Observabilidad segura (diseño):** configurar Uvicorn sin el access log predeterminado que puede incluir query strings, reemplazándolo por eventos estructurados sanitizados con metadatos permitidos (ruta sin parámetros, estado HTTP, latencia y trace_id; métricas RAG cuando estén disponibles). No registrar cuerpos de solicitudes, encabezados de autenticación, credenciales, documentos completos ni excepciones o errores de validación con entradas sensibles. Aplicar la política también a los registros de error y a la salida del contenedor; conservar la correlación de trazas. La implementación y las pruebas de fuga quedan pendientes en H1/H5.

**Estado y límites:** arquitectura objetivo M3, no implementación ya validada. Se reutilizarán [ServicioRAG](../gate2/servicio.py), [índice](../gate2/indice.py), prompt v3-gate2 y controles existentes. Agenda simulada se implementará con datos sintéticos de solo lectura. Las consultas reales desconocidas se abstienen incluso cuando haya datos simulados. La supervisión mediante [LangGraph](../gate2/supervision.py) se conserva como extensión deseable RF-05, no como componente requerido del diagrama MVP. La verificación sintáctica de citas y el detector de patrones de inyección no garantizan seguridad ni respaldo semántico universal. No existe integración productiva, autenticación productiva ni aislamiento multi-tenant acreditado; no se conectará ni modificará Booking Core real.

## 4. Criterios de aceptación

- CA-01 (RF-01): Enviar POST /consulta con Content-Type application/json y cuerpo JSON cuyo campo "pregunta" contiene "¿Qué verificaciones y confirmación se requieren para modificar una cita?"; se recibe HTTP 200 y un objeto JSON con los campos "estado", "respuesta", "fuentes" y "trace_id".
- CA-02 (RF-01): Enviar POST /consulta con cuerpo JSON {"pregunta": ""}; se recibe un error HTTP 422 en JSON.
- CA-03 (RF-02): Para la pregunta de CA-01, la respuesta cita "03_reprogramacion.md" y expresa las verificaciones de identidad, titularidad, disponibilidad, confirmación y resultado exitoso de la API, sustentadas en el documento original; una fuente solo recuperada no cuenta como citada.
- CA-04 (RF-03): Ante la pregunta "¿Cuál es el precio vigente hoy de un corte en AES Barber?", la respuesta declara que no puede confirmar el precio real y no afirma ningún importe como precio vigente; puede citar fuentes que explican la falta de información.
- CA-05 (RF-04): Con una agenda sintética DEMO-CORTE para 2030-01-15 que contiene 10:00 y 11:00 disponibles y 12:00 ocupado, consultar "¿Qué horas ficticias hay para DEMO-CORTE el 2030-01-15?" devuelve en el campo "horarios" exactamente 10:00 y 11:00, sin 12:00.
- CA-06 (RF-04): En la consulta de CA-05, el campo "simulado" del JSON es true (booleano), identificando las franjas como ficticias.
- CA-07 (RNF-01): Ejecutar por HTTP los 10 casos con evidencia positiva de data/etiquetas_b27_l3_booking_core.json, una vez cada uno, con Gemini real e índice previamente cargado; al menos 9 entregan una respuesta válida en menos de 20 segundos medidos desde el envío hasta recibir el cuerpo completo. Los errores rápidos no cuentan como éxitos.
- CA-08 (RNF-02): Ejecutar 10 consultas controladas con preguntas distinguibles, textos de documentos del corpus y credenciales sintéticas de prueba mediante dependencias offline, nunca claves reales; capturar todos los logs de aplicación y acceso/error ASGI y, en la ejecución Docker, stdout/stderr. Buscar las preguntas completas, documentos completos y credenciales de prueba, incluidas sus representaciones codificadas URL y escapadas JSON pertinentes; 0 líneas pueden contener coincidencias. Registrar solo conteos y resultado sin exponer valores sensibles. Incluir en regresiones complementarias una entrada inválida y una pregunta accidental en query string, verificando que tampoco se registren datos crudos.
- CA-09 (RNF-03): Para los 10 casos positivos de data/etiquetas_b27_l3_booking_core.json, comprobar automáticamente que las citas utilizadas referencian fuentes permitidas y pertinentes según la evidencia etiquetada; después realizar revisión humana de cada respuesta frente al corpus original. Al menos 9 casos deben responder la pregunta, contener una cita pertinente efectivamente utilizada y tener respaldo para cada afirmación factual material. Una contradicción, afirmación sin sustento, omisión de la respuesta esperada o abstención en un caso positivo cuenta como FAIL. Registrar una matriz por caso con respuesta esperada, afirmaciones materiales, cita, evidencia y veredicto PASS/FAIL justificado; no confundir presencia de una cita con respaldo semántico ni exigir un LLM juez.
- CA-10 (RNF-04): Ejecutar las 10 consultas válidas del conjunto positivo etiquetado; los 10 valores de "trace_id" de las respuestas son no vacíos, distintos y cada uno aparece en los eventos de aplicación correspondientes a esa consulta.
- CA-11 (RNF-05): En 1 instalación limpia de referencia con Docker operativo y acceso a dependencias, sin contenedor anterior del servicio ni imagen propia preconstruida, seguir exclusivamente el README desde la preparación del servicio hasta obtener respuesta de salud HTTP 200 en menos de 15 minutos; registrar entorno, estado de caché de bases/dependencias, provisión del índice persistido y tiempo total real, incluyendo los pasos necesarios para que el servicio arranque. Usar copia o volumen de prueba sin destruir el índice existente. La funcionalidad integrada se prueba aparte con los demás CA.
- CA-12 (RF-03): Enviar exclusivamente al servicio académico local la pregunta "¿Tiene AES Barber horas reales disponibles el 15 de enero de 2030 para un corte?"; el servicio informa explícitamente que no puede confirmar disponibilidad real y no presenta las franjas 10:00 o 11:00 del fixture como disponibilidad real. No se consulta ningún canal ni sistema productivo.

Los contratos JSON, ruta de consulta, controles de logging, fixture y procedimiento de pruebas se implementarán en las unidades siguientes; aquí son condiciones de diseño, no evidencia de ejecución. El conjunto positivo corresponde a SERV-01/02, DISP-01/02, REPRO-01/02, CANC-01/02 y PRIV-01/02. RF-05 no forma parte del MVP y requerirá sus propios criterios de aprobación/rechazo si se incorpora.

## 5. Plan de construcción por hitos
Horas disponibles: 24 h
Margen de imprevistos: 4,8 h

**Disponibilidad estimada confirmada por el autor el 26/11/2026:** 24 h. El presupuesto ya fue comprobado con presupuesto/presupuesto_booking_core.py para este escenario; recalcular si cambia la disponibilidad. Las cifras mantienen la reserva del 30% y el margen del 20%. No se incorpora RF-05 al plan de 24 h.

- H1 (3 h): Servicio FastAPI ejecutable con POST /consulta, contrato JSON, validación de entrada y configuración inicial de logging sanitizado, inicialmente con dependencias inyectadas offline (U3.2); la aceptación integral de logging se realiza en H5. Cubre: RF-01. Se comprueba con: CA-01, CA-02.
- H2 (3 h): Servicio HTTP integrado con RAG existente, índice persistido, citas y abstención (M2 y U3.2). Cubre: RF-02, RF-03. Se comprueba con: CA-03, CA-04.
- H3 (3 h): Servicio empaquetado en Docker que responde a la comprobación de salud siguiendo el README de referencia (U3.3). Cubre: RNF-05. Se comprueba con: CA-11.
- H4 (2 h): Servicio integrado con agenda sintética de solo lectura y separación de consultas ficticias y reales (U3.4). Cubre: RF-04, RF-03. Se comprueba con: CA-05, CA-06, CA-12.
- H5 (7,2 h): Servicio final ejecutable con pruebas de aceptación, informe de resultados, README reproducible y ensayo de defensa (U3.5 a U3.7); repetir la regresión funcional y Docker sobre la versión final. Cubre: RNF-01, RNF-02, RNF-03, RNF-04, RNF-05, RF-01, RF-02, RF-03, RF-04. Se comprueba con: CA-01, CA-02, CA-03, CA-04, CA-05, CA-06, CA-07, CA-08, CA-09, CA-10, CA-11, CA-12.

Construcción H1–H4: 11 h de 12 h netas; H5: 7,2 h de reserva de pruebas, documentación y defensa. Total planificado: 18,2 h de 19,2 h posibles. Holgura adicional de construcción: 1 h. Margen de imprevistos de 4,8 h sin asignar. Conciliación del total disponible: 11 h + 7,2 h + 1 h + 4,8 h = 24 h. Docker se comprueba temprano por riesgo y se repite en la versión final. La revisión humana y la prueba ciega todavía deben realizarse; el diseño no se considera aceptado por el solo resultado del verificador.
