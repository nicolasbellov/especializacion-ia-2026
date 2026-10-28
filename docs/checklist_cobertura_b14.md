# Bloque 14 · Lección 2 — Checklist de cobertura del cliente modular

> **Fuente principal:** Skillnest, «Checklist de cliente modular: qué se revisa» (Bloque 14, U2.1), material compartido el 27/10/2026 (Chile).
> **Propósito:** preparar la siguiente actividad «Escribe tus pruebas unitarias y verifica que pasen», sin adelantar ni atribuir a pytest cobertura que solo existe en ensayos de bloques anteriores.

## 1. Criterios del curso vs. evidencia actual

| ID | Función | Comportamiento que debe verificarse | Evidencia existente | Estado para la suite pytest final |
| --- | --- | --- | --- | --- |
| EP-01 | `enviar_peticion` | 401 → `ValueError` | `test_cliente.py::test_enviar_peticion_credencial_invalida` | **Cubierto** |
| EP-02 | `enviar_peticion` | 403 → `ValueError` | Misma rama `401/403` en `cliente_api.py`; sin test pytest específico | **Pendiente** |
| EP-03 | `enviar_peticion` | 429 → `TimeoutError` | `test_cliente.py::test_enviar_peticion_limite_de_uso` | **Cubierto, simulado** |
| EP-04 | `enviar_peticion` | 500 o superior → `TimeoutError` | `pruebas_cierre_b13.py` incluye recuperación tras HTTP 500 simulado | **Pendiente de prueba unitaria dedicada en pytest** |
| EP-05 | `enviar_peticion` | 200 devuelve exactamente el JSON | `test_cliente.py::test_enviar_peticion_exito` | **Cubierto** |
| RI-01 | `con_reintento` | Reintenta ante `TimeoutError` | `pruebas_cliente_b13.py::prueba_backoff` | **Pendiente de integrar en pytest** |
| RI-02 | `con_reintento` | No reintenta `ValueError` ni otra excepción no transitoria | `pruebas_cliente_b13.py::prueba_autenticacion` | **Pendiente de integrar en pytest** |
| RI-03 | `con_reintento` | Al agotar intentos propaga el `TimeoutError` original | `pruebas_cliente_b12.py::prueba_agotamiento` verifica `RuntimeError` externo, no identidad de excepción en `con_reintento` | **Pendiente, prueba unitaria directa** |
| CO-01 | `registrar_costo` | Calcula correctamente usando `usageMetadata.totalTokenCount` | `pruebas_cliente_b13.py::prueba_costos` | **Pendiente de integrar en pytest** |
| CO-02 | `registrar_costo` | Acumula el costo de más de una operación | `pruebas_cliente_b13.py::prueba_costos`, dos respuestas (42 y 57 tokens) | **Pendiente de integrar en pytest** |
| CM-01 | `consultar_modelo` | Convierte un `TimeoutError` agotado en `RuntimeError` claro | `pruebas_cliente_b12.py::prueba_agotamiento`; `pruebas_cierre_b13.py` verifica tres 429 simulados | **Pendiente de integrar en pytest** |
| CM-02 | `consultar_modelo` | Propaga `ValueError` sin transformarlo | `pruebas_cliente_b12.py::prueba_autenticacion`; `pruebas_cierre_b13.py` verifica 401 | **Pendiente de integrar en pytest** |

**Criterio de auditoría:** «pendiente de integrar en pytest» no significa que el cliente esté roto. Significa que la evidencia está hoy en una prueba manual/simulada anterior o falta una prueba unitaria aislada dentro del archivo que evaluará la actividad final.

Los doce comportamientos se derivan de descomponer las frases del checklist. El ejemplo de siete nombres de pruebas proporcionado por el curso es **ilustrativo**, no una demostración de que siete sean suficientes para todos los criterios individuales.

## 2. Archivos y rutas de patch reales

| Recurso que se sustituye durante la prueba | Ruta correcta de `patch` |
| --- | --- |
| Petición de red dentro de `cliente_api.enviar_peticion` | `cliente_api.requests.post` |
| Espera dentro de `cliente_reintento.con_reintento` | `cliente_reintento.time.sleep` |
| Jitter dentro de `cliente_reintento.con_reintento` (solo si se verifica su fórmula) | `cliente_reintento.random.uniform` |
| Envío invocado por `cliente.consultar_modelo` | `cliente.enviar_peticion` |

Skillnest muestra `cliente.requests.post` y `cliente.time.sleep` porque parte de un ejemplo monolítico. Nuestro código está repartido en módulos: copiar literalmente esas rutas produciría errores o un mock sin efecto.

## 3. Estrategia para la actividad siguiente

1. Conservar las tres pruebas aprobadas en `test_cliente.py`.
2. Extender la cobertura con funciones `test_*` con nombre descriptivo o parametrizar casos donde corresponda.
3. Usar `Mock`, `patch` y `pytest.raises` para aislar red, errores y tiempos; no hacer peticiones reales.
4. Sustituir `time.sleep` por mock: comprobar llamadas y cantidad. No asertar una duración aleatoria sin controlar el jitter.
5. Aislar el contador global `cliente.costo_total_sesion` con fixture o restablecimiento antes/después de cada caso, para evitar contaminación entre pruebas.
6. Ejecutar primero una prueba aislada con `python -m pytest test_cliente.py::nombre -v`, luego la suite completa y, finalmente, el pipeline GitHub Actions con regresión de bloques anteriores.
7. Cuando la actividad esté completa, registrar resultados comprobables y verificar esta matriz fila por fila.

## 4. Estado y límites de esta lección

- **Lección actual:** checklist estudiado y auditado; su entregable es el mapa de cobertura, no la suite final.
- **Siguiente actividad formal:** «Escribe tus pruebas unitarias y verifica que pasen».
- **Diferencia esencial:** un 429 simulado no sustituye la evidencia de un 429 real requerida por el Bloque 13.
- **Costo:** tests offline = sin consumo de cuota API; los costos registrados por el cliente siguen siendo referenciales y no cargos auditados.
- **Estado académico U2.1 tras este checklist:** **6/9 lecciones** (66,7 %) por seguimiento interno, sin inferir calificación institucional.
