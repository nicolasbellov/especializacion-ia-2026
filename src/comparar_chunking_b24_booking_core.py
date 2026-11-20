"""Extensión B24/L2: comparar chunking sobre las FAQs FICTICIAS de Booking Core.

A diferencia de la lección oficial, esta extensión conserva metadatos de
fuente/sección de cada chunk. Comparación local SIN embeddings, sin Chroma y
sin conectarse a APIs de agenda.

Ejecutar:
    python -m src.comparar_chunking_b24_booking_core
"""

from __future__ import annotations

import argparse
from collections import Counter
from typing import Literal

from langchain_core.documents import Document
from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)

from src.rag_b24_booking_core import crear_documentos_demo

Estrategia = Literal["fijo", "recursivo"]


def dividir_documentos(
    documentos: list[Document],
    estrategia: Estrategia,
    chunk_size: int = 110,
    chunk_overlap: int = 20,
) -> list[Document]:
    """Dividir por secciones, manteniendo trazabilidad sin acceso a la agenda.

    Fijo no usa overlap (comparación de Skillnest).
    Recursivo usa overlap como objetivo máximo, no repetición garantizada.
    Se conserva el origen y se añade estrategia e índice interno por sección.
    """
    if chunk_size < 1:
        raise ValueError("chunk_size debe ser positivo")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap debe estar entre 0 y chunk_size - 1")

    if estrategia == "fijo":
        splitter = CharacterTextSplitter(
            separator="", chunk_size=chunk_size, chunk_overlap=0
        )
    elif estrategia == "recursivo":
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
    else:
        raise ValueError("Estrategia desconocida: usa 'fijo' o 'recursivo'")

    resultado: list[Document] = []
    for doc in documentos:
        for indice, fragmento in enumerate(splitter.split_text(doc.page_content)):
            resultado.append(
                Document(
                    page_content=fragmento,
                    metadata={
                        **doc.metadata,
                        "estrategia": estrategia,
                        "indice_chunk": indice,
                    },
                )
            )
    return resultado


def resumir_fragmentos(documentos: list[Document]) -> dict[str, int]:
    """Cantidad de chunks por sección, sin scores ni conclusiones de calidad."""
    return dict(Counter(d.metadata["seccion"] for d in documentos))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Comparación local de chunking — Booking Core AI ficticio"
    )
    parser.add_argument("--chunk-size", type=int, default=110)
    parser.add_argument("--overlap", type=int, default=20)
    args = parser.parse_args()

    originales = crear_documentos_demo()
    print("Corpus:", len(originales), "secciones ficticias")
    print("Índice Chroma existente: NO modificado")

    for estrategia in ("fijo", "recursivo"):
        fragmentos = dividir_documentos(
            originales,
            estrategia,
            chunk_size=args.chunk_size,
            chunk_overlap=args.overlap,
        )
        print(f"\n=== {estrategia.upper()} ===")
        print("Total de chunks:", len(fragmentos))
        print("Chunks por sección:", resumir_fragmentos(fragmentos))
        print("Longitudes:", [len(d.page_content) for d in fragmentos])
        for doc in fragmentos[:3]:
            print(
                f"  [{doc.metadata['seccion']} #{doc.metadata['indice_chunk']}]"
                f" {len(doc.page_content)} caracteres:"
            )
            print(" ", repr(doc.page_content[:120]))
    print(
        "\nNota: el número y tamaño de chunks NO determinan por sí solos "
        "la precisión del retrieval. La evaluaremos en el Bloque 27."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
