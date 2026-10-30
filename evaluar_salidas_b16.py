"""U2.2 / Bloque 16, leccion 3: evaluar y guardar respuestas reales.

Reutiliza resultados_b15.json (respuestas reales ya obtenidas del cliente).
No realiza llamadas nuevas a Gemini ni necesita API key.

Ejecucion desde la raiz del proyecto:
    python evaluar_salidas_b16.py
"""

import json
from pathlib import Path

from metricas_texto import calcular_precision_cobertura_f1
from pipeline_texto import procesar_texto


def calcular_metricas(
    texto_referencia: str, texto_respuesta: str
) -> dict[str, float]:
    """Integra preprocesamiento y metricas de coincidencia lexica."""
    return calcular_precision_cobertura_f1(
        procesar_texto(texto_referencia),
        procesar_texto(texto_respuesta),
    )


def evaluar_respuestas(casos: list[dict]) -> list[dict]:
    """Evalua las respuestas REALES guardadas por el cliente en Bloque 15."""
    resultados = []

    for posicion, caso in enumerate(casos, start=1):
        consulta = caso["consulta"]
        referencia = caso["referencia"]
        respuesta = caso["respuesta_real"]

        metricas = calcular_metricas(referencia, respuesta)
        resultados.append(
            {
                "caso": caso.get("caso", posicion),
                "consulta": consulta,
                "referencia": referencia,
                "respuesta": respuesta,
                **metricas,
            }
        )

    return resultados


def resumir_metricas(resultados: list[dict]) -> dict[str, float]:
    """Promedios por caso (macro), no puntajes de correccion factual."""
    if not resultados:
        return {
            "precision_promedio": 0.0,
            "cobertura_promedio": 0.0,
            "f1_promedio": 0.0,
        }

    cantidad = len(resultados)
    return {
        "precision_promedio": sum(
            caso["precision"] for caso in resultados
        ) / cantidad,
        "cobertura_promedio": sum(
            caso["cobertura"] for caso in resultados
        ) / cantidad,
        "f1_promedio": sum(caso["f1"] for caso in resultados) / cantidad,
    }


def peores_casos(resultados: list[dict], cantidad: int = 3) -> list[dict]:
    """Ordena por F1 ascendente; no equivale a ordenar por calidad real."""
    if cantidad < 0:
        raise ValueError("cantidad no puede ser negativa")
    return sorted(resultados, key=lambda caso: caso["f1"])[:cantidad]


def guardar_resultados(resultados: list[dict], ruta: Path) -> None:
    """Guarda respuestas, referencias y metricas para auditoria posterior."""
    ruta.write_text(
        json.dumps(resultados, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    carpeta = Path(__file__).resolve().parent
    origen = carpeta / "resultados_b15.json"
    destino = carpeta / "resultados_metricas.json"

    casos = json.loads(origen.read_text(encoding="utf-8"))
    resultados = evaluar_respuestas(casos)
    guardar_resultados(resultados, destino)

    print("Bloque 16 L3 | Respuestas reales reutilizadas, sin API")
    for caso in resultados:
        print(
            f"[Caso {caso['caso']}] {caso['consulta']} | "
            f"P={caso['precision']:.1%} "
            f"R={caso['cobertura']:.1%} "
            f"F1={caso['f1']:.1%}"
        )

    resumen = resumir_metricas(resultados)
    print(
        "\nPromedio: "
        f"P={resumen['precision_promedio']:.1%} "
        f"R={resumen['cobertura_promedio']:.1%} "
        f"F1={resumen['f1_promedio']:.1%}"
    )
    print("\nCasos prioritarios para revision (F1 ascendente):")
    for caso in peores_casos(resultados):
        print(f"  {caso['consulta']} -> F1={caso['f1']:.1%}")

    print(f"\nEvidencia guardada en: {destino}")
    print("Advertencia: F1 mide coincidencia de tokens, no calidad semantica.")


if __name__ == "__main__":
    main()
