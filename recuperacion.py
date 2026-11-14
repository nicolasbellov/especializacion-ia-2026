"""Skillnest U2.5 / Bloque 26 / Lección 3: recuperar y crear un prompt citado.

Entrega académica: corpus PROPIO pero 100 % FICTICIO de Booking Core AI.
NO se reindexa: vectorstore/ ya tiene metadata, IDs deterministas y 10 chunks
procedentes de cinco archivos (confirmado en la práctica B24/L3).

Desde la raíz del repositorio y con .venv:
    python recuperacion.py --modo inspeccionar                       # sin API
    python recuperacion.py --modo comparar                          # 2 embeddings de consulta
    python recuperacion.py --modo recuperar --pregunta "..."        # 1 embedding
    python recuperacion.py --modo responder --pregunta "..."        # 1 embedding + 1 chat Gemini

El índice es leído con colección explícita. No utiliza from_documents,
add_documents, upsert ni elimina/reconstruye vectorstore/ en ninguna operación.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any

from langchain_core.documents import Document

from citas_demo import CITA_INVALIDA, PROMPT_TEMPLATE, formatear_contexto, mapear_citas
from src.rag_b24_booking_core import RAIZ, clasificar_fallo, crear_embeddings

# Importamos indexar_corpus dentro de las funciones: el job general CI no
# instala langchain-text-splitters, pero el job RAG sí.
DIRECTORIO_INDICE = RAIZ / "vectorstore"
COLECCION = "booking_core_b24_l3"
PREGUNTA_CAMBIO = "¿Cómo puedo cambiar mi cita para otro día?"
PREGUNTA_PRIVACIDAD = "¿Cómo se separan los datos de clientes de distintas empresas?"
PREGUNTA_SIN_RESPUESTA = "¿Cuál es el precio real de un corte hoy en AES Barber?"


@dataclass(frozen=True)
class ResultadoRecuperacion:
    pregunta: str
    prompt: str
    citas: dict[int, str]
    documentos: list[Document]


def validar_pregunta_y_k(pregunta: str, k: int) -> None:
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")
    if type(k) is not int or k < 1:
        raise ValueError("k debe ser un entero positivo.")


def comprobar_fuentes(directorio: Path = DIRECTORIO_INDICE) -> dict[str, Any]:
    """Gate de integridad totalmente local; sin embeddings ni reindexación."""
    from indexar_corpus import (
        ARCHIVO_MANIFIESTO,
        COLECCION as COLECCION_INDEXADA,
        comprobar_indice,
    )
    from langchain_chroma import Chroma

    ruta = Path(directorio).resolve()
    if COLECCION != COLECCION_INDEXADA:
        raise RuntimeError("La colección B26 no coincide con la de B24/L3.")
    if not (ruta / "chroma.sqlite3").is_file() or not (
        ruta / ARCHIVO_MANIFIESTO
    ).is_file():
        raise FileNotFoundError(
            "Falta vectorstore/ persistido o su manifiesto B24/L3. "
            "No crear índice nuevo de forma automática."
        )

    estado = comprobar_indice(ruta)
    if estado["documentos"] < 5 or estado["chunks"] < 5:
        raise ValueError("El índice requiere al menos cinco fuentes/chunks.")
    # Reabrir con embedding_function=None permite get/count sin llamar a Gemini.
    store = Chroma(
        collection_name=COLECCION,
        persist_directory=str(ruta),
        embedding_function=None,
    )
    registros = store.get(include=["metadatas"])
    metas = registros.get("metadatas") or []
    ids = registros.get("ids") or []
    fuentes_reales = set()
    for meta in metas:
        if not isinstance(meta, dict):
            raise ValueError("Hay un chunk sin metadata en el índice.")
        fuente = meta.get("fuente")
        if not isinstance(fuente, str) or not fuente.strip() or fuente == "desconocida":
            raise ValueError("Falta metadata.fuente en algún chunk; no citarlo.")
        if meta.get("origen") != "FICTICIO_ACADEMICO":
            raise ValueError("El índice incluye un origen no académico: abortar.")
        if "indice_chunk" not in meta:
            raise ValueError("Falta índice ordinal del chunk.")
        fuentes_reales.add(fuente)
    if len(ids) != estado["chunks"] or len(ids) != len(set(ids)):
        raise ValueError("Cantidad o unicidad de IDs inválida.")
    if fuentes_reales != set(estado["fuentes"]):
        raise ValueError("Las fuentes Chroma no coinciden con el manifiesto.")
    return estado


def abrir_vectorstore(directorio: Path = DIRECTORIO_INDICE, embeddings: Any = None):
    """Reabrir el índice existente, NUNCA crear otro desde documentos."""
    from langchain_chroma import Chroma

    ruta = Path(directorio).resolve()
    comprobar_fuentes(ruta)
    modelo = embeddings if embeddings is not None else crear_embeddings()
    return Chroma(
        collection_name=COLECCION,
        persist_directory=str(ruta),
        embedding_function=modelo,
    )


def construir_resultado(
    pregunta: str,
    persist_directory: Path = DIRECTORIO_INDICE,
    k: int = 3,
    store: Any | None = None,
) -> ResultadoRecuperacion:
    """Retriever -> chunks -> contexto [n] -> prompt y fuentes originales.

    El store opcional permite tests con un retriever simulado. En ejecución real
    se conecta con Chroma y Gemini únicamente para el embedding de consulta.
    """
    validar_pregunta_y_k(pregunta, k)
    vectorstore = store if store is not None else abrir_vectorstore(persist_directory)
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    docs = list(retriever.invoke(pregunta))
    if not docs:
        raise ValueError("No se recuperaron chunks: revisar colección y ruta.")
    if len(docs) > k:
        raise ValueError("El retriever devolvió más chunks que k.")
    for doc in docs:
        fuente = doc.metadata.get("fuente")
        if not isinstance(fuente, str) or not fuente.strip() or fuente == "desconocida":
            raise ValueError("Chunk recuperado sin metadata.fuente; abortar.")
    contexto, citas = formatear_contexto(docs)
    if list(citas) != list(range(1, len(docs) + 1)):
        raise ValueError("Numeración de citas discontinua.")
    # No modificar el texto de la pregunta; respetar la consigna.
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)
    return ResultadoRecuperacion(pregunta, prompt, citas, docs)


def construir_prompt(
    pregunta: str,
    persist_directory: Path = DIRECTORIO_INDICE,
    k: int = 3,
    store: Any | None = None,
) -> tuple[str, dict[int, str]]:
    """Contrato solicitado por Skillnest: devuelve (prompt, citas)."""
    resultado = construir_resultado(pregunta, persist_directory, k, store)
    return resultado.prompt, resultado.citas


def mostrar_resultado(resultado: ResultadoRecuperacion) -> None:
    print("Pregunta exacta:", resultado.pregunta)
    print("Chunks recuperados:", len(resultado.documentos))
    print("Mapa de citas:", resultado.citas)
    print("\n--- Prompt dinámico con fuentes ---")
    print(resultado.prompt)
    print("\n--- Trazabilidad para revisión manual ---")
    for numero, doc in enumerate(resultado.documentos, 1):
        print(f"[{numero}] {doc.metadata['fuente']} | {doc.metadata.get('titulo', '')}")
        print("    Contenido:", doc.page_content)
    print("ADVERTENCIA: son documentos ficticios, no disponibilidad ni precios reales.")


def respuesta_llm(prompt: str) -> str:
    """ÚNICA llamada al chat Gemini; se ejecuta solo en --modo responder."""
    from dotenv import load_dotenv
    from langchain_google_genai import ChatGoogleGenerativeAI

    load_dotenv(dotenv_path=RAIZ / ".env")
    if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
        raise RuntimeError("Falta GEMINI_API_KEY en el .env local.")
    nombre_modelo = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    modelo = ChatGoogleGenerativeAI(model=nombre_modelo)
    respuesta = modelo.invoke(prompt)
    # Patrón de extracción ya utilizado en los ejercicios U2.3.
    texto = respuesta.text
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("El modelo no devolvió una respuesta textual.")
    return texto


def mostrar_citas_respuesta(respuesta: str, citas: dict[int, str]) -> bool:
    """Verificación sintáctica, NO verificación semántica del respaldo."""
    mapeo = mapear_citas(respuesta, citas)
    if not mapeo:
        print("Sin citas numeradas. Revisar: ¿es abstención o respuesta sin respaldo?")
        return False
    correctas = True
    for indice, fuente in mapeo:
        print(f"Cita [{indice}] -> {fuente}")
        if fuente == CITA_INVALIDA:
            correctas = False
    print(
        "IMPORTANTE: referencias existentes no prueban que las afirmaciones "
        "estén justificadas por los textos. Revisar [1] manualmente."
    )
    return correctas


def main() -> int:
    parser = argparse.ArgumentParser(
        description="B26/L3: recuperación Gemini y prompt con citas del corpus propio"
    )
    parser.add_argument(
        "--modo", choices=["inspeccionar", "recuperar", "comparar", "responder"],
        default="inspeccionar",
    )
    parser.add_argument("--pregunta", default=PREGUNTA_CAMBIO)
    parser.add_argument("--k", type=int, default=3)
    args = parser.parse_args()
    try:
        if args.modo == "inspeccionar":
            estado = comprobar_fuentes()
            print("Índice original B24/L3 validado SIN Gemini.")
            print("Colección:", COLECCION)
            print("Fuentes:", estado["documentos"])
            print("Chunks:", estado["chunks"])
            print("Ruta:", estado["ruta"])
            print("Todos los chunks tienen metadata.fuente e IDs existentes.")
            print("NO borrar ni reindexar vectorstore/.")
            return 0
        validar_pregunta_y_k(args.pregunta, args.k)
        if args.modo == "comparar":
            # Una sola apertura del índice; dos embeddings de consulta Gemini.
            store = abrir_vectorstore()
            a = construir_resultado(PREGUNTA_CAMBIO, k=args.k, store=store)
            b = construir_resultado(PREGUNTA_PRIVACIDAD, k=args.k, store=store)
            for numero, item in enumerate([a, b], 1):
                print(f"Pregunta {numero}: {item.pregunta}")
                print("Fuentes recuperadas:", list(item.citas.values()))
                print("Primer fragmento:", item.documentos[0].page_content)
                print("Contexto numerado:", len(item.citas), "chunks")
                print("--- Prompt dinámico ---")
                print(item.prompt)
                print("--- Fin del prompt ---")
            firmas_a = [(d.page_content, d.metadata.get("fuente")) for d in a.documentos]
            firmas_b = [(d.page_content, d.metadata.get("fuente")) for d in b.documentos]
            cambiado = firmas_a != firmas_b
            print("¿Cambió el contexto entre preguntas?:", cambiado)
            if not cambiado:
                print("AVISO: revisar consultas, k o índice antes de cerrar la actividad.")
                return 2
        else:
            res = construir_resultado(args.pregunta, k=args.k)
            mostrar_resultado(res)
            if args.modo == "responder":
                print("\n--- Respuesta real Gemini (puede consumir cuota) ---")
                texto = respuesta_llm(res.prompt)
                print(texto)
                print("\n--- Citas en respuesta real ---")
                mostrar_citas_respuesta(texto, res.citas)
                print("Para revisar [1], comparar su afirmación con el chunk [1] impreso.")
        return 0
    except Exception as error:
        print("Error:", clasificar_fallo(error))
        # Clasificador central no expone secretos ni el texto de proveedores.
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
