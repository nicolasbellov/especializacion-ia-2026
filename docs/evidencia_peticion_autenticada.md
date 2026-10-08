# U1.2 - Evidencia de petición HTTP autenticada

## Identificación

- Fecha: 08/10/2026
- Unidad: U1.2 - Setup técnico
- Cliente HTTP: Postman para VS Code
- Proveedor: Google Gemini API
- Modelo: gemini-3.5-flash
- Método HTTP: POST
- Endpoint: https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent

## Resultado

- Código HTTP: 200 OK
- Tiempo de respuesta observado: 2,61 segundos
- Autenticación: encabezado x-goog-api-key
- Credencial: variable privada GEMINI_API_KEY
- Resultado: petición procesada y texto generado correctamente

## Fragmento de respuesta generada

¡Hola! Confirmado: nuestra conexión funciona perfectamente.
Si estás leyendo esto, todo está en orden.

## Incidencia y resolución

Error inicial:
400 INVALID_ARGUMENT.

Causa:
Content-Type fue incorporado incorrectamente como parámetro
de consulta de la URL.

Solución:
Eliminar Content-Type de Params y conservarlo únicamente
en Headers con el valor application/json.

Resultado posterior:
HTTP 200 OK con contenido generado por Gemini.

## Seguridad

La credencial real permanece en el archivo local .env,
excluido mediante .gitignore.

La petición utiliza una referencia a GEMINI_API_KEY.
No se almacena ni publica el valor de la credencial.
