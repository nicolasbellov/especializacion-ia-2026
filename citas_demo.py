"""U2.5/B26/L2: contexto numerado, trazabilidad y citas (Skillnest).

Ejecutar desde la raíz del repositorio con .venv activo:
    python citas_demo.py

Este ejercicio es 100 % offline: NO usa Gemini, Chroma, claves API ni índices.
El corpus es el ejemplo ficticio OFICIAL, no datos reales de clientes.
"""

from __future__ import annotations

import re
from typing import Iterable

from langchain_core.documents import Document

# Fuente oficial B26/L2: exactamente dos documentos con una metadata cada uno.
CORPUS = [
    "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente. "
    "Los errores de autenticacion nunca se reintentan: fallan de inmediato con un "
    "ValueError.",
    "El costo de cada llamada se calcula a partir de totalTokenCount y la tarifa "
    "vigente por cada 1000 tokens.",
]
METADATAS = [
    {"fuente": "manual_cliente.md"},
    {"fuente": "manual_costos.md"},
]
CHUNK_SIZE = 90
CHUNK_OVERLAP = 10

# Texto de instrucciones extraído de la lección (no invoca a un modelo).
PROMPT_TEMPLATE = """Responde la pregunta usando SOLO el contexto de abajo. Cita la \
fuente de cada afirmacion con su numero entre corchetes, como [1]. Si el contexto no \
alcanza para responder, dilo explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""

PREGUNTA_DEMO = "Que hace el cliente si hay un TimeoutError?"
RESPUESTA_DEMO = "El cliente reintenta hasta 3 veces [1]."
RESPUESTA_CITAS_MULTIPLES = (
    "El cliente reintenta 3 veces [1], pero falla en autenticacion [2]. "
    "El costo usa tokens [3] y [99]."
)
CITA_INVALIDA = "Cita invalida / no encontrada"


def crear_chunks(
    corpus: list[str] | None = None,
    metadatas: list[dict[str, str]] | None = None,
) -> list[Document]:
    """El splitter copia la metadata de cada documento a todos sus chunks."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    textos = CORPUS if corpus is None else corpus
    fuentes = METADATAS if metadatas is None else metadatas
    if len(textos) != len(fuentes):
        raise ValueError("Debe existir una metadata por cada documento original.")
    if not textos or any(not isinstance(t, str) or not t.strip() for t in textos):
        raise ValueError("El corpus requiere textos no vacíos.")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.create_documents(textos, metadatas=fuentes)


def formatear_contexto(chunks_recuperados: Iterable[Document]) -> tuple[str, dict[int, str]]:
    """Replica oficial: texto [n] para el prompt y mapa n -> metadata.fuente."""
    lineas: list[str] = []
    citas: dict[int, str] = {}
    for i, doc in enumerate(chunks_recuperados, start=1):
        fuente = doc.metadata.get("fuente", "desconocida")
        lineas.append(f"[{i}] {doc.page_content}")
        citas[i] = fuente
    contexto = "\n\n".join(lineas)
    return contexto, citas


def construir_prompt(contexto: str, pregunta: str) -> str:
    """Genera instrucciones; no llama al modelo ni valida veracidad."""
    if not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")
    return PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta.strip())


def mapear_citas(respuesta: str, citas: dict[int, str]) -> list[tuple[int, str]]:
    """Extensión propia: extrae [n] y comprueba que n exista en el mapa.

    Una cita existente demuestra trazabilidad del número, NO que la afirmación
    esté realmente respaldada por el texto; el chequeo semántico es posterior.
    """
    # Un LLM puede agrupar varias referencias en un mismo corchete: [1, 3].
    # Extraer cada número conservando su orden y también las repeticiones.
    grupos = re.findall(r"\[\s*(\d+(?:\s*,\s*\d+)*)\s*\]", respuesta)
    indices = [int(numero.strip()) for grupo in grupos for numero in grupo.split(",")]
    return [(indice, citas.get(indice, CITA_INVALIDA)) for indice in indices]


def main() -> int:
    chunks = crear_chunks()
    print("--- Chunks y su fuente ---")
    for c in chunks:
        print(repr(c.page_content[:40]), "->", c.metadata)

    contexto, citas = formatear_contexto(chunks)
    print("\n--- Contexto numerado ---")
    print(contexto)
    print("\n--- Mapa de citas ---")
    print(citas)

    prompt = construir_prompt(contexto, PREGUNTA_DEMO)
    print("\n--- Prompt final ---")
    print(prompt)

    print("\n--- Cita reconstruida ---")
    print("La cita [1] corresponde a:", citas.get(1, CITA_INVALIDA))

    print("\n--- Citas múltiples e inválidas (extensión propia) ---")
    for indice, fuente in mapear_citas(RESPUESTA_CITAS_MULTIPLES, citas):
        print(f"Cita [{indice}]: {fuente}")

    print("\nModo local: sin Gemini, Chroma ni solicitud de API.")
    print("Nota: las citas son referencias de chunks, no verificaciones automáticas de verdad.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
