"""U2.4 / Bloque 21: agente con dos herramientas y traza de decisiones.

Laboratorio basado en la leccion de Skillnest. No accede al backend de
Booking Core AI ni utiliza datos reales de clientes o reservas.
"""

from __future__ import annotations

import ast
import operator
import os

from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI


@tool
def buscar_en_documentacion(consulta: str) -> str:
    """Busca informacion interna sobre reintentos y costos del cliente.

    Usa esta herramienta cuando la pregunta se refiera al funcionamiento
    documentado del cliente, los reintentos, los timeouts o los costos.
    """
    texto = consulta.lower()
    if any(palabra in texto for palabra in ("reintento", "reintenta", "timeout")):
        return (
            "El cliente reintenta hasta 3 veces ante un TimeoutError, "
            "con espera creciente."
        )
    if any(palabra in texto for palabra in ("costo", "coste", "token")):
        return (
            "El costo se calcula a partir de totalTokenCount, "
            "segun la tarifa vigente."
        )
    return "No se encontro informacion sobre esa consulta en la documentacion."


def _evaluar_aritmetica(expresion: str) -> int | float:
    """Evalua aritmetica basica mediante AST, sin ejecutar codigo Python."""
    if not expresion.strip() or len(expresion) > 80:
        raise ValueError("La expresion esta vacia o es demasiado larga.")

    operaciones = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    def evaluar(nodo: ast.AST) -> int | float:
        if isinstance(nodo, ast.Expression):
            return evaluar(nodo.body)
        if isinstance(nodo, ast.Constant) and type(nodo.value) in (int, float):
            if abs(nodo.value) > 1_000_000_000:
                raise ValueError("Numero fuera del limite permitido.")
            return nodo.value
        if isinstance(nodo, ast.UnaryOp) and type(nodo.op) in (ast.UAdd, ast.USub):
            valor = evaluar(nodo.operand)
            return valor if isinstance(nodo.op, ast.UAdd) else -valor
        if isinstance(nodo, ast.BinOp) and type(nodo.op) in operaciones:
            izquierda = evaluar(nodo.left)
            derecha = evaluar(nodo.right)
            resultado = operaciones[type(nodo.op)](izquierda, derecha)
            if abs(resultado) > 1_000_000_000_000:
                raise ValueError("Resultado fuera del limite permitido.")
            return resultado
        raise ValueError("Solo se permiten sumas, restas, productos y divisiones.")

    return evaluar(ast.parse(expresion, mode="eval"))


@tool
def calcular(expresion: str) -> str:
    """Calcula una expresion aritmetica simple, como '340 + 215'.

    Usa esta herramienta cuando la pregunta requiera un calculo numerico.
    """
    try:
        return str(_evaluar_aritmetica(expresion))
    except (SyntaxError, ValueError, ZeroDivisionError, OverflowError) as error:
        return f"Error al evaluar la expresion: {error}"


def crear_ejecutor() -> AgentExecutor:
    """Construye el agente con Gemini y habilita su traza estructurada."""
    load_dotenv()
    nombre_modelo = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    modelo = ChatGoogleGenerativeAI(model=nombre_modelo)
    herramientas = [buscar_en_documentacion, calcular]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Eres un asistente que responde preguntas usando las "
                "herramientas disponibles cuando las necesite. "
                "Si una herramienta devuelve un error, no inventes resultados.",
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


def main() -> None:
    """Ejecuta un caso que puede necesitar ambas herramientas."""
    ejecutor = crear_ejecutor()
    resultado = ejecutor.invoke(
        {
            "entrada": (
                "¿Cuantas veces reintenta el cliente, "
                "y cuanto seria eso multiplicado por 2?"
            )
        }
    )
    print("\nRESPUESTA FINAL:")
    print(resultado["output"])
    print("\nTRAZA ESTRUCTURADA:")
    for accion, observacion in resultado["intermediate_steps"]:
        print(accion.tool, accion.tool_input, "->", observacion)


if __name__ == "__main__":
    main()
