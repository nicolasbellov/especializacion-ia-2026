"""Actualización incremental explícita de un índice académico B24.

No cambia el índice al consultar. Si una escritura parcial falla, se deja un
marcador de bloqueo: restaurar un respaldo antes de volver a usarlo.
Ejecutar actualizaciones con un solo proceso, sin otros escritores/lectores.
"""
from __future__ import annotations

import json
from pathlib import Path

from indexar_corpus import (
    ARCHIVO_MANIFIESTO, COLECCION, MODELO_EMBEDDING, TAMANO_CHUNK,
    OVERLAP_CHUNK, cargar_documentos, crear_chunks, ids_estables,
    huella_corpus, comprobar_indice, indexar_corpus,
)

MARCADOR = "actualizacion_gate2_pendiente"


def verificar_bloqueo(ruta):
    if (Path(ruta) / MARCADOR).exists():
        raise RuntimeError("Actualización incompleta: restaurar respaldo del índice.")


def preparar_indice(ruta, corpus, embeddings, *, actualizar=False):
    """Crear o reutilizar. Cambiar corpus requiere actualización explícita."""
    ruta, corpus = Path(ruta), Path(corpus)
    verificar_bloqueo(ruta)
    if actualizar and (ruta / ARCHIVO_MANIFIESTO).is_file():
        return actualizar_incremental(ruta, corpus, embeddings)
    return indexar_corpus(corpus, ruta, embeddings)


def actualizar_incremental(ruta, corpus, embeddings):
    """Upsert solo nuevos/cambiados; elimina IDs obsoletos; conserva los demás."""
    from langchain_chroma import Chroma

    ruta, corpus = Path(ruta), Path(corpus)
    verificar_bloqueo(ruta)
    comprobar_indice(ruta)
    documentos = cargar_documentos(corpus)
    chunks = crear_chunks(documentos)
    ids = ids_estables(chunks)
    nuevos = dict(zip(ids, chunks))
    manifiesto = ruta / ARCHIVO_MANIFIESTO
    previo = json.loads(manifiesto.read_text(encoding="utf-8"))
    if (previo["modelo"], previo["chunk_size"], previo["chunk_overlap"]) != (
        MODELO_EMBEDDING, TAMANO_CHUNK, OVERLAP_CHUNK
    ):
        raise ValueError("Modelo o parámetros incompatibles: no modificar índice.")
    store = Chroma(collection_name=COLECCION, persist_directory=str(ruta),
                   embedding_function=embeddings)
    datos = store.get(include=["documents", "metadatas"])
    actuales = {i: (t, m) for i, t, m in zip(
        datos["ids"], datos["documents"], datos["metadatas"]
    )}
    cambios = [i for i, d in nuevos.items()
               if actuales.get(i) != (d.page_content, d.metadata)]
    eliminados = sorted(set(actuales) - set(nuevos))
    conservados = len(nuevos) - len(cambios)
    huella = huella_corpus(documentos)
    if not cambios and not eliminados:
        if previo["huella"] != huella:
            raise ValueError("Huella inconsistente: revisar el índice.")
        return {"estado": "sin_cambios", "documentos": len(documentos),
                "chunks": len(ids), "upserts": 0, "eliminados": 0,
                "conservados": conservados, "huella": huella}
    # Este marcador evita abrir un índice parcial con el servicio Gate 2.
    # No promete rollback transaccional entre Chroma y el manifiesto.
    marcador = ruta / MARCADOR
    with marcador.open("x", encoding="utf-8") as f:
        f.write("Actualización iniciada. Si falla, restaurar respaldo.\n")
    if cambios:
        store.add_documents([nuevos[i] for i in cambios], ids=cambios)
    if eliminados:
        store.delete(ids=eliminados)
    final = store.get(include=["documents", "metadatas"])
    verificado = {i: (t, m) for i, t, m in zip(
        final["ids"], final["documents"], final["metadatas"]
    )}
    if verificado != {i: (d.page_content, d.metadata) for i, d in nuevos.items()}:
        raise RuntimeError("Índice incremental no coincide con el corpus.")
    info = {**previo, "huella": huella, "ids": ids,
            "total_chunks": len(ids),
            "fuentes": sorted(d.metadata["fuente"] for d in documentos)}
    temporal = manifiesto.with_suffix(".tmp")
    temporal.write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    temporal.replace(manifiesto)
    comprobar_indice(ruta)
    marcador.unlink()
    return {"estado": "actualizado_incremental", "documentos": len(documentos),
            "chunks": len(ids), "upserts": len(cambios),
            "eliminados": len(eliminados), "conservados": conservados,
            "huella": huella}
