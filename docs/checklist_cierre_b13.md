# Checklist de cierre del Bloque 13 (U2.1)

**Fuente:** Skillnest, lección «Límites de uso y registro de costo, ya incorporados al cliente», material compartido el 27/10/2026 (Chile).

**Estado:** repaso efectuado; criterio de observar un HTTP 429 autentico todavía pendiente. No equivale a aprobación institucional.

## Arquitectura del cliente

| Responsabilidad | Archivo / método | Comprobación |
| --- | --- | --- |
| Comunicación HTTP | cliente_api.py / enviar_peticion | Timeout 10 s, claves en variables de entorno, errores 401/403, 400 API_KEY_INVALID, 429 y 5xx clasificados |
| Reintentos | cliente_reintento.py / con_reintento | Hasta 3 intentos; 2 esperas base de 2 y 4 s, máximo 30 s, jitter |
| Costo referencial | cliente.py / registrar_costo | usageMetadata.totalTokenCount; costo por operación y acumulado de proceso |
| Interfaz pública | cliente.py / consultar_modelo | Recibe pregunta y system_instruction, llama con reintentos y devuelve texto o error claro |

El curso presenta un archivo monolitico ilustrativo. Ya tenemos las cuatro responsabilidades en módulos; **no copiar nuevamente el archivo completo** ni incrustar claves en la URL.

## Checklist de la lección

| Criterio que pide Skillnest | Estado propio | Evidencia |
| --- | --- | --- |
| Backoff exponencial con techo y jitter | **Cumplido** | Cinco pruebas B13 previas, simuladas |
| Registrar tokens reales de respuestas correctas y sumar costos | **Cumplido al nivel académico** | Llamada real (25 tokens) y ensayo de 10 llamadas (110 tokens), costo didáctico |
| Provocar un HTTP 429 **real** y registrar lo observado | **Pendiente** | 10 solicitudes reales terminaron HTTP 200; prueba 429 simulada sí pasó |
| RuntimeError final y comprensible tras agotar reintentos | **Verificado con mocks** | Bloque 12 + nueva prueba integrada de tres HTTP 429 simulados |

**No se puede certificar todo el Bloque 13** mientras falte el criterio de 429 real, a menos que Skillnest acepte explícitamente la simulación como sustituto.

## Comprobaciones complementarias automatizadas

El archivo [pruebas_cierre_b13.py](../pruebas_cierre_b13.py) prueba por simulacion y sin gastar cuota:

- HTTP 429 seguido de HTTP 200: respuesta correcta, system_instruction presente y costo registrado exactamente una vez.
- Tres respuestas 429: RuntimeError tras tres intentos, esperas 2 y 4 segundos; costo de sesión cero.
- HTTP 401: ValueError, sin segundo intento y sin costo en el registro local.
- HTTP 500 seguido de HTTP 200: recuperación y costo solo al completar la respuesta.

GitHub Actions comprueba estos casos con una **clave ficticia**. Su éxito demuestra comportamiento en simulación, no que Gemini haya enviado un 429 real.

## Matices técnicos importantes

- Tres intentos totales implican dos esperas, no tres. Con cuatro intentos se observaria una tercera espera base de 8 s.
- La tarifa de **USD 0,002 por 1.000 tokens** es una referencia del material, no el precio actual ni un cobro comprobado de Gemini.
- Una operación no sumada en nuestro contador tras error no prueba que el proveedor nunca facture trabajo parcialmente procesado.
- El estado global costo_total_sesion no persiste entre ejecuciones y no es un diseño de concurrencia productivo.
- Traducir 429, 5xx y errores de red a TimeoutError simplifica el ejercicio, pero pierde especificidad. No se interpreta Retry-After todavía.

## Punto de continuidad

1. Obtener una validación automatizada verde de la nueva prueba integrada.
2. Mantener pendiente el experimento de 429 real sin aumentar indiscriminadamente las solicitudes.
3. Pasar a estudiar el **Bloque 14: Pruebas unitarias**, conservando la trazabilidad de este criterio pendiente.
4. Mantener el avance de U2.1 en **4/9 lecciones**, porque el checklist de cierre de este bloque no se ha completado íntegramente.
