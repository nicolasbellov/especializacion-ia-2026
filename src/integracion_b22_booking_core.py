"""U2.4 / Bloque 22 / Lección 3: integración final de Booking Core AI.

Reutiliza la herramienta Pydantic, AgentExecutor y memoria por session_id
ya implementados en B22/L1-L2. No consulta Supabase ni reservas reales.

Uso:
    python -m src.integracion_b22_booking_core
    python -m src.integracion_b22_booking_core --agente
"""

from __future__ import annotations

import argparse
from typing import Any

from langchain_core.runnables import RunnableLambda
from pydantic import ValidationError

from src.herramienta_b22_booking_core import (
    ArgumentosDisponibilidad,
    consultar_disponibilidad_detallada,
)
from src.memoria_b22_booking_core import (
    cerrar_sesion,
    crear_agente_con_memoria,
    envolver_con_memoria,
    obtener_historial,
)


def probar_integracion_sin_api() -> None:
    """Valida la herramienta y dos historiales aislados sin llamar a Gemini."""
    herramienta = consultar_disponibilidad_detallada
    assert herramienta.name == "consultar_disponibilidad_con_filtros"
    assert herramienta.args_schema is ArgumentosDisponibilidad
    campos = ArgumentosDisponibilidad.model_fields
    assert set(campos) == {
        "fecha", "servicio", "hora_desde", "incluir_duracion"
    }
    assert all(campo.description for campo in campos.values())

    base = herramienta.invoke({
        "fecha": "2026-11-11", "servicio": "corte"
    })
    filtrado = herramienta.invoke({
        "fecha": "2026-11-11",
        "servicio": "corte",
        "hora_desde": "18:00",
        "incluir_duracion": True,
    })
    assert "10:00" in base and "16:00" in base and "18:30" in base
    assert "18:30" in filtrado and "40 minutos" in filtrado
    assert "10:00" not in filtrado and "16:00" not in filtrado

    try:
        herramienta.invoke({
            "fecha": "2026-11-11",
            "servicio": "corte",
            "incluir_duracion": "tal vez",
        })
    except ValidationError:
        pass
    else:
        raise AssertionError("Pydantic debió rechazar el booleano inválido.")

    print("BLOQUE 1 OK: herramienta con args_schema, nombre y validación.")

    def responder_simulado(datos: dict[str, Any]) -> dict[str, str]:
        """Respuesta de prueba: observa el historial que recibe la sesión."""
        anterior = datos["chat_history"]
        return {"output": f"Historial previo: {len(anterior)} mensajes."}

    agente_simulado = envolver_con_memoria(RunnableLambda(responder_simulado))
    sesion_a = "b22_integracion_cliente_a"
    sesion_b = "b22_integracion_cliente_b"
    cerrar_sesion(sesion_a)
    cerrar_sesion(sesion_b)

    config_a = {"configurable": {"session_id": sesion_a}}
    config_b = {"configurable": {"session_id": sesion_b}}

    primero_a = agente_simulado.invoke(
        {"entrada": "Quiero corte el 11 de noviembre de 2026."},
        config=config_a,
    )
    primero_b = agente_simulado.invoke(
        {"entrada": "Quiero perfilado de barba el 12 de noviembre de 2026."},
        config=config_b,
    )
    segundo_a = agente_simulado.invoke(
        {"entrada": "¿Y después de las 18:00?"},
        config=config_a,
    )

    assert primero_a["output"] == "Historial previo: 0 mensajes."
    assert primero_b["output"] == "Historial previo: 0 mensajes."
    assert segundo_a["output"] == "Historial previo: 2 mensajes."

    mensajes_a = obtener_historial(sesion_a).messages
    mensajes_b = obtener_historial(sesion_b).messages
    assert len(mensajes_a) == 4 and len(mensajes_b) == 2
    assert "corte" in mensajes_a[0].content.lower()
    assert "barba" in mensajes_b[0].content.lower()
    assert all("barba" not in str(msg.content).lower() for msg in mensajes_a)
    assert all("corte" not in str(msg.content).lower() for msg in mensajes_b)

    print("BLOQUE 2 OK: conversación A de 2 turnos (4 mensajes).")
    print("BLOQUE 3 OK: conversación B independiente (2 mensajes).")

    cerrar_sesion(sesion_a)
    cerrar_sesion(sesion_b)
    print("LIMPIEZA OK: sesiones eliminadas.")
    print("\nB22/L3: INTEGRACIÓN SIN API VERIFICADA.")


def probar_integracion_con_gemini() -> None:
    """Comprueba dos turnos relacionados y una segunda sesión real aislada."""
    cliente_a = "b22_final_a"
    cliente_b = "b22_final_b"
    cerrar_sesion(cliente_a)
    cerrar_sesion(cliente_b)

    agente = crear_agente_con_memoria()
    config_a = {"configurable": {"session_id": cliente_a}}
    config_b = {"configurable": {"session_id": cliente_b}}

    consulta_1 = (
        "¿Qué horarios simulados hay para un corte de cabello "
        "el 11 de noviembre de 2026?"
    )
    consulta_2 = "¿Y después de las 18:00? Incluye cuánto dura."

    print("\nCLIENTE A / TURNO 1:", consulta_1)
    respuesta_1 = agente.invoke({"entrada": consulta_1}, config=config_a)
    print("RESPUESTA:", respuesta_1["output"])
    assert len(obtener_historial(cliente_a).messages) == 2

    print("\nCLIENTE A / TURNO 2:", consulta_2)
    respuesta_2 = agente.invoke({"entrada": consulta_2}, config=config_a)
    print("RESPUESTA:", respuesta_2["output"])
    assert len(obtener_historial(cliente_a).messages) == 4

    llamadas = [
        accion.tool_input
        for accion, _ in respuesta_2["intermediate_steps"]
        if accion.tool == "consultar_disponibilidad_con_filtros"
    ]
    for accion, observacion in respuesta_2["intermediate_steps"]:
        print("TRAZA:", accion.tool, accion.tool_input, "->", observacion)

    assert any(
        isinstance(args, dict)
        and args.get("fecha") == "2026-11-11"
        and args.get("servicio") == "corte"
        and args.get("hora_desde") == "18:00"
        and args.get("incluir_duracion") is True
        for args in llamadas
    ), "No se comprobó que el agente recuperara el contexto de A."

    assert len(obtener_historial(cliente_b).messages) == 0
    consulta_b = (
        "¿Qué servicio y fecha te mencioné antes en ESTA conversación? "
        "Si no te mencioné ninguno, dilo; no inventes."
    )
    print("\nCLIENTE B / TURNO 1:", consulta_b)
    respuesta_b = agente.invoke({"entrada": consulta_b}, config=config_b)
    print("RESPUESTA:", respuesta_b["output"])
    assert len(obtener_historial(cliente_b).messages) == 2
    assert len(obtener_historial(cliente_a).messages) == 4
    assert obtener_historial(cliente_b).messages[0].content == consulta_b

    # Inspección de todas las acciones de B: no debe ejecutar una consulta
    # con los valores concretos de A, porque su historial está vacío.
    for accion, observacion in respuesta_b["intermediate_steps"]:
        print("TRAZA CLIENTE B:", accion.tool, accion.tool_input, "->", observacion)
        args = accion.tool_input
        if isinstance(args, dict):
            assert not (
                args.get("fecha") == "2026-11-11"
                and args.get("servicio") == "corte"
            ), "La sesión B reutilizó argumentos exclusivos de A."

    print("\nB22/L3: AGENTE INTEGRADO Y SESIONES AISLADAS VERIFICADOS.")
    cerrar_sesion(cliente_a)
    cerrar_sesion(cliente_b)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--agente",
        action="store_true",
        help="Ejecuta además 3 turnos reales con Gemini (consume API).",
    )
    args = parser.parse_args()
    probar_integracion_sin_api()
    if args.agente:
        probar_integracion_con_gemini()


if __name__ == "__main__":
    main()
