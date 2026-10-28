# Bitácora de estudio — Especialización IA 2026

## Propósito y reglas

Registro incremental de sesiones, aprendizaje, evidencias, errores y punto de reanudación. Se actualiza cuando existan datos verificables. **Nunca inferir tiempo efectivo a partir de la duración de un chat o de timestamps de Git**; registrar pausas, inicio y término explícitos cuando estén disponibles.

**Campos por sesión:** fecha Chile · módulo/unidad · actividad · inicio · término · tiempo efectivo · avance acumulado · contenidos · ejecución/evidencia · incidentes y solución · pendientes · punto exacto de continuidad.

## Registro acumulado

| Fecha (Chile) | Sesión | Actividad | Inicio | Término | Tiempo efectivo | Resultado |
| --- | --- | --- | --- | --- | --- | --- |
| 21/10/2026 | Antecedente M1 | Ensayo de instalación limpia del Gate 1, documentado en el repositorio | No registrado | No registrado | No registrado | 19/19 pruebas; Gemini real; reproducción local validada |
| **27/10/2026** | **M2-001** | **U2.1, Bloque 12: tres lecciones** | No cronometrado | No cronometrado | **Pendiente de informar** | **Cliente modular integrado; 4/4 pruebas, consulta real y push exitoso** |

> La fila de M1 recupera evidencia del repositorio; **no** significa que la calificación institucional del Gate 1 haya sido recibida.

## Detalle de la sesión M2-001 · 27/10/2026

**Programa:** Skillnest / Accenture / CChIA. **Etapa activa:** Módulo 2, U2.1 — Consumo avanzado de APIs. **Bloque:** 12.

### Contenidos desarrollados

1. Clasificación HTTP: `401/403` → autenticación/permisos sin reintento; `429` y fallas potencialmente transitorias → candidato a reintento; caso de `400 API_KEY_INVALID` observado en la práctica del cliente.
2. Manejo de `requests.post(..., timeout=10)`, variables de entorno con `python-dotenv` y protección de `.env`.
3. Reintentos mediante `con_reintento()`: máximo tres intentos, espera fija de dos segundos entre fallos, captura selectiva de `TimeoutError`.
4. Interfaz pública `consultar_modelo(pregunta, system_instruction="")`, encapsulación del envío, reintentos y extracción de texto.
5. Pruebas con `unittest.mock.patch` para evitar consumo innecesario de cuota; separación entre pruebas simuladas y llamada real.

### Evidencia verificada

- `cliente_api.py` creado, Gemini respondió correctamente a la prueba «Di hola».
- Prueba con credencial inválida en memoria: `ValueError` esperado; la clave real no se modificó en el archivo de entorno.
- `cliente_reintento.py`: dos errores simulados seguidos de respuesta exitosa en tercer intento.
- `pruebas_cliente_b12.py`: **4/4 escenarios correctos**: consulta normal, autenticación sin reintentos, recuperación y agotamiento con `RuntimeError`.
- `cliente.py`: consulta real «¿Cuál es la capital de Chile?» respondida por Gemini con Santiago.
- `git status`: `.env` ignorado; cambios duplicados en `requirements.txt` revertidos antes del commit.
- Commit **[`f69c0f8`](https://github.com/nicolasbellov/especializacion-ia-2026/commit/f69c0f86bdef23bdac20a4be2f0d9975e6b94607)** en `main`, push a `origin/main` confirmado y repositorio sin cambios pendientes después de publicarlo.

### Hallazgos / resoluciones

- **Archivo faltante:** `cliente_api.py` no existía inicialmente en la raíz; se creó mediante PowerShell.
- **Carga del entorno:** se añadió `load_dotenv()` para que `.env` se lea explícitamente.
- **API key inválida:** el proveedor puede responder `400 API_KEY_INVALID`; se incorporó clasificación adicional para no confundirlo con un error genérico.
- **Resultado inicialmente exitoso con clave supuestamente inválida:** se evitó asumir qué versión de `.env` estaba guardada; se probó el caso reemplazando el header **solo en memoria**.
- **Dependencias duplicadas:** se detectaron líneas extra de `requests` y `python-dotenv`; se restituyó `requirements.txt` a la versión original.
- **Avisos LF/CRLF:** Git advirtió conversión de finales de línea; no impidieron validación, commit ni ejecución.

### Limitaciones que quedan abiertas

- Los fallos `429` y los reintentos fueron verificados **por simulación**; no se reporta una medición de rate limit real.
- No hay todavía backoff exponencial, `Retry-After`, métricas por operación ni control de presupuesto.
- El código del Módulo 2 está en archivos independientes en la raíz; revisar futura integración con `src/consumir_gemini.py` para reducir duplicaciones.
- Tiempo efectivo de esta sesión: **no registrado**; completar solo con dato facilitado por el estudiante.

### Avance y punto de continuidad

- **U2.1: 3/9 lecciones = 33,3 % por conteo.**
- **Bloque 12: completado técnicamente y publicado.**
- **Próximo:** leer **Bloque 13 / «Backoff y control de costo, operación por operación»**, preservar las cuatro pruebas ya aprobadas y extender gradualmente el cliente.
- **Pendiente administrativo:** confirmar estado/calificación oficial del Gate 1 cuando se disponga de ese dato.

## Plantilla para próximas sesiones

```markdown
### AAAA-MM-DD · Sesión M2-00X
- Módulo / unidad / bloque / lección:
- Inicio (hora Chile):
- Término (hora Chile):
- Pausas:
- Tiempo efectivo:
- Avance anterior → nuevo:
- Conceptos aprendidos:
- Código / archivos modificados:
- Pruebas y resultados:
- Errores y resolución:
- Evidencia (commit, enlace, salida):
- Pendientes:
- Punto exacto de reanudación:
```
