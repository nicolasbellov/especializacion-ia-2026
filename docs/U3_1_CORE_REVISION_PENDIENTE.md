# Guía de revisión pendiente — U3.1 Core

Documento de trabajo, NO registro de revisión ni evidencia de entrega. Fuente Skillnest 23509. La ficha con cinco secciones queda preparada el 26/11/2026. El autor confirmó 24 h de disponibilidad estimada el 26/11/2026 y eligió la modalidad de persona externa. La identidad, fecha y resultado de revisión aún no se han comunicado. No se crea docs/revision_alcance.md hasta que exista revisión auténtica.

## Modalidades permitidas

1. Par del programa: revisión de 40 minutos, intercambio de fichas.
2. Si no hay par, persona que no conozca el proyecto.
3. Solo si no hay nadie: autorrevisión después de al menos un día de terminar la ficha, declarar autorrevisión, incluir acierto y al menos dos hallazgos. No retrofechar. Esperar un día desde la terminación efectiva, no solo un cambio de fecha.

## Pauta y prueba ciega

Enviar la ficha y el diagrama. Presentar problema y MVP; pedir a la persona que explique cómo verificaría cada CA sin ayuda y examine las cinco secciones: problema, alcance, arquitectura, criterios y plan. Solicitar dos o tres hallazgos con observación, motivo y propuesta, más un acierto concreto. Registrar fecha real, modalidad y nombre con su permiso. El autor decide y justifica cada hallazgo; aplicar cambios aceptados.

## Formato a completar SOLO después de la revisión

```markdown
# Revisión del alcance
Revisor: [nombre real y modalidad]
Fecha: [fecha real]

- Hallazgo 1 (criterio N): [observación, motivo y propuesta]
  Decisión: [aceptado/rechazado/aplazado]. [Cambio, motivo o cuándo se reconsidera]

- Hallazgo 2 (criterio N): [observación, motivo y propuesta]
  Decisión: [aceptado/rechazado/aplazado]. [Cambio, motivo o cuándo se reconsidera]

Acierto: [evidencia concreta]
Prueba ciega: [resultado real]
```

No copiar marcadores a un registro final. La sangría de cada Decisión: son dos espacios; minúsculas y tilde exacta. Las observaciones IA de la lección anterior ya se reflejan como propuestas técnicas (CA-12 y CA-09 reforzado), no como decisiones atribuidas al autor ni hallazgos de una persona.

## Verificación

Ejecutar presupuesto propio, resumen y verificador completo. Sin registro de revisión, el único fallo esperado de la ficha actual es "falta docs/revision_alcance.md". La suite Core usa registro sintético en un directorio temporal para probar la rama exitosa: ese PASS no es una revisión auténtica. El verificador oficial cuenta hallazgos y decisiones, no certifica identidad, fecha, orden, decisión aplicada ni prueba ciega; verificarlos manualmente. Se corrigió el patrón de hallazgo del texto recibido para reconocer paréntesis opcionales según el ejemplo. No enviar a Skillnest hasta completar la revisión auténtica, aplicar las decisiones del autor y verificar la ficha final.
