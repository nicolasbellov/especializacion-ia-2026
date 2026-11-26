"""Servicio final Gate 2: RAG persistido + auditoría + supervisión BC-01.

Modo por defecto: ensayo reproducible sin API con índice separado.
--modo real: Gemini embeddings y chat sobre vectorstore/ académico.
--actualizar: explícito; para modo real, respaldar primero vectorstore/.
--supervision interactiva: una persona decide sobre DEMO-001, solo en memoria.
No usa clientes reales, disponibilidad comercial ni APIs de Booking Core.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from io import StringIO
import json
import os
from pathlib import Path
import re
import sys
import time

from langchain_core.messages import AIMessage

from gate2.indice import preparar_indice, verificar_bloqueo
from gate2.servicio import ServicioRAG, RESPONDIDA
from gate2.supervision import ensayo_supervision
from logging_rag import configurar_logger

RAIZ = Path(__file__).resolve().parent
CORPUS = RAIZ / "data" / "corpus_b24_l3"
INDICE_REAL = RAIZ / "vectorstore"
INDICE_SIMULADO = RAIZ / ".local" / "gate2_simulado"
PREGUNTA = "¿Qué requisitos ficticios se deben cumplir para reprogramar una cita?"


class EmbeddingsEnsayo:
    """Vectores didácticos deterministas, NO un modelo semántico real."""
    def __init__(self):
        self.documentos_embebidos = 0

    def embed_query(self, texto):
        t = texto.casefold()
        return [1.0 + float(t.count(p)) for p in (
            "cita", "reprogram", "privacidad", "disponibilidad", "cancel",
            "servicio", "precio", "cliente",
        )] + [1.0]

    def embed_documents(self, textos):
        self.documentos_embebidos += len(textos)
        return [self.embed_query(t) for t in textos]


def generador_ensayo(mensajes):
    """Devuelve un extracto del contexto recuperado, no una respuesta Gemini."""
    cuerpo = mensajes[1].content
    contexto = cuerpo.split("<contexto_recuperado>", 1)[1].split("</contexto_recuperado>", 1)[0]
    hallazgo = re.search(r"\[(\d+)\]\s*(.*?)(?=\n\n\[\d+\]|\Z)", contexto, re.S)
    if not hallazgo:
        raise ValueError("No hay fuente en el contexto de ensayo.")
    texto = " ".join(hallazgo.group(2).split())
    return AIMessage(
        content=f"Extracto del corpus ficticio: {texto} [{hallazgo.group(1)}].",
        usage_metadata={"input_tokens": 120, "output_tokens": 22, "total_tokens": 142},
    )


def abrir_preparado(ruta, corpus, embeddings, *, actualizar=False):
    """Indexa solo si falta; comprueba y reabre el índice existente."""
    from recuperacion import abrir_vectorstore
    inicio = time.perf_counter()
    estado = preparar_indice(ruta, corpus, embeddings, actualizar=actualizar)
    verificar_bloqueo(ruta)
    store = abrir_vectorstore(directorio=ruta, embeddings=embeddings)
    return store, {**estado, "latencia_indice_ms": round((time.perf_counter()-inicio)*1000, 3)}


def ejecutar_consulta(store, pregunta, generador, *, simulado, k=3, estado_indice=None):
    """Único contrato integrado para CLI, ensayo y pruebas oficiales.

    Auditoría JSON real de aplicación capturada en memoria. No se capturan
    preguntas, texto de documentos ni respuestas en los eventos de logging.
    """
    buffer = StringIO()
    logger = configurar_logger(buffer)
    retriever = store.as_retriever(search_kwargs={"k": k})
    resultado = ServicioRAG(retriever.invoke, generador, logger=logger,
                            k=k, simulado=simulado).consultar(pregunta)
    auditoria = [json.loads(linea) for linea in buffer.getvalue().splitlines()]
    if estado_indice:
        auditoria.insert(0, {
            "evento": "gate2_indice", "trace_id": resultado.trace_id,
            "estado": estado_indice["estado"],
            "documentos": estado_indice["documentos"],
            "chunks": estado_indice["chunks"],
            "latencia_indice_ms": estado_indice["latencia_indice_ms"],
            "simulado": simulado,
        })
    return resultado, auditoria


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modo", choices=("simulado", "real"), default="simulado")
    parser.add_argument("--pregunta", default=PREGUNTA)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--actualizar", action="store_true",
                        help="Actualización incremental explícita; respaldar primero el índice real.")
    parser.add_argument("--supervision", choices=("ninguna", "demo", "interactiva"), default="demo")
    args = parser.parse_args()
    try:
        if not args.pregunta.strip() or len(args.pregunta) > 2000 or not 1 <= args.k <= 20:
            raise ValueError("Pregunta o k fuera de límites.")
        simulado = args.modo == "simulado"
        if simulado:
            ruta = INDICE_SIMULADO
            embeddings = EmbeddingsEnsayo()
            generar = generador_ensayo
        else:
            from dotenv import load_dotenv
            from langchain_google_genai import ChatGoogleGenerativeAI
            from src.rag_b24_booking_core import crear_embeddings
            load_dotenv(RAIZ / ".env")
            ruta = INDICE_REAL
            embeddings = crear_embeddings()
            modelo = ChatGoogleGenerativeAI(
                model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"), temperature=0
            )
            generar = modelo.invoke
        store, estado = abrir_preparado(ruta, CORPUS, embeddings, actualizar=args.actualizar)
        resultado, auditoria = ejecutar_consulta(
            store, args.pregunta, generar, simulado=simulado, k=args.k,
            estado_indice=estado,
        )
        for evento in auditoria:
            print(json.dumps(evento, ensure_ascii=False))
        print("--- RESPUESTA DEL SERVICIO (no es log) ---")
        print(json.dumps(asdict(resultado), ensure_ascii=False, indent=2))
        print("Modo:", "SIMULADO (embeddings y LLM)" if simulado else "REAL GEMINI")
        if resultado.estado != RESPONDIDA:
            print("Respuesta retenida o sin evidencia. No es una respuesta factual aprobada.")
            return 2
        if args.supervision != "ninguna":
            ensayo_supervision(interactivo=args.supervision == "interactiva")
        print("Proceso terminado sin errores. Sin reservas reales.")
        return 0
    except Exception as exc:
        # No imprimir mensajes de proveedores, credenciales o contenido crudo.
        print(f"ERROR Gate2: {type(exc).__name__}. Revisar entorno, índice y cuota.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
