"""U2.4 / B23-L1: supervision humana de acciones de riesgo alto.

Laboratorio 100% SIMULADO de cancelacion de reservas Booking Core AI.
No importa clientes, no conecta a Supabase y no modifica reservas reales.

Ejecutar desde la raiz del repositorio:
    python -m src.supervision_b23_booking_core
    python -m src.supervision_b23_booking_core --interactivo
    python -m src.supervision_b23_booking_core --agente
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Literal

from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool, tool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field, ValidationError


EstadoDecision = Literal[
    "aprobado", "rechazado", "timeout", "sin_terminal",
    "sin_supervisor", "error_aprobador"
]


@dataclass(frozen=True)
class DecisionSupervisor:
    """Respuesta de un canal independiente del modelo de IA."""

    estado: EstadoDecision
    origen: str

    @property
    def aprobado(self) -> bool:
        return self.estado == "aprobado"


@dataclass
class EntornoReservasDemo:
    """Datos ficticios y bitacora volatiles de esta ejecucion."""

    reservas: dict[str, str] = field(
        default_factory=lambda: {
            "DEMO-001": "confirmada",
            "DEMO-002": "confirmada",
        }
    )
    registro_aprobaciones: list[dict[str, object]] = field(default_factory=list)
    # Impide que un agente solicite repetidamente autorizacion tras un rechazo.
    intentos_de_cancelacion: set[str] = field(default_factory=set)


Aprobador = Callable[[str], DecisionSupervisor]


class ArgumentosCancelacion(BaseModel):
    """Argumentos que el modelo puede proponer, nunca la autorizacion."""

    reserva_id: str = Field(
        description="Identificador de reserva FICTICIA, por ejemplo DEMO-001.",
        pattern=r"^DEMO-\d{3}$",
    )
    motivo: str = Field(
        description="Breve motivo de la cancelacion simulada.",
        default="Cambio de planes",
        min_length=3,
        max_length=120,
    )


def _mensaje_seguro(texto: str) -> str:
    """Evita saltos y controles de terminal en textos generados por un modelo."""
    return re.sub(r"[\x00-\x1f\x7f]", " ", texto).strip()


def esperar_aprobacion_con_timeout(
    mensaje: str, tiempo_limite_segundos: float = 60
) -> DecisionSupervisor:
    """Pide una autorizacion de consola; ante error o timeout, rechaza.

    Windows: msvcrt.kbhit/getwch, porque select.select NO espera stdin aqui.
    Linux/macOS: select.select sobre stdin. No se usan hilos bloqueados.
    """
    if tiempo_limite_segundos <= 0:
        return DecisionSupervisor("timeout", "consola_demo")
    if not sys.stdin.isatty():
        return DecisionSupervisor("sin_terminal", "consola_demo")

    print(mensaje + " ¿Aprobar? (s/n): ", end="", flush=True)

    if os.name == "nt":
        import msvcrt

        caracteres: list[str] = []
        limite = time.monotonic() + tiempo_limite_segundos
        while time.monotonic() < limite:
            if not msvcrt.kbhit():
                time.sleep(0.05)
                continue
            tecla = msvcrt.getwch()
            if tecla in ("\x00", "\xe0"):
                # Saltar secuencias de teclas especiales (flechas, F-keys).
                msvcrt.getwch()
                continue
            if tecla in ("\r", "\n"):
                print()
                estado = "aprobado" if "".join(caracteres).strip().lower() == "s" else "rechazado"
                return DecisionSupervisor(estado, "consola_demo")
            if tecla in ("\b", "\x7f"):
                if caracteres:
                    caracteres.pop()
                    print("\b \b", end="", flush=True)
                continue
            if tecla == "\x03":
                print("\nCancelado desde teclado.")
                return DecisionSupervisor("rechazado", "consola_demo")
            if tecla.isprintable() and len(caracteres) < 8:
                caracteres.append(tecla)
                print(tecla, end="", flush=True)
        print("\nTiempo de aprobacion agotado: no autorizado.")
        return DecisionSupervisor("timeout", "consola_demo")

    import select

    listo, _, _ = select.select([sys.stdin], [], [], tiempo_limite_segundos)
    if not listo:
        print("\nTiempo de aprobacion agotado: no autorizado.")
        return DecisionSupervisor("timeout", "consola_demo")
    respuesta = sys.stdin.readline()
    estado = "aprobado" if respuesta.strip().lower() == "s" else "rechazado"
    return DecisionSupervisor(estado, "consola_demo")


def crear_herramientas(
    entorno: EntornoReservasDemo,
    aprobador: Aprobador | None = None,
) -> tuple[BaseTool, BaseTool]:
    """Separa consulta de cancelacion y mantiene el aprobador FUERA del LLM."""

    @tool("consultar_reserva_simulada")
    def consultar_reserva(reserva_id: str) -> str:
        """Consulta el estado de una reserva FICTICIA. Solo lectura.

        Utilizar para preguntas sobre si una reserva de prueba sigue vigente.
        No requiere aprobacion para acceder a esta informacion inventada.
        """
        estado = entorno.reservas.get(reserva_id)
        if estado is None:
            return "No existe esa reserva en el entorno SIMULADO."
        return f"Reserva FICTICIA {reserva_id}: estado {estado}."

    @tool("cancelar_reserva_simulada", args_schema=ArgumentosCancelacion)
    def cancelar_reserva(reserva_id: str, motivo: str = "Cambio de planes") -> str:
        """Solicita cancelar una reserva FICTICIA, accion de riesgo alto.

        Usar solo si se solicita expresamente cancelar una reserva. Antes de
        cambiar el estado requiere aprobacion externa, nunca del propio LLM.
        """
        estado_actual = entorno.reservas.get(reserva_id)
        if estado_actual is None:
            return "No existe esa reserva en el entorno SIMULADO."
        if estado_actual != "confirmada":
            return f"Reserva FICTICIA {reserva_id}: ya esta {estado_actual}."
        if reserva_id in entorno.intentos_de_cancelacion:
            return (
                f"La cancelacion de {reserva_id} ya fue presentada al "
                "supervisor en esta prueba. No se repetira automaticamente."
            )

        motivo_visible = _mensaje_seguro(motivo)
        mensaje = (
            f"ACCION SIMULADA: cancelar {reserva_id} "
            f"(estado actual: confirmada). Motivo: {motivo_visible}."
        )
        entorno.intentos_de_cancelacion.add(reserva_id)

        try:
            decision = (
                aprobador(mensaje) if aprobador is not None
                else DecisionSupervisor("sin_supervisor", "sin_canal")
            )
            if not isinstance(decision, DecisionSupervisor):
                decision = DecisionSupervisor("error_aprobador", "canal_invalido")
        except (Exception, KeyboardInterrupt):
            # Un fallo del canal de aprobacion nunca habilita una escritura.
            decision = DecisionSupervisor("error_aprobador", "canal_fallido")

        ejecutada = False
        if decision.aprobado and entorno.reservas.get(reserva_id) == "confirmada":
            # UNICA mutacion: diccionario ficticio del proceso Python.
            entorno.reservas[reserva_id] = "cancelada"
            ejecutada = True

        entorno.registro_aprobaciones.append(
            {
                "herramienta": "cancelar_reserva_simulada",
                "argumentos": {
                    "reserva_id": reserva_id,
                    "motivo": motivo_visible,
                },
                "aprobado": decision.aprobado,
                "decision": decision.estado,
                "origen": decision.origen,
                "ejecutada": ejecutada,
                "momento_utc": datetime.now(timezone.utc).isoformat(),
            }
        )

        if not ejecutada:
            return (
                f"Cancelacion SIMULADA de {reserva_id} NO ejecutada. "
                f"Decision: {decision.estado}."
            )
        return (
            f"Reserva FICTICIA {reserva_id} marcada cancelada "
            "en memoria tras aprobacion externa de prueba. "
            "No hubo cambios en Booking Core real."
        )

    return consultar_reserva, cancelar_reserva


def _aprobador_de_prueba(estado: EstadoDecision) -> Aprobador:
    """Doble de prueba; NO es una autorizacion humana ni de produccion."""
    return lambda _mensaje: DecisionSupervisor(estado, "doble_prueba")


def probar_sin_api() -> None:
    """Cubre rechazo, timeout, falta de supervisor y aprobacion ficticia."""
    args = {"reserva_id": "DEMO-001", "motivo": "Cambio de planes"}

    entorno_denegado = EntornoReservasDemo()
    consulta, cancelar = crear_herramientas(
        entorno_denegado, _aprobador_de_prueba("rechazado")
    )
    assert "confirmada" in consulta.invoke({"reserva_id": "DEMO-001"})
    assert "NO ejecutada" in cancelar.invoke(args)
    assert entorno_denegado.reservas["DEMO-001"] == "confirmada"
    assert entorno_denegado.registro_aprobaciones[0]["aprobado"] is False
    assert entorno_denegado.registro_aprobaciones[0]["ejecutada"] is False
    # Un segundo intento automatico no vuelve a pedir aprobacion.
    assert "No se repetira" in cancelar.invoke(args)
    assert len(entorno_denegado.registro_aprobaciones) == 1
    print("RECHAZO OK: no se cancela ni se repite la solicitud.")

    entorno_sin_canal = EntornoReservasDemo()
    _, cancelar_sin_canal = crear_herramientas(entorno_sin_canal)
    assert "sin_supervisor" in cancelar_sin_canal.invoke(args)
    assert entorno_sin_canal.reservas["DEMO-001"] == "confirmada"
    assert esperar_aprobacion_con_timeout("DEMO", 0).estado == "timeout"
    print("SIN CANAL/TIMEOUT OK: rechazo por defecto.")

    entorno_aprobado = EntornoReservasDemo()
    _, cancelar_aprobado = crear_herramientas(
        entorno_aprobado, _aprobador_de_prueba("aprobado")
    )
    assert "marcada cancelada" in cancelar_aprobado.invoke(args)
    assert entorno_aprobado.reservas["DEMO-001"] == "cancelada"
    assert entorno_aprobado.registro_aprobaciones[0]["ejecutada"] is True
    assert entorno_aprobado.registro_aprobaciones[0]["origen"] == "doble_prueba"
    print("APROBACION FICTICIA OK: solo cambia el diccionario demo.")

    try:
        cancelar_aprobado.invoke(
            {"reserva_id": "REAL-001", "motivo": "Prueba de rechazo"}
        )
    except ValidationError:
        print("PYDANTIC OK: rechaza un identificador fuera de DEMO-###.")
    else:
        raise AssertionError("El esquema deberia rechazar un ID no ficticio.")

    print("REGISTRO DE AUDITORIA (ejemplo de prueba):")
    for registro in entorno_aprobado.registro_aprobaciones:
        print(registro)
    print("\nB23/L1: CONTROLES DE APROBACION SIMULADA VERIFICADOS.")


def probar_interactivo(tiempo_limite_segundos: float) -> None:
    """Solicita s/n a una persona en la consola local, sin usar Gemini."""
    entorno = EntornoReservasDemo()
    _, cancelar = crear_herramientas(
        entorno,
        lambda mensaje: esperar_aprobacion_con_timeout(
            mensaje, tiempo_limite_segundos
        ),
    )
    print("DEMO INTERACTIVA: no hay integraciones ni reservas reales.")
    print(cancelar.invoke({
        "reserva_id": "DEMO-001", "motivo": "Solicitud de prueba"
    }))
    print("ESTADO FINAL:", entorno.reservas["DEMO-001"])
    print("AUDITORIA:", entorno.registro_aprobaciones)


def probar_con_agente(tiempo_limite_segundos: float) -> None:
    """Permite a Gemini PROPONER la cancelacion, no aprobarla."""
    entorno = EntornoReservasDemo()
    herramientas = crear_herramientas(
        entorno,
        lambda mensaje: esperar_aprobacion_con_timeout(
            mensaje, tiempo_limite_segundos
        ),
    )
    load_dotenv()
    modelo = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Eres Booking Core AI en un laboratorio 100% FICTICIO. "
                "Dispones de una herramienta de consulta y otra para "
                "cancelacion SIMULADA. Si el usuario pide expresamente "
                "cancelar DEMO-001, usa cancelar_reserva_simulada. "
                "El control externo decide si se ejecuta; tu no puedes "
                "aprobar ni omitir ese control. "
                "No afirmes que existen reservas reales. Responde en espanol."
            ),
            ("human", "{entrada}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
    agente = create_tool_calling_agent(modelo, list(herramientas), prompt)
    ejecutor = AgentExecutor(
        agent=agente,
        tools=list(herramientas),
        return_intermediate_steps=True,
        verbose=True,
        max_iterations=3,
    )
    resultado = ejecutor.invoke({
        "entrada": (
            "Por favor, cancela la reserva ficticia DEMO-001. "
            "Motivo: cambio de planes."
        )
    })
    print("\nTRAZA DE EJECUCION:")
    for accion, observacion in resultado["intermediate_steps"]:
        print(accion.tool, accion.tool_input, "->", observacion)

    assert any(
        accion.tool == "cancelar_reserva_simulada"
        for accion, _ in resultado["intermediate_steps"]
    ), "Gemini no solicito la herramienta de cancelacion simulada."
    assert len(entorno.registro_aprobaciones) == 1, (
        "Se esperaba exactamente una decision registrada."
    )
    registro = entorno.registro_aprobaciones[0]
    assert registro["ejecutada"] is (
        registro["aprobado"] is True
    ), "Estado y autorizacion no concuerdan."
    assert entorno.reservas["DEMO-001"] == (
        "cancelada" if registro["aprobado"] else "confirmada"
    )
    print("ESTADO FINAL DEMO-001:", entorno.reservas["DEMO-001"])
    print("AUDITORIA:", registro)
    print("\nB23/L1: SUPERVISION DEL AGENTE VERIFICADA.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    modos = parser.add_mutually_exclusive_group()
    modos.add_argument(
        "--interactivo",
        action="store_true",
        help="Pide s/n en consola, sin Gemini, para una cancelacion ficticia.",
    )
    modos.add_argument(
        "--agente",
        action="store_true",
        help="Gemini solicita cancelacion demo y la persona autoriza o rechaza.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Segundos maximos para la confirmacion interactiva (por defecto: 60).",
    )
    opciones = parser.parse_args()
    if not 0 < opciones.timeout <= 300:
        parser.error("--timeout debe estar entre 0 y 300 segundos.")

    if opciones.interactivo:
        probar_interactivo(opciones.timeout)
    elif opciones.agente:
        probar_con_agente(opciones.timeout)
    else:
        probar_sin_api()


if __name__ == "__main__":
    main()
