"""Skillnest U2.2 / Bloque 16: precision, cobertura y F1 por tokens.

Reutiliza las respuestas reales guardadas en resultados_b15.json.
No llama a Gemini ni necesita credenciales.

Ejecutar desde la raiz: python metricas_texto.py
"""

import json
from collections import Counter
from pathlib import Path

from pipeline_texto import procesar_texto


def contar_coincidencias(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> int:
    """Cuenta el solapamiento de tokens respetando sus repeticiones."""
    for nombre, tokens in (
        ("tokens_referencia", tokens_referencia),
        ("tokens_respuesta", tokens_respuesta),
    ):
        if not isinstance(tokens, list) or any(
            not isinstance(token, str) for token in tokens
        ):
            raise TypeError(f"{nombre} debe ser una lista de str")

    conteo_referencia = Counter(tokens_referencia)
    conteo_respuesta = Counter(tokens_respuesta)
    interseccion = conteo_referencia & conteo_respuesta
    return sum(interseccion.values())


def calcular_precision_cobertura_f1(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> dict[str, float]:
    """Mide coincidencia lexica, no correccion factual ni semantica."""
    coincidencias = contar_coincidencias(tokens_referencia, tokens_respuesta)

    if not tokens_referencia or not tokens_respuesta:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    precision = coincidencias / len(tokens_respuesta)
    cobertura = coincidencias / len(tokens_referencia)
    f1 = (
        2 * precision * cobertura / (precision + cobertura)
        if precision + cobertura > 0
        else 0.0
    )
    return {"precision": precision, "cobertura": cobertura, "f1": f1}


def calcular_metricas_casos(
    casos: list[dict],
) -> list[dict]:
    """Recalcula las tres metricas a partir de respuestas ya guardadas."""
    resultados = []
    for caso in casos:
        referencia = procesar_texto(caso["referencia"])
        respuesta = procesar_texto(caso["respuesta_real"])
        metricas = calcular_precision_cobertura_f1(referencia, respuesta)
        resultados.append(
            {
                "caso": caso["caso"],
                "consulta": caso["consulta"],
                "tokens_referencia": len(referencia),
                "tokens_respuesta": len(respuesta),
                "coincidencias": contar_coincidencias(referencia, respuesta),
                **metricas,
            }
        )
    return resultados


def main() -> None:
    origen = Path(__file__).with_name("resultados_b15.json")
    casos = json.loads(origen.read_text(encoding="utf-8"))
    resultados = calcular_metricas_casos(casos)

    print("Bloque 16 | Precision, cobertura y F1 (sin llamadas a Gemini)")
    for item in resultados:
        print(
            f"[Caso {item['caso']}] "
            f"ref={item['tokens_referencia']} "
            f"respuesta={item['tokens_respuesta']} "
            f"coincidencias={item['coincidencias']} | "
            f"precision={item['precision']:.1%} "
            f"cobertura={item['cobertura']:.1%} "
            f"f1={item['f1']:.1%}"
        )

    print(
        "\nAviso: las metricas son lexicas; no prueban calidad "
        "semantica ni exactitud factual."
    )


if __name__ == "__main__":
    main()
