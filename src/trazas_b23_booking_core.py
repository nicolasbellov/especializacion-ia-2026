"""U2.4/B23-L2: trazas de decisiones de Booking Core AI en formato JSONL.

Registro academico con datos 100% SIMULADOS, sin acceso a Booking Core real.

    python -m src.trazas_b23_booking_core
    python -m src.trazas_b23_booking_core --agente

Salida: trazas_agente_b23.jsonl (ignorada por Git).
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ARCHIVO_TRAZAS = Path("trazas_agente_b23.jsonl")
HERRAMIENTAS_ALTO_RIESGO = {"cancelar_reserva_simulada"}


def _texto_visible(contenido: Any) -> str:
    """Solo texto de salidas del LLM; excluye signatures y otros metadatos."""
    if isinstance(contenido, str):
        return contenido
    if isinstance(contenido, list):
        return "\n".join(
            item["text"] for item in contenido
            if isinstance(item, dict) and item.get("type") == "text"
            and isinstance(item.get("text"), str)
        )
    return str(contenido)


def registrar_traza(
    session_id: str,
    entrada: str,
    resultado: dict[str, Any],
    archivo: Path = ARCHIVO_TRAZAS,
    aprobaciones: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Escribe una interaccion completa como UNA linea JSON UTF-8.

    'aprobaciones' debe venir del control EXTERNO de supervision,
    nunca de una respuesta ni argumento generado por el modelo.
    """
    acciones = []
    for accion, observacion in resultado.get("intermediate_steps", []):
        acciones.append(
            {
                "herramienta": accion.tool,
                "argumentos": accion.tool_input,
                "observacion": _texto_visible(observacion),
            }
        )

    # Solo exportamos los campos explicitamente producidos por la herramienta
    # de supervision; no recolectamos cadenas internas del proveedor.
    decisiones = []
    for decision in aprobaciones or []:
        decisiones.append(
            {
                clave: decision.get(clave)
                for clave in (
                    "herramienta", "argumentos", "aprobado", "decision",
                    "origen", "ejecutada", "momento_utc",
                )
            }
        )

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "entrada": entrada,
        "acciones": acciones,
        "aprobaciones": decisiones,
        "respuesta_final": _texto_visible(resultado.get("output", "")),
    }
    archivo = Path(archivo)
    archivo.parent.mkdir(parents=True, exist_ok=True)
    with archivo.open("a", encoding="utf-8") as destino:
        destino.write(json.dumps(registro, ensure_ascii=False) + "\n")
    return registro


def revisar_trazas(archivo: Path = ARCHIVO_TRAZAS) -> dict[str, int]:
    """Marca candidatos a revision; no determina automaticamente culpabilidad."""
    archivo = Path(archivo)
    resumen = {
        "registros": 0,
        "repeticiones": 0,
        "alto_riesgo": 0,
        "sin_registro_aprobacion": 0,
        "inconsistencias": 0,
        "lineas_invalidas": 0,
    }
    try:
        origen = archivo.open(encoding="utf-8")
    except FileNotFoundError:
        print(f"Archivo no encontrado: {archivo}. Primero registra una traza.")
        return resumen

    with origen:
        for numero, linea in enumerate(origen, 1):
            if not linea.strip():
                continue
            try:
                registro = json.loads(linea)
                if not isinstance(registro, dict):
                    raise ValueError("registro no es un objeto JSON")
                acciones = registro.get("acciones", [])
                aprobaciones = registro.get("aprobaciones", [])
                if not isinstance(acciones, list) or not isinstance(aprobaciones, list):
                    raise ValueError("acciones/aprobaciones deben ser listas")
            except (ValueError, TypeError) as exc:
                resumen["lineas_invalidas"] += 1
                print(f"REVISAR FORMATO: linea {numero}: {exc}")
                continue

            resumen["registros"] += 1
            sesion = registro.get("session_id", "desconocida")
            nombres = [
                item.get("herramienta", "")
                for item in acciones if isinstance(item, dict)
            ]
            if any(a == b for a, b in zip(nombres, nombres[1:])):
                resumen["repeticiones"] += 1
                print(f"REVISAR REPETICION: linea {numero}, sesion {sesion}")

            for accion in acciones:
                if not isinstance(accion, dict):
                    continue
                if accion.get("herramienta") not in HERRAMIENTAS_ALTO_RIESGO:
                    continue
                resumen["alto_riesgo"] += 1
                args = accion.get("argumentos", {})
                print(
                    f"REVISAR ALTO RIESGO: linea {numero}, sesion {sesion}, "
                    f"herramienta {accion['herramienta']}"
                )
                # Correlacion por herramienta y reserva (no se infiere
                # aprobacion a partir del texto del modelo).
                reserva_id = args.get("reserva_id") if isinstance(args, dict) else None
                correlativas = [
                    ap for ap in aprobaciones if isinstance(ap, dict)
                    and ap.get("herramienta") == accion["herramienta"]
                    and isinstance(ap.get("argumentos"), dict)
                    and ap["argumentos"].get("reserva_id") == reserva_id
                ]
                if not correlativas:
                    resumen["sin_registro_aprobacion"] += 1
                    print("  FALTA AUDITORIA: no hay una decision correlativa.")
                for ap in correlativas:
                    if ap.get("ejecutada") is True and ap.get("aprobado") is not True:
                        resumen["inconsistencias"] += 1
                        print("  INCONSISTENCIA: ejecucion sin aprobacion valida.")

    print("RESUMEN DE REVISION:", resumen)
    return resumen


def _paso(herramienta: str, argumentos: dict[str, Any]) -> SimpleNamespace:
    """Construye un paso sintético con la misma interfaz de AgentAction."""
    return SimpleNamespace(tool=herramienta, tool_input=argumentos)


def probar_sin_api(archivo: Path) -> None:
    """Guarda trazas de un laboratorio ficticio y comprueba su lectura."""
    from src.supervision_b23_booking_core import (
        DecisionSupervisor,
        EntornoReservasDemo,
        crear_herramientas,
    )

    entorno = EntornoReservasDemo()
    consultar, cancelar = crear_herramientas(
        entorno,
        lambda _mensaje: DecisionSupervisor("rechazado", "doble_prueba"),
    )

    args_consulta = {"reserva_id": "DEMO-001"}
    observacion = consultar.invoke(args_consulta)
    registrar_traza(
        "cliente_demo_consulta",
        "¿Cuál es el estado ficticio de DEMO-001?",
        {
            "output": "La reserva ficticia está confirmada.",
            "intermediate_steps": [
                (_paso("consultar_reserva_simulada", args_consulta), observacion)
            ],
        },
        archivo=archivo,
    )
    args_cancelar = {"reserva_id": "DEMO-001", "motivo": "Cambio de planes"}
    respuesta = cancelar.invoke(args_cancelar)
    assert entorno.reservas["DEMO-001"] == "confirmada"
    denegada = registrar_traza(
        "cliente_demo_denegado",
        "Cancela mi reserva ficticia DEMO-001.",
        {
            "output": respuesta,
            "intermediate_steps": [
                (_paso("cancelar_reserva_simulada", args_cancelar), respuesta)
            ],
        },
        archivo=archivo,
        aprobaciones=entorno.registro_aprobaciones,
    )
    assert denegada["aprobaciones"][0]["aprobado"] is False
    assert denegada["aprobaciones"][0]["ejecutada"] is False

    # Dos llamadas consecutivas a la misma herramienta: candidato a revision.
    registrar_traza(
        "cliente_demo_repeticion",
        "Consulta dos reservas ficticias.",
        {
            "output": "Ambas consultas son datos de demostración.",
            "intermediate_steps": [
                (
                    _paso("consultar_reserva_simulada", {"reserva_id": "DEMO-001"}),
                    "confirmada",
                ),
                (
                    _paso("consultar_reserva_simulada", {"reserva_id": "DEMO-002"}),
                    "confirmada",
                ),
            ],
        },
        archivo=archivo,
    )

    # Sin intermediate_steps no hay KeyError; se guarda lista vacia.
    sin_pasos = registrar_traza(
        "cliente_demo_sin_acciones",
        "Solo saluda.",
        {"output": "¡Hola!"},
        archivo=archivo,
    )
    assert sin_pasos["acciones"] == []

    # Registros sinteticos SIN auditoria: alerta a revisar, no una escritura real.
    registrar_traza(
        "cliente_demo_sin_auditoria",
        "Caso sintético de supervisión ausente (NO ejecutado).",
        {
            "output": "NO se realizó ningún cambio real ni ficticio.",
            "intermediate_steps": [
                (
                    _paso("cancelar_reserva_simulada", args_cancelar),
                    "Caso sintético sin registro de aprobación.",
                ),
            ],
        },
        archivo=archivo,
    )

    resumen = revisar_trazas(archivo)
    assert resumen["registros"] >= 5
    assert resumen["repeticiones"] >= 1
    assert resumen["alto_riesgo"] >= 2
    assert resumen["sin_registro_aprobacion"] >= 1
    assert resumen["inconsistencias"] == 0
    print(f"\nTRAZAS JSONL ESCRITAS EN: {archivo.resolve()}")
    print("B23/L2: REGISTRO Y ANALISIS DE TRAZAS SIN API VERIFICADOS.")


def probar_con_gemini(archivo: Path) -> None:
    """Traza real de Gemini; ninguna cancelación se autoriza sin supervisor."""
    from dotenv import load_dotenv
    from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_google_genai import ChatGoogleGenerativeAI
    from src.supervision_b23_booking_core import (
        EntornoReservasDemo,
        crear_herramientas,
    )

    entorno = EntornoReservasDemo()
    herramientas = list(crear_herramientas(entorno))  # Sin aprobador => denegar
    load_dotenv()
    modelo = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Eres Booking Core AI en un entorno 100% FICTICIO. "
                "Responde en español y utiliza cancelar_reserva_simulada "
                "cuando el usuario solicite cancelar una reserva ficticia. "
                "La herramienta controla la aprobación; no puedes aprobar "
                "la acción por ti mismo. No hay reservas reales."
            ),
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
        max_iterations=3,
    )
    entrada = "Cancela la reserva ficticia DEMO-001 por cambio de planes."
    resultado = ejecutor.invoke({"entrada": entrada})
    registro = registrar_traza(
        session_id="cliente_demo_gemini",
        entrada=entrada,
        resultado=resultado,
        archivo=archivo,
        aprobaciones=entorno.registro_aprobaciones,
    )
    assert any(
        accion["herramienta"] == "cancelar_reserva_simulada"
        for accion in registro["acciones"]
    ), "Gemini no selecciono la herramienta de cancelacion."
    assert entorno.reservas["DEMO-001"] == "confirmada"
    assert len(entorno.registro_aprobaciones) == 1
    assert entorno.registro_aprobaciones[0]["decision"] == "sin_supervisor"
    assert entorno.registro_aprobaciones[0]["ejecutada"] is False
    print("GEMINI: herramienta registrada y cancelacion bloqueada sin supervisor.")
    print("B23/L2: TRAZA REAL DE GEMINI PERSISTIDA.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--agente", action="store_true",
        help="Además guarda una invocación real a Gemini (consume API).",
    )
    parser.add_argument(
        "--archivo", type=Path, default=ARCHIVO_TRAZAS,
        help="Ruta del JSONL local (por defecto trazas_agente_b23.jsonl).",
    )
    args = parser.parse_args()
    probar_sin_api(args.archivo)
    if args.agente:
        probar_con_gemini(args.archivo)
        revisar_trazas(args.archivo)


if __name__ == "__main__":
    main()
