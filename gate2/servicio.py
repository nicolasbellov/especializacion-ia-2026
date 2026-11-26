"""U2.8 Gate 2 — servicio RAG modular, trazable y fail-closed.

Arquitectura:
  recuperador inyectable -> documentos LangChain -> filtro B31 ->
  gate BC-02 -> contexto con citas B26 -> generador inyectable ->
  uso B31 -> chequeo sintáctico de citas -> respuesta.

Solo corpus FICTICIO_ACADEMICO. Nunca conecta el backend de reservas.
No indexa ni modifica Chroma; el índice del Bloque 24 se administra aparte.
Las pruebas inyectan recuperadores/LLM falsos sin consumo de API.

IMPORTANTE: citar [n] correctamente no garantiza respaldo semántico; una
evaluación manual y pruebas con Gemini real siguen siendo necesarias.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import time
from typing import Callable, Iterable
import uuid

from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from citas_demo import CITA_INVALIDA, formatear_contexto, mapear_citas
from logging_rag import (
    LOGGER,
    evento,
    filtrar_documentos_sospechosos,
    registrar_consumo,
    trace_id_var,
)
from src.mitigacion_inyeccion_b31_booking_core import PLANTILLA_USUARIO
from gate2.prompt import prompt_activo
from gate2.medicion import estimar_costo_generacion


# Los códigos son un contrato para CLI y futuras interfaces HTTP.
RESPONDIDA = "RESPONDIDA"
CONTEXTO_LISTO = "CONTEXTO_LISTO"
SIN_EVIDENCIA = "SIN_EVIDENCIA"
REQUIERE_REVISION = "REQUIERE_REVISION"
REVISAR_CITAS = "REVISAR_CITAS"

AVISO = (
    "Datos ficticios del laboratorio: no se confirman precios, horarios "
    "ni reservas reales. No hay conexión de escritura a Booking Core."
)
NO_EVIDENCIA = (
    "No tengo documentación ficticia suficiente para fundamentar "
    "una respuesta. No puedo confirmar datos de la agenda real."
)
REVISAR = (
    "La consulta requiere revisión manual por contenido documental "
    "sospechoso. Se detuvo la generación automáticamente."
)
CITAS_INSUFICIENTES = (
    "La respuesta generada no contiene citas verificables a las "
    "fuentes recuperadas. Se retuvo para revisión."
)


@dataclass(frozen=True)
class ResultadoGate2:
    trace_id: str
    estado: str
    respuesta: str
    fuentes: dict[int, str]
    citas_utilizadas: tuple[int, ...]
    documentos_recuperados: int
    documentos_descartados: int
    consumo: dict | None
    latencia_ms: float
    simulado: bool


class ServicioRAG:
    """Inyección de dependencias: permite tests offline y ejecución real.

    recuperador(pregunta)->Iterable[Document]
    generador([SystemMessage, HumanMessage])->AIMessage

    Por defecto, el servicio no posee generador y solo recupera.
    Si encuentra cualquier documento sospechoso, el servicio NO genera,
    incluso si también recuperó documentos legítimos (BC-02 / B32/L2).
    """

    def __init__(
        self,
        recuperador: Callable[[str], Iterable[Document]],
        generador: Callable[[list[SystemMessage | HumanMessage]], AIMessage] | None = None,
        *,
        logger: logging.Logger | None = None,
        simulado: bool = False,
        k: int = 3,
    ):
        if not callable(recuperador):
            raise TypeError("Se necesita un recuperador invocable.")
        if generador is not None and not callable(generador):
            raise TypeError("El generador debe ser invocable o None.")
        if type(k) is not int or not 1 <= k <= 20:
            raise ValueError("k debe ser un entero de 1 a 20.")
        self.recuperador = recuperador
        self.generador = generador
        self.logger = LOGGER if logger is None else logger
        self.simulado = simulado
        self.k = k

    def consultar(self, pregunta: str) -> ResultadoGate2:
        if not isinstance(pregunta, str) or not pregunta.strip():
            raise ValueError("La pregunta no debe estar vacía.")
        if len(pregunta) > 2000:
            raise ValueError("La pregunta supera el límite de 2000 caracteres.")

        trace_id = "gate2-" + uuid.uuid4().hex[:16]
        token = trace_id_var.set(trace_id)
        inicio = time.perf_counter()
        log = self.logger

        def finalizar(
            estado: str,
            respuesta: str,
            *,
            fuentes: dict[int, str] | None = None,
            citas: tuple[int, ...] = (),
            recuperados: int = 0,
            descartados: int = 0,
            consumo: dict | None = None,
        ) -> ResultadoGate2:
            latencia = round((time.perf_counter() - inicio) * 1000, 3)
            evento(
                log,
                logging.INFO,
                "consulta Gate2 finalizada",
                evento="gate2_finalizada",
                estado=estado,
                latencia_ms=latencia,
                recuperados=recuperados,
                descartados=descartados,
            )
            return ResultadoGate2(
                trace_id=trace_id,
                estado=estado,
                respuesta=respuesta,
                fuentes={} if fuentes is None else fuentes,
                citas_utilizadas=citas,
                documentos_recuperados=recuperados,
                documentos_descartados=descartados,
                consumo=consumo,
                latencia_ms=latencia,
                simulado=self.simulado,
            )

        try:
            evento(
                log, logging.INFO, "consulta Gate2 recibida",
                evento="gate2_consulta",
                pregunta_len=len(pregunta),
                k=self.k,
                simulado=self.simulado,
            )
            t_recuperacion = time.perf_counter()
            documentos = list(self.recuperador(pregunta))
            if len(documentos) > self.k:
                raise ValueError("El recuperador excedió el máximo k.")
            evento(
                log, logging.INFO, "recuperación RAG finalizada",
                evento="gate2_recuperacion",
                n_recuperados=len(documentos),
                latencia_ms=round((time.perf_counter() - t_recuperacion) * 1000, 3),
            )
            if not documentos:
                return finalizar(
                    SIN_EVIDENCIA, NO_EVIDENCIA,
                    recuperados=0,
                )
            for doc in documentos:
                if not isinstance(doc, Document):
                    raise TypeError("La recuperación exige documentos LangChain.")
                fuente = doc.metadata.get("fuente")
                if not isinstance(fuente, str) or not fuente.strip():
                    raise ValueError("El chunk no tiene metadata.fuente.")

            limpios, descartados = filtrar_documentos_sospechosos(documentos, log)
            if descartados:
                evento(
                    log, logging.WARNING, "gate de inyección activado",
                    evento="gate2_revision_humana_requerida",
                    riesgo="BC-02",
                    n_descartados=len(descartados),
                )
                return finalizar(
                    REQUIERE_REVISION, REVISAR,
                    recuperados=len(documentos),
                    descartados=len(descartados),
                )

            if not limpios:
                return finalizar(
                    SIN_EVIDENCIA, NO_EVIDENCIA,
                    recuperados=len(documentos),
                )

            contexto, fuentes = formatear_contexto(limpios)
            prompt = prompt_activo()
            mensajes = [
                SystemMessage(content=prompt["texto"]),
                HumanMessage(content=PLANTILLA_USUARIO.format(
                    contexto=contexto, pregunta=pregunta
                )),
            ]
            evento(
                log, logging.INFO, "prompt con fuentes construido",
                evento="gate2_prompt",
                n_fuentes=len(fuentes),
                version_prompt=prompt["version"], huella_prompt=prompt["huella"],
            )
            if self.generador is None:
                return finalizar(
                    CONTEXTO_LISTO,
                    "Contexto con fuentes recuperado; no se invocó un modelo.",
                    fuentes=fuentes,
                    recuperados=len(documentos),
                )

            t_generacion = time.perf_counter()
            respuesta_llm = self.generador(mensajes)
            evento(log, logging.INFO, "generación finalizada", evento="gate2_generacion",
                   latencia_ms=round((time.perf_counter() - t_generacion) * 1000, 3))
            if not isinstance(respuesta_llm, AIMessage):
                raise TypeError("El generador debe devolver AIMessage.")
            consumo = registrar_consumo(respuesta_llm, log, simulado=self.simulado)
            costo = estimar_costo_generacion(consumo)
            evento(log, logging.INFO, "estimación de costo", evento="gate2_costo",
                   costo_estimado=costo)
            consumo = {**consumo, "costo_estimado": costo}
            # AIMessage puede contener bloques textuales en vez de una cadena.
            texto = respuesta_llm.text
            if not isinstance(texto, str) or not texto.strip():
                return finalizar(
                    REVISAR_CITAS, CITAS_INSUFICIENTES,
                    fuentes=fuentes, recuperados=len(documentos), consumo=consumo,
                )
            verificadas = mapear_citas(texto, fuentes)
            if (
                not verificadas
                or any(fuente == CITA_INVALIDA for _, fuente in verificadas)
            ):
                evento(
                    log, logging.WARNING, "citas no verificables",
                    evento="gate2_revision_citas",
                    n_citas=len(verificadas),
                )
                return finalizar(
                    REVISAR_CITAS, CITAS_INSUFICIENTES,
                    fuentes=fuentes, recuperados=len(documentos), consumo=consumo,
                )
            return finalizar(
                RESPONDIDA, texto + "\nFuentes citadas: " + "; ".join(
                    f"[{i}] {fuentes[i]}" for i in dict.fromkeys(indice for indice, _ in verificadas)
                ),
                fuentes=fuentes,
                citas=tuple(indice for indice, _ in verificadas),
                recuperados=len(documentos),
                consumo=consumo,
            )

        except Exception as exc:
            # Nunca incluir str(exc), prompts, contenido documental o claves.
            evento(
                log, logging.ERROR, "consulta Gate2 fallida",
                evento="gate2_error", tipo_error=type(exc).__name__,
            )
            raise
        finally:
            trace_id_var.reset(token)
