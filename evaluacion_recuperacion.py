"""Skillnest U2.5/B27/L3: métricas REALES con 12 etiquetas congeladas.

Precondiciones:
- 8–15 preguntas etiquetadas ANTES de consultar al retriever.
- IDs SHA-256 originales de los 10 chunks B24/L3. No reindexa.
- índice local vectorstore/ intacto, GEMINI_API_KEY en .env local.

Modo 1: python evaluacion_recuperacion.py --modo etiquetas    (sin API)
Modo 2: python evaluacion_recuperacion.py --modo inventario  (sin API)
Modo 3: python evaluacion_recuperacion.py --modo evaluar --k 3
Modo 4: python evaluacion_recuperacion.py --modo evaluar --k 5

Los modos evaluar consultan Gemini SOLO para embeddings de pregunta:
12 preguntas x 2 repeticiones = 24 consultas por k, sin LLM generador.
Las salidas se guardan sin sobrescribir corridas previas.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any

from evaluacion_rag import precision_at_k, promediar, recall_at_k

RAIZ = Path(__file__).resolve().parent
RUTA_ETIQUETAS = RAIZ / "data" / "etiquetas_b27_l3_booking_core.json"
RUTA_RESULTADOS = RAIZ / "resultados_evaluacion.txt"
COLECCION = "booking_core_b24_l3"
FUENTES = (
    "01_servicios.md",
    "02_disponibilidad.md",
    "03_reprogramacion.md",
    "04_cancelacion.md",
    "05_privacidad.md",
)


def id_estable(fuente: str, ordinal: int) -> str:
    """Misma clave que indexar_corpus.ids_estables, SIN consultar Chroma."""
    return hashlib.sha256(f"{fuente}|{ordinal}".encode("utf-8")).hexdigest()


def cargar_etiquetas(ruta: Path = RUTA_ETIQUETAS) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Leer etiquetas FIJADAS; no aprender ni editar labels desde retrieval."""
    config = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if (
        config.get("estado") != "ETIQUETAS_FIJADAS_PREVIAS_A_RETRIEVAL"
        or config.get("coleccion") != COLECCION
        or config.get("chunk_size") != 550
        or config.get("chunk_overlap") != 80
    ):
        raise ValueError("Etiquetas incompatibles con la colección B24/L3.")

    casos = config.get("casos")
    if not isinstance(casos, list) or not 8 <= len(casos) <= 15:
        raise ValueError("Skillnest exige entre 8 y 15 casos etiquetados.")
    universo = {id_estable(fuente, indice) for fuente in FUENTES for indice in (0, 1)}
    vistos_ids: set[str] = set()
    vistos_preguntas: set[str] = set()
    normalizados: list[dict[str, Any]] = []

    for caso in casos:
        if not isinstance(caso, dict):
            raise ValueError("Cada caso debe ser un objeto JSON.")
        cid, pregunta = caso.get("id"), caso.get("pregunta")
        relevantes = caso.get("ids_relevantes")
        evidencia = caso.get("evidencia")
        if (
            not isinstance(cid, str) or not cid.strip() or cid in vistos_ids
            or not isinstance(pregunta, str) or not pregunta.strip()
            or pregunta in vistos_preguntas
            or not isinstance(relevantes, list)
            or len(relevantes) != len(set(relevantes))
            or not isinstance(evidencia, str) or not evidencia.strip()
        ):
            raise ValueError("Caso malformado o duplicado; revisar etiquetas.")
        if not set(relevantes) <= universo:
            raise ValueError(f"ID etiquetado inexistente en corpus: {cid}.")
        vistos_ids.add(cid)
        vistos_preguntas.add(pregunta)
        normalizados.append({
            "id": cid,
            "pregunta": pregunta,
            "ids_relevantes": set(relevantes),
            "evidencia": evidencia,
        })
    if len([c for c in normalizados if c["ids_relevantes"]]) < 8:
        raise ValueError("Se requieren al menos ocho preguntas con evidencia positiva.")
    return config, normalizados


def preflight_indice(
    config: dict[str, Any],
    casos: list[dict[str, Any]],
    directorio: Path | None = None,
) -> dict[str, Any]:
    """Verifica Chroma/métadatos/manifiesto/chunks SIN ninguna API ni escritura.

    Recalcula los chunks desde las fuentes y contrasta los diez textos con Chroma.
    No se aceptan IDs inventados ni modificaciones del índice después de etiquetar.
    """
    from indexar_corpus import (
        ARCHIVO_MANIFIESTO, COLECCION as COLECCION_B24,
        DIRECTORIO_VECTORSTORE, OVERLAP_CHUNK, TAMANO_CHUNK,
        cargar_documentos, comprobar_indice, crear_chunks, huella_corpus,
        ids_estables,
    )
    from langchain_chroma import Chroma

    ruta = Path(directorio if directorio is not None else DIRECTORIO_VECTORSTORE).resolve()
    if COLECCION != COLECCION_B24 or (TAMANO_CHUNK, OVERLAP_CHUNK) != (
        config["chunk_size"], config["chunk_overlap"]
    ):
        raise ValueError("Configuración B24/L3 incompatible con etiquetas congeladas.")

    estado = comprobar_indice(ruta)
    documentos = cargar_documentos()
    chunks = crear_chunks(documentos)
    ids = ids_estables(chunks)
    esperado = dict(zip(ids, chunks))
    manifiesto = json.loads((ruta / ARCHIVO_MANIFIESTO).read_text(encoding="utf-8"))
    if (
        len(documentos) != 5 or len(chunks) != 10
        or set(ids) != {id_estable(fuente, i) for fuente in FUENTES for i in (0, 1)}
        or estado["huella"] != huella_corpus(documentos)
        or manifiesto.get("huella") != huella_corpus(documentos)
        or manifiesto.get("chunk_size") != TAMANO_CHUNK
        or manifiesto.get("chunk_overlap") != OVERLAP_CHUNK
    ):
        raise ValueError("Corpus, parámetros o huella cambiaron desde el etiquetado.")

    store = Chroma(
        collection_name=COLECCION,
        persist_directory=str(ruta),
        embedding_function=None,
    )
    datos = store.get(include=["metadatas", "documents"])
    if set(datos["ids"]) != set(esperado) or len(datos["ids"]) != 10:
        raise ValueError("IDs del índice no coinciden con los chunks etiquetados.")
    for ident, meta, texto in zip(
        datos["ids"], datos["metadatas"], datos["documents"]
    ):
        chunk = esperado[ident]
        if (
            texto != chunk.page_content
            or not isinstance(meta, dict)
            or meta.get("fuente") != chunk.metadata["fuente"]
            or meta.get("indice_chunk") != chunk.metadata["indice_chunk"]
            or meta.get("origen") != "FICTICIO_ACADEMICO"
        ):
            raise ValueError(f"Texto o metadata del chunk no coincide: {ident}")
    permitidos = set(datos["ids"])
    if any(not c["ids_relevantes"] <= permitidos for c in casos):
        raise ValueError("Las etiquetas incluyen IDs ausentes del índice real.")

    return {
        "estado": estado,
        "chunks": [
            {"id": ident, "fuente": esperado[ident].metadata["fuente"],
             "ordinal": esperado[ident].metadata["indice_chunk"],
             "texto": esperado[ident].page_content}
            for ident in ids
        ],
    }


def evaluar_una_pasada(
    retriever: Any,
    casos: list[dict[str, Any]],
    k: int,
    ids_conocidos: set[str],
) -> tuple[list[dict[str, Any]], float, float]:
    """Una evaluación; usa Document.id y NO reinterpreta relevancia."""
    if type(k) is not int or k not in (3, 5):
        raise ValueError("Para esta actividad se compara k=3 con k=5.")
    resultados: list[dict[str, Any]] = []
    for caso in casos:
        docs = retriever.invoke(caso["pregunta"])
        obtenidos = [getattr(d, "id", None) for d in docs]
        if len(obtenidos) != k:
            raise ValueError(f"Retriever devolvió {len(obtenidos)}, se esperaban {k}.")
        if (
            any(not isinstance(i, str) or i not in ids_conocidos for i in obtenidos)
            or len(obtenidos) != len(set(obtenidos))
        ):
            raise ValueError(f"Document.id inválido, desconocido o duplicado: {caso['id']}")
        p = precision_at_k(obtenidos, caso["ids_relevantes"])
        r = recall_at_k(obtenidos, caso["ids_relevantes"])
        if not 0 <= p <= 1 or (r is not None and not 0 <= r <= 1):
            raise ValueError("Métricas fuera de [0, 1]: revisar IDs y etiquetas.")
        resultados.append({
            "id": caso["id"],
            "pregunta": caso["pregunta"],
            "ids_recuperados": obtenidos,
            "precision": p,
            "recall": r,
        })
    return (
        resultados,
        promediar(fila["precision"] for fila in resultados),
        promediar(fila["recall"] for fila in resultados),
    )


def verificar_repetibilidad(
    primera: tuple[list[dict[str, Any]], float, float],
    segunda: tuple[list[dict[str, Any]], float, float],
) -> bool:
    """Comparar las secuencias de IDs, no solo promedios que podrían coincidir."""
    return primera == segunda


def formatear_informe(
    config: dict[str, Any],
    pasada_1: tuple[list[dict[str, Any]], float, float],
    pasada_2: tuple[list[dict[str, Any]], float, float],
    k: int,
    huella: str,
    fecha: str,
) -> str:
    """Reporte Skillnest con fecha, k, chunking y ambas corridas reales."""
    lineas = [
        f"Fecha: {fecha}",
        f"Configuracion: k={k}, chunk_size={config['chunk_size']}, "
        f"chunk_overlap={config['chunk_overlap']}",
        f"Coleccion: {COLECCION}",
        f"Huella de corpus: {huella}",
        f"Etiquetas congeladas: {RUTA_ETIQUETAS.relative_to(RAIZ)}",
        f"Casos: {len(pasada_1[0])}",
    ]
    for numero, (filas, precision, recall) in enumerate((pasada_1, pasada_2), 1):
        lineas.extend(["", f"Corrida {numero}:"])
        for fila in filas:
            rtxt = "n/a" if fila["recall"] is None else f"{fila['recall']:.2f}"
            lineas.append(
                f"{fila['precision']:.2f}  {rtxt}  {fila['pregunta']}"
            )
            lineas.append(
                f"  caso={fila['id']}  ids={','.join(fila['ids_recuperados'])}"
            )
        lineas.append(
            f"promedio -> precision: {precision:.3f}  recall: {recall:.3f}"
        )
    lineas.extend([
        "",
        "Repetibilidad de secuencias de IDs y métricas: "
        + ("PASS" if verificar_repetibilidad(pasada_1, pasada_2) else "FAIL"),
        "Datos: preguntas y documentos 100% ficticios, no transacciones ni clientes reales.",
        "El caso sin relevantes reporta recall n/a y no se incluye en la media de recall.",
    ])
    return "\n".join(lineas) + "\n"


def guardar_sin_sobrescribir(contenido: str, salida: Path = RUTA_RESULTADOS) -> Path:
    """Primera corrida usa nombre oficial; siguientes conservan histórico."""
    ruta = Path(salida)
    if ruta.exists():
        marca = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        ruta = ruta.with_name(f"{ruta.stem}_{marca}{ruta.suffix}")
    with ruta.open("x", encoding="utf-8") as archivo:
        archivo.write(contenido)
    return ruta


def ejecutar_evaluacion(
    k: int,
    repeticiones: int = 2,
    salida: Path = RUTA_RESULTADOS,
    store: Any | None = None,
    inventario: dict[str, Any] | None = None,
) -> tuple[Path, tuple[list[dict[str, Any]], float, float]]:
    """Al ejecutar realmente: 12 preguntas x 2 embeddings por k."""
    if type(k) is not int or k not in (3, 5) or repeticiones != 2:
        raise ValueError("Comparar k=3/k=5 con dos corridas por configuración.")
    config, casos = cargar_etiquetas()
    preflight = inventario if inventario is not None else preflight_indice(config, casos)
    if store is None:
        # Este import instancia los embeddings Gemini, no reconstruye índice.
        from recuperacion import abrir_vectorstore
        store = abrir_vectorstore()

    ids = {c["id"] for c in preflight["chunks"]}
    retriever = store.as_retriever(search_kwargs={"k": k})
    print(f"Evaluando {len(casos)} casos, k={k}, dos corridas, Gemini query embeddings.")
    primera = evaluar_una_pasada(retriever, casos, k, ids)
    segunda = evaluar_una_pasada(retriever, casos, k, ids)
    if not verificar_repetibilidad(primera, segunda):
        print("ERROR: las dos corridas no tienen los mismos IDs/ métricas.")
        raise RuntimeError("Recuperación no repetible: revisar modelo o índice.")
    contenido = formatear_informe(
        config, primera, segunda, k,
        preflight["estado"]["huella"], datetime.now().date().isoformat()
    )
    ruta = guardar_sin_sobrescribir(contenido, salida)
    print(contenido)
    print(f"Resultados guardados en {ruta}")
    print("Ningún chunk fue reindexado. No subir .env ni vectorstore/ al repositorio.")
    return ruta, primera


def main() -> int:
    parser = argparse.ArgumentParser(description="B27/L3: evaluación real y repetible RAG")
    parser.add_argument("--modo", choices=["etiquetas", "inventario", "evaluar"],
                        default="etiquetas")
    parser.add_argument("--k", type=int, choices=[3, 5], default=3)
    args = parser.parse_args()
    try:
        config, casos = cargar_etiquetas()
        if args.modo == "etiquetas":
            print("Etiquetas PREVIAS al retrieval, sin API:", len(casos))
            for c in casos:
                print(c["id"], c["pregunta"], sorted(c["ids_relevantes"]))
            print("Positivos:", sum(bool(c["ids_relevantes"]) for c in casos))
            print("Sin respuesta factual:", sum(not c["ids_relevantes"] for c in casos))
            return 0
        preflight = preflight_indice(config, casos)
        print(
            "Índice validado SIN Gemini: "
            f"{preflight['estado']['documentos']} fuentes, "
            f"{preflight['estado']['chunks']} chunks, "
            f"colección {COLECCION}."
        )
        if args.modo == "inventario":
            for c in preflight["chunks"]:
                print(f"\n{c['fuente']}#{c['ordinal']}  id={c['id']}")
                print(c["texto"])
            print("\nEtiquetas congeladas antes de consultar Gemini.")
            return 0
        ejecutar_evaluacion(args.k, inventario=preflight)
        return 0
    except Exception as error:
        # Mantener el mismo tratamiento de errores que B26; no imprimir tokens.
        from src.rag_b24_booking_core import clasificar_fallo
        print("Error:", clasificar_fallo(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
