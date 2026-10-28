# Bloque 13 · Ensayo de rate limit — evidencia técnica

**Fecha del ensayo (Chile):** 27/10/2026.  
**Módulo:** 2 · U2.1 · Bloque 13 · Lección 2, «Provocamos un rate limit a propósito, para aprender a manejarlo».  
**Origen de evidencia:** salidas de PowerShell proporcionadas por el estudiante.  
**Estado:** **ejecutado, pero sin observar HTTP 429 real**. No equivale a completar el requisito de provocar un 429 auténtico.

## Configuración

- Rama: `feature/u21-b13-ensayo-rate-limit`, PR #2.
- Archivo de ensayo: [`ensayo_rate_limit_b13.py`](../ensayo_rate_limit_b13.py).
- Tope: diez operaciones; cada una permite hasta tres intentos HTTP solo ante fallos reintentables.
- Preguntas cortas solicitando `OK`, sin esperas artificiales entre operaciones.
- La instrumentación observa `requests.post` y registra `status_code` antes de que el cliente lo convierta a excepción.
- Credenciales almacenadas solo en el `.env` local; no incorporadas a la evidencia.

## 1. Pruebas offline con respuestas HTTP simuladas

Comando: `./venv/Scripts/python.exe ./pruebas_ensayo_rate_limit_b13.py` (adaptar separadores a PowerShell).

| Escenario simulado | Comprobación | Resultado |
| --- | --- | --- |
| `429` seguido de `200` | Reintento y parada al observar 429 | APROBADO |
| `200` por tres operaciones | No informar 429 inexistente | APROBADO |
| `401` | Error no reintentable, finaliza tras una llamada | APROBADO |
| Solicitar 11 operaciones | Rechazo del ensayo por exceder el máximo de 10 | APROBADO |

**Resultado: 4/4 aprobadas.** En estas pruebas no se envía una petición a Gemini. La expresión «HTTP 429 REAL OBSERVADO» que figuró en la primera ejecución provenía de un `requests.post` **simulado** y no demostraba un límite real. Se corrigieron los mensajes posteriores para distinguir ambos modos.

## 2. Ensayo real con Gemini

Comando ejecutado: `.\venv\Scripts\python.exe .\ensayo_rate_limit_b13.py`.

| Medición | Resultado observado |
| --- | --- |
| Operaciones solicitadas | 10 |
| Operaciones exitosas | 10 |
| Operaciones fallidas | 0 |
| Llamadas HTTP observadas | 10 |
| Respuestas HTTP | `{200: 10}` |
| HTTP 429 reales | **0** |
| Primer 429 | No aplica |
| Esperas de backoff observadas | Ninguna (`[]`) |
| Tokens informados | 11 por operación; 110 en total |
| Costo acumulado a tarifa didáctica | **USD 0,000220** |

**Interpretación:** el proveedor respondió satisfactoriamente a las diez operaciones. El ensayo **no llegó al límite de uso** y por eso tampoco observó reintentos en producción. Este resultado no permite inferir la cantidad de peticiones necesaria para provocar un 429.

La cifra en dólares usa el ejemplo académico de USD 0,002 por 1.000 tokens y **no representa facturación real, precio actual verificado ni cargos confirmados**.

## 3. Conclusión, limitación y siguiente paso

- **Verificado:** el cliente funciona con diez llamadas reales seguidas; el ensayo está acotado; el cálculo referencial se acumula; el flujo `429 → 200` funciona **en simulación**.
- **No verificado:** un código HTTP 429 auténtico enviado por Gemini; su reintento real; el comportamiento del proveedor al agotar una cuota.
- **Seguimiento:** conservar el resultado como **lección parcialmente validada** (U2.1: 4/9). No aumentar indiscriminadamente el número de peticiones para forzar una limitación.
- **Próxima actividad:** valorar una comprobación de cuota autorizada y controlada, si la evidencia de un 429 real es imprescindible; registrar después el dato real sin confundirlo con simulaciones.


## 4. Validación continua posterior a la corrección

- **GitHub Actions:** [ejecución #40620650829](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40620650829) — **resultado success**, 27/10/2026 (Chile).
- **Python:** 3.12 en GitHub Actions, con una credencial **ficticia** y pruebas offline.
- **Etapas completadas correctamente:** pruebas Gate 1, pruebas cliente Bloque 12, pruebas cliente Bloque 13 y pruebas de rate limit simulado (incluida la corrección terminológica posterior al primer ensayo).
- **Alcance:** confirma las pruebas automatizadas también fuera del equipo local, **no** demuestra un HTTP 429 auténtico de Gemini ni una facturación real.
