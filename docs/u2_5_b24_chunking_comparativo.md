# U2.5 · Bloque 24 · Lección 2 — Dos estrategias de chunking comparadas en vivo

**Programa:** Skillnest / Accenture / CChIA · Especialización IA 2026  
**Fecha:** 13/11/2026 (Chile)  
**Fuente principal:** texto completo de la lección B24/L2 compartido por el estudiante.  
**Estado:** material oficial recibido y reproducido en código; **prueba local en Windows pendiente de registrar**. La lección no exige API ni tokens.

## 1. Lo que enseña la lección oficial

Se compara `CharacterTextSplitter` con `separator=""`, `chunk_size=110`, `chunk_overlap=0` frente a `RecursiveCharacterTextSplitter` con `chunk_size=110`, `chunk_overlap=20`. Ambos procesan exactamente la misma cadena `texto` sobre tres párrafos: reintentos ante `TimeoutError`, errores de autenticación y costo acumulado.

| Control del ejemplo oficial | Chunking fijo | Chunking recursivo |
| --- | --- | --- |
| Total de chunks | 3 | 3 |
| Longitudes esperadas | 110, 110, 93 | 102, 108, 99 |
| Frontera de palabra | Divide `Los errores` en `Los er` y `rores` | Respeta los tres párrafos |
| Efecto del overlap del ejemplo | 0 | No se repiten caracteres entre párrafos completos |
| Intención del diseño | Corte predecible por caracteres | Priorizar delimitadores del contenido |

**Matiz complementario:** por defecto los separadores recursivos son `["\\n\\n", "\\n", " ", ""]`. No incluyen un separador explícito por oración como `". "`: preserva párrafos/líneas/palabras cuando es posible, pero no segmenta oraciones gramaticalmente de manera garantizada. `chunk_overlap` es un **objetivo/límite de configuración**, no una promesa de 20 caracteres exactos en cada fragmento.

No existe un `chunk_size` universal. El curso recomienda empezar con pocos cientos de caracteres y alrededor de 15–20 % de `overlap`, luego ajustar según recuperación observada en Bloque 27.

## 2. Reproducción de la lección oficial, sin Gemini

Archivo [`test_chunking.py`](../test_chunking.py): contiene **el script completo y continuo** (mismo `texto` y dos estrategias), con encabezados adicionales y resumen de longitudes. Se ejecuta desde la raíz del repositorio:

```powershell
python -c "import langchain_text_splitters; print('OK')"
python test_chunking.py
```

Esperamos el mismo resultado de longitudes indicado por Skillnest. Si aparece un desajuste, contrastar la versión real del paquete y las salidas de consola; no falsear resultados. Si el import falla, en el entorno virtual instalar dependencias del proyecto con `python -m pip install -r requirements-rag.txt`.

El chunking sucede enteramente **en memoria**: ninguna operación genera embeddings, usa `.env`, indexa Chroma o consulta la agenda.

## 3. Extensión propia: Booking Core AI y sus cinco secciones

Archivo [`src/comparar_chunking_b24_booking_core.py`](../src/comparar_chunking_b24_booking_core.py):

- Carga el corpus académico `data/rag_demo_booking_core.md` con `crear_documentos_demo()` de B24/L1.
- Mantiene cada sección `##` aislada; ninguna estrategia mezcla contenidos de secciones diferentes.
- Compara ambos splitters **con el mismo `chunk_size=110`**, overlap fijo 0 y overlap recursivo 20.
- Agrega los metadatos `fuente`, `seccion`, `origen=FICTICIO_ACADEMICO`, `estrategia` e `indice_chunk`.
- Imprime cantidad, longitudes y muestra de fragmentos; **no clasifica calidad ni obtiene puntajes semánticos**.

```powershell
python -m src.comparar_chunking_b24_booking_core
```

El corpus de B24/L1 sigue indexado en `.local/chroma_b24` usando un chunk por sección. **No alteramos ni reindexamos esa base**: esto es una comparación previa a seleccionar una estrategia para la actividad de indexación posterior.

**Importante para el proyecto integrador:** un vector store no debe conservar disponibilidad horaria actual como si fuera fuente transaccional. La intención es emplear RAG para respuestas documentales y APIs autenticadas de Booking Core para servicios/citas actuales, con aislamiento por tenant y controles de autorización.

## 4. Validaciones automáticas

```powershell
python -m unittest discover -s tests -p "test_chunking_b24_booking_core.py" -v
```

Cobertura: reproducción exacta del ejemplo oficial; longitud de fragmentos; conservación de fuente y sección; separación de palabras del fijo; respeto de párrafos cortos por el recursivo; validación del overlap; no mutación del corpus. El workflow `.github/workflows/pruebas-offline.yml` también incluye B24/L2.

**Estado de pruebas:** consultar GitHub Actions para el commit de la rama; no registrar como aprobadas en Windows hasta recibir la consola local.

## 5. Interpretación y preguntas de repaso

1. ¿Por qué dos estrategias con `chunk_size=110` pueden producir fragmentos diferentes?
2. ¿Qué información se pierde si un texto de políticas de cancelación queda dividido a mitad de oración?
3. ¿Por qué el valor `chunk_overlap=20` no necesariamente produce 20 caracteres repetidos en el ejemplo?
4. ¿Qué preferirías para FAQs de barbería: corte por longitud fija o por párrafos? Justifica a partir de los casos y sin afirmar que ya medimos precisión del RAG.

## 6. Próximo paso exacto

1. En Windows: verificar `git status --short` y, si está limpio, ejecutar `git pull --ff-only` en `feature/u2-5-b24-rag-booking-core`.
2. Ejecutar `python -c "import langchain_text_splitters; print('OK')"`, `python test_chunking.py`, `python -m src.comparar_chunking_b24_booking_core` y los tests B24/L2; compartir salidas.
3. Registrar evidencia y cerrar técnicamente L2 **solo si se reprodujo la práctica**.
4. Continuar a Bloque 24/L3: indexar corpus de ejemplo con embeddings reales y persistencia, manteniendo el índice anterior intacto hasta decidir la estrategia.
