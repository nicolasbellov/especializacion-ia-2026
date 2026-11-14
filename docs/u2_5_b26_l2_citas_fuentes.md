# U2.5 · Bloque 26 / Lección 2 — Por qué la respuesta debe citar su fuente

**Fuente oficial:** Skillnest, «Recuperación semántica y prompt dinámico con fuente citada (Bloque 26) / Por qué la respuesta debe citar su fuente», compartida el 14/11/2026. **Tipo: Ver.** No requiere API ni clave.

## 1. Concepto del curso

Aunque RAG recupere información pertinente, el modelo puede alucinar. La respuesta debe señalar el **chunk concreto** que respalda cada afirmación, usando referencias numeradas y un mapa que permita reconstruir la fuente original.

**Cadena lógica:**

1. **Dos documentos ficticios**: política de reintentos/autenticación y política de costos por tokens.
2. **Metadata por documento**: fuente=manual_cliente.md y fuente=manual_costos.md.
3. **Chunking**: RecursiveCharacterTextSplitter con tamaño **90** y solapamiento **10**. Las fuentes se propagan a todos los chunks.
4. **Formateo**: se asigna un número local [1], [2], ... a **cada chunk recibido**, no al documento global. El programa construye (a) un contexto numerado para el prompt y (b) un mapa de números a fuentes.
5. **Prompt**: obliga a responder **SOLO con el contexto** y citar cada afirmación; si no hay datos suficientes, declarar que no se puede responder.
6. **Validación de citas**: la respuesta puede mencionar [99] sin que exista esa referencia; usar búsquedas seguras y expresiones regulares en lugar de dar por válidos todos los números.

## 2. Resultado esperado exacto

El corpus oficial produce cuatro chunks a partir de dos documentos. El mismo documento de origen puede aparecer más de una vez.

| Chunk local | Comienzo del texto | Fuente heredada |
| --- | --- | --- |
| [1] | El cliente reintenta hasta 3 veces ante... | manual_cliente.md |
| [2] | errores de autenticacion nunca se reintentan... | manual_cliente.md |
| [3] | El costo de cada llamada se calcula... | manual_costos.md |
| [4] | por cada 1000 tokens. | manual_costos.md |

El mapa exacto es:

~~~python
{
    1: "manual_cliente.md",
    2: "manual_cliente.md",
    3: "manual_costos.md",
    4: "manual_costos.md",
}
~~~

Ejemplo oficial de respuesta: «El cliente reintenta hasta 3 veces [1].». La cita [1] remite a manual_cliente.md. En una respuesta múltiple, [99] debe marcarse **«Cita invalida / no encontrada»**, sin lanzar una excepción.

**Precisión importante:** el número [1] es **local al orden del contexto que construimos**; si los chunks se recuperan en otra secuencia, la fuente que recibe el número [1] puede ser distinta. La fuente no se infiere de la posición global en Chroma.

## 3. Ejecución desde GitHub

**Código:** [citas_demo.py](../citas_demo.py)  
**Pruebas:** [tests/test_citas_demo_b26.py](../tests/test_citas_demo_b26.py)

El código conserva exactamente el corpus, el tamaño/solapamiento, la función de contexto y el prompt oficiales. Añade una función **propia** para extraer y mapear múltiples citas y una validación previa de la cantidad de metadatos, con fines de diagnóstico.

~~~powershell
git status --short
git pull --ff-only
python -c "import langchain_text_splitters; print('OK')"
python citas_demo.py
python -m unittest discover -s tests -p "test_citas_demo_b26.py" -v
git status --short
~~~

Esta prueba es **100 % local**, sin Gemini, Chroma, red ni variables secretas. No reindexa ni modifica los cuatro índices persistentes usados en B24/B25/B26/L1. Las pruebas complementarias comprueban herencia de metadata, número de chunks, numeración, fuente ausente, [99] inválida y reglas del prompt.

## 4. Límites y buenas prácticas (ampliación técnica propia)

- **Cita existente no implica respaldo verdadero**: la presencia de [1] en el mapa demuestra que existe un chunk con ese número, pero no que su texto justifique la afirmación del modelo.
- **Fuente «desconocida»** evita una excepción si falta metadata, pero oculta un defecto de linaje: conviene detectar la ausencia en QA antes de usar el sistema para decisiones importantes.
- **No interpolar libremente documentos como instrucciones de sistema**. La documentación recuperada es contenido no confiable para el modelo: el prompt debe seguir las reglas del sistema y no obedecer instrucciones incrustadas en un chunk.
- **Trazabilidad y privacidad**: no publicar datos reales de pacientes/clientes ni credenciales; en un RAG productivo se necesitarían enlaces a versiones de documentos y permisos de consulta por usuario/tenant.
- Esta lección **no ejecuta ningún LLM** ni verifica una respuesta generada por uno; reconstruye citas sobre una **respuesta simulada** del curso.

## 5. Continuidad académica

**Lección oficial estudiada; ejecución local aún por corroborar**. Se conservan **7/15 lecciones** cerradas en U2.5 (B24 3/3, B25 3/3, B26/L1 1/3). El ejercicio y sus pruebas se versionan en la rama académica por preferencia expresa del estudiante; esto **no es entrega institucional**.

**Siguiente actividad anunciada:** Bloque 26/L3 «Desarrolla tu recuperación y tu prompt dinámico», que integrará recuperación y contexto citables sobre el corpus del estudiante. Los requisitos específicos se estudiarán cuando el usuario comparta su consigna.
