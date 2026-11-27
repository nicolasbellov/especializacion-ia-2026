# Revisión complementaria de Gemini — U3.1 Core

Fecha de recepción: 26/11/2026 (Chile). Fuente: respuesta de Gemini compartida por el estudiante, revisión de la ficha del commit 1f748ecf74ca5ae628e3956fb32c3242e92cc5b8. Veredicto de Gemini: viable con ajustes. Este análisis es una segunda opinión mediante IA, no revisión humana, prueba ciega humana ni revisión formal del programa. Las decisiones del autor sobre esta segunda opinión se registran al final. No se certifica que Gemini haya accedido al repositorio; sus observaciones se contrastaron con la ficha real.

## Contraste de hallazgos y decisiones recomendadas (no decisiones del autor)

| ID Gemini | Evaluación | Recomendación |
|---|---|---|
| H-01 | La supuesta discrepancia no existe. La propia ecuación de Gemini omite 1 h de holgura: 11+7,2+4,8=23. La ficha ya expresa correctamente 11+7,2+1+4,8=24. El tope 19,2 h excluye 4,8 h de margen; los hitos son 18,2 h. | Rechazar error aritmético; tabla de conciliación opcional, sin cambiar cifras ni alcance. |
| H-02 | Riesgo real: Uvicorn incluye la query string en logs de acceso HTTP cuando están habilitados, incluso para POST con query. El cuerpo JSON no es registrado por defecto en ese access log, pero middleware, validaciones y excepciones pueden exponer datos. RNF-02 es viable con controles, no impracticable. | Aceptar: POST /consulta con pregunta en cuerpo JSON; logging estructurado de metadatos permitidos, sanitizar logs de acceso, errores y validaciones, verificar no fuga con centinelas sintéticos. Mantener trace_id. |
| H-03 | Una cita a archivo pertinente no prueba respaldo semántico. CA-09 ya exige inspección humana por caso y falla ante afirmaciones sin sustento. | Aceptar como complemento: comprobación automática de citas reales/permitidas y referencia pertinente por caso, más revisión humana asistida por matriz de afirmaciones y evidencia. Sin rebajar el umbral 9/10 ni incorporar un LLM juez obligatorio. |

## Propuestas acotadas de diseño para ratificación del autor

- Sección 3: POST /consulta con JSON {"pregunta": "..."}; no enviar preguntas ni credenciales por URL. Configurar logs de acceso sin query string (o desactivar access log por defecto y sustituirlo por eventos sanitizados); conservar logs de error sin datos crudos y trace_id correlacionable. No registrar payload, headers de autenticación, documentos ni excepciones con entrada sensible. CA-01 explicitar método, ruta y HTTP 200; CA-02 conservar 422.
- RNF-02 / CA-08: preservar 0 líneas y 10 consultas; incluir logs de aplicación, acceso/error ASGI y stdout/stderr del contenedor cuando corresponda. Buscar centinelas sintéticos y textos de prueba, incluidas representaciones URL-encoded/JSON-escaped pertinentes; utilizar fixtures offline para credenciales falsas, nunca claves reales. Registrar solo conteos, no contenido sensible. CA-10 conserva trazabilidad. Probar consultas inválidas y parámetros de URL accidentales como regresiones complementarias, no como nuevo requisito.
- CA-09: filtro automático de cita sintáctica y fuente permitida/pertinente; matriz por cada caso positivo (respuesta esperada, afirmaciones materiales, referencia y evidencia, PASS/FAIL motivado), revisión humana de contenido. Una fuente presente no acredita que el contenido sea correcto. No gastar cuota en juez LLM.
- CA-07: la ficha ya mide cliente HTTP desde envío hasta cuerpo completo; no se detecta ambigüedad real en el inicio. Registrar condiciones de carga y proveedor, no asumir latencias garantizadas.
- CA-11: definir entorno limpio de referencia en README (contenedor anterior ausente, sin imagen propia preconstruida; declarar estado de caché de bases/dependencias y cómo se provisiona índice persistido, sin ocultar tiempos requeridos). No declarar PASS ni 15 min garantizados hasta prueba real. No destruir vectorstore existente.
- CA-12: consulta negativa exclusivamente al servicio académico local/simulado, nunca canales productivos. AES Barber es una referencia a información real desconocida, no sandbox real. La agenda es ficticia.

## Acierto y límites

Gemini identifica correctamente el valor de persistir Chroma en un volumen y reutilizar embeddings de documentos. Esto no garantiza reproducibilidad exacta de respuestas generativas, latencia, arranque en 15 minutos ni seguridad industrial. La pregunta puede requerir embeddings nuevos; el proveedor externo sigue siendo una dependencia. No se infiere aceptación real de los CA a partir del análisis documental.

## Referencias técnicas consultadas

- Uvicorn, código de access log y pruebas de query string: https://github.com/Kludex/uvicorn/blob/main/uvicorn/protocols/http/httptools_impl.py ; https://github.com/Kludex/uvicorn/blob/main/tests/protocols/test_http.py
- FastAPI, request body y manejo de RequestValidationError: https://fastapi.tiangolo.com/tutorial/body/ ; https://fastapi.tiangolo.com/tutorial/handling-errors/

## Decisiones ratificadas por el autor — 26/11/2026

El estudiante ratificó expresamente las tres recomendaciones: H-01 rechazado, H-02 aceptado, H-03 aceptado con ajustes. Se incorporan las precisiones a la ficha en este mismo commit.

- Hallazgo H-01 — Supuesto error presupuestario.
  Decisión: rechazado. Motivo: el presupuesto original concilia las 24 h, incluida la holgura de 1 h; la igualdad propuesta por Gemini omite esa hora. Se añade la conciliación explícita en la sección 5, sin cambiar horas ni hitos.
- Hallazgo H-02 — Seguridad de los logs.
  Decisión: aceptado. Cambio: RF-01 y arquitectura precisan POST /consulta con cuerpo JSON, RNF-02 amplía explícitamente las superficies de logs a comprobar, CA-01/02 precisan el contrato y CA-08 define la captura y búsqueda de valores sintéticos y sus representaciones; H1 incorpora configuración inicial y H5 conserva la aceptación integral. No hay ampliación de funcionalidades del MVP.
- Hallazgo H-03 — Evaluación semántica.
  Decisión: aceptado con ajustes. Cambio: CA-09 exige filtro programático de referencias permitidas y pertinentes más revisión humana asistida por matriz de evidencia por caso; se conserva el umbral de 9/10 y no se añade un LLM juez.

También se concretan las condiciones de entorno limpio en CA-11 y se explicita que CA-12 solo se ejecuta en el servicio académico, como precisiones de la revisión complementaria. CA-07 conserva su método de medición cliente HTTP. No se modifica el diagrama porque los componentes y relaciones de arquitectura son los mismos; no se incorpora un componente nuevo de logging separado.

## Estado

Decisiones IA ratificadas e incorporadas a la ficha. Presupuesto 24 h, 12 CA, cinco hitos y alcance intactos. Revisión humana externa y prueba ciega pendientes; no crear docs/revision_alcance.md con hallazgos IA como si fueran humanos. Los controles son especificaciones, no evidencia de implementación. Validación Windows de la ficha revisada pendiente; no se ejecutaron nuevas pruebas en este corte.
