# Unidad 2.3 · Bloque 20 · Actividad Core: verificación de extremo a extremo

**Programa:** Especialización en Desarrollo con IA Generativa 2026 — Skillnest / Accenture / CChIA  
**Actividad oficial:** «Verifica la ejecución de tu chain de extremo a extremo [Core]»  
**Repositorio:** [nicolasbellov/especializacion-ia-2026](https://github.com/nicolasbellov/especializacion-ia-2026)  
**Rama de entrega:** `feature/u2-3-b20-core-verificacion`  
**Estado:** código y suite Core publicados; **validación local Core y envío Skillnest pendientes**.

## 1. Objetivo y alcance

Verificar el flujo académico original de soporte ficticio para TrakCare Analytics.
La clasificación determina si la entrada es `pregunta`, `queja` o
`sugerencia`; `RunnableBranch` escoge una respuesta especializada; la ruta de
quejas dispone de un fallback y la función de entrada tiene un `try/except`
global con registro de errores. No se utilizan datos clínicos ni conexiones a
instancias reales de InterSystems.

Se conserva la implementación modular desarrollada durante los Bloques 18–20;
no se sustituye por un archivo monolítico de demostración.

## 2. Código verificable

- [Clasificación y rutas (Bloque 19)](../src/bloque19_01_enrutamiento.py): `PromptTemplate`, `StrOutputParser`, normalización, `RunnablePassthrough.assign` y `RunnableBranch`.
- [Recuperación y entrada segura (Bloque 20)](../src/bloque20_01_fallbacks.py): `construir_cadena_queja_segura`, `construir_flujo_con_respaldo` y `procesar_mensaje_seguro(cadena, mensaje)`.
- [Suite Core](../tests/test_orquestacion.py): pruebas integradas con clasificación y rutas inyectadas.
- [Regresión de rutas](../tests/test_bloque19_02_rutas.py): pruebas por categoría y por defecto.
- [Regresión de fallos](../tests/test_bloque20_fallbacks.py): fallbacks sucesivos y errores globales.

El fallback final proporciona un mensaje razonable y no promete contacto humano
ni resultados de consulta que no se hayan verificado. El manejador global
comprueba también que la respuesta final sea texto no vacío; los errores se
registran por su **tipo**, sin copiar mensajes ni credenciales.

## 3. Matriz de cumplimiento del checklist oficial

| Pregunta del checklist | Evidencia técnica | Estado |
| --- | --- | --- |
| ¿La clasificación se normaliza? | `test_core_clasificacion_normaliza_antes_de_comparar` y tests del Bloque 19 | Implementado; pendiente prueba Core local |
| ¿Cada ruta tiene una prueba, incluida la predeterminada? | `test_core_enrutamiento_y_ruta_default` (queja, sugerencia, pregunta, desconocida y entrada vacía) | Implementado; pendiente prueba Core local |
| ¿Los prompts son distintos? | `test_core_cada_ruta_usa_un_prompt_distinto` | Implementado; pendiente prueba Core local |
| ¿Hay al menos un `with_fallbacks` probado? | `test_core_cadena_queja_usa_fallback_ante_fallo` y `test_core_flujo_completo_recupera_queja_sin_ejecutar_otras_rutas` | Implementado; pendiente prueba Core local |
| ¿Un fallo de clasificación no propaga excepción? | `test_core_try_except_cubre_error_del_clasificador_y_registra_evento` | Implementado; pendiente prueba Core local |
| ¿Se rechazan respuestas vacías o de otro tipo? | `test_core_resultado_vacio_o_invalido_activa_red_de_seguridad` | Extensión propia; pendiente prueba Core local |

**Límites:** los tests del Bloque 19 y las ejecuciones manuales previas
demostraron funcionamiento en ejemplos concretos, no precisión perfecta de Gemini.
Las pruebas Core son offline y los errores de red son **simulados**.
Un `try/except` general no reemplaza depuración de causas raíz.

## 4. Evidencias previas confirmadas por el participante

- **Bloque 19:** 3 categorías correctamente enrutadas con Gemini real:
  `pregunta`, `sugerencia` y `queja` (esta última en dos ejecuciones).
  Modelo informado: `gemini-3.5-flash-lite`; respuestas `str`.
- **Bloque 20, primera práctica:** pruebas de fallbacks y captura global
  **8/8 aprobadas**, con demostración offline y registro `ConnectionError`.
- **Suite `tests/` antes de Core:** **40/40 aprobadas** en PowerShell,
  Python 3.12.8 y pytest 9.2.0.

Estos resultados pertenecen a las versiones previas a la actividad Core.
**No se declara ejecutada la nueva suite por la mera publicación del código.**

## 5. Procedimiento de validación Core — pendiente

Desde la raíz del proyecto en Windows, con `.venv` activo:

```powershell
git fetch origin
git switch --track origin/feature/u2-3-b20-core-verificacion
python -m pytest tests/test_orquestacion.py -v
python -m pytest -q tests
python -m src.bloque20_01_fallbacks
git status -sb
```

Si la rama local ya existe, utilizar `git switch feature/u2-3-b20-core-verificacion`
y `git pull --ff-only` en lugar de `git switch --track`.

Si PowerShell bloquea la activación del entorno:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**Resultado previsto:** 14 casos nuevos de pytest en `test_orquestacion.py`,
y 54 casos totales en `tests/`, sin llamadas reales a Gemini. Confirmar
la cifra exclusivamente después de ver la salida de consola.

**Registro de ejecución Core:** pendiente de añadir tras recibir evidencia
del estudiante.

## 6. Entrega institucional

Skillnest ofrece entrega mediante **enlace a GitHub**. Compartir el enlace de
esta guía publicada en la rama, una vez validados los comandos del apartado 5.
No se ha enviado todavía el formulario ni existe aprobación institucional
confirmada.

**Punto de continuidad:** ejecutar la suite Core; completar este registro
con resultados reales; enviar el enlace en Skillnest; pasar a U2.4,
Bloque 21 («Chain vs. agente»).
