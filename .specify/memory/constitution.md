# Especialización en Desarrollo con IA Generativa — 2026 Constitution

Constitución técnica del repositorio `especializacion-ia-2026`, correspondiente a la
Especialización en Desarrollo con IA Generativa — 2026 de Skillnest, Accenture y CChIA (en
adelante, «Especialización IA 2026»). Rige los ejercicios académicos, las implementaciones
Python, la integración con Gemini y LangChain, las pruebas automatizadas, las evidencias
técnicas y el futuro proyecto integrador.

## Core Principles

### I. Fidelidad a los enunciados oficiales de Skillnest

- El enunciado, los criterios de aceptación y los entregables oficiales de Skillnest DEBEN ser
  la fuente primaria de requisitos de cada actividad. Ninguna especificación, plan o tarea
  puede contradecirlos.
- Toda especificación DEBE citar la actividad de origen (módulo, unidad, bloque, lección o
  identificador de actividad) y reproducir o enlazar sus criterios de aceptación.
- Las mejoras, generalizaciones o interpretaciones propias DEBEN marcarse como tales y NO DEBEN
  sustituir lo pedido. Si un ejemplo docente difiere de la implementación del repositorio, se
  documenta la diferencia en lugar de reemplazar el código sin pedirlo (ver DT-007).
- Ante ambigüedad del enunciado se DEBE registrar la duda y la interpretación adoptada; las
  ambigüedades que cambian el resultado evaluable se escalan al desarrollador.

**Razón:** la evaluación institucional se hace contra los criterios oficiales; una solución
técnicamente superior que no cumple el enunciado no aprueba.

### II. Spec-Driven Development proporcional

- El nivel de artefactos de Spec Kit DEBE ser proporcional a la complejidad y al riesgo de la
  actividad, según los niveles de la sección «Flujo de trabajo y puertas de calidad».
- Los ejercicios pequeños NO DEBEN generar `spec.md`, `plan.md` y `tasks.md` completos por
  defecto; basta el registro mínimo de su nivel.
- Las actividades evaluables con varios componentes, los Gates y el proyecto integrador DEBEN
  seguir el flujo completo (`/speckit-specify` → `/speckit-clarify` cuando haya ambigüedad →
  `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement`).
- Ningún documento se crea solo para cumplir con la forma: cada artefacto DEBE aportar
  requisitos, decisiones o evidencia que no estén ya registrados en otro lugar.

**Razón:** la especificación previa reduce retrabajo en entregas complejas, pero la burocracia
en ejercicios de minutos consume tiempo de estudio sin mejorar la calidad.

### III. Evidencia verificable antes de declarar completitud (NO NEGOCIABLE)

- Una actividad NO DEBE declararse «completada técnicamente» sin: (a) pruebas automatizadas que
  cubran sus criterios de aceptación, (b) ejecución local exitosa de esas pruebas y de las
  regresiones afectadas y (c) evidencia registrada (comando, resultado y conteo de pruebas).
- Las pruebas automatizadas DEBEN ser deterministas y ejecutarse sin red ni credenciales reales,
  usando `unittest.mock`/`pytest` para simular al proveedor. Las llamadas reales a Gemini son
  validaciones complementarias, se ejecutan solo de forma explícita y se registran por separado.
- La evidencia simulada NO DEBE presentarse como evidencia real (p. ej., un HTTP 429 de un mock
  no acredita un 429 de Gemini; ver DT-006).
- Se DEBEN distinguir los estados: *evidencia técnica verificada*, *completada en entorno
  local*, *entrega publicada* y *aprobación formal informada por Skillnest*. Ningún agente puede
  afirmar el último estado sin comprobante del desarrollador o de la plataforma.
- Un resultado fallido u omitido DEBE informarse tal cual, con su salida; no se reescriben
  pruebas para que pasen sin justificar el cambio del criterio.

**Razón:** la credibilidad de las entregas y del portafolio depende de que cada afirmación sea
reproducible.

### IV. Protección de credenciales, datos sensibles e información clínica (NO NEGOCIABLE)

- Las credenciales (p. ej., `GEMINI_API_KEY`) DEBEN residir solo en `.env` local o en secretos
  del entorno de ejecución. `.env` NO DEBE versionarse; `.env.example` contiene solo nombres de
  variables y valores ficticios.
- El repositorio es público: NO DEBEN incluirse en código, pruebas, prompts, registros, salidas
  JSON, capturas ni documentación claves, tokens, rutas internas institucionales, datos
  personales ni información clínica real.
- Las demostraciones, pruebas y conjuntos de evaluación DEBEN usar datos sintéticos,
  identificados como tales.
- En este repositorio académico, sus ejercicios, pruebas y evidencias NO DEBEN utilizarse datos
  clínicos reales, incluidos los anonimizados o seudonimizados. Esta prohibición se limita al
  ámbito académico del repositorio y no regula el tratamiento de datos en entornos
  profesionales privados que cuenten con autorización y controles de seguridad propios; esos
  datos tampoco DEBEN copiarse, referenciarse ni resumirse aquí.
- Antes de cada commit se DEBE revisar `git status`/`git diff` para confirmar que no se agregan
  secretos ni archivos de entorno. Si una credencial se expone, se DEBE revocar y rotar; borrarla
  del historial no basta.
- La CI DEBE operar con credenciales ficticias y pruebas offline.

**Razón:** una filtración de credenciales o de datos clínicos tiene consecuencias legales,
económicas y éticas que ninguna entrega académica justifica.

### V. Trazabilidad de extremo a extremo

- Cada requisito implementado DEBE poder rastrearse: criterio oficial → especificación o
  registro → código → prueba → evidencia de ejecución → commit.
- Las decisiones técnicas relevantes DEBEN registrarse en `docs/DECISIONES_TECNICAS.md` (formato
  DT-NNN: contexto, elección, razón, evidencia, límites y condición de revisión) o en un ADR
  enlazado desde ese índice (p. ej., ADR-001 en `docs/decision-arquitectura.md`). Se distingue lo *implementado y observado* de lo *propuesto*.
- El estado de avance DEBE mantenerse en `docs/ESTADO_ACADEMICO.md`, y las sesiones de estudio en
  `docs/BITACORA_ESTUDIO.md`, sin inferir tiempos efectivos desde Git o desde la duración de un
  chat.
- Los resultados de ejecución (JSON, CSV, registros) DEBEN conservarse con fecha, modelo,
  modo (`simulado` o `real`) y el script que los generó. Los costos son referenciales salvo que
  procedan de facturación real.
- Los commits DEBEN usar mensajes descriptivos con prefijo convencional y alcance de la unidad
  (p. ej., `feat(u2.3): …`, `test(u2.3): …`, `docs(u2.3): …`).

**Razón:** permite reanudar el trabajo, defender las decisiones ante evaluadores y reutilizar
componentes en el proyecto integrador.

### VI. Colaboración asistida por IA con control humano

- El desarrollador es la única autoridad de decisión sobre alcance, interpretación de
  enunciados, aceptación de entregas y publicación. Claude Code, ChatGPT y otros asistentes
  proponen, implementan y verifican dentro del alcance delegado.
- Los agentes NO DEBEN ejecutar `git commit`, `git push`, merges, reescritura de historial,
  publicación de entregas ni operaciones destructivas sin autorización explícita para ese
  alcance concreto.
- El contenido generado por cualquier asistente DEBE tratarse como propuesta: se valida con
  pruebas, ejecución local o lectura contra el enunciado antes de incorporarlo. Las afirmaciones
  sobre versiones de bibliotecas, modelos, tarifas o APIs DEBEN verificarse contra el entorno o
  la documentación vigente.
- Los artefactos de Spec Kit (`spec.md`, `plan.md`, `tasks.md`) y los documentos de `docs/` son
  el contexto compartido entre herramientas; el traspaso entre asistentes DEBE apoyarse en ellos
  y no en memoria conversacional no registrada.
- Un agente que no puede verificar algo DEBE declararlo como incertidumbre, sin presentarlo
  como hecho.

**Razón:** los asistentes aceleran el trabajo, pero la responsabilidad académica y el
aprendizaje son del desarrollador.

### VII. Compatibilidad y cambios mínimos

- Los ejercicios existentes, sus pruebas, sus evidencias y sus rutas de importación DEBEN seguir
  funcionando. Todo cambio DEBE ejecutar las suites afectadas y, como mínimo, la suite de la CI
  (`.github/workflows/pruebas-offline.yml`).
- NO DEBEN realizarse refactorizaciones, renombres, movimientos de archivos, actualizaciones de
  dependencias ni cambios de estilo no solicitados (ver DT-004). Las mejoras detectadas se
  registran como propuesta o deuda técnica.
- Las nuevas actividades DEBEN agregarse de forma incremental (nuevos módulos o archivos) sin
  reemplazar implementaciones de actividades anteriores ya entregadas.
- Las dependencias nuevas DEBEN fijarse en `requirements.txt` con versión verificada, sin
  regenerar el archivo completo; se DEBE confirmar `pip check` tras instalarlas.
- Las evidencias históricas (`resultados_*.json`, registros de `docs/`) NO DEBEN modificarse
  para ajustar resultados; las correcciones se registran como nueva entrada.

**Razón:** las entregas evaluadas deben seguir siendo reproducibles, y la base incremental debe
llegar estable al proyecto integrador.

## Restricciones técnicas y de seguridad

- **Lenguaje y entorno:** Python 3.12 (mínimo compatible 3.10), entorno virtual local (`venv/` o
  `.venv/`) excluido del control de versiones. Los comandos documentados se ejecutan desde la
  raíz del repositorio en Windows/PowerShell, y la CI en Ubuntu.
- **Proveedor de IA:** Google Gemini (modelo configurable mediante `GEMINI_MODEL`; referencia
  vigente en `docs/DECISIONES_TECNICAS.md`). La orquestación usa LangChain y
  `langchain-google-genai` en las versiones fijadas en `requirements.txt`.
- **Pruebas:** `unittest` y `pytest`. Convención vigente, que DEBE respetarse:
  - `tests/test_*.py`: suite principal (`python -m unittest discover -s tests -p "test_*.py"`,
    compatible también con `pytest`).
  - `test_*.py` y `pruebas_*.py` en la raíz: suites de bloques anteriores, se conservan en su
    ubicación.
  - `tests/manual/`: demostraciones manuales que no forman parte de la suite automática.
- **Costos y cuotas:** los scripts que consumen la API real DEBEN advertirlo, limitar el número
  de llamadas y no ejecutarse en la CI.
- **Seguridad de salidas:** las respuestas del modelo que alimentan lógica (JSON, clasificación,
  enrutamiento) DEBEN validarse contra esquema o reglas explícitas antes de usarse.
- **Datos:** solo datos sintéticos o públicos con licencia compatible, identificados en el
  código o la documentación.

## Flujo de trabajo y puertas de calidad

**Niveles de SDD proporcional:**

| Nivel | Aplica a | Artefactos mínimos |
| --- | --- | --- |
| 0 — Ejercicio | Lección o práctica breve, un archivo, sin decisión de diseño | Código + prueba + resultado registrado en `docs/ESTADO_ACADEMICO.md` o en la bitácora |
| 1 — Actividad | Actividad core o evaluable de un bloque, varios archivos o decisiones | Nivel 0 + registro de validación en `docs/` (criterios → evidencia) + DT si hay decisión relevante |
| 2 — Integración | Gate, entrega multiunidad, proyecto integrador o cambio transversal | Flujo Spec Kit completo en `specs/` con `spec.md`, `plan.md`, `tasks.md` y `/speckit-analyze` sin hallazgos CRITICAL |

El desarrollador puede elevar o bajar el nivel de una actividad indicando el motivo.

**Puertas de calidad (Definition of Done técnica):**

1. Los criterios de aceptación oficiales están identificados y mapeados a pruebas o evidencias.
2. Las pruebas nuevas y las regresiones afectadas se ejecutan localmente y pasan; se registra
   el comando y el conteo.
3. No hay secretos, datos reales ni archivos de entorno en el diff.
4. No hay cambios fuera de alcance en ejercicios existentes.
5. La documentación de estado, decisiones y evidencia está actualizada según el nivel.
6. El commit y el push quedan pendientes de la autorización explícita del desarrollador.

**Constitution Check en `/speckit-plan`:** cada plan DEBE verificar los principios I a VII y
justificar cualquier excepción en la sección «Complexity Tracking» del plan.

## Governance

- Esta constitución prevalece sobre prácticas informales del repositorio y guía la ejecución de
  los comandos de Spec Kit. No reemplaza las reglas de Skillnest, las políticas institucionales
  aplicables ni las instrucciones explícitas del desarrollador en una tarea concreta. Si hay
  conflicto, prevalece el enunciado oficial y se registra la discrepancia.
- **Términos normativos:** «DEBE»/«NO DEBE» equivalen a MUST/MUST NOT y «DEBERÍA» equivale a
  SHOULD (RFC 2119). Las violaciones de un «DEBE» son hallazgos CRITICAL en
  `/speckit-analyze` y `/speckit-converge`.
- **Enmiendas:** se proponen mediante `/speckit-constitution`, incluyen un Sync Impact Report y
  requieren la aprobación explícita del desarrollador antes del commit. Las enmiendas se
  versionan en Git con un mensaje `docs: amend constitution to vX.Y.Z (…)`.
- **Versionado semántico:** MAJOR para eliminar o redefinir principios de forma incompatible;
  MINOR para agregar principios o secciones, o para ampliar materialmente la guía; PATCH para
  aclaraciones y redacción.
- **Revisión de cumplimiento:** se verifica en cada plan (Constitution Check), antes de declarar
  completada una actividad y al cierre de cada unidad o Gate. Al iniciar el proyecto
  integrador, se DEBE revisar si los niveles de SDD y las restricciones técnicas siguen
  vigentes.

**Version**: 1.0.0 | **Ratified**: 2026-11-06 | **Last Amended**: 2026-11-06
