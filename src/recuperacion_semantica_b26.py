"""U2.5/B26/L1: recuperación semántica con Chroma (sin reindexar).

Fuente principal: Skillnest, "Buscar por significado, no por palabra".

Ejecutar desde la raíz, con .venv activo:
    python -m src.recuperacion_semantica_b26 --modo fake
    python -m src.recuperacion_semantica_b26 --modo real
    python -m src.recuperacion_semantica_b26 --modo real-search
    python -m src.recuperacion_semantica_b26 --modo real-retriever

--modo fake no necesita red ni GEMINI_API_KEY; prueba solo la MECÁNICA.
Los modos real usan el índice Gemini B25/L1 existente de 3 documentos.
Cada ejecución real calcula el embedding de la consulta (usa cuota), pero
NUNCA reindexa el corpus, inserta chunks ni cambia el modelo del índice.
"""

from __future__ import annotations

import argparse
import math
from uuid import uuid4

from langchain_core.documents import Document
from src.receta_indexacion_b25 import (
    COLECCION,
    CORPUS_EJEMPLO,
    DIRECTORIO_B25,
    cargar_vectorstore,
    verificar_indice,
)
from src.rag_b24_booking_core import clasificar_fallo, crear_embeddings


# Corpus de CINCO textos del ejemplo oficial B26/L1 (no datos reales).
CORPUS_FAKE = [
    "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente.",
    "Los errores de autenticacion nunca se reintentan: fallan de inmediato con un "
    "ValueError.",
    "El costo de cada llamada se calcula a partir de totalTokenCount y la tarifa "
    "vigente por cada 1000 tokens.",
    "El agente de la Unidad 2.4 decide por si mismo que herramienta usar, segun la "
    "descripcion de cada una.",
    "Las pruebas unitarias del cliente usan mocks, de forma que la suite completa "
    "corre en menos de un segundo.",
]
PREGUNTA_CURSO = "que pasa si la conexion tarda demasiado"
PREGUNTA_RETRIEVER = "cuanto cuesta cada llamada"
K_CURSO = 3


def validar_entrada(pregunta: str, k: int) -> str:
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")
    if not isinstance(k, int) or k < 1:
        raise ValueError("k debe ser un entero positivo.")
    return pregunta.strip()


def crear_demo_fake():
    """Chroma efímero: vectores deterministas por hash, SIN semántica ni API."""
    from langchain_chroma import Chroma
    from langchain_core.embeddings import DeterministicFakeEmbedding

    fake_emb = DeterministicFakeEmbedding(size=16)
    return Chroma.from_texts(
        texts=CORPUS_FAKE,
        embedding=fake_emb,
        metadatas=[{"fuente": f"doc{i}.md"} for i in range(len(CORPUS_FAKE))],
        collection_name=f"demo_similarity_b26_{uuid4().hex[:8]}",
    )


def recuperar_documentos(store, pregunta: str, k: int = K_CURSO) -> list[Document]:
    return store.similarity_search(validar_entrada(pregunta, k), k=k)


def recuperar_con_distancia(store, pregunta: str, k: int = K_CURSO):
    resultados = store.similarity_search_with_score(validar_entrada(pregunta, k), k=k)
    for _, distancia in resultados:
        if not isinstance(distancia, (int, float)) or not math.isfinite(distancia):
            raise ValueError("Chroma devolvió una distancia inválida.")
    return resultados


def crear_retriever(store, k: int = 2):
    if not isinstance(k, int) or k < 1:
        raise ValueError("k debe ser un entero positivo.")
    return store.as_retriever(search_kwargs={"k": k})


def mostrar_documentos(resultados: list[Document]) -> None:
    print(f"Documentos recuperados: {len(resultados)}")
    for i, doc in enumerate(resultados, 1):
        print(f"[{i}] Fuente: {doc.metadata.get('fuente', 'no informada')}")
        print(doc.page_content)


def mostrar_distancias(resultados) -> None:
    print(f"Documentos y distancias: {len(resultados)}")
    for i, (doc, distancia) in enumerate(resultados, 1):
        print(f"[{i}] Distancia={distancia:.4f} | fuente={doc.metadata.get('fuente')}")
        print(doc.page_content)
    print("MENOR distancia = MAYOR cercanía. No es porcentaje de similitud.")


def abrir_indice_real():
    """Comprobar corpus/IDs antes de crear embeddings de consulta.

    Usamos el B25/L1 porque ya contiene el chunk sobre TimeoutError, el mismo
    dominio semántico de la pregunta oficial B26/L1.
    """
    if not (DIRECTORIO_B25 / "chroma.sqlite3").is_file():
        raise FileNotFoundError(
            "Falta el índice B25/L1. No se crea uno vacío automáticamente."
        )
    n = verificar_indice(CORPUS_EJEMPLO, DIRECTORIO_B25)
    if n != 3:
        raise ValueError(f"Índice B25/L1 inesperado: {n} chunks (esperados: 3).")
    emb = crear_embeddings()
    return cargar_vectorstore(DIRECTORIO_B25, embeddings=emb)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="B26/L1 - similarity_search, distancias y as_retriever"
    )
    parser.add_argument(
        "--modo",
        choices=["fake", "real", "real-search", "real-retriever"],
        default="fake",
    )
    parser.add_argument("--pregunta", default=PREGUNTA_CURSO)
    parser.add_argument("--k", type=int, default=K_CURSO)
    args = parser.parse_args()

    try:
        pregunta = validar_entrada(args.pregunta, args.k)
        if args.modo == "fake":
            store = crear_demo_fake()
            print("MODO FAKE - prueba mecánica sin Gemini; NO evaluar relevancia.")
            print("Colección efímera de demostración; no toca índices persistentes.")
            print("Chunks en Chroma:", store._collection.count())
            print("\nsimilarity_search:")
            mostrar_documentos(recuperar_documentos(store, pregunta, args.k))
            print("\nsimilarity_search_with_score:")
            mostrar_distancias(recuperar_con_distancia(store, pregunta, args.k))
            print("\nas_retriever.invoke:")
            mostrar_documentos(
                crear_retriever(store, k=2).invoke(PREGUNTA_RETRIEVER)
            )
        else:
            store = abrir_indice_real()
            print("MODO GEMINI REAL - consulta a índice ya persistido B25/L1.")
            print("Índice:", DIRECTORIO_B25.resolve())
            print("Colección:", COLECCION)
            print("Chunks originales (sin reindexar):", store._collection.count())
            print("Consulta:", pregunta)
            if args.modo == "real":
                mostrar_distancias(recuperar_con_distancia(store, pregunta, args.k))
            elif args.modo == "real-search":
                mostrar_documentos(recuperar_documentos(store, pregunta, args.k))
            else:
                mostrar_documentos(
                    crear_retriever(store, k=args.k).invoke(pregunta)
                )
            print("No se añadieron chunks; Gemini solo embebe la pregunta.")
            print("No confirmar relevancia hasta revisar el orden de los resultados.")
        return 0
    except Exception as error:
        print("Error:", clasificar_fallo(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
