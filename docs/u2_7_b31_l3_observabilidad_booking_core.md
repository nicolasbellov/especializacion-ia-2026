# U2.7 · Bloque 31 / Lección 3 — Instrumenta tu RAG (Booking Core AI)

**Fuente oficial:** Skillnest, «Instrumenta tu solución y registro de consumo [Actividad práctica]», texto entregado el **26/11/2026**.
**Estado académico:** implementación versionada en GitHub; **no** asumir aprobación, entrega institucional ni pruebas Windows hasta recibir evidencias.
**Repositorio académico:** nicolasbellov/especializacion-ia-2026, rama feature/u2-7-b31-l2-mitigacion-booking-core.

## 1. Qué exige Skillnest

La actividad pide instrumentar el RAG de U2.5 con:
1. Cada consulta genera un trace_id propio con contextvars y escribe JSON por evento.
2. AIMessage.usage_metadata se registra como input_tokens, output_tokens, total_tokens.
3. Los documentos pasan por un filtro de prompt injection ANTES de construir el prompt final; log de descartes con fuente y número de patrones.
4. Dos consultas independientes deben tener trace_id diferentes y no mezclarse.
5. El flujo real con Gemini es opcional y la entrega es código versionado en Git.

Los logs no deben guardar preguntas, documentos o respuestas completos sin justificación.

## 2. Adaptación propia al proyecto Booking Core AI

- [logging_rag.py](../logging_rag.py) reutiliza detectar_inyeccion y los roles/delimitadores de [B31/L2](../src/mitigacion_inyeccion_b31_booking_core.py).
- Reutiliza el formateo de contexto **con citas numeradas** y mapa hacia metadata.fuente de [citas_demo.py](../citas_demo.py), probado en U2.5/B26.
- Usa objetos Document del corpus académico con metadata.origen=FICTICIO_ACADEMICO, como los del índice B24/L3, y una interfaz recuperador(pregunta) compatible con BaseRetriever.invoke de U2.5/B26.
- Filtra documentos ANTES de construir contexto/prompt (no reutiliza directamente construir_resultado de U2.5 porque ese método arma el prompt con todos los chunks, sin filtro).
- No elimina ni reindexa vectorstore/. No utiliza APIs de citas, disponibilidad ni clientes del backend Booking Core.
- Un generador de prueba devuelve AIMessage con usage_metadata sintética **210/18/228**, explicitando simulado=true. Es una prueba del registro, **NO medición de tokens de Gemini**.
- En los logs registra trace_id, eventos, longitud de pregunta, cantidades, fuentes ficticias normalizadas y tokens; no contenido ni preguntas ni respuestas.
- Se evita registrar el mensaje de una excepción porque podría revelar datos sensibles.
- No calcula un **costo monetario** sin tarifas del proveedor. Los tokens permiten estimarlo si se agrega una tabla de precios vigente, identificación del modelo y reglas de facturación.
- El filtro por regex tiene falsos positivos/negativos y NO autoriza acciones del agente: roles, delimitadores y validaciones del backend siguen siendo necesarios.

## 3. Pasos de ejecución (Windows / PowerShell)

El estudiante viene de la rama B31/L2, por eso ahora **solo debe hacer pull en esa misma rama**, sin cambiar de rama ni crear archivos manualmente.

~~~powershell
cd C:\Users\nbello\dev\especializacion-ia-2026
git branch --show-current
git status --short
git pull --ff-only

# Valida funcionalidad B31/L3, SIN Gemini ni claves
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_logging_rag_b31.py" -v

# Dos consultas distintas, prompt injection, usage_metadata simulada.
.\venv\Scripts\python.exe logging_rag.py --modo demo
$LASTEXITCODE

# Regresión específica de B31/L2 (debe conservar 9/9)
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_mitigacion_inyeccion_b31.py" -v

git status --short
~~~

**Preservar el archivo local** verificar_tuning.py (no rastreado). No hacer git add -A, git clean ni borrar archivos locales.

## 4. Checklist de aceptación (pendiente de evidencias Windows)

- Un documento ficticio legítimo y otro malicioso → evento documento_descartado_por_inyeccion únicamente para el malicioso, con fuente ticket_ficticio_881 y tres patrones.
- AIMessage sintético → evento consumo_llm con input=210, output=18, total=228, simulado=true.
- Dos consultas → dos trace_id distintos; cada secuencia consulta_recibida, documentos_recuperados, contexto_filtrado, consumo_llm y consulta_finalizada se correlaciona por trace_id.
- Los mensajes tienen roles system y human, delimitadores contexto_recuperado, citas [1] y ningún contenido malicioso.
- 15 pruebas unitarias definidas en tests/test_logging_rag_b31.py deben pasar en Windows; registrar cantidad observada sin inventar resultados.
- La demo imprime un PASS final y retorna exit code 0 cuando cumple sus verificaciones.
- No llama a Gemini por defecto, no expone secretos y no modifica el índice ni la base transaccional.

## 5. Integración opcional con U2.5 real

Solo si se desea probar la API **explícitamente** y el estudiante dispone de su índice local (B24/L3, cinco fuentes/10 chunks) y credencial Gemini:

~~~powershell
.\venv\Scripts\python.exe logging_rag.py --modo real --pregunta "¿Como puedo reprogramar una cita?"
~~~

Ese modo abre el índice existente con la función abrir_vectorstore de recuperacion.py, usa su retriever y ChatGoogleGenerativeAI. **Consume API de embeddings y chat** y puede generar costos/cuotas. No es requisito de B31/L3. **Nunca borra ni reconstruye** vectorstore, ni modifica reservas reales. El sistema de registro distingue simulado=false si el proveedor entrega usage_metadata; si falta, los campos se registran como null, no 0.

## 6. Bitácora

- Fecha: 26/11/2026.
- Fuente oficial B31/L3: recibida.
- Adaptación técnica: código, pruebas y documentación preparados en el repositorio académico.
- Validación local Windows y demo: pendiente.
- Tiempo efectivo / entrega institucional Skillnest: no informados.
- Punto siguiente: pull de la rama U2.7, 15 tests, ejecución demo, revisión de stdout JSON y exit code; después B32/L1.
