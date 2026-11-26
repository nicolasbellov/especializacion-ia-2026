"""BC-01: LangGraph pausa ANTES de cancelar una reserva ficticia.

Nunca conecta una agenda externa; la decisión cambia únicamente el estado del
hilo de LangGraph en memoria. La persona decide por consola, fuera del LLM.
"""
from __future__ import annotations

from typing import TypedDict
import uuid

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, END, StateGraph
from langgraph.types import interrupt, Command


class EstadoCancelacion(TypedDict):
    reserva_id: str
    estado_reserva: str
    aprobado: bool
    ejecutada: bool


def supervisar(estado):
    if estado["reserva_id"] not in {"DEMO-001", "DEMO-002"}:
        raise ValueError("Solo se admiten reservas ficticias conocidas.")
    if estado["estado_reserva"] != "confirmada" or estado["ejecutada"]:
        raise ValueError("Estado inicial inválido.")
    decision = interrupt({"riesgo": "BC-01", "accion": "cancelar_reserva_simulada",
                          "reserva_id": estado["reserva_id"],
                          "estado_actual": estado["estado_reserva"]})
    if type(decision) is not bool:
        raise ValueError("La decisión debe ser booleana.")
    return {"aprobado": decision}


def aplicar(estado):
    if estado["reserva_id"] not in {"DEMO-001", "DEMO-002"}:
        raise ValueError("Reserva ajena al laboratorio.")
    return {"estado_reserva": "cancelada" if estado["aprobado"] is True else "confirmada",
            "ejecutada": estado["aprobado"] is True}


def crear_supervision(reserva_id="DEMO-001"):
    if reserva_id not in {"DEMO-001", "DEMO-002"}:
        raise ValueError("Reserva ajena al laboratorio.")
    g = StateGraph(EstadoCancelacion)
    g.add_node("supervisar", supervisar)
    g.add_node("aplicar", aplicar)
    g.add_edge(START, "supervisar")
    g.add_edge("supervisar", "aplicar")
    g.add_edge("aplicar", END)
    return g.compile(checkpointer=InMemorySaver()), {
        "reserva_id": reserva_id, "estado_reserva": "confirmada",
        "aprobado": False, "ejecutada": False,
    }


def resolver(app, config, decision):
    if type(decision) is not bool:
        raise ValueError("Decisión inválida.")
    estado = app.get_state(config)
    if "supervisar" not in estado.next or not estado.interrupts:
        raise ValueError("No hay aprobación pendiente.")
    return app.invoke(Command(resume=decision), config=config)


def ensayo_supervision(interactivo=False):
    app, entrada = crear_supervision()
    config = {"configurable": {"thread_id": "gate2-bc01-" + uuid.uuid4().hex}}
    pausa = app.invoke(entrada, config=config)
    assert "__interrupt__" in pausa
    assert pausa["estado_reserva"] == "confirmada" and not pausa["ejecutada"]
    print("__interrupt__:", pausa["__interrupt__"][0].value)
    if interactivo:
        # Reutiliza B23: canal de consola con timeout, fail-closed.
        from src.supervision_b23_booking_core import esperar_aprobacion_con_timeout
        decision = esperar_aprobacion_con_timeout(
            "BC-01: cancelar DEMO-001 SOLO EN MEMORIA.", 60
        )
        aprobar = decision.aprobado
        print("decision de consola:", decision.estado)
    else:
        aprobar = False
        print("DECISION AUTOMATICA DE PRUEBA: rechazo; no es aprobación humana.")
    final = resolver(app, config, aprobar)
    assert "__interrupt__" not in final
    assert final["ejecutada"] is aprobar
    print("BC-01:", final)
    print("PASS: supervisión pausó y retomó; no hay reservas reales.")
    return final
