# Bloque 14 · Lección 2 — Checklist de cobertura del cliente modular

> **Fuente principal:** Skillnest, «Checklist de cliente modular: qué se revisa» (Bloque 14, U2.1), material compartido el 27/10/2026 (Chile).
> **Actualización posterior a la actividad core:** los doce criterios ya tienen pruebas en test_cliente.py y GitHub Actions las ejecutó correctamente. Los textos de planificación posteriores a esta matriz reflejan la secuencia de estudio.

## 1. Criterios del curso vs. evidencia actual

| ID | Función | Comportamiento que debe verificarse | Evidencia existente | Estado para la suite pytest final |
| --- | --- | --- | --- | --- |
| EP-01 | `enviar_peticion` | 401 → `ValueError` | `test_cliente.py::test_enviar_peticion_credencial_invalida` | **Verificado con pytest (HTTP simulado donde aplica)** |
| EP-02 | `enviar_peticion` | 403 → `ValueError` | `test_cliente.py::test_enviar_peticion_sin_permiso_403` | **Verificado con pytest (HTTP simulado donde aplica)** |
| EP-03 | `enviar_peticion` | 429 → `TimeoutError` | `test_cliente.py::test_enviar_peticion_limite_de_uso` | **Verificado con pytest (HTTP simulado donde aplica)** |
| EP-04 | `enviar_peticion` | 500 o superior → `TimeoutError` | `test_cliente.py::test_enviar_peticion_error_500` | **Verificado con pytest (HTTP simulado donde aplica)** |
| EP-05 | `enviar_peticion` | 200 devuelve exactamente el JSON | `test_cliente.py::test_enviar_peticion_exito` | **Verificado con pytest (HTTP simulado donde aplica)** |
| RI-01 | `con_reintento` | Reintenta ante `TimeoutError` | `test_cliente.py::test_con_reintento_recupera_timeout` | **Verificado con pytest (HTTP simulado donde aplica)** |
| RI-02 | `con_reintento` | No reintenta `ValueError` ni otra excepción no transitoria | `test_cliente.py::test_con_reintento_no_reintenta_value_error` | **Verificado con pytest (HTTP simulado donde aplica)** |
| RI-03 | `con_reintento` | Al agotar intentos propaga el `TimeoutError` original | `test_cliente.py::test_con_reintento_agota_intentos_y_propaga_error_original` | **Verificado con pytest (HTTP simulado donde aplica)** |
| CO-01 | `registrar_costo` | Calcula correctamente usando `usageMetadata.totalTokenCount` | `test_cliente.py::test_registrar_costo_calcula_tokens` | **Verificado con pytest (HTTP simulado donde aplica)** |
| CO-02 | `registrar_costo` | Acumula el costo de más de una operación | `test_cliente.py::test_registrar_costo_acumula` | **Verificado con pytest (HTTP simulado donde aplica)** |
| CM-01 | `consultar_modelo` | Convierte un `TimeoutError` agotado en `RuntimeError` claro | `test_cliente.py::test_consultar_modelo_convierte_error` | **Verificado con pytest (HTTP simulado donde aplica)** |
| CM-02 | `consultar_modelo` | Propaga `ValueError` sin transformarlo | `test_cliente.py::test_consultar_modelo_propaga_value_error` | **Verificado con pytest (HTTP simulado donde aplica)** |

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

## 3. Estrategia aplicada durante la actividad core

1. Conservar las tres pruebas aprobadas en `test_cliente.py`.
2. Extender la cobertura con funciones `test_*` con nombre descriptivo o parametrizar casos donde corresponda.
3. Usar `Mock`, `patch` y `pytest.raises` para aislar red, errores y tiempos; no hacer peticiones reales.
4. Sustituir `time.sleep` por mock: comprobar llamadas y cantidad. No asertar una duración aleatoria sin controlar el jitter.
5. Aislar el contador global `cliente.costo_total_sesion` con fixture o restablecimiento antes/después de cada caso, para evitar contaminación entre pruebas.
6. Ejecutar primero una prueba aislada con `python -m pytest test_cliente.py::nombre -v`, luego la suite completa y, finalmente, el pipeline GitHub Actions con regresión de bloques anteriores.
7. Cuando la actividad esté completa, registrar resultados comprobables y verificar esta matriz fila por fila.

## 4. Resultado final y trazabilidad

- Entregable de la actividad core: [test_cliente.py](../test_cliente.py), **13 pruebas** (12 escenarios de la matriz y caso adicional de metadata ausente).
- Todas las pruebas de la tabla pasan por una función de producción real, sustituyendo solo la red, el paso del tiempo o una dependencia concreta.
- Fixture automático de pytest con autouse=True: costo_total_sesion se reinicia antes y después de cada prueba.
- Python -m pytest test_cliente.py -v ejecutado en [GitHub Actions #40623902722](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/40623902722): **success**, incluidas regresiones Gate 1, B12 y B13.
- **Precisión:** todos los HTTP 429 de pytest son simulados. La evidencia de 429 real exigida en B13 continúa ausente; diez consultas reales anteriores obtuvieron HTTP 200.
- **Avance académico:** actividad core B14 completada técnicamente; U2.1 7/9 (77,8 %). La unidad no se declara íntegramente cerrada.

## 5. Punto desde donde continuar

Material siguiente del curso: Bloque 15 / U2.2 (limpieza y tokenización). Mantener como pendiente heredado el HTTP 429 real del B13, sin incrementar solicitudes al proveedor indiscriminadamente.
