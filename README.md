# Especialización IA 2026 — Booking Core AI | Gate 2

**Entrega académica U2.8, Módulo 2.** Véase [portada de Gate 2 y rúbrica](docs/U2_8_GATE2_CORE_ENTREGA.md). El sistema integra un servicio RAG de políticas de barbería ficticias; no accede a Booking Core real. Estado: instalación limpia y cuatro criterios validados en Windows, corrida Gemini real y supervisión PASS; abstención ante precios y disponibilidad reales PASS; evidencia completa en la portada. Gate 2 entregado en Skillnest el 26/11/2026; calificación institucional pendiente.

## Reproducir el servicio de Gate 2 (Windows PowerShell)

~~~powershell
git clone --branch feature/u2-8-gate2-rag-booking-core-ai https://github.com/nicolasbellov/especializacion-ia-2026.git
cd especializacion-ia-2026
py -3.12 -m venv .venv-gate2
$py = '.\.venv-gate2\Scripts\python.exe'
& $py -m pip install -r requirements.txt
& $py -m pip check
& $py verificar_entorno.py --modo simulado --permitir-indice-nuevo
& $py -m pytest test_gate2.py -v
& $py -m unittest discover -s tests -p 'test_gate2_incremental.py' -v
& $py ensayo_gate2.py
& $py servicio_rag.py --modo simulado
& $py servicio_rag.py --modo simulado
~~~

Python 3.12 es la versión de referencia; en Linux/macOS crear venv con python3 y usar .venv-gate2/bin/python. La primera corrida simulada crea un índice Chroma separado en .local/gate2_simulado; siguientes corridas lo reutilizan. Los embeddings y el LLM de ese modo son sintéticos. No requiere Gemini ni llamadas de red para las pruebas (instalar paquetes sí requiere acceso a paquetes).

### Real Gemini (opt-in)

Crear .env a partir de .env.example y definir GEMINI_API_KEY y GEMINI_MODEL localmente, sin publicar la clave. El script utiliza la misma colección académica B24 y modelo de embeddings. La primera corrida en un clon limpio indexa cinco documentos, consume cuota; siguientes corridas reutilizan el índice. No copia ni sube vectorstore/.

~~~powershell
git check-ignore .env
& $py verificar_entorno.py --modo real --permitir-indice-nuevo
& $py servicio_rag.py --modo real --supervision interactiva --pregunta '¿Qué requisitos ficticios se deben cumplir para reprogramar una cita?'
$LASTEXITCODE
~~~

El flujo imprime auditoría JSON de aplicación y después respuesta, fuentes, consumo y latencia. La consola solicita s/n para una cancelación **solo ficticia**. Las decisiones automatizadas de demo no son una aprobación humana. No introduzca información real de clientes. Un resultado retenido por falta de citas o contexto devuelve 2; un error controlado devuelve 1. Una ejecución normal con respuesta citada devuelve 0.

### Cambios del corpus

El servicio no reindexa en cada consulta. Ante cambios, usar --actualizar de forma explícita. El test incremental crea y modifica su propio índice temporal sin tocar el índice original. Si se actualiza vectorstore/ real, primero respaldarlo con procesos cerrados. Una actualización parcial deja bloqueo y requiere restauración de respaldo.

### Evidencia y gobernanza

- [Autochequeo 4 criterios](test_gate2.py), [ensayo funcional](ensayo_gate2.py), [actualización incremental](tests/test_gate2_incremental.py).
- [Métricas reales B27](resultados_evaluacion.txt), [mediciones reales B28](registros_latencia_costo.jsonl), [decisión de personalización](decision_personalizacion.md).
- [Matriz de riesgos Gate 2](data/matriz_riesgos_gate2.json), [registro prompt activo](prompts/booking_core_ai/registro_gate2.json), [supervisión](gate2/supervision.py), [autoevaluación](rubrica_gate2.py).
- No registrar PII ni textos crudos en logs de aplicación; no publicar .env ni bases vectoriales. Los costos se estiman con tarifas ficticias B28 y se etiquetan, no son facturación.

---

## Historial del Módulo 1 — Gate 1

## Miniaplicación Gate 1 — Módulo 1

Proyecto académico desarrollado para la Especialización en Desarrollo con IA Generativa de Skillnest, Accenture y CChIA.

### 1. Objetivo

Implementar una miniaplicación Python que consuma un modelo de inteligencia artificial generativa mediante una API REST.

La aplicación permite:

- Construir solicitudes HTTP para Gemini.
- Autenticarse mediante una API key almacenada fuera del repositorio.
- Enviar preguntas y recibir respuestas del modelo.
- Incorporar instrucciones de sistema y esquemas JSON.
- Extraer y validar respuestas estructuradas.
- Gestionar errores HTTP, conexión, tiempo de espera y JSON.
- Ejecutar pruebas automatizadas.

### 2. Tecnologías

- Python 3.12.8 (versión utilizada durante el desarrollo).
- Google Gemini API.
- requests.
- python-dotenv.
- Git y GitHub.
- unittest.

Modelo utilizado y validado:
`gemini-3.5-flash-lite`

El modelo puede cambiarse mediante la variable `GEMINI_MODEL`.

### 3. Estructura del proyecto

- `src/consumir_gemini.py`: cliente REST principal.
- `src/comparar_modelos_u14.py`: comparación de modelos.
- `src/reanudar_comparacion_u14.py`: recuperación de mediciones.
- `prompts/`: banco de prompts y validaciones U1.5.
- `tests/`: pruebas automatizadas y ejercicios.
- `docs/`: arquitectura, evidencias y mediciones.
- `requirements.txt`: dependencias fijadas.
- `.env.example`: ejemplo de configuración.
- `.gitignore`: exclusiones de seguridad.
- `modulos/`: organización del programa académico.

### 4. Instalación

Clonar el repositorio:

```powershell
git clone https://github.com/nicolasbellov/especializacion-ia-2026.git
cd especializacion-ia-2026
```

Crear el entorno virtual:

```powershell
py -3.12 -m venv venv
```

Si no está disponible el lanzador de Python 3.12, utilizar una instalación compatible de Python 3.10 o superior.

Instalar dependencias:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Comprobar su consistencia:

```powershell
.\venv\Scripts\python.exe -m pip check
```

No es obligatorio activar el entorno virtual en PowerShell. Los comandos utilizan directamente su intérprete Python.

### 5. Configuración

Crear el archivo local:

```powershell
Copy-Item .env.example .env
```

Editar `.env` e incorporar una credencial real:

```dotenv
GEMINI_API_KEY=tu_clave_real
GEMINI_MODEL=gemini-3.5-flash-lite
```

La credencial debe obtenerse mediante el proveedor de la API.

**Seguridad:** nunca subir `.env` ni compartir claves reales. El archivo se encuentra excluido mediante `.gitignore`.

### 6. Ejecución principal

Desde la raíz del proyecto:

```powershell
.\venv\Scripts\python.exe -m src.consumir_gemini
```

Si la conexión funciona, la aplicación muestra un texto generado por Gemini.

Ejemplo de una ejecución validada durante el desarrollo:

```text
Resultado: ¡Conexión establecida y funcionando perfectamente!
```

Para comprobar el código de salida en PowerShell:

```powershell
$LASTEXITCODE
```

El valor esperado es `0` cuando finaliza correctamente.

Ante errores controlados, el programa muestra un mensaje y termina con código `1`.

### 7. Pruebas automatizadas

Ejecutar:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

Resultado verificado en el entorno de desarrollo:

```text
Ran 19 tests

OK
```

Las pruebas cubren extracción de respuestas, errores de conexión, autenticación simulada, timeouts, estructura de peticiones y validación JSON.

Estas pruebas utilizan simulaciones para verificar el cliente sin necesitar llamadas reales al proveedor.

### 8. Respuestas JSON estructuradas

El cliente permite configurar instrucciones de sistema y un esquema de respuesta mediante:

```python
armar_peticion(
    pregunta,
    system_instruction,
    response_schema
)
```

Posteriormente, la salida puede procesarse con:

```python
parsear_respuesta_json(texto, response_schema)
```

Ejemplo de respuesta validada durante U1.5:

```json
{
  "intencion": "crear",
  "confianza": 0.99
}
```

La validación básica verifica claves obligatorias, tipos de datos y restricciones definidas en el esquema.

### 9. Manejo de errores

La aplicación contempla:

- Preguntas vacías o inválidas.
- Errores de autenticación HTTP 401/403.
- Solicitudes rechazadas HTTP 400.
- Límites de cuota HTTP 429.
- Respuestas HTTP no exitosas, incluido 503.
- Fallos de conexión y timeout.
- Respuestas sin JSON válido.
- Estructuras de respuesta inesperadas.

Los errores se comunican mediante excepciones y mensajes controlados.

### 10. Comparación de modelos — U1.4

Los scripts de U1.4 permiten registrar latencia, consumo de tokens, respuestas y costos estimados.

Las mediciones se almacenan en:

`docs/mediciones_modelos_u14.csv`

Las tarifas utilizadas son referencias del ejercicio y deben comprobarse nuevamente antes de utilizarlas para estimaciones actuales.

Estos scripts son complementarios y no forman parte de la ejecución principal del Gate 1.

**Nota:** ejecutarlos genera nuevas solicitudes reales a la API y podría consumir cuota o generar cargos.

### 11. Documentación de arquitectura

El directorio `docs/` contiene las decisiones de arquitectura, los diagramas y las evidencias técnicas generadas durante el Módulo 1.

La documentación se conserva para evolucionar la aplicación durante los módulos siguientes.

### 12. Estado del proyecto

- Cliente REST implementado.
- Manejo básico de errores implementado.
- Pruebas automatizadas: 19/19 aprobadas.
- Conexión real con Gemini verificada.
- Respuesta JSON estructurada verificada.
- Ensayo de instalación limpia: completado satisfactoriamente desde GitHub, con 19/19 pruebas aprobadas. Evidencia en docs/registro_ensayo_gate1.md.
- Gate 1: pendiente de evaluación formal.

## Evolución del programa

- Módulo 1: fundamentos técnicos y consumo de API.
- Módulo 2: orquestación, agentes y RAG.
- Módulo 3: integración, despliegue y validación end-to-end.

El repositorio constituye una base incremental para los siguientes módulos de la especialización.

## Evidencia del Gate 1

Se realizó un ensayo de instalación limpia
clonando el repositorio directamente desde GitHub.

Resultados:
- 19/19 pruebas automatizadas aprobadas.
- Instalación de dependencias sin conflictos.
- Consumo exitoso de la API Gemini.
- Código de salida 0.
- Exclusión de credenciales locales verificada.

Consultar el [registro completo del ensayo](docs/registro_ensayo_gate1.md).

## Proyecto integrador en evolución: Booking Core AI (agenda de barbería)

**Objetivo final:** conectar un agente conversacional con la agenda real de **Booking Core**, con **AES Barber** como piloto, para consultar servicios y disponibilidad, y preparar solicitudes de reservas, cambios o cancelaciones mediante el backend autorizado.

- **Repositorio académico (este):** Gemini, prompts, herramientas, memoria, supervisión, trazas y RAG.
- **Aplicación de agenda (repositorio separado `nicolasbellov/booking-core`):** fuente transaccional de servicios, profesionales, clientes y citas.
- **U2.4:** herramientas y reservas **simuladas**, sin conexión a la agenda real.
- **U2.5/Bloque 24/L1:** [primer laboratorio RAG para documentación ficticia](docs/u2_5_b24_rag_booking_core.md), con embeddings Gemini y Chroma local. No conecta ni modifica Booking Core.
- **U2.5/Bloque 24/L2:** [comparación de chunking fijo y recursivo](docs/u2_5_b24_chunking_comparativo.md), validada en Windows.
- **U2.5/Bloque 24/L3 (actividad práctica completada técnicamente):** [indexación de cinco documentos propios y persistencia Chroma](docs/u2_5_b24_l3_indexacion_booking_core.md), scripts `indexar_corpus.py` y `verificar_vectorstore_b24.py`. En Windows se generaron **10 chunks con Gemini real**, se verificaron desde un proceso independiente y la segunda ejecución evitó volver a calcular embeddings. La suite L3 cerró con **9/9 pruebas Windows**, y el índice `vectorstore/` sigue excluido de Git. **Bloque 24: 3/3; U2.5: 3/15 lecciones completadas técnicamente**. Siguiente: B25/L1.
- **U2.5/Bloque 25/L1 (completada técnicamente):** [receta reutilizable de indexación y persistencia](docs/u2_5_b25_receta_indexacion.md) en `src/receta_indexacion_b25.py`, reproducida con **3 textos del curso → 3 chunks reales Gemini** en `.local/chroma_b25_receta/`. **7/7 pruebas Windows aprobadas**, recarga de 3 chunks desde otro proceso y reejecución sin re-embedding. El índice se mantiene aislado de `vectorstore/` y `.local/chroma_b24/`. **U2.5: 4/15 lecciones completadas técnicamente**; siguiente B25/L2 (troubleshooting).
- **U2.5/Bloque 25/L2 (guía estudiada):** [troubleshooting oficial de vector stores y extensión segura](docs/u2_5_b25_troubleshooting_vectorstores.md). Diagnóstico read-only en `src/diagnosticar_chroma_b25.py` y pruebas de errores 429, consistencia y permisos en `tests/test_troubleshooting_b25.py`. No requiere nueva indexación Gemini ni altera los índices existentes. **U2.5: 5/15 lecciones; Bloque 25: 2/3**, con siguiente actividad B25/L3 pendiente de su consigna.
- **U2.5/Bloque 25/L3 (completada técnicamente en Windows):** [script de tienda ficticia](replica_ejemplo.py) y [guía B25/L3](docs/u2_5_b25_l3_replica_corpus_ejemplo.md). Corpus oficial de **5 textos/490 caracteres**, chunking **150/20**, **8/8 pruebas Windows OK**, **5 chunks indexados con Gemini real** en `.local/chroma_b25_tienda_ejemplo/`; recarga independiente y repetición **sin re-embedding**. El curso no exige commit/entrega; se versionó solo el código a petición del estudiante. **B25 3/3; U2.5 6/15**, siguiente Bloque 26 (búsqueda semántica).
- **U2.5/Bloque 26/L1 (completada técnicamente en Windows):** [recuperación semántica, distancias y Retriever](docs/u2_5_b26_l1_recuperacion_semantica.md), código `src/recuperacion_semantica_b26.py` y `tests/test_recuperacion_semantica_b26.py`. Demo offline con `DeterministicFakeEmbedding(size=16)` reprodujo el ranking del curso; **9/9 tests Windows OK**. Búsqueda real Gemini (solo embedding de pregunta) en el índice B25/L1 existente → **TimeoutError 1.º (distancia 0.5494)**, mocks 2.º (0.7277), costos 3.º (0.7557). Sin reindexar ni alterar corpus persistidos. **U2.5: 7/15; siguiente B26/L2 (citas de fuentes).**
- **U2.5/Bloque 26/L2 (lección «Ver» completada; sin Gemini):** [citas y fuentes](docs/u2_5_b26_l2_citas_fuentes.md) con `citas_demo.py` y `tests/test_citas_demo_b26.py`. Dos documentos oficiales con metadata → **4 chunks** (splitter **90/10**) y mapa **[1]/[2] manual_cliente.md; [3]/[4] manual_costos.md**. Prompt restringido al contexto y manejo de cita inexistente **[99]**. **11/11 tests CI y 11/11 tests Windows PASS** (`1.651s`); ejecución local del mapa y prompt verificada, sin API. **U2.5 8/15; Bloque 26 2/3**. Siguiente B26/L3, recuperación y prompt dinámico sobre corpus propio.
- **U2.5/Bloque 26/L3 (validada técnicamente con Gemini real en Windows):** [recuperación + prompt dinámico con citas](docs/u2_5_b26_l3_recuperacion_prompt.md), [código](recuperacion.py) y [14 tests](tests/test_recuperacion_b26_l3.py). Reutiliza **SIN BORRAR NI REINDEXAR** `vectorstore/` de B24/L3 (**5 documentos, 10 chunks Gemini, metadata e IDs propios**). **12/12 tests Windows**, dos preguntas con **contextos diferentes** (`True`), respuesta Gemini **se abstuvo** de inventar el precio real de AES Barber y respuesta de reprogramación con cita `[1]` **contrastada** en `03_reprogramacion.md`. El bug de citas agrupadas `[1, 3]` se corrigió en `citas_demo.py` y se verificó en [CI #43557790465](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/43557790465) (**13/13 B26/L2 y 14/14 B26/L3**). **B26 3/3, U2.5 9/15**; entrega institucional en Skillnest pendiente de confirmación.
- **U2.5/Bloque 27/L1 («Ver» completada; precisión, recall y F1):** [ejemplo oficial de métricas](metricas_recuperacion.py), [15 pruebas offline](tests/test_metricas_recuperacion_b27.py) y [apunte](docs/u2_5_b27_l1_metricas_recuperacion.md). Sobre cinco documentos **ficticios del curso**, `doc0` es el único relevante: **precision@3 = 0.3333, recall@3 = 1.0 y F1@3 = 0.500**, máximo del ranking fijo en k=3. [CI #44136512566](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/44136512566) PASS **y 15/15 tests Windows OK** (`0.121s`); script reprodujo la tabla oficial, Git quedó limpio, sin Chroma ni API. **NO son métricas medidas del retriever de Booking Core**, cuyo conjunto etiquetado sigue pendiente. **B27 1/3; U2.5 10/15**. Siguiente B27/L2: evaluación con preguntas etiquetadas.
- **U2.5/Bloque 27/L2 («Ver» completada: evaluación de varias preguntas):** [script oficial](evaluacion_rag.py), [18 tests offline](tests/test_evaluacion_rag_b27.py) y [guía](docs/u2_5_b27_l2_evaluacion_conjunto.md). Dataset didáctico de **4 preguntas**, con etiquetas `doc0..doc3` y recuperaciones **simuladas** del curso: **precisión promedio=0.25, recall promedio=0.75**; clave API inválida falla con P=R=0. Casos borde: P=0.0 sin recuperados y R=`None` sin relevantes (promedio ignora `None`). **[CI #44407807479](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/44407807479) PASS y 18/18 tests Windows OK** (`0.168s`); script local reprodujo resultados oficiales, Git limpio al término, sin Gemini ni indexación. Estos resultados **NO miden** el retriever real de Booking Core. **B27 2/3; U2.5 11/15**, siguiente B27/L3 sobre conjunto etiquetado del índice propio.
- **U2.5/Bloque 27/L3 (actividad real preparada, métricas Gemini pendientes):** [evaluacion_recuperacion.py](evaluacion_recuperacion.py), [12 preguntas etiquetadas ANTES del retrieval](data/etiquetas_b27_l3_booking_core.json), [18 tests offline](tests/test_evaluacion_recuperacion_b27_l3.py) y [guía de entrega](docs/u2_5_b27_l3_evaluacion_real.md). Cinco fuentes ficticias, **10 chunks con IDs SHA-256 originales** y chunking **550/80**; diez preguntas con fragmentos relevantes y dos sin respuesta factual. El evaluador verifica inventario/huella sin API, compara k=3 y k=5 con **dos corridas reales por configuración** (Gemini solo embeddings de pregunta) y guarda registros sin sobrescribir. **18/18 tests CI PASS** en [#44411526152](https://github.com/nicolasbellov/especializacion-ia-2026/actions/runs/44411526152), **NO** son resultados de recuperación real. Pendiente Windows, `resultados_evaluacion.txt` real y entrega Skillnest. **B27 continúa 2/3, U2.5 11/15**; no reindexar ni subir `.env`/`vectorstore/`.
- **Regla arquitectónica:** RAG para documentación relativamente estable y fuentes citables; las horas disponibles y las operaciones sobre citas requieren APIs autenticadas, control de tenant y validación del backend. No usar la base vectorial como autoridad de disponibilidad.
- **Seguridad:** jamás colocar claves, datos clínicos/personales, historiales reales de reservas o índices vectoriales locales en este repositorio público.

**Importante:** la integración productiva con Booking Core sigue pendiente. Las demostraciones existentes no constituyen reservas reales ni pruebas de autorización multi-tenant.
