# Corpus demostrativo — Booking Core AI / U2.5 Bloque 24

**ATENCIÓN:** documentación 100 % FICTICIA creada para estudiar chunking,
embeddings y recuperación semántica. NO describe políticas vigentes de AES Barber,
NO contiene información de clientes y NO representa disponibilidad de Booking Core.

## Servicios de la barbería ficticia
EJEMPLO FICTICIO: el catálogo académico incluye corte de cabello, perfilado de
barba y un servicio combinado. Los nombres se usan para comprender consultas
semánticas. Cualquier servicio, precio o duración real debe consultarse mediante
la API autorizada de Booking Core, respetando el tenant autenticado.

## Cambios de una cita ficticia
EJEMPLO FICTICIO: para cambiar una cita, el usuario puede solicitar otra fecha y
hora. El agente deberá consultar disponibilidad actualizada en Booking Core
antes de presentar alternativas. Nunca debe afirmar que el cambio fue realizado
si el backend no confirmó la operación. Este texto NO autoriza un cambio real.

## Cancelación de una cita ficticia
EJEMPLO FICTICIO: una petición de cancelación requiere verificar la identidad y
autorización correspondiente en el backend, además de contar con aprobación
externa para las operaciones de riesgo definidas por el sistema. Una respuesta
generada por IA no cancela por sí misma una cita. Este texto NO es una política
comercial real de AES Barber.

## Preguntas frecuentes y horarios
EJEMPLO FICTICIO: el asistente puede explicar cómo preguntar por un servicio y
cómo solicitar una hora disponible. Las franjas horarias cambian con cada reserva:
no deben indexarse como verdad vigente en Chroma. La disponibilidad, confirmación
y reprogramación deben consultar las APIs transaccionales de Booking Core.

## Privacidad y separación de clientes
EJEMPLO FICTICIO: el asistente debe separar la información de cada cliente y
cada organización. No se cargan datos personales o historiales reales en este
corpus de estudio. En una futura integración, las autorizaciones y el aislamiento
multi-tenant se verifican en el backend, no mediante instrucciones al modelo.
