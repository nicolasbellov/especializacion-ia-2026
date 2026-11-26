"""Skillnest | U2.7 / Bloque 32 / Actividad CORE | PASO 2.

LangGraph HITL real: proponer -> interrupt -> aplicar (SOLO EN MEMORIA).
Aprueba o rechaza la huella del prompt Booking Core AI del PASO 1.
SIN despliegue real, sin Gemini, sin permisos sobre reservas productivas.

Uso:
    python grafo_supervision.py
    python grafo_supervision.py --modo interactivo
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from typing import TypedDict
import uuid

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from registro_prompts import validar_registro
from src.versionado_supervision_b32 import cargar_registro


class EstadoDespliegue(TypedDict):
    version_actual: str
    version_nueva: str
    huella_nueva: str
    aprobado: bool
    version_activa_simulada: str
    resultado: str


def proponer(estado: EstadoDespliegue) -> dict:
    """Sin acciones externas."""
    return {}


def supervisar(estado: EstadoDespliegue) -> dict:
    """Checkpoint humano REAL en LangGraph; pendiente hasta Command(resume=...)."""
    decision = interrupt({
        "motivo": "Revisar propuesta de prompt de Booking Core AI (laboratorio)",
        "version_propuesta": estado["version_nueva"],
        "huella_propuesta": estado["huella_nueva"],
        "version_actual": estado["version_actual"],
    })
    if type(decision) is not bool:
        raise ValueError("Se requiere decision booleana True o False.")
    return {"aprobado": decision}


def aplicar(estado: EstadoDespliegue) -> dict:
    """Solo cambia estado simulado; nunca publica archivos ni llama al backend."""
    if type(estado["aprobado"]) is not bool:
        raise ValueError("Decision booleana no valida.")
    if estado["aprobado"]:
        return {
            "version_activa_simulada": estado["version_nueva"],
            "resultado": "APROBADA_SOLO_EN_SIMULACION",
        }
    return {
        "version_activa_simulada": estado["version_actual"],
        "resultado": "RECHAZADA_VERSION_ORIGINAL_CONSERVADA",
    }


def crear_grafo():
    graph = StateGraph(EstadoDespliegue)
    graph.add_node("proponer", proponer)
    graph.add_node("supervisar", supervisar)
    graph.add_node("aplicar", aplicar)
    graph.add_edge(START, "proponer")
    graph.add_edge("proponer", "supervisar")
    graph.add_edge("supervisar", "aplicar")
    graph.add_edge("aplicar", END)
    return graph.compile(checkpointer=InMemorySaver())


@dataclass(frozen=True)
class Solicitud:
    config: dict
    version_nueva: str
    huella_nueva: str


def iniciar_solicitud(app, version_actual: str, version_nueva: str, huella_nueva: str) -> Solicitud:
    """Cada propuesta tiene thread_id independiente; el nodo aplicar NO se ejecuta."""
    config = {"configurable": {"thread_id": "b32-core-" + uuid.uuid4().hex}}
    estado: EstadoDespliegue = {
        "version_actual": version_actual,
        "version_nueva": version_nueva,
        "huella_nueva": huella_nueva,
        "aprobado": False,
        "version_activa_simulada": version_actual,
        "resultado": "PENDIENTE",
    }
    inicial = app.invoke(estado, config=config)
    if "__interrupt__" not in inicial:
        raise RuntimeError("El grafo no se detuvo ante el interrupt.")
    return Solicitud(config=config, version_nueva=version_nueva, huella_nueva=huella_nueva)


def obtener_pendiente(app, solicitud: Solicitud) -> dict:
    """La persona revisa la huella del checkpoint, no un valor inventado."""
    estado = app.get_state(solicitud.config)
    if "supervisar" not in estado.next or not estado.interrupts:
        raise ValueError("No hay aprobacion pendiente en este thread_id.")
    if (
        estado.values.get("version_nueva") != solicitud.version_nueva
        or estado.values.get("huella_nueva") != solicitud.huella_nueva
    ):
        raise ValueError("La propuesta registrada difiere del estado del grafo.")
    if estado.values.get("resultado") != "PENDIENTE":
        raise ValueError("La propuesta no tiene estado pendiente.")
    return {
        "thread_id": solicitud.config["configurable"]["thread_id"],
        "motivo": estado.interrupts[0].value["motivo"],
        "version_propuesta": estado.interrupts[0].value["version_propuesta"],
        "huella_propuesta": estado.interrupts[0].value["huella_propuesta"],
        "version_actual": estado.values["version_actual"],
    }


def resolver(app, solicitud: Solicitud, aprobar: bool, *, huella_revisada: str) -> dict:
    if type(aprobar) is not bool:
        raise ValueError("La respuesta debe ser booleano True/False.")
    pendiente = obtener_pendiente(app, solicitud)
    if pendiente["huella_propuesta"] != huella_revisada:
        raise ValueError("La huella aprobada no corresponde a la propuesta.")
    return app.invoke(Command(resume=aprobar), config=solicitud.config)


def ejecutar(interactivo: bool = False) -> None:
    registro = cargar_registro()
    anterior, nueva = validar_registro(registro)
    app = crear_grafo()
    print("=== BOOKING CORE AI | PASO 2: SUPERVISION HUMANA ===")
    print("Huella de la nueva version (PASO 1):", nueva["huella"])
    primera = iniciar_solicitud(
        app, anterior["version"], nueva["version"], nueva["huella"]
    )
    pendiente = obtener_pendiente(app, primera)
    print("1) __interrupt__ pendiente:", json.dumps(pendiente, ensure_ascii=False))
    print("   No se ha ejecutado aplicar: sigue activa en memoria", anterior["version"])

    if interactivo:
        entrada = input("¿Aprobar la version ficticia propuesta? [s/n]: ").strip().lower()
        if entrada not in ("s", "n"):
            raise ValueError("La decision debe ser s o n.")
        aprobar = entrada == "s"
        print("DECISION INGRESADA MANUALMENTE (sin autenticacion productiva).")
    else:
        aprobar = True
        print("DECISION AUTOMATIZADA PARA LA DEMO; no es aprobacion humana autenticada.")

    resultado = resolver(app, primera, aprobar, huella_revisada=pendiente["huella_propuesta"])
    print("2) tras Command(resume=...):", resultado["resultado"])
    print("   version activa SIMULADA:", resultado["version_activa_simulada"])
    if resultado["version_activa_simulada"] != (
        nueva["version"] if aprobar else anterior["version"]
    ):
        raise AssertionError("El gate no aplico correctamente la decision.")

    if not interactivo:
        segunda = iniciar_solicitud(
            app, anterior["version"], nueva["version"], nueva["huella"]
        )
        if primera.config == segunda.config:
            raise AssertionError("Los thread_id deberian ser distintos.")
        segundo_pendiente = obtener_pendiente(app, segunda)
        rechazo = resolver(
            app, segunda, False, huella_revisada=segundo_pendiente["huella_propuesta"]
        )
        print("3) rechazo con un NUEVO thread_id:", rechazo["resultado"])
        if rechazo["version_activa_simulada"] != anterior["version"]:
            raise AssertionError("El rechazo debe preservar la version anterior.")

    print("PASS: interrupt real, get_state, aprobacion/rechazo de la huella del proyecto.")
    print("SOLO SIMULACION: no cambia el prompt operativo ni las reservas reales.")


def main() -> int:
    parser = argparse.ArgumentParser(description="B32 CORE: supervisor de prompts académico")
    parser.add_argument("--modo", choices=("demo", "interactivo"), default="demo")
    args = parser.parse_args()
    try:
        ejecutar(interactivo=args.modo == "interactivo")
        return 0
    except Exception as exc:
        print("ERROR:", type(exc).__name__, "(verificar entrada, estado y entorno).")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
