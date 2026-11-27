# B34/L2 — Práctica de revisión y revisión interna preliminar

Fuente: Skillnest 23508 (26/11/2026). No es revisión formal entre pares. La actividad Core requiere una devolución auténtica de un compañero y decisiones del autor; no se inventa revisor ni se da por cumplido ese requisito.

## Práctica del curso

El resumen es descriptivo, no un gate de aceptación. Se reparan dos patrones del texto recibido: CA con paréntesis literales y grupo de cobertura, H con paréntesis e interpolación de NUMERO. Se preservan reglas y salida del curso. La ficha defectuosa vive únicamente en un directorio temporal al ejecutar el fixture de prueba; no se agrega practica_revision/ al repositorio.

Hallazgos esperados, no ejecución todavía: RF-03 sin CA; 18 h sobre tope 16 h; CA-06 huérfano y H4 sin CA. Corrección de práctica: incorporar CA-04 para RF-03, H4 referencia CA-04, H5 6 h y referencias CA-05/06. Un acierto: los RNF del ejemplo conservan sus umbrales.

## Pre-revisión interna del diseño Booking Core AI (asistente IA)

Base: ficha B33 (secciones 1–3 validadas) y borrador B34/L1 (secciones 4–5 aún no integradas). No es evaluación institucional, ni revisión de un compañero.

| Pauta | Evidencia | Evaluación preliminar |
|---|---|---|
| 1. Problema | Personal de barbería ficticia, 30 consultas/semana y 3 min estimados, objetivo <1 min | Coherente; estimación no medida. |
| 2. Alcance | 7 RF, 5 RNF, cuatro imprescindibles, datos reales excluidos | Coherente; no confundir extensión RF-05 con MVP. |
| 3. Arquitectura | Gemini, Chroma, LangChain existentes; FastAPI/Docker futuros, PNG revisado | Nombres coinciden; etiquetas gráficas parcialmente recortadas, mejora pendiente antes de Gate 3. |
| 4. CA | 11 CA propuestos cubren 9 requerimientos obligatorios | Falta precisar prueba negativa de disponibilidad real y regla semántica. |
| 5. Hitos | 18,2 h de 19,2 h posibles, margen 4,8 h intacto | Aritmética coherente, viabilidad real pendiente de confirmar horas disponibles. |

### Tres hallazgos propuestos (no decisiones del autor)

1. Pauta 5, prioridad alta: 24 h son un supuesto. Sin disponibilidad efectiva, el plan no se puede comprometer. Propuesta: confirmar horas restantes de laboratorio/evidencia y recalcular antes de Core; preservar margen del 20%.
2. Pauta 4, prioridad alta: CA-04 cubre precio real desconocido, pero el RF-03 también cubre horarios reales. Propuesta: añadir CA-12 negativo para disponibilidad real de AES Barber; exigir abstención y ausencia de franjas ficticias presentadas como reales, asignarlo a H4 (regresión H5). No agrega una funcionalidad nueva.
3. Pauta 4, prioridad media: CA-09 define 9/10 con cita pertinente, pero una fuente correcta puede acompañar una afirmación falsa. Propuesta: fijar una pauta por pregunta que exija respaldo de cada afirmación factual material y registrar motivo PASS/FAIL; no contar citas meramente presentes.

Acierto concreto: los 11 CA propuestos ya cubren RF-01 a RF-04 y RNF-01 a RNF-05, reutilizando umbrales y el conjunto de evaluación del Módulo 2. Se separan disponibilidad simulada y conocimiento documental.

El autor decide aceptar, rechazar o aplazar. No escribir todavía docs/revision_alcance.md ni cambiar la ficha oficial hasta recibir consigna Core y revisión del par. La revisión interna no sustituye al compañero.
