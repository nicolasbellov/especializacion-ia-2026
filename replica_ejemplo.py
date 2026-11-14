"""U2.5/B25/L3: réplica guiada sobre la tienda ficticia del curso Skillnest.

Por petición del estudiante se versiona el CÓDIGO en GitHub, aunque la lección
oficial indica que no es necesario entregar ni commitear este ejercicio.
Nunca se versiona la base Chroma, las credenciales ni los embeddings reales.

Desde la raíz, en .venv:
    python replica_ejemplo.py --modo preparar  # sin API
    python replica_ejemplo.py --modo indexar   # Gemini real solo la primera vez
    python replica_ejemplo.py --modo verificar # proceso nuevo, sin API
    python replica_ejemplo.py --modo indexar   # reutiliza sin re-embedding
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

# Texto del ejemplo OFICIAL: conservar exactamente para comparar los resultados.
CORPUS_EJEMPLO = [
    "Los pedidos se pueden cancelar dentro de las primeras 24 horas despues de "
    "realizados, sin costo adicional.",
    "Las devoluciones se aceptan hasta 30 dias despues de la entrega, siempre que "
    "el producto este sin usar.",
    "El reembolso se procesa en un plazo de 5 a 10 dias habiles despues de recibir "
    "el producto devuelto.",
    "Los productos en oferta o liquidacion no tienen devolucion, salvo defecto de "
    "fabrica.",
    "El envio de una devolucion corre por cuenta del cliente, excepto cuando el "
    "producto llego danado.",
]

CHUNK_SIZE = 150
CHUNK_OVERLAP = 20
TAMANOS_ESPERADOS = [106, 103, 99, 85, 97]
TOTAL_ESPERADO = 490
MODELO = "models/gemini-embedding-001"
COLECCION = "tienda_ficticia_b25_replica"
MANIFIESTO = "manifiesto_replica_b25.json"

REPO = Path(__file__).resolve().parent
INDICE = REPO / ".local" / "chroma_b25_tienda_ejemplo"


def preparar_chunks():
    """Pasos 1 y 2: fragmentar y validar SIN Gemini ni escritura en Chroma."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.create_documents(
        CORPUS_EJEMPLO,
        metadatas=[
            {"fuente": f"tienda_ficticia_{i + 1}", "origen": "CURSO_B25"}
            for i in range(len(CORPUS_EJEMPLO))
        ],
    )

    textos = [chunk.page_content for chunk in chunks]
    longitudes = [len(texto) for texto in textos]
    vacios = [i for i, texto in enumerate(textos) if not texto.strip()]
    duplicados = len(textos) != len(set(textos))
    total = sum(longitudes)
    total_original = sum(map(len, CORPUS_EJEMPLO))

    print(f"{len(chunks)} chunks generados")
    for i, chunk in enumerate(chunks):
        print(f"--- chunk {i} ({len(chunk.page_content)} caracteres) ---")
        print(chunk.page_content)
    print("chunks vacios:", vacios)
    print("hay duplicados:", duplicados)
    print("total de caracteres en los chunks:", total)
    print("total de caracteres en el corpus original:", total_original)

    if (
        len(chunks) != 5
        or longitudes != TAMANOS_ESPERADOS
        or vacios
        or duplicados
        or total != TOTAL_ESPERADO
        or total_original != TOTAL_ESPERADO
        or textos != CORPUS_EJEMPLO
    ):
        raise ValueError(
            "El corpus o el chunking difieren de los resultados oficiales. "
            "No se solicitarán embeddings."
        )

    print("PREFLIGHT OK: 5 chunks, 490 caracteres, sin vacios ni duplicados.")
    return chunks


def _identidad(chunks):
    """Extensión propia: huella e IDs estables para evitar duplicados."""
    info = {
        "coleccion": COLECCION,
        "modelo": MODELO,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "documentos": [
            {"texto": c.page_content, "metadatos": c.metadata} for c in chunks
        ],
    }
    huella = hashlib.sha256(
        json.dumps(info, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    ids = [
        "tienda_b25_" + hashlib.sha256(
            f"{i}|{c.page_content}".encode("utf-8")
        ).hexdigest()
        for i, c in enumerate(chunks)
    ]
    return huella, ids


def verificar(chunks):
    """Paso 5: reabrir la colección desde disco y comparar IDs, sin Gemini."""
    from langchain_chroma import Chroma

    base = INDICE / "chroma.sqlite3"
    meta = INDICE / MANIFIESTO
    if not base.is_file() or not meta.is_file():
        raise FileNotFoundError(
            "Falta el índice o el manifiesto. Ejecuta primero --modo indexar."
        )

    huella, ids = _identidad(chunks)
    datos = json.loads(meta.read_text(encoding="utf-8"))
    if (
        datos.get("huella") != huella
        or datos.get("ids") != ids
        or datos.get("coleccion") != COLECCION
        or datos.get("modelo") != MODELO
    ):
        raise ValueError(
            "La configuración difiere del índice. No mezclar modelos ni corpus; "
            "crear otra carpeta después de respaldar."
        )

    store = Chroma(
        collection_name=COLECCION,
        embedding_function=None,
        persist_directory=str(INDICE),
    )
    guardados = store.get(include=["metadatas"])["ids"]
    if store._collection.count() != len(chunks) or set(guardados) != set(ids):
        raise RuntimeError("Los chunks de Chroma no coinciden con el manifiesto.")
    return len(guardados)


def indexar(chunks):
    """Pasos 3 y 4: calcular embeddings SOLO si el índice aún no existe."""
    from dotenv import load_dotenv
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_chroma import Chroma

    base = INDICE / "chroma.sqlite3"
    meta = INDICE / MANIFIESTO
    if base.is_file() and meta.is_file():
        cantidad = verificar(chunks)
        print(f"Estado: reutilizado sin re-embedding. Chunks: {cantidad}")
        return

    if INDICE.exists() and any(INDICE.iterdir()):
        raise RuntimeError(
            "Índice parcial o no reconocido: NO borrar automáticamente. "
            "Revisar o respaldar antes de reintentar."
        )

    # Misma clave local usada en B24/B25; no crear ni publicar otra .env.
    load_dotenv(dotenv_path=REPO / ".env")
    if not os.environ.get("GEMINI_API_KEY"):
        raise RuntimeError("Falta GEMINI_API_KEY en el entorno o .env del repositorio.")

    embedding = GoogleGenerativeAIEmbeddings(model=MODELO)
    huella, ids = _identidad(chunks)
    store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        collection_name=COLECCION,
        persist_directory=str(INDICE),
        ids=ids,
    )
    if store._collection.count() != len(chunks):
        raise RuntimeError("El número de chunks indexados no coincide con el corpus.")

    meta.write_text(
        json.dumps(
            {"huella": huella, "ids": ids, "coleccion": COLECCION, "modelo": MODELO},
            indent=2, ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"Estado: indexado con Gemini real. Chunks: {len(chunks)}")
    print("Índice:", INDICE)


def main():
    parser = argparse.ArgumentParser(description="Skillnest B25/L3 - réplica tienda ficticia")
    parser.add_argument("--modo", choices=["preparar", "indexar", "verificar"],
                        default="preparar")
    args = parser.parse_args()

    try:
        chunks = preparar_chunks()
        if args.modo == "preparar":
            print("Preparación sin Gemini ni escritura del índice.")
        elif args.modo == "indexar":
            indexar(chunks)
        else:
            print("Índice recargado sin Gemini, chunks:", verificar(chunks))
        return 0
    except Exception as error:
        mensaje = str(error).upper()
        if "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
            print("Cuota Gemini 429: revisar límites y reintentar cuando corresponda.")
        elif "API KEY" in mensaje or "401" in mensaje or "403" in mensaje:
            print("Error de credenciales Gemini: revisar .env local, sin compartir claves.")
        else:
            print("Error:", type(error).__name__)
            if type(error).__module__ == "builtins" and isinstance(
                error, (ValueError, RuntimeError, FileNotFoundError)
            ):
                print(str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
