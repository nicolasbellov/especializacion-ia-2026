"""U2.2 / B16 L2: cuatro fallos interpretativos de F1 lexico.

Ejecutar: python ejemplos_limites_b16.py
Sin acceso a Internet ni consumo de Gemini.
"""

from metricas_texto import calcular_precision_cobertura_f1
from pipeline_texto import procesar_texto


CASOS = (
    {
        "nombre": "Sinónimos equivalentes (material Skillnest)",
        "referencia": "El auto es veloz.",
        "respuesta": "El vehículo es rápido.",
        "limite": "F1 penaliza palabras distintas aunque el significado sea equivalente.",
    },
    {
        "nombre": "Dato numérico diferente (material Skillnest)",
        "referencia": "Python fue creado en 1991.",
        "respuesta": "Python fue creado en 1989.",
        "limite": "Una fecha diferente apenas afecta la coincidencia léxica.",
    },
    {
        "nombre": "Negación omitida (material Skillnest)",
        "referencia": "Python no es un lenguaje compilado.",
        "respuesta": "Python es un lenguaje compilado.",
        "limite": "Quitar 'no' invierte la afirmación pero puede dejar F1 muy alto.",
    },
    {
        "nombre": "Negación agregada (pregunta del material Skillnest)",
        "referencia": "El congreso aprobó la ley por 45 votos a favor.",
        "respuesta": "El congreso no aprobó la ley por 45 votos a favor.",
        "limite": "Agregar 'no' invierte el sentido y el F1 permanece alto.",
    },
)


def evaluar(caso: dict[str, str]) -> dict[str, float]:
    return calcular_precision_cobertura_f1(
        procesar_texto(caso["referencia"]),
        procesar_texto(caso["respuesta"]),
    )


def main() -> None:
    print("Bloque 16 L2 | Límites del solapamiento léxico (sin API)")
    for indice, caso in enumerate(CASOS, start=1):
        valores = evaluar(caso)
        print(f"\n[Caso {indice}] {caso['nombre']}")
        print(f"Referencia: {caso['referencia']}")
        print(f"Respuesta:  {caso['respuesta']}")
        print(
            "Precisión={precision:.1%} Cobertura={cobertura:.1%} "
            "F1={f1:.1%}".format(**valores)
        )
        print(f"Límite: {caso['limite']}")


if __name__ == "__main__":
    main()
