"""U2.3 · Bloque 18 · Leccion 1: PromptTemplate.

Construye un prompt parametrizado sin hacer llamadas a Gemini.
Requiere langchain-core (instalado como dependencia de langchain).
"""

from langchain_core.prompts import PromptTemplate


def main() -> None:
    plantilla = PromptTemplate.from_template(
        "Explica el concepto de {tema} en un párrafo, "
        "para alguien que recién empieza en {area}."
    )

    prompt = plantilla.invoke(
        {"tema": "tokenización", "area": "procesamiento de texto"}
    )

    resultado_esperado = (
        "Explica el concepto de tokenización en un párrafo, "
        "para alguien que recién empieza en procesamiento de texto."
    )
    assert prompt.text == resultado_esperado, "El prompt no coincide con el esperado."
    print(prompt.text)


if __name__ == "__main__":
    main()
