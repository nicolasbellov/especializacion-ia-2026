"""U2.4 · B22/L1: herramienta personalizada para Booking Core AI.

Ejercicio académico: usa el catálogo y la agenda SIMULADOS del Bloque 21.
No consulta servicios externos ni crea, modifica o cancela reservas.

Uso:
    python -m src.herramienta_b22_booking_core
    python -m src.herramienta_b22_booking_core --agente
"""

from __future__ import annotations

import argparse
import os
from datetime import date
from typing import Literal

from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field, ValidationError

from src.agente_b21_booking_core import (
    AGENDA_SIMULADA,
    SERVICIOS_SIMULADOS,
    consultar_servicios,
)

ServicioId = Literal["corte", "barba", "corte_barba"]


class ArgumentosDisponibilidad(BaseModel):
    """Esquema que el modelo ve para construir la llamada a la herramienta."""

    fecha: str = Field(
        description=(
            "Fecha que se desea consultar, en formato AAAA-MM-DD. "
            "Ejemplo: 2026-11-11."
        ),
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    servicio: ServicioId = Field(
        description=(
            "Identificador del servicio: 'corte' (cabello), "
            "'barba' (perfilado) o 'corte_barba' (ambos)."
        ),
    )
    hora_desde: str | None = Field(
        default=None,
        description=(
            "Hora mínima opcional en formato HH:MM (24 horas). "
            "Si no se especifica, devolver todos los horarios del día."
        ),
        pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$",
    )
    incluir_duracion: bool = Field(
        default=False,
        strict=True,
        description=(
            "Si es true, incluir la duración estimada del servicio "
            "en minutos; false para mostrar solo horarios."
        ),
    )


@tool(
    "consultar_disponibilidad_con_filtros",
    args_schema=ArgumentosDisponibilidad,
)
def consultar_disponibilidad_detallada(
    fecha: str,
    servicio: ServicioId,
    hora_desde: str | None = None,
    incluir_duracion: bool = False,
) -> str:
    """Consulta horarios SIMULADOS por fecha y servicio, con filtro horario opcional.

    Usar cuando el cliente pregunte por disponibilidad, horarios después
    de cierta hora o duración del servicio junto con sus cupos.
    No consulta agenda real ni efectúa reservas.
    """
    try:
        date.fromisoformat(fecha)
        agenda_dia = AGENDA_SIMULADA.get(fecha)
        if agenda_dia is None:
            return (
                f"No hay datos SIMULADOS cargados para {fecha}; "
                "esto no implica que no haya horas reales."
            )

        horas = agenda_dia.get(servicio, [])
        if hora_desde is not None:
            horas = [hora for hora in horas if hora >= hora_desde]

        nombre = SERVICIOS_SIMULADOS[servicio]["nombre"]
        if not horas:
            return (
                f"No hay horarios SIMULADOS para {nombre} el {fecha}"
                + (f" desde las {hora_desde}" if hora_desde else "")
                + ". Esto no representa disponibilidad real."
            )

        respuesta = (
            f"AGENDA SIMULADA: {nombre}, fecha {fecha}, "
            f"horarios: {', '.join(horas)}."
        )
        if incluir_duracion:
            respuesta += (
                " Duración estimada: "
                f"{SERVICIOS_SIMULADOS[servicio]['duracion_min']} minutos."
            )
        return respuesta + " Horarios ficticios; ninguna reserva ha sido creada."
    except ValueError:
        return "Error: fecha inexistente; utiliza AAAA-MM-DD."


def crear_ejecutor() -> AgentExecutor:
    """Integra la herramienta avanzada a un agente con Gemini."""
    load_dotenv()
    modelo = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    )
    herramientas = [consultar_servicios, consultar_disponibilidad_detallada]
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Eres Booking Core AI en un entorno de DEMOSTRACIÓN. "
                "Los servicios y horarios son 100% ficticios. "
                "Consulta el catálogo para precios y la herramienta de "
                "disponibilidad para horarios. Si piden horas después de "
                "cierta hora, usa hora_desde. Si también quieren la duración "
                "al consultar horarios, incluye incluir_duracion=true. "
                "Nunca inventes reservas ni afirmes consultar una agenda real. "
                "Responde en español.",
            ),
            ("human", "{entrada}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
    agente = create_tool_calling_agent(modelo, herramientas, prompt)
    return AgentExecutor(
        agent=agente,
        tools=herramientas,
        return_intermediate_steps=True,
        verbose=True,
        max_iterations=4,
    )


def probar_herramienta() -> None:
    """Pruebas directas sin API: valores por defecto, filtro y validación."""
    herramienta = consultar_disponibilidad_detallada
    print("Nombre expuesto al modelo:", herramienta.name)
    assert herramienta.name == "consultar_disponibilidad_con_filtros"

    basico = herramienta.invoke({"fecha": "2026-11-11", "servicio": "corte"})
    print("\nCASO BASE:\n", basico)
    assert "10:00" in basico and "16:00" in basico and "18:30" in basico

    filtrado = herramienta.invoke(
        {
            "fecha": "2026-11-11",
            "servicio": "corte",
            "hora_desde": "18:00",
            "incluir_duracion": True,
        }
    )
    print("\nCASO FILTRADO:\n", filtrado)
    assert "18:30" in filtrado and "40 minutos" in filtrado
    assert "10:00" not in filtrado and "16:00" not in filtrado

    try:
        herramienta.invoke(
            {
                "fecha": "2026-11-11",
                "servicio": "corte",
                "incluir_duracion": "tal vez",
            }
        )
    except ValidationError as error:
        print("\nVALIDACIÓN PYDANTIC: rechazo correcto del booleano inválido")
        print("Campo:", error.errors()[0]["loc"])
    else:
        raise AssertionError("Se esperaba ValidationError por booleano inválido.")

    print("\nB22/L1: TRES COMPROBACIONES DIRECTAS CORRECTAS.")


def probar_agente() -> None:
    """Invocación opcional con Gemini real para observar args_schema en acción."""
    ejecutor = crear_ejecutor()
    resultado = ejecutor.invoke(
        {
            "entrada": (
                "¿Qué horarios simulados hay para un corte el 11 de noviembre "
                "de 2026 después de las 18:00? Incluye cuánto dura."
            )
        }
    )
    print("\nTRAZA ESTRUCTURADA:")
    herramientas = []
    for accion, observacion in resultado["intermediate_steps"]:
        herramientas.append(accion.tool)
        print(accion.tool, accion.tool_input, "->", observacion)

    if "consultar_disponibilidad_con_filtros" not in herramientas:
        raise AssertionError(
            "Gemini no utilizó la herramienta personalizada; "
            f"herramientas usadas: {herramientas}"
        )
    print("\nAGENTE: herramienta personalizada invocada correctamente.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--agente",
        action="store_true",
        help="Ejecutar también una invocación real a Gemini (consume API).",
    )
    args = parser.parse_args()
    probar_herramienta()
    if args.agente:
        probar_agente()


if __name__ == "__main__":
    main()
