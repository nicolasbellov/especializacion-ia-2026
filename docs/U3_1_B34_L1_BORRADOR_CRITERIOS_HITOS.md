# U3.1 / B34/L1 — Borrador de criterios y plan por hitos

Fuente: Skillnest 23507, 26/11/2026. Propuesta propia, aún no incorporada a la ficha oficial. No es evidencia de aceptación de la aplicación. IDs del ejemplo de tienda independientes de los de Booking Core AI.

## Criterios propuestos

- CA-01 (RF-01): Al enviar la pregunta «¿Qué requisitos deben verificarse antes de modificar una cita?» al endpoint de consulta, se obtiene un JSON con campos estado, respuesta, fuentes y trace_id.
- CA-02 (RF-01): Al enviar una pregunta vacía al endpoint, se obtiene un error HTTP 422 en JSON (contrato propuesto, pendiente U3.2).
- CA-03 (RF-02): Para la pregunta de CA-01, las fuentes citadas incluyen 03_reprogramacion.md y la afirmación sobre identidad, titularidad y disponibilidad se sustenta en dicho documento. Revisar la cita realmente usada, no solo los documentos recuperados.
- CA-04 (RF-03): Ante «¿Cuál es el precio vigente real de un corte en AES Barber?», la respuesta se abstiene explícitamente de confirmar un precio real y no inventa importes. Puede citar documentación que explica la falta de información.
- CA-05 (RF-04): Con fixture sintético propuesto DEMO-CORTE, 2030-01-15, dos horarios disponibles 10:00 y 11:00, y uno ocupado 12:00, consultar esa fecha/servicio devuelve exactamente las franjas disponibles del fixture (10:00 y 11:00). No se consulta la agenda real. Fixture pendiente de implementación.
- CA-06 (RF-04): En esa consulta, el resultado identifica explícitamente que los horarios son ficticios (campo simulado=true propuesto).
- CA-07 (RNF-01): Para los 10 casos documentales positivos de data/etiquetas_b27_l3_booking_core.json, con Gemini real y el índice cargado, medir por HTTP las 10 latencias extremo a extremo; al menos 9 son estrictamente menores que 20 s, con respuesta válida. No contabilizar errores rápidos como éxitos.
- CA-08 (RNF-02): Tras 10 consultas de prueba con entradas y secretos ficticios controlados, inspeccionar los logs de aplicación y comprobar 0 líneas que expongan preguntas completas, documentos completos o credenciales.
- CA-09 (RNF-03): Para los mismos 10 casos positivos etiquetados, contrastar cada respuesta y su cita utilizada con el corpus original; al menos 9 tienen una fuente pertinente que respalda su afirmación. Registrar revisión humana por caso; no confundir recall con respaldo semántico.
- CA-10 (RNF-04): Para 10 consultas válidas, los 10 trace_id devueltos son únicos y cada uno coincide con sus eventos de aplicación.
- CA-11 (RNF-05): Desde una instalación limpia de referencia con Docker operativo y dependencias accesibles, siguiendo el README, el servicio construido e iniciado responde a la comprobación de salud en menos de 15 minutos; registrar tiempo real, condiciones y resultado. Verificar funcionalidad integrada por separado.

Caso negativo adicional para discusión: pregunta sobre disponibilidad real sin autorización; abstención, sin reutilizar horarios ficticios como reales. No hay CA obligatorio para RF-05 deseable; si entra se definirán aprobación/rechazo antes de cualquier operación ficticia. RF-06 y RF-07 excluidos.

## Plan provisional

Horas disponibles: 24 h (supuesto no confirmado).
Margen de imprevistos: 4,8 h (no asignar).

| Hito | Entrega ejecutable | Cubre | Se comprueba con | Horas | Unidad de apoyo |
|---|---|---|---|---:|---|
| H1 | API de consultas con contrato y entrada inválida controlada; primero dependencias inyectadas offline | RF-01 | CA-01, CA-02 | 3 | U3.2 |
| H2 | API integrada con RAG existente, citas y abstención | RF-02, RF-03 | CA-03, CA-04 | 3 | M2 / U3.2 |
| H3 | Servicio empaquetado que responde a comprobación de salud desde contenedor | RNF-05 | CA-11 | 3 | U3.3 |
| H4 | API integrada con agenda ficticia, disponibilidad de solo lectura | RF-04 | CA-05, CA-06 | 2 | U3.4 |
| H5 | Servicio final verificable con resultados de pruebas, README y defensa ensayada; repetir criterios funcionales y contenedor de versión final | RNF-01, RNF-02, RNF-03, RNF-04 | CA-07, CA-08, CA-09, CA-10 (y regresión CA-01 a CA-06, CA-11) | 7,2 | U3.5 a U3.7 |

Construcción: 11 h. Pruebas/documentación/defensa: 7,2 h. Hitos: 18,2 h; tope 19,2 h (=24-4,8); holgura no asignada de construcción: 1 h, además del margen de 4,8 h. Si cambia la disponibilidad, recalcular con presupuesto_booking_core.py. No comprometer RF-05 sin recalcular y revisar alcance. H3 se prueba temprano por riesgo Docker; repetir sobre versión final. No comprometer fechas sin calendario y disponibilidad.

Los 11 CA cubren los cuatro RF imprescindibles y cinco RNF. Los ejemplos de fixture y contrato son propuestas; no existe evidencia de implementación. Las preguntas de referencia se reutilizan del corpus académico y dataset previamente congelado. No usar producción, datos reales ni secretos. La ficha oficial conserva las secciones 4 y 5 pendientes hasta la actividad Core B34.
