"""U2.4 · Bloque 21 · Actividad práctica: agente Booking Core AI.

Prototipo académico con dos herramientas propias y datos SIMULADOS.
No consulta Booking Core, no conecta con Supabase y no crea reservas.
"""

from __future__ import annotations

import os
import re
import unicodedata
from datetime import date

from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI


# Datos ficticios creados exclusivamente para el laboratorio.
SERVICIOS_SIMULADOS = {
    "corte": {"nombre": "Corte de cabello", "precio_clp": 15000, "duracion_min": 40},
    "barba": {"nombre": "Perfilado de barba", "precio_clp": 10000, "duracion_min": 20},
    "corte_barba": {
        "nombre": "Corte de cabello y barba",
        "precio_clp": 22000,
        "duracion_min": 60,
    },
}

AGENDA_SIMULADA = {
    "2026-11-11": {
        "corte": ["10:00", "16:00", "18:30"],
        "barba": ["11:00", "17:00"],
        "corte_barba": ["12:00", "19:00"],
    },
    "2026-11-12": {
        "corte": ["09:30", "18:00"],
        "barba": ["14:00"],
        "corte_barba": ["15:30"],
    },
}


def _normalizar(texto: str) -> str:
    """Normaliza palabras de servicio sin depender del LLM."""
    limpio = unicodedata.normalize("NFKD", texto.lower().strip())
    return "".join(c for c in limpio if not unicodedata.combining(c))


def _identificar_servicio(consulta: str) -> str | None:
    """Mapea descripciones habituales a uno de los tres IDs simulados."""
    texto = _normalizar(consulta)
    if not texto:
        return None
    if texto in SERVICIOS_SIMULADOS:
        return texto
    if "combo" in texto or ("corte" in texto and "barba" in texto):
        return "corte_barba"
    if "barba" in texto:
        return "barba"
    if any(palabra in texto for palabra in ("corte", "cabello", "pelo")):
        return "corte"
    return None


@tool
def consultar_servicios(servicio: str = "") -> str:
    """Consulta PRECIOS, DURACIONES y CATALOGO de servicios de la barbería ficticia.

    Usa esta herramienta si el usuario pregunta cuánto cuesta un servicio,
    cuánto dura o qué servicios hay. Para horarios usa consultar_disponibilidad.
    El argumento 'servicio' puede ser 'corte', 'barba', 'corte_barba' o vacío
    si el usuario quiere conocer todo el catálogo.
    """
    if not isinstance(servicio, str):
        return "Error: el servicio debe ser texto."

    servicio_id = _identificar_servicio(servicio)
    if not servicio.strip():
        seleccion = list(SERVICIOS_SIMULADOS.items())
    elif servicio_id:
        seleccion = [(servicio_id, SERVICIOS_SIMULADOS[servicio_id])]
    else:
        return "Servicio no encontrado en el catálogo SIMULADO. Opciones: corte, barba, corte_barba."

    filas = [
        f"{datos['nombre']} (id={clave}): "
        f"${datos['precio_clp']:,} CLP; {datos['duracion_min']} minutos."
        for clave, datos in seleccion
    ]
    return "CATÁLOGO SIMULADO (precios de ejemplo, no reales): " + " | ".join(filas)


@tool
def consultar_disponibilidad(fecha: str, servicio: str) -> str:
    """Consulta HORARIOS DISPONIBLES de un servicio en una AGENDA FICTICIA.

    Usa esta herramienta cuando el usuario pide horarios, cupos o disponibilidad.
    'fecha' debe tener formato AAAA-MM-DD (por ejemplo 2026-11-11).
    'servicio' puede ser 'corte', 'barba' o 'corte_barba'.
    No utiliza reservas reales ni crea o modifica citas.
    """
    try:
        if not isinstance(fecha, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fecha):
            return "Error: fecha inválida. Usa AAAA-MM-DD."
        date.fromisoformat(fecha)
        if not isinstance(servicio, str):
            return "Error: servicio inválido."
        servicio_id = _identificar_servicio(servicio)
        if servicio_id is None:
            return "Error: servicio desconocido. Opciones: corte, barba, corte_barba."

        agenda_dia = AGENDA_SIMULADA.get(fecha)
        if agenda_dia is None:
            return (
                f"No hay datos SIMULADOS para {fecha}. "
                "Esto no significa que no existan horas en Booking Core."
            )
        horarios = agenda_dia.get(servicio_id, [])
        if not horarios:
            return (
                f"No hay horarios SIMULADOS cargados para {servicio_id} el {fecha}. "
                "No representa disponibilidad real."
            )
        return (
            f"AGENDA SIMULADA: {SERVICIOS_SIMULADOS[servicio_id]['nombre']}, "
            f"fecha {fecha}, horarios: {', '.join(horarios)}. "
            "Estos cupos son ficticios; no constituyen reservas reales."
        )
    except ValueError:
        return "Error: la fecha no existe en el calendario. Usa AAAA-MM-DD."


def _texto_visible(salida: object) -> str:
    """Extrae solo el texto, incluso si Gemini devuelve bloques con metadatos."""
    if isinstance(salida, str):
        return salida
    if isinstance(salida, list):
        return "\n".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in salida
            if isinstance(item, str) or (isinstance(item, dict) and item.get("type") == "text")
        )
    return str(salida)


def crear_ejecutor() -> AgentExecutor:
    """Configura Gemini, las herramientas y la captura de pasos intermedios."""
    load_dotenv()
    modelo = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    )
    herramientas = [consultar_servicios, consultar_disponibilidad]
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Eres Booking Core AI, un asistente de una barbería de PRUEBA. "
                "TODOS los precios y horarios son datos SIMULADOS, no reales. "
                "Responde en español y nunca inventes precios, cupos ni reservas. "
                "Para consultas de precio o duración usa consultar_servicios. "
                "Para consultas solo de horas disponibles usa directamente "
                "consultar_disponibilidad, sin consultar antes el catálogo. "
                "Si falta una fecha concreta, pide que la especifiquen. "
                "No puedes reservar, cancelar ni modificar citas."
            ),
            ("human", "{entrada}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
    agente = create_tool_calling_agent(modelo, herramientas, prompt)
    return AgentExecutor(
        agent=agente,
        tools=herramientas,
        verbose=True,
        return_intermediate_steps=True,
        max_iterations=4,
    )


def ejecutar_caso(
    ejecutor: AgentExecutor, pregunta: str, herramienta_esperada: str
) -> None:
    """Realiza una prueba MANUAL real con Gemini y verifica intermediate_steps."""
    print(f"\nPREGUNTA: {pregunta}")
    resultado = ejecutor.invoke({"entrada": pregunta})
    pasos = resultado["intermediate_steps"]
    nombres = [accion.tool for accion, _ in pasos]

    print("\nRESPUESTA:")
    print(_texto_visible(resultado["output"]))
    print("\nTRAZA ESTRUCTURADA:")
    for accion, observacion in pasos:
        print(f"- {accion.tool} {accion.tool_input} -> {observacion}")

    # No solo comprobamos el texto: validamos qué herramienta decidió usar.
    if not nombres or set(nombres) != {herramienta_esperada}:
        raise AssertionError(
            f"Se esperaba solo {herramienta_esperada!r}; "
            f"el agente usó {nombres!r}."
        )
    print(f"VALIDACIÓN MANUAL: OK (herramienta: {herramienta_esperada})")


def main() -> None:
    """Ejecuta dos escenarios, uno por cada herramienta propia."""
    ejecutor = crear_ejecutor()
    ejecutar_caso(
        ejecutor,
        "En esta barbería de prueba, ¿cuánto cuesta un corte de cabello?",
        "consultar_servicios",
    )
    ejecutar_caso(
        ejecutor,
        "¿Qué horarios simulados hay para un corte el 11 de noviembre de 2026?",
        "consultar_disponibilidad",
    )
    print("\nACTIVIDAD B21: DOS VALIDACIONES MANUALES CORRECTAS.")


if __name__ == "__main__":
    main()
