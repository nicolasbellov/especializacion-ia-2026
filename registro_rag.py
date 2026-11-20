r"""Skillnest U2.5/B28 Core — latencia y tokens REALES de RAG académico.

Usa exclusivamente el corpus FICTICIO ya indexado en vectorstore/.
No reindexa, ni modifica Booking Core, ni consulta servicios transaccionales.

Comandos desde la raíz del repositorio:
    .\.venv\Scripts\python.exe registro_rag.py --modo preflight
    .\.venv\Scripts\python.exe registro_rag.py --modo evaluar --caso SERV-01 --k 3
    .\.venv\Scripts\python.exe registro_rag.py --modo evaluar --caso DISP-01 --k 3
    .\.venv\Scripts\python.exe registro_rag.py --modo evaluar --caso PRIV-01 --k 3
    .\.venv\Scripts\python.exe registro_rag.py --modo evaluar --caso SERV-01 --k 6
"""

from __future__ import annotations

import argparse
import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from citas_demo import PROMPT_TEMPLATE, formatear_contexto
from indexar_corpus import (
    COLECCION,
    DIRECTORIO_VECTORSTORE,
    OVERLAP_CHUNK,
    TAMANO_CHUNK,
    comprobar_indice,
)
from src.rag_b24_booking_core import MODELO_EMBEDDING, clasificar_fallo, crear_embeddings

RAIZ = Path(__file__).resolve().parent
ETIQUETAS = RAIZ / "data" / "etiquetas_b27_l3_booking_core.json"
REGISTROS = RAIZ / "registros_latencia_costo.jsonl"


@contextmanager
def medir(tiempos: dict[str, float], etapa: str):
    inicio = time.perf_counter()
    try:
        yield
    finally:
        tiempos[etapa] = time.perf_counter() - inicio


def validar_local() -> dict[str, str]:
    """Preflight sin API, sin reindexación y sin revelar credenciales."""
    estado = comprobar_indice(DIRECTORIO_VECTORSTORE)
    if estado["documentos"] != 5 or estado["chunks"] != 10:
        raise ValueError("Se esperaban 5 fuentes y 10 chunks indexados.")
    etiquetas = json.loads(ETIQUETAS.read_text(encoding="utf-8"))
    if (etiquetas.get("coleccion") != COLECCION
            or etiquetas.get("chunk_size") != TAMANO_CHUNK
            or etiquetas.get("chunk_overlap") != OVERLAP_CHUNK):
        raise ValueError("Las etiquetas no corresponden al índice actual.")
    return {c["id"]: c["pregunta"] for c in etiquetas["casos"]}


def registrar_consulta(caso: str, k: int) -> dict:
    """Una corrida real: 1 embedding de consulta + 1 generación."""
    preguntas = validar_local()
    if caso not in preguntas:
        raise ValueError(f"Caso desconocido: {caso}.")
    if k not in (3, 6):
        raise ValueError("Para el Core se usa k=3 y k=6.")

    load_dotenv(RAIZ / ".env")
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("Falta GEMINI_API_KEY en el archivo .env local.")
    modelo_chat = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    from langchain_chroma import Chroma
    from langchain_google_genai import ChatGoogleGenerativeAI

    embeddings = crear_embeddings()  # Mismo modelo que indexación B24/L3
    store = Chroma(
        collection_name=COLECCION,
        persist_directory=str(DIRECTORIO_VECTORSTORE),
        embedding_function=None,
    )
    chat = ChatGoogleGenerativeAI(model=modelo_chat, temperature=0)
    pregunta = preguntas[caso]
    tiempos: dict[str, float] = {}

    with medir(tiempos, "embed_query"):
        vector = embeddings.embed_query(pregunta)

    with medir(tiempos, "busqueda_vectorial"):
        chunks = store.similarity_search_by_vector(embedding=vector, k=k)
    if len(chunks) != k or any(not c.metadata.get("fuente") for c in chunks):
        raise ValueError("Índice incorrecto: faltan chunks o metadatos de fuente.")

    contexto, citas = formatear_contexto(chunks)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)
    with medir(tiempos, "generacion"):
        respuesta = chat.invoke(prompt)

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "caso": caso,
        "pregunta": pregunta,
        "k": k,
        "coleccion": COLECCION,
        "modelo_embedding": MODELO_EMBEDDING,
        "modelo_generacion": modelo_chat,
        "chunk_size": TAMANO_CHUNK,
        "chunk_overlap": OVERLAP_CHUNK,
        "tiempos_ms": {etapa: round(valor * 1000, 2)
                       for etapa, valor in tiempos.items()},
        "tiempo_total_ms": round(sum(tiempos.values()) * 1000, 2),
        "tokens": dict(respuesta.usage_metadata) if respuesta.usage_metadata else None,
        "fuentes": [citas[i] for i in citas],
        "tipo_datos": "FICTICIO_ACADEMICO",
    }
    # Una línea por consulta realmente exitosa, nunca datos simulados.
    with REGISTROS.open("a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
    return registro


def main() -> int:
    parser = argparse.ArgumentParser(description="U2.5/B28: RAG real, sin reindexar")
    parser.add_argument("--modo", choices=("preflight", "evaluar"), default="preflight")
    parser.add_argument("--caso", default="")
    parser.add_argument("--k", type=int, choices=(3, 6), default=3)
    args = parser.parse_args()
    try:
        if args.modo == "preflight":
            casos = validar_local()
            print(f"Preflight OK: colección={COLECCION}, 5 fuentes, 10 chunks, "
                  f"chunk_size={TAMANO_CHUNK}, overlap={OVERLAP_CHUNK}.")
            print(f"Casos disponibles: {', '.join(casos)}")
            print("Ninguna llamada a Gemini; no se reindexó.")
        else:
            if not args.caso:
                parser.error("Para evaluar indica --caso SERV-01, DISP-01, PRIV-01, etc.")
            registro = registrar_consulta(args.caso, args.k)
            print(json.dumps(registro, ensure_ascii=False, indent=2))
            print(f"Registro agregado: {REGISTROS}")
        return 0
    except Exception as error:
        if "404" in str(error) or "not_found" in str(error).lower():
            print("Error: modelo Gemini no disponible (404); revisa GEMINI_MODEL en .env.")
        else:
            print("Error:", clasificar_fallo(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
