"""U2.5 / Bloque 24: fundamentos RAG aplicados a Booking Core AI.

Laboratorio exclusivamente académico con corpus FICTICIO. No consulta ni modifica
la agenda real de Booking Core, Supabase ni información de clientes.

Ejecutar desde la raíz:
    python -m src.rag_b24_booking_core --modo embedding
    python -m src.rag_b24_booking_core --modo indexar
    python -m src.rag_b24_booking_core --modo buscar --pregunta "¿Cómo se solicita un cambio?"
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.documents import Document

RAIZ = Path(__file__).resolve().parents[1]
CORPUS_DEMO = RAIZ / "data" / "rag_demo_booking_core.md"
DIRECTORIO_CHROMA = RAIZ / ".local" / "chroma_b24"
COLECCION = "booking_core_rag_demo_b24"
MODELO_EMBEDDING = "models/gemini-embedding-001"
TEXTO_PRUEBA = "El cliente reintenta ante un error"


def crear_documentos_demo(ruta: Path = CORPUS_DEMO) -> list[Document]:
    """Un chunk por sección Markdown '##': estrategia simple SOLO para B24/L1.

    Metadatos conservan fuente y sección para futuras citas. El texto incluye
    su encabezado y la advertencia explícita de que es documentación ficticia.
    """
    texto = Path(ruta).read_text(encoding="utf-8")
    secciones = re.split(r"(?=^## )", texto, flags=re.MULTILINE)
    documentos: list[Document] = []
    for seccion in secciones:
        seccion = seccion.strip()
        if not seccion.startswith("## "):
            continue
        titulo = seccion.splitlines()[0].removeprefix("## ").strip()
        if not titulo:
            raise ValueError("El corpus contiene una sección sin título.")
        documentos.append(
            Document(
                page_content=seccion,
                metadata={
                    "fuente": Path(ruta).name,
                    "seccion": titulo,
                    "origen": "FICTICIO_ACADEMICO",
                },
            )
        )
    if not documentos:
        raise ValueError("El corpus no contiene secciones Markdown '##'.")
    return documentos


def id_estable(documento: Document) -> str:
    """ID por fuente y título: evita duplicar la misma sección en reindexaciones.

    Si una sección desaparece del corpus, corresponde eliminar el índice local
    y reconstruirlo; esta demo no implementa gestión de borrados.
    """
    clave = f"{documento.metadata['fuente']}|{documento.metadata['seccion']}"
    return hashlib.sha256(clave.encode("utf-8")).hexdigest()


def crear_embeddings() -> Any:
    """Modelo oficial de la lección. No se ejecuta ninguna API al importarlo."""
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY"):
        raise RuntimeError('Falta GEMINI_API_KEY en el archivo local ".env".')
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    return GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDING)


def crear_store(embeddings: Any, directorio: Path = DIRECTORIO_CHROMA) -> Any:
    """Chroma local y persistente; nunca usa credenciales de Booking Core."""
    from langchain_chroma import Chroma

    return Chroma(
        collection_name=COLECCION,
        embedding_function=embeddings,
        persist_directory=str(directorio),
    )


def indexar_demo(store: Any, documentos: list[Document]) -> int:
    """Inserta/actualiza los chunks con ID determinista en Chroma."""
    if not documentos:
        raise ValueError("No hay chunks para indexar.")
    store.add_documents(documents=documentos, ids=[id_estable(d) for d in documentos])
    return len(documentos)


def buscar_demo(store: Any, pregunta: str, k: int = 3) -> list[Document]:
    """Recuperación documental; NO consulta horarios ni reserva citas."""
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("Escribe una pregunta no vacía.")
    if k < 1:
        raise ValueError("k debe ser positivo.")
    return store.similarity_search(pregunta.strip(), k=k)


def clasificar_fallo(error: Exception) -> str:
    """Diagnóstico sin imprimir respuestas externas ni posibles credenciales."""
    mensaje = str(error).lower()
    if "429" in mensaje or "resource_exhausted" in mensaje:
        return "Cuota de Gemini agotada (429); reintenta más tarde."
    if any(x in mensaje for x in ("api key", "401", "403", "permission_denied")):
        return "Autenticación o permisos de Gemini; revisa GEMINI_API_KEY."
    return f"Fallo de tipo {type(error).__name__}; revisar configuración/red."


def main() -> int:
    parser = argparse.ArgumentParser(description="RAG B24: solo documentos ficticios")
    parser.add_argument("--modo", choices=("embedding", "indexar", "buscar"), default="embedding")
    parser.add_argument("--pregunta", default="")
    args = parser.parse_args()

    try:
        if args.modo == "buscar" and not DIRECTORIO_CHROMA.exists():
            raise RuntimeError("Índice local inexistente: ejecuta --modo indexar primero.")
        if args.modo == "buscar" and not args.pregunta.strip():
            raise ValueError("Para buscar debes pasar --pregunta con texto.")

        embeddings = crear_embeddings()
        if args.modo == "embedding":
            vector = embeddings.embed_query(TEXTO_PRUEBA)
            print("Dimensiones:", len(vector))
            print("Primeros cinco valores:", vector[:5])
        elif args.modo == "indexar":
            documentos = crear_documentos_demo()
            store = crear_store(embeddings)
            print("Chunks indexados:", indexar_demo(store, documentos))
            print("Índice local:", DIRECTORIO_CHROMA)
            print("AVISO: corpus 100% ficticio; no contiene disponibilidad real.")
        else:
            store = crear_store(embeddings)
            documentos = buscar_demo(store, args.pregunta)
            print("Fragmentos recuperados de corpus FICTICIO:", len(documentos))
            for i, documento in enumerate(documentos, start=1):
                print(f"\n[{i}] {documento.metadata.get('fuente')} / {documento.metadata.get('seccion')}")
                print(documento.page_content)
            print("\nAVISO: estos resultados no autorizan ni confirman reservas.")
        return 0
    except Exception as error:
        print("Error:", clasificar_fallo(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
