"""U2.5 / Bloque 25 / Lección 1: receta reutilizable de indexación RAG.

El ejemplo de tres textos proviene de Skillnest. No modifica Booking Core ni
los índices B24: almacena la réplica en .local/chroma_b25_receta/.

Desde la raíz y con .venv activo:
    python -m src.receta_indexacion_b25 --modo preparar   # 0 llamadas Gemini
    python -m src.receta_indexacion_b25 --modo indexar    # Gemini primera vez
    python -m src.receta_indexacion_b25 --modo verificar  # proceso nuevo, sin Gemini
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.rag_b24_booking_core import MODELO_EMBEDDING, RAIZ, clasificar_fallo, crear_embeddings

CORPUS_EJEMPLO = [
    "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente.",
    "El costo de cada llamada se calcula a partir de totalTokenCount.",
    "Las pruebas unitarias del cliente usan mocks y corren en menos de un segundo.",
]
DIRECTORIO_B25 = RAIZ / ".local" / "chroma_b25_receta"
COLECCION = "receta_b25_ejemplo"
MANIFIESTO = "manifiesto_b25_receta.json"


def preparar_chunks(
    corpus: list[str], chunk_size: int = 200, chunk_overlap: int = 30
) -> list[Document]:
    """Paso 1-2: separar cada texto antes de cualquier embedding."""
    if not corpus or any(not isinstance(t, str) or not t.strip() for t in corpus):
        raise ValueError("El corpus debe contener textos no vacíos.")
    if chunk_size <= 0 or not 0 <= chunk_overlap < chunk_size:
        raise ValueError("Se requiere chunk_size > 0 y 0 <= chunk_overlap < chunk_size.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return splitter.create_documents(
        corpus,
        metadatas=[
            {"fuente": f"ejemplo_skillnest_{i + 1}", "origen": "EJEMPLO_ACADEMICO"}
            for i in range(len(corpus))
        ],
    )


def _firma(chunks: list[Document], tamano: int, solapamiento: int) -> tuple[str, list[str]]:
    datos = {
        "modelo": MODELO_EMBEDDING,
        "chunk_size": tamano,
        "chunk_overlap": solapamiento,
        "chunks": [
            {"texto": d.page_content, "metadatos": d.metadata}
            for d in chunks
        ],
    }
    huella = hashlib.sha256(
        json.dumps(datos, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    ids = [
        hashlib.sha256(
            f"{d.metadata['fuente']}|{i}|{d.page_content}".encode("utf-8")
        ).hexdigest()
        for i, d in enumerate(chunks)
    ]
    return huella, ids


def cargar_vectorstore(
    persist_directory: str | Path, embeddings: Any | None = None
) -> Any:
    """Paso 5: reabrir Chroma desde disco SIN reindexar y sin llamar a Gemini.

    Para similarity_search puede pasarse embeddings=crear_embeddings();
    el simple conteo no necesita ningún modelo.
    """
    from langchain_chroma import Chroma

    ruta = Path(persist_directory)
    if not (ruta / "chroma.sqlite3").is_file():
        raise FileNotFoundError("No hay índice persistido en la ruta solicitada.")
    return Chroma(
        collection_name=COLECCION,
        persist_directory=str(ruta),
        embedding_function=embeddings,
    )


def indexar_corpus(
    corpus: list[str],
    persist_directory: str | Path,
    chunk_size: int = 200,
    chunk_overlap: int = 30,
    embeddings: Any | None = None,
) -> tuple[Any, str, int]:
    """Pasos 1-4; evita duplicación y llamadas Gemini en reejecuciones."""
    from langchain_chroma import Chroma

    chunks = preparar_chunks(corpus, chunk_size, chunk_overlap)
    firma, ids = _firma(chunks, chunk_size, chunk_overlap)
    ruta = Path(persist_directory)
    meta = ruta / MANIFIESTO

    if (ruta / "chroma.sqlite3").exists() and meta.is_file():
        info = json.loads(meta.read_text(encoding="utf-8"))
        if (info.get("firma") != firma or info.get("ids") != ids
                or info.get("coleccion") != COLECCION):
            raise ValueError(
                "El corpus o la configuración cambiaron: usa otro directorio, "
                "no mezcles embeddings ni sobrescribas el índice anterior."
            )
        store = cargar_vectorstore(ruta, embeddings=embeddings)
        if set(store.get(include=[])["ids"]) != set(ids):
            raise ValueError("El índice persistido no coincide con el manifiesto.")
        return store, "reutilizado sin re-embedding", len(chunks)

    if ruta.exists() and any(ruta.iterdir()):
        raise RuntimeError(
            "Índice parcial o carpeta ocupada: revisar/respaldar antes de reintentar."
        )

    modelo = embeddings if embeddings is not None else crear_embeddings()
    store = Chroma.from_documents(
        documents=chunks,
        embedding=modelo,
        collection_name=COLECCION,
        persist_directory=str(ruta),
        ids=ids,
    )
    if store._collection.count() != len(chunks):
        raise RuntimeError("Chroma no guardó todos los fragmentos.")

    meta.write_text(
        json.dumps(
            {"firma": firma, "ids": ids, "coleccion": COLECCION},
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    return store, "indexado con embeddings", len(chunks)


def verificar_indice(
    corpus: list[str],
    persist_directory: str | Path,
    chunk_size: int = 200,
    chunk_overlap: int = 30,
) -> int:
    """Reconexión en proceso nuevo; compara cantidad, IDs y corpus sin Gemini."""
    ruta = Path(persist_directory)
    meta = ruta / MANIFIESTO
    if not meta.is_file():
        raise FileNotFoundError("Falta el manifiesto de persistencia.")
    chunks = preparar_chunks(corpus, chunk_size, chunk_overlap)
    firma, ids = _firma(chunks, chunk_size, chunk_overlap)
    info = json.loads(meta.read_text(encoding="utf-8"))
    store = cargar_vectorstore(ruta)
    if (info.get("firma") != firma or info.get("ids") != ids
            or set(store.get(include=[])["ids"]) != set(ids)
            or store._collection.count() != len(chunks)):
        raise ValueError("Diferencias entre corpus, manifiesto e índice persistido.")
    return len(chunks)


def main() -> int:
    parser = argparse.ArgumentParser(description="Receta oficial B25/L1 aislada de B24")
    parser.add_argument("--modo", choices=["preparar", "indexar", "verificar"], default="preparar")
    args = parser.parse_args()

    try:
        if args.modo == "preparar":
            chunks = preparar_chunks(CORPUS_EJEMPLO)
            print("Corpus de ejemplo:", len(CORPUS_EJEMPLO), "textos")
            print("Chunking local:", len(chunks), "chunks")
            print("Tamaños:", [len(d.page_content) for d in chunks])
            print("Sin llamadas a Gemini ni escritura del índice.")
        elif args.modo == "indexar":
            _, estado, n = indexar_corpus(CORPUS_EJEMPLO, DIRECTORIO_B25)
            print("Estado:", estado)
            print(f"Indexados {n} chunks en {DIRECTORIO_B25}")
        else:
            n = verificar_indice(CORPUS_EJEMPLO, DIRECTORIO_B25)
            print("Índice recargado sin re-embedding:", n, "chunks")
        print("B24 vectorstore/ y .local/chroma_b24: NO modificados.")
        return 0
    except Exception as error:
        print("Error:", clasificar_fallo(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
