"""U2.5 / Bloque 24 / Lección 2 — ejemplo oficial Skillnest (continuo).

Comparación local de chunking fijo vs. recursivo. No consume tokens,
no necesita GEMINI_API_KEY, no abre Chroma ni modifica reservas.

Desde la raíz del repositorio:
    python test_chunking.py
"""

from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter

# 1. Texto de prueba proporcionado en la lección oficial.
texto = (
    "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente "
    "entre intento e intento.\n\n"
    "Los errores de autenticacion nunca se reintentan: fallan de inmediato con un "
    "ValueError, sin ninguna espera.\n\n"
    "El costo de cada llamada se acumula en una variable de sesion mientras el "
    "programa sigue corriendo."
)

# 2. Estrategia fija: corta por caracteres, sin conservar límites semánticos.
splitter_fijo = CharacterTextSplitter(
    separator="", chunk_size=110, chunk_overlap=0
)
chunks_fijo = splitter_fijo.split_text(texto)

print("=== ESTRATEGIA 1: TAMANO FIJO ===")
for i, chunk in enumerate(chunks_fijo):
    print(f"--- chunk {i} ({len(chunk)} caracteres) ---")
    print(chunk)

# 3. Estrategia recursiva: prioriza separadores naturales.
splitter_recursivo = RecursiveCharacterTextSplitter(
    chunk_size=110, chunk_overlap=20,
)
chunks_recursivo = splitter_recursivo.split_text(texto)

print("\n=== ESTRATEGIA 2: RECURSIVA ===")
for i, chunk in enumerate(chunks_recursivo):
    print(f"--- chunk {i} ({len(chunk)} caracteres) ---")
    print(chunk)

# 4. Resumen comparativo de las mismas variables definidas arriba.
print("\n=== COMPARACION ===")
print("Fijo:", len(chunks_fijo), "chunks; longitudes:", [len(c) for c in chunks_fijo])
print(
    "Recursivo:", len(chunks_recursivo),
    "chunks; longitudes:", [len(c) for c in chunks_recursivo]
)
