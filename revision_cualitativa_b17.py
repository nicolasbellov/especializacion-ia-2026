"""Skillnest U2.2 / Bloque 17 L1: muestra y rúbrica cualitativa.

Usa exclusivamente resultados_metricas.json, generado en el Bloque 16.
No consulta el modelo. No califica automáticamente las respuestas.
Ejecución: python revision_cualitativa_b17.py

La plantilla se crea SOLO si no existe: nunca sobrescribe juicios humanos.
"""

import json
from pathlib import Path


def seleccionar_muestra(
    resultados: list[dict], por_extremo: int = 5
) -> list[dict]:
    """Selecciona F1 bajos y altos sin duplicar respuestas.

    Con hasta 2*por_extremo casos se revisan todos (nuestras tres
    respuestas reales quedan incluidas una sola vez).
    """
    if por_extremo < 1:
        raise ValueError("por_extremo debe ser positivo")

    ordenados = sorted(resultados, key=lambda caso: caso["f1"])
    if len(ordenados) <= 2 * por_extremo:
        seleccion = ordenados
    else:
        seleccion = ordenados[:por_extremo] + ordenados[-por_extremo:]

    ids = [caso["caso"] for caso in seleccion]
    if len(ids) != len(set(ids)):
        raise ValueError("Se encontraron identificadores de caso duplicados")
    return seleccion


def preparar_revision(resultados: list[dict], por_extremo: int = 5) -> list[dict]:
    """Crea la plantilla a partir de respuestas reales, sin emitir juicios."""
    muestra = seleccionar_muestra(resultados, por_extremo)
    return [
        {
            "caso": caso["caso"],
            "consulta": caso["consulta"],
            "referencia": caso["referencia"],
            "respuesta": caso["respuesta"],
            "f1": caso["f1"],
            "correccion_factual": None,
            "completitud": None,
            "contradiccion": None,
            "justificacion": "",
        }
        for caso in muestra
    ]


def validar_revision(registro: dict) -> bool:
    """Valida estructura mínima de una evaluación humana.

    Corrección factual/completitud: si, no, parcialmente.
    Contradicción: si, no. None indica que la revisión aún es pendiente.
    Si se informa un juicio, se requieren los tres y una justificación.
    """
    campos = ("correccion_factual", "completitud", "contradiccion")
    valores = [registro[campo] for campo in campos]
    if all(valor is None for valor in valores):
        return registro["justificacion"] == ""

    if any(valor is None for valor in valores):
        return False

    return (
        registro["correccion_factual"] in {"si", "no", "parcialmente"}
        and registro["completitud"] in {"si", "no", "parcialmente"}
        and registro["contradiccion"] in {"si", "no"}
        and isinstance(registro["justificacion"], str)
        and bool(registro["justificacion"].strip())
    )


def guardar_plantilla_si_no_existe(ruta: Path, registros: list[dict]) -> bool:
    """No pierde anotaciones previas: nunca reemplaza una plantilla existente."""
    with ruta.open("x", encoding="utf-8") as archivo:
        json.dump(registros, archivo, indent=2, ensure_ascii=False)
        archivo.write("\n")
    return True


def main() -> None:
    carpeta = Path(__file__).resolve().parent
    origen = carpeta / "resultados_metricas.json"
    destino = carpeta / "revision_cualitativa_b17.json"
    resultados = json.loads(origen.read_text(encoding="utf-8"))
    registros = preparar_revision(resultados)

    print("Bloque 17 L1 | Rúbrica cualitativa, sin Gemini")
    for caso in registros:
        print(
            f"[Caso {caso['caso']}] F1={caso['f1']:.1%} | "
            f"{caso['consulta']}"
        )
    print("Rúbrica: corrección factual, completitud y contradicción.")
    if destino.exists():
        guardados = json.loads(destino.read_text(encoding="utf-8"))
        if not isinstance(guardados, list) or not all(
            validar_revision(caso) for caso in guardados
        ):
            raise ValueError("La revisión existente contiene campos inválidos")
        print(f"Archivo existente preservado sin cambios: {destino}")
    else:
        guardar_plantilla_si_no_existe(destino, registros)
        print(f"Plantilla creada, juicios pendientes: {destino}")

    print("Revisa cada referencia y respuesta; NO interpretes F1 como veracidad.")


if __name__ == "__main__":
    main()
