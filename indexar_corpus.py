"""Skillnest U2.5 / B24-L3: indexar cinco documentos propios con Gemini + Chroma.

EJERCICIO ACADÉMICO: el corpus es ficticio, no toca Booking Core ni Supabase.
No volver a indexar por cada pregunta; la lectura se hace en otro proceso.

Uso desde la raíz, con .venv:
    python indexar_corpus.py
    python verificar_vectorstore_b24.py

El índice nuevo se guarda en vectorstore/; NO sustituye .local/chroma_b24.
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

DIRECTORIO_CORPUS = RAIZ / "data" / "corpus_b24_l3"
DIRECTORIO_VECTORSTORE = RAIZ / "vectorstore"
ARCHIVO_MANIFIESTO = "manifiesto_b24_l3.json"
COLECCION = "booking_core_b24_l3"
TAMANO_CHUNK = 550
OVERLAP_CHUNK = 80
MINIMO_DOCUMENTOS = 5


def cargar_documentos(directorio: Path = DIRECTORIO_CORPUS) -> list[Document]:
    """Leer cinco archivos propios, cada uno con título y texto académico."""
    archivos = sorted(Path(directorio).glob("*.md"))
    if len(archivos) < MINIMO_DOCUMENTOS:
        raise ValueError("El corpus debe incluir al menos cinco archivos Markdown.")

    resultado = []
    for archivo in archivos:
        contenido = archivo.read_text(encoding="utf-8").strip()
        lineas = contenido.splitlines()
        if not lineas or not lineas[0].startswith("# "):
            raise ValueError("Cada documento requiere un título inicial '# '.")
        titulo = lineas[0].removeprefix("# ").strip()
        cuerpo = " ".join(line.strip() for line in lineas[1:] if line.strip())
        if not titulo or not cuerpo or "EJEMPLO FICTICIO" not in cuerpo:
            raise ValueError("Documento sin título, contenido o aviso FICTICIO.")

        # Unimos el título al primer párrafo ANTES de segmentar. Evita crear
        # chunks aislados de solo encabezado, como vimos en B24/L2.
        texto = f"{titulo}. {cuerpo}"
        resultado.append(
            Document(
                page_content=texto,
                metadata={
                    "fuente": archivo.name,
                    "titulo": titulo,
                    "origen": "FICTICIO_ACADEMICO",
                },
            )
        )
    return resultado


def crear_chunks(documentos: list[Document]) -> list[Document]:
    """Aplicar chunking recursivo POR documento, antes de los embeddings."""
    if len(documentos) < MINIMO_DOCUMENTOS:
        raise ValueError("Se requieren cinco documentos para esta actividad.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=TAMANO_CHUNK,
        chunk_overlap=OVERLAP_CHUNK,
    )
    chunks: list[Document] = []
    for documento in documentos:
        segmentos = splitter.split_text(documento.page_content)
        for numero, texto in enumerate(segmentos):
            if not texto:
                continue
            chunks.append(
                Document(
                    page_content=texto,
                    metadata={
                        **documento.metadata,
                        "indice_chunk": numero,
                        "metodo_chunking": "recursivo",
                    },
                )
            )
    if not chunks:
        raise ValueError("El splitter no generó fragmentos.")
    return chunks


def ids_estables(chunks: list[Document]) -> list[str]:
    """IDs deterministas para evitar duplicados accidentales."""
    claves = [
        f"{d.metadata['fuente']}|{d.metadata['indice_chunk']}"
        for d in chunks
    ]
    ids = [hashlib.sha256(clave.encode("utf-8")).hexdigest() for clave in claves]
    if len(set(ids)) != len(ids):
        raise ValueError("Se detectaron IDs de chunks duplicados.")
    return ids


def huella_corpus(documentos: list[Document]) -> str:
    """Huella del contenido, tamaño/overlap y modelo de embeddings."""
    payload = {
        "modelo": MODELO_EMBEDDING,
        "chunk_size": TAMANO_CHUNK,
        "chunk_overlap": OVERLAP_CHUNK,
        "documentos": [
            {"fuente": d.metadata["fuente"], "contenido": d.page_content}
            for d in documentos
        ],
    }
    contenido = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(contenido.encode("utf-8")).hexdigest()


def comprobar_indice(directorio: Path = DIRECTORIO_VECTORSTORE) -> dict[str, Any]:
    """Abrir Chroma DESDE DISCO sin realizar embedding ni consultar Gemini."""
    from langchain_chroma import Chroma

    ruta = Path(directorio)
    manifiesto = ruta / ARCHIVO_MANIFIESTO
    if not (ruta / "chroma.sqlite3").is_file() or not manifiesto.is_file():
        raise FileNotFoundError("No existe índice completo; primero ejecuta indexar_corpus.py.")

    info = json.loads(manifiesto.read_text(encoding="utf-8"))
    if info.get("coleccion") != COLECCION or info.get("modelo") != MODELO_EMBEDDING:
        raise ValueError("Manifiesto incompatible con el índice B24/L3.")

    # embedding_function=None: solo count/get, SIN API y SIN volver a indexar.
    store = Chroma(
        collection_name=COLECCION,
        persist_directory=str(ruta),
        embedding_function=None,
    )
    datos = store.get(include=["metadatas"])
    ids = datos["ids"]
    metadatos = datos["metadatas"]
    fuentes = {m.get("fuente") for m in metadatos if m}
    if (
        len(ids) != info["total_chunks"]
        or set(ids) != set(info["ids"])
        or fuentes != set(info["fuentes"])
        or len(fuentes) < MINIMO_DOCUMENTOS
    ):
        raise ValueError("El índice persistido no concuerda con el manifiesto.")

    return {
        "documentos": len(fuentes),
        "chunks": len(ids),
        "fuentes": sorted(fuentes),
        "huella": info["huella"],
        "ruta": str(ruta),
    }


def indexar_corpus(
    directorio_corpus: Path = DIRECTORIO_CORPUS,
    directorio_vectorstore: Path = DIRECTORIO_VECTORSTORE,
    embeddings: Any | None = None,
) -> dict[str, Any]:
    """Indexar una vez usando Chroma.from_documents; no duplicar ni sobrescribir."""
    from langchain_chroma import Chroma

    documentos = cargar_documentos(directorio_corpus)
    chunks = crear_chunks(documentos)
    ids = ids_estables(chunks)
    huella = huella_corpus(documentos)
    ruta = Path(directorio_vectorstore)
    manifiesto = ruta / ARCHIVO_MANIFIESTO

    if manifiesto.exists():
        estado = comprobar_indice(ruta)
        if estado["huella"] != huella:
            raise ValueError(
                "El corpus cambió desde la indexación. Conserva o renombra "
                "el índice previo antes de construir una versión nueva."
            )
        return {"estado": "existente; sin re-embedding", **estado}

    if ruta.exists() and any(ruta.iterdir()):
        raise RuntimeError(
            "El directorio contiene un índice parcial o ajeno. "
            "Revisarlo y renombrarlo antes de reintentar; no se borra automáticamente."
        )

    # Gemini real SOLO se instancia cuando falta el índice. El test offline
    # inyecta un objeto fake y verifica persistencia con Chroma real.
    modelo = embeddings if embeddings is not None else crear_embeddings()
    store = Chroma.from_documents(
        documents=chunks,
        embedding=modelo,
        collection_name=COLECCION,
        persist_directory=str(ruta),
        ids=ids,
    )
    if store._collection.count() != len(chunks):
        raise RuntimeError("La cantidad de chunks persistidos no coincide.")

    info = {
        "coleccion": COLECCION,
        "modelo": MODELO_EMBEDDING,
        "chunk_size": TAMANO_CHUNK,
        "chunk_overlap": OVERLAP_CHUNK,
        "huella": huella,
        "total_chunks": len(chunks),
        "fuentes": sorted(d.metadata["fuente"] for d in documentos),
        "ids": ids,
    }
    manifiesto.write_text(
        json.dumps(info, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "estado": "creado con embeddings",
        "documentos": len(documentos),
        "chunks": len(chunks),
        "ruta": str(ruta),
        "fuentes": info["fuentes"],
        "huella": huella,
    }


def main() -> int:
    argparse.ArgumentParser(
        description="B24/L3: indexación académica de 5 documentos propios"
    ).parse_args()
    try:
        resultado = indexar_corpus()
        print("Estado:", resultado["estado"])
        print("Documentos fuente:", resultado["documentos"])
        print("Chunks indexados:", resultado["chunks"])
        print("Índice persistido:", resultado["ruta"])
        print("El vectorstore anterior .local/chroma_b24 no se modifica.")
        print("AVISO: corpus ficticio, sin datos ni citas reales de Booking Core.")
        return 0
    except Exception as error:
        print("Error:", clasificar_fallo(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
