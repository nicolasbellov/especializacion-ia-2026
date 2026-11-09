"""U2.4 / B22-L2: memoria conversacional para Booking Core AI.

Lección basada en RunnableWithMessageHistory (API del curso).
Todas las consultas utilizan datos SIMULADOS del Bloque 21.
No accede a Supabase ni realiza reservas.

Uso (desde la raíz del repositorio):
    python -m src.memoria_b22_booking_core
    python -m src.memoria_b22_booking_core --agente
"""

from __future__ import annotations

import argparse
import os
from typing import Any

from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI

from src.agente_b21_booking_core import consultar_servicios
from src.herramienta_b22_booking_core import consultar_disponibilidad_detallada


# Almacenamiento VOLÁTIL, sólo durante la vida del proceso Python.
historiales: dict[str, InMemoryChatMessageHistory] = {}


def obtener_historial(session_id: str) -> InMemoryChatMessageHistory:
    """Obtiene o crea el historial de una sesión concreta."""
    if session_id not in historiales:
        historiales[session_id] = InMemoryChatMessageHistory()
    return historiales[session_id]


def cerrar_sesion(session_id: str) -> None:
    """Limpia los mensajes de una sesión de esta ejecución."""
    historiales.pop(session_id, None)


def _texto_visible(salida: Any) -> str:
    """Normaliza a texto la respuesta, que Gemini puede entregar por bloques."""
    if isinstance(salida, str):
        return salida
    if isinstance(salida, list):
        return "\n".join(
            bloque.get("text", "") if isinstance(bloque, dict) else bloque
            for bloque in salida
            if isinstance(bloque, str)
            or (isinstance(bloque, dict) and bloque.get("type") == "text")
        )
    return str(salida)


def _normalizar_respuesta(resultado: dict[str, Any]) -> dict[str, Any]:
    """Garantiza que la memoria guarde un AIMessage de texto, no bloques JSON."""
    normalizado = dict(resultado)
    normalizado["output"] = _texto_visible(resultado["output"])
    return normalizado


def envolver_con_memoria(ejecutor: Any) -> RunnableWithMessageHistory:
    """Conecta un ejecutor al historial de sesión, incluyendo normalización."""
    # En nuestras pruebas anteriores Gemini devolvió bloques con signature.
    # RunnableWithMessageHistory espera un str o BaseMessage como output.
    pipeline = ejecutor | RunnableLambda(_normalizar_respuesta)
    return RunnableWithMessageHistory(
        pipeline,
        obtener_historial,
        input_messages_key="entrada",
        history_messages_key="chat_history",
        output_messages_key="output",
    )


def crear_agente_con_memoria() -> RunnableWithMessageHistory:
    """Construye agente clásico y reutiliza herramientas de Booking Core AI."""
    load_dotenv()
    modelo = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    )
    herramientas = [consultar_servicios, consultar_disponibilidad_detallada]
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Eres Booking Core AI en un laboratorio de DEMOSTRACIÓN. "
                "Todos los precios, servicios y horarios son ficticios. "
                "Responde en español, no inventes disponibilidad ni reservas. "
                "Usa consultar_disponibilidad_con_filtros para horarios y "
                "consultar_servicios para catálogo/precios. "
                "El historial anterior permite interpretar referencias como "
                "'y después de las 18:00' conservando la fecha y el servicio. "
                "Si esa información no existe en el historial ni en la "
                "pregunta actual, pide aclaración. "
                "No puedes crear, cancelar ni modificar reservas."
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{entrada}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
    agente = create_tool_calling_agent(modelo, herramientas, prompt)
    ejecutor = AgentExecutor(
        agent=agente,
        tools=herramientas,
        verbose=True,
        return_intermediate_steps=True,
        max_iterations=4,
    )
    return envolver_con_memoria(ejecutor)


def probar_memoria_sin_api() -> None:
    """Comprueba almacenamiento, aislamiento y limpieza sin usar Gemini."""
    def responder_simulado(entrada: dict[str, Any]) -> dict[str, str]:
        return {
            "output": (
                "Mensaje recibido; "
                f"mensajes anteriores={len(entrada['chat_history'])}"
            )
        }

    demo = RunnableWithMessageHistory(
        RunnableLambda(responder_simulado),
        obtener_historial,
        input_messages_key="entrada",
        history_messages_key="chat_history",
        output_messages_key="output",
    )
    sesion_a, sesion_b = "prueba_a_b22", "prueba_b_b22"
    cerrar_sesion(sesion_a)
    cerrar_sesion(sesion_b)

    config_a = {"configurable": {"session_id": sesion_a}}
    primero = demo.invoke({"entrada": "Quiero un corte"}, config=config_a)
    assert "mensajes anteriores=0" in primero["output"]
    assert len(obtener_historial(sesion_a).messages) == 2
    print("SESIÓN A / TURNO 1: 2 mensajes guardados (usuario + asistente)")

    segundo = demo.invoke(
        {"entrada": "Y después de las 18:00"},
        config=config_a,
    )
    assert "mensajes anteriores=2" in segundo["output"]
    assert len(obtener_historial(sesion_a).messages) == 4
    print("SESIÓN A / TURNO 2: 4 mensajes guardados")

    assert obtener_historial(sesion_b).messages == []
    print("SESIÓN B: historial independiente, 0 mensajes")

    # Gemini puede devolver listas de bloques con una firma; no guardarla.
    bloques = [
        {"type": "text", "text": "Mensaje del agente", "extras": {"signature": "x"}}
    ]
    assert _texto_visible(bloques) == "Mensaje del agente"
    print("NORMALIZACIÓN: texto sin metadatos del proveedor")

    cerrar_sesion(sesion_a)
    assert sesion_a not in historiales
    cerrar_sesion(sesion_b)
    print("LIMPIEZA: sesiones eliminadas")
    print("\nB22/L2: PRUEBAS DE MEMORIA SIN API CORRECTAS.")


def probar_memoria_con_gemini() -> None:
    """Dos turnos reales: en el segundo se omiten fecha y servicio."""
    sesion = "cliente_demo_memoria_b22"
    cerrar_sesion(sesion)
    agente = crear_agente_con_memoria()
    config = {"configurable": {"session_id": sesion}}

    pregunta_1 = (
        "¿Qué horarios SIMULADOS hay para un corte de cabello "
        "el 11 de noviembre de 2026?"
    )
    print(f"\nTURNO 1: {pregunta_1}")
    respuesta_1 = agente.invoke({"entrada": pregunta_1}, config=config)
    print("RESPUESTA 1:\n", respuesta_1["output"])
    mensajes_1 = len(obtener_historial(sesion).messages)
    print("MENSAJES GUARDADOS:", mensajes_1)
    assert mensajes_1 == 2, "El primer turno no se conservó en el historial."

    pregunta_2 = "¿Y después de las 18:00? Incluye cuánto dura."
    print(f"\nTURNO 2: {pregunta_2}")
    respuesta_2 = agente.invoke({"entrada": pregunta_2}, config=config)
    print("RESPUESTA 2:\n", respuesta_2["output"])
    print("TRAZA DEL SEGUNDO TURNO:")

    llamadas_disponibilidad = []
    for accion, observacion in respuesta_2["intermediate_steps"]:
        print(f"- {accion.tool} {accion.tool_input} -> {observacion}")
        if accion.tool == "consultar_disponibilidad_con_filtros":
            llamadas_disponibilidad.append(accion.tool_input)

    assert any(
        isinstance(argumentos, dict)
        and argumentos.get("fecha") == "2026-11-11"
        and argumentos.get("servicio") == "corte"
        and argumentos.get("hora_desde") == "18:00"
        and argumentos.get("incluir_duracion") is True
        for argumentos in llamadas_disponibilidad
    ), "No se verificó que el segundo turno recuperara fecha y servicio."

    mensajes_2 = len(obtener_historial(sesion).messages)
    print("MENSAJES GUARDADOS:", mensajes_2)
    assert mensajes_2 == 4, "El segundo turno no quedó guardado."
    print("\nB22/L2: CONTEXTO ENTRE DOS INTERACCIONES VERIFICADO.")
    cerrar_sesion(sesion)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--agente",
        action="store_true",
        help="Además ejecuta dos turnos reales con Gemini (consume cuota/API).",
    )
    args = parser.parse_args()
    probar_memoria_sin_api()
    if args.agente:
        probar_memoria_con_gemini()


if __name__ == "__main__":
    main()
