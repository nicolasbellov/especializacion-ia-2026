"""Verificación independiente de persistencia Chroma para Skillnest B24/L3.

NO importa Gemini, NO genera embeddings y NO recalcula el corpus:
    python verificar_vectorstore_b24.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from indexar_corpus import DIRECTORIO_VECTORSTORE, comprobar_indice
from src.rag_b24_booking_core import clasificar_fallo


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reabrir un índice Chroma desde disco sin llamadas a Gemini"
    )
    parser.add_argument(
        "--ruta",
        type=Path,
        default=DIRECTORIO_VECTORSTORE,
        help="Directorio de Chroma ya persistido",
    )
    args = parser.parse_args()

    try:
        resultado = comprobar_indice(args.ruta)
        print("Persistencia confirmada: Chroma reabierto sin reindexación ni Gemini.")
        print("Documentos de origen:", resultado["documentos"])
        print("Chunks persistidos:", resultado["chunks"])
        print("Carpeta:", resultado["ruta"])
        print("Archivos fuente:")
        for nombre in resultado["fuentes"]:
            print("-", nombre)
        return 0
    except Exception as error:
        print("Error:", clasificar_fallo(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
