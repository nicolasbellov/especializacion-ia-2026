"""U2.3 · Bloque 18 · Lección 2: chain de tres pasos con LangChain.

Ejecutar desde la raíz del repositorio:
    python .\\src\\bloque18_03_chain_tres_pasos.py
    python .\\src\\bloque18_03_chain_tres_pasos.py --pasos

Ambos modos hacen TRES llamadas a Gemini, que pueden consumir cuota.
El modo --pasos muestra resultados intermedios para facilitar la depuración.
"""

import argparse
import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


TEXTO_PRUEBA = (
    "Los modelos de lenguaje grandes generan texto prediciendo un token "
    "a la vez, basándose en el texto que ya generaron antes. Cada token "
    "puede ser una palabra completa, parte de una palabra o un signo "
    "de puntuación. Antes de generar una respuesta, el texto de entrada "
    "se divide en tokens mediante un proceso llamado tokenización."
)


def crear_pasos(modelo: ChatGoogleGenerativeAI):
    """Devuelve tres pasos que reciben diccionarios y producen texto plano."""
    plantilla_extraccion = PromptTemplate.from_template(
        "Lee el siguiente texto y devuelve solo sus 3 puntos "
        "clave, uno por línea, sin desarrollarlos:\n\n{texto}"
    )
    plantilla_simplificacion = PromptTemplate.from_template(
        "Reescribe estos puntos en lenguaje simple, sin jerga "
        "técnica, para alguien sin conocimientos previos:\n\n{puntos}"
    )
    plantilla_formato = PromptTemplate.from_template(
        "Convierte este texto en una lista de viñetas markdown, "
        "de máximo 3 líneas, sin introducción:\n\n{texto_simple}"
    )

    # El parser elimina el contenedor AIMessage y conserva solo el texto.
    paso_extraccion = plantilla_extraccion | modelo | StrOutputParser()
    paso_simplificacion = plantilla_simplificacion | modelo | StrOutputParser()
    paso_formato = plantilla_formato | modelo | StrOutputParser()
    return paso_extraccion, paso_simplificacion, paso_formato


def main() -> None:
    argumento = argparse.ArgumentParser(description=__doc__)
    argumento.add_argument(
        "--pasos",
        action="store_true",
        help="Ejecutar y mostrar las tres etapas por separado",
    )
    args = argumento.parse_args()

    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "tu_llave_aqui":
        raise SystemExit("Configura GEMINI_API_KEY en .env antes de ejecutar.")

    nombre_modelo = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    modelo = ChatGoogleGenerativeAI(model=nombre_modelo, temperature=0)
    extraccion, simplificacion, formato = crear_pasos(modelo)

    print(f"Modelo: {nombre_modelo}")
    print("Se realizarán tres llamadas a Gemini.\n")

    if args.pasos:
        puntos = extraccion.invoke({"texto": TEXTO_PRUEBA})
        assert isinstance(puntos, str)
        print("PASO 1 — Extracción:\n", puntos, "\n", sep="")

        simple = simplificacion.invoke({"puntos": puntos})
        assert isinstance(simple, str)
        print("PASO 2 — Simplificación:\n", simple, "\n", sep="")

        resultado = formato.invoke({"texto_simple": simple})
    else:
        # Cada lambda adapta un string a la clave que exige el prompt siguiente.
        cadena_tres_pasos = (
            extraccion
            | (lambda puntos: {"puntos": puntos})
            | simplificacion
            | (lambda texto_simple: {"texto_simple": texto_simple})
            | formato
        )
        resultado = cadena_tres_pasos.invoke({"texto": TEXTO_PRUEBA})

    assert isinstance(resultado, str)
    print("PASO 3 — Resultado final en Markdown:\n", resultado, sep="")
    print(f"\nTipo de salida: {type(resultado).__name__}")


if __name__ == "__main__":
    main()
