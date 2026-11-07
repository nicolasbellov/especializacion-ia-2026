# Unidad 2.3 · Bloque 20 · Actividad Core: verificación de extremo a extremo

**Programa:** Especialización en Desarrollo con IA Generativa 2026 — Skillnest / Accenture / CChIA  
**Actividad oficial:** «Verifica la ejecución de tu chain de extremo a extremo [Core]»  
**Repositorio:** [nicolasbellov/especializacion-ia-2026](https://github.com/nicolasbellov/especializacion-ia-2026)  
**Rama de entrega:** `feature/u2-3-b20-core-verificacion`  
**Estado:** **actividad Core validada técnicamente en Windows (14/14 pruebas nuevas y 54/54 en regresión)** y **entrega registrada en Skillnest el 06/11/2026; actualmente en revisión por el instructor**. Evaluación/calificación formal pendiente.

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
| ¿La clasificación se normaliza? | `test_core_clasificacion_normaliza_antes_de_comparar` y tests del Bloque 19 | Validado en Windows: pytest Core aprobado |
| ¿Cada ruta tiene una prueba, incluida la predeterminada? | `test_core_enrutamiento_y_ruta_default` (queja, sugerencia, pregunta, desconocida y entrada vacía) | Validado en Windows: pytest Core aprobado |
| ¿Los prompts son distintos? | `test_core_cada_ruta_usa_un_prompt_distinto` | Validado en Windows: pytest Core aprobado |
| ¿Hay al menos un `with_fallbacks` probado? | `test_core_cadena_queja_usa_fallback_ante_fallo` y `test_core_flujo_completo_recupera_queja_sin_ejecutar_otras_rutas` | Validado en Windows: pytest Core aprobado |
| ¿Un fallo de clasificación no propaga excepción? | `test_core_try_except_cubre_error_del_clasificador_y_registra_evento` | Validado en Windows: pytest Core aprobado |
| ¿Se rechazan respuestas vacías o de otro tipo? | `test_core_resultado_vacio_o_invalido_activa_red_de_seguridad` | Extensión propia validada en Windows |

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

Estos resultados corresponden a la etapa previa a Core. La validación posterior de la nueva suite se registra en la sección siguiente.

## 5. Validación Core — ejecución confirmada por el participante

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

**Resultado confirmado por consola compartida:**

```text
python -m pytest tests/test_orquestacion.py -v
collected 14 items
14 passed in 2.49s

python -m pytest -q tests
54 passed in 1.89s
```

- **Entorno informado:** Windows (`win32`), Python 3.12.8, `pytest` 9.2.0, intérprete `.venv\\Scripts\\python.exe`.
- **Rama local verificada:** `feature/u2-3-b20-core-verificacion`, creada por seguimiento de `origin/feature/u2-3-b20-core-verificacion` tras `git fetch`.
- **Casos Core aprobados:** normalización; cinco variantes de categoría/entrada (queja, sugerencia, pregunta, desconocida y vacía); diferenciación de prompts; recuperación de queja; fallo de clasificación con registro; cuatro salidas inválidas (vacío, espacios, `None`, `123`).
- **Regresión completa:** 54 pruebas aprobadas, **cero fallos observados**.
- **Alcance:** las pruebas se ejecutaron sin Gemini real; demuestra el comportamiento de la orquestación ante simulaciones. No se infiere precisión de clasificación general ni disponibilidad del proveedor.
- **Fecha/hora y tiempo efectivo del ensayo:** no informados explícitamente.

**Resultado técnico de la actividad Core: verificado.** El envío a Skillnest y la evaluación oficial son pasos separados.

## 6. Entrega institucional

Skillnest ofrece entrega mediante **enlace a GitHub**. El enlace listo para pegar es:

`https://github.com/nicolasbellov/especializacion-ia-2026/blob/feature/u2-3-b20-core-verificacion/docs/u2_3_b20_core_verificacion.md`

### Constancia de recepción en Skillnest — 06/11/2026

- **Actividad:** «Bloque 20 - Verifica la ejecución de tu chain de extremo a extremo [Core]».
- **Estado mostrado en pantalla:** «Entrega registrada».
- **Confirmación oficial de la interfaz:** la tarea «ha sido registrada exitosamente y está siendo revisada por el instructor».
- **Fecha de envío visible:** 06/11/2026.
- **Evidencia:** captura de la pantalla de confirmación compartida por el estudiante en la conversación; no se incorpora la imagen al repositorio público porque muestra datos personales de la sesión.
- **Documento de evidencia:** esta guía de GitHub, validada con 14/14 pruebas Core y 54/54 en regresión.
- **Estado institucional:** **entrega registrada y en revisión; aún sin calificación ni aprobación formal confirmada**.

**Punto de continuidad:** comenzar U2.4, Bloque 21 («Chain vs. agente») y revisar la retroalimentación institucional cuando esté disponible.
