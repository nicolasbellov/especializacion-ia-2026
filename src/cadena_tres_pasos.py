"""U2.3 - Bloque 18 / Actividad 20344: chain original de tres pasos.

Caso ficticio: análisis, validación y comunicación de una incidencia de
TrakCare Analytics. No contiene datos clínicos ni accede a sistemas reales.

Desde la raíz del repositorio:
    python -m src.cadena_tres_pasos

Hace tres llamadas reales a Gemini (puede consumir cuota).
"""

import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


INCIDENCIA_FICTICIA = (
    "CASO FICTICIO PARA LA ESPECIALIZACIÓN (NO ES UN INCIDENTE REAL). "
    "En un ambiente simulado de TrakCare Analytics, el tablero de urgencias "
    "presenta 36 atenciones del 02/11/2026, pero una extracción de la fuente "
    "simulada contiene 42 episodios para esa misma fecha. La diferencia se "
    "observa después de una actualización nocturna del cubo analítico. "
    "Todavía no se han comparado los filtros por estado de episodio, "
    "zona horaria ni rango de fechas. No hay causa raíz confirmada ni "
    "se han realizado correcciones."
)


def construir_cadena(modelo):
    """Construye la cadena sin ejecutarla; permite inyectar un modelo falso."""
    # Paso 1: interpretar y clasificar la incidencia sin inventar diagnósticos.
    plantilla_analisis = PromptTemplate.from_template(
        "Eres analista técnico de sistemas de información de salud. "
        "Lee la incidencia ficticia y entrega: (1) categoría del problema, "
        "(2) hechos observables, (3) datos faltantes para investigarlo. "
        "Distingue hechos de sospechas y no declares una causa raíz. "
        "Responde en texto breve y estructurado.\n\n{incidencia}"
    )

    # Paso 2: planificar validaciones a partir del análisis anterior.
    plantilla_validacion = PromptTemplate.from_template(
        "A partir EXCLUSIVAMENTE del siguiente análisis, propone tres "
        "verificaciones técnicas de solo lectura, en orden, para investigar "
        "la diferencia. No afirmes que las verificaciones se ejecutaron, "
        "ni propongas cambios en datos de origen.\n\n{analisis}"
    )

    # Paso 3: comunicar el plan como un informe operativo trazable.
    plantilla_informe = PromptTemplate.from_template(
        "Convierte el siguiente plan preliminar en un informe Markdown "
        "para el equipo de implementación. Incluye un breve objetivo, "
        "tres validaciones sugeridas y una nota de que se trata de "
        "hipótesis sin causa raíz confirmada. No inventes pruebas ni "
        "resultados ejecutados. No agregues hechos ajenos al plan.\n\n{plan}"
    )

    analisis = plantilla_analisis | modelo | StrOutputParser()
    validacion = plantilla_validacion | modelo | StrOutputParser()
    informe = plantilla_informe | modelo | StrOutputParser()

    return (
        analisis
        | (lambda texto_analisis: {"analisis": texto_analisis})
        | validacion
        | (lambda texto_plan: {"plan": texto_plan})
        | informe
    )


def main():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "tu_llave_aqui":
        raise SystemExit("Configura GEMINI_API_KEY en .env, sin subirla a GitHub.")

    modelo_id = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    modelo = ChatGoogleGenerativeAI(model=modelo_id)
    cadena = construir_cadena(modelo)

    print("Actividad 20344 | Caso ficticio: consistencia de indicador de urgencias")
    print(f"Modelo: {modelo_id} | llamadas previstas: 3")
    resultado = cadena.invoke({"incidencia": INCIDENCIA_FICTICIA})
    assert isinstance(resultado, str), "La cadena debe devolver texto plano."
    print("\nINFORME FINAL:\n")
    print(resultado)
    print(f"\nSalida compatible con str: {isinstance(resultado, str)}")


if __name__ == "__main__":
    main()
