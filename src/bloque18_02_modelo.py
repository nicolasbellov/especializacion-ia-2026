"""U2.3 · Bloque 18 · Lección 1: PromptTemplate conectado con Gemini.

Ejecutar desde la raíz del repositorio:
    python .\\src\\bloque18_02_modelo.py

Realiza UNA llamada real a la API (puede consumir cuota).
La clave se lee desde .env y nunca se imprime.
"""

import os

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


def main() -> None:
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "tu_llave_aqui":
        raise SystemExit(
            "Falta una API key válida. Configura GEMINI_API_KEY en .env "
            "(sin subir ese archivo a GitHub)."
        )

    # Reutilizamos la selección de modelo del cliente del Módulo 1.
    nombre_modelo = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    modelo = ChatGoogleGenerativeAI(
        model=nombre_modelo,
        temperature=0,
    )

    plantilla = PromptTemplate.from_template(
        "Explica el concepto de {tema} en un párrafo, "
        "para alguien que recién empieza en {area}."
    )

    # LCEL: la salida de la plantilla se entrega automáticamente al modelo.
    cadena_simple = plantilla | modelo

    print(f"Modelo configurado: {nombre_modelo}")
    print("Invocando una vez a Gemini...")
    respuesta = cadena_simple.invoke(
        {"tema": "embeddings", "area": "búsqueda semántica"}
    )

    print("\nRespuesta de Gemini:")
    print(respuesta.text)
    print(f"Tipo de respuesta: {type(respuesta).__name__}")


if __name__ == "__main__":
    main()
