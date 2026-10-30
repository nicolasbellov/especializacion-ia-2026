"""B17 Core: muestra de 5 F1 bajos + 5 altos, evaluada por una persona.

No llama a Gemini ni asigna juicios automáticos.
    python core_b17_revisar.py --preparar
    python core_b17_revisar.py --revisar
    python core_b17_revisar.py --validar
    python core_b17_revisar.py --informe

Guarda después de cada caso. Mantiene valoraciones ya registradas.
"""

import argparse
from datetime import date
import json
from pathlib import Path

from core_b17_generar import (
    ORIGEN_B15, DESTINO_CORE, construir_base,
    leer_json, validar_guardados, guardar_json_atomico,
)
from revision_cualitativa_b17 import preparar_revision, validar_revision


RAIZ = Path(__file__).resolve().parent
DESTINO_REVISION = RAIZ / "revision_manual_core_b17.json"
DESTINO_INFORME = RAIZ / "docs" / "revision_manual_core_b17.md"
TERNARIOS = {"si", "no", "parcialmente"}
BINARIOS = {"si", "no"}


def construir_muestra_core(resultados: list[dict]) -> list[dict]:
    ids = [r["caso"] for r in resultados]
    if len(resultados) != 20 or set(ids) != set(range(1, 21)):
        raise ValueError("Se requieren 20 casos reales únicos antes de revisar")
    muestra = preparar_revision(resultados, por_extremo=5)
    if len(muestra) != 10 or len({r["caso"] for r in muestra}) != 10:
        raise ValueError("La muestra debe tener 10 casos sin duplicados")
    return [{**r, "fecha_revision": None} for r in muestra]


def leer_o_preparar(ruta: Path, muestra: list[dict]) -> list[dict]:
    """No sobrescribe valoraciones existentes ni acepta corpus modificado."""
    if not ruta.exists():
        guardar_json_atomico(ruta, muestra)
        return muestra
    guardados = leer_json(ruta)
    if len(guardados) != 10:
        raise ValueError("La muestra guardada requiere 10 casos")
    for actual, esperado in zip(guardados, muestra):
        for clave in ("caso", "consulta", "referencia", "respuesta", "f1"):
            if actual.get(clave) != esperado[clave]:
                raise ValueError("El corpus cambió: proteger la revisión previa")
        if not validar_revision(actual):
            raise ValueError(f"Rúbrica inválida en caso {actual['caso']}")
        fecha = actual.get("fecha_revision")
        if actual["correccion_factual"] is None and fecha is not None:
            raise ValueError("No registrar fecha de revisión inexistente")
        if actual["correccion_factual"] is not None and not (
            isinstance(fecha, str) and fecha
        ):
            raise ValueError("Caso revisado sin fecha")
    return guardados


def contar_revisados(registros: list[dict]) -> int:
    return sum(r["correccion_factual"] is not None for r in registros)


def elegir(nombre: str, opciones: set[str]) -> str:
    while True:
        valor = input(f"{nombre} ({'/'.join(sorted(opciones))}): ").strip().lower()
        if valor in opciones:
            return valor
        print("Opción inválida: vuelve a ingresar el valor.")


def pedir_juicio(caso: dict) -> dict:
    print("\n" + "=" * 70)
    print(f"Caso {caso['caso']} | F1={caso['f1']:.1%}")
    print("Consulta:", caso["consulta"])
    print("Referencia:", caso["referencia"])
    print("Respuesta REAL:", caso["respuesta"])
    factual = elegir("Corrección factual", TERNARIOS)
    completitud = elegir("Completitud", TERNARIOS)
    contradiccion = elegir("Contradicción", BINARIOS)
    nota = ""
    while not nota:
        nota = input("Justificación (obligatoria): ").strip()
    registro = {
        **caso,
        "correccion_factual": factual,
        "completitud": completitud,
        "contradiccion": contradiccion,
        "justificacion": nota,
        "fecha_revision": date.today().isoformat(),
    }
    if not validar_revision(registro):
        raise ValueError("Juicio humano inválido")
    return registro


def redactar_informe(registros: list[dict]) -> str:
    """Transcribe fielmente los juicios humanos, sin reinterpretarlos."""
    if len(registros) != 10 or contar_revisados(registros) != 10:
        raise ValueError("Se requieren 10 juicios humanos terminados")
    if not all(validar_revision(r) and r.get("fecha_revision") for r in registros):
        raise ValueError("Hay registros inválidos")
    lineas = [
        "# B17 Core — Revisión cualitativa de respuestas reales",
        "",
        "**Fuente:** resultados_core_b17.json; 20 respuestas reales "
        "(3 originales B15 y 17 nuevas B17 Core).",
        "**Muestra:** cinco F1 menores y cinco F1 mayores, "
        "10 casos únicos revisados con la rúbrica de Skillnest.",
        "**Importante:** todos los juicios y notas siguientes se "
        "transcribieron desde revisión_manual_core_b17.json; "
        "no se generaron automáticamente.",
        "",
        "| Caso | F1 | Corrección factual | Completitud | Contradicción | Fecha |",
        "| ---: | ---: | --- | --- | --- | --- |",
    ]
    for r in registros:
        lineas.append(
            f"| {r['caso']} | {r['f1']:.1%} | "
            f"{r['correccion_factual']} | {r['completitud']} | "
            f"{r['contradiccion']} | {r['fecha_revision']} |"
        )
    lineas.extend(["", "## Evidencia por caso", ""])
    for r in registros:
        lineas.extend([
            f"### Caso {r['caso']} — F1 {r['f1']:.1%}",
            "",
            f"**Consulta:** {r['consulta']}",
            "",
            f"**Referencia:** {r['referencia']}",
            "",
            f"**Respuesta real:** {r['respuesta']}",
            "",
            f"**Rúbrica:** corrección factual {r['correccion_factual']}; "
            f"completitud {r['completitud']}; "
            f"contradicción {r['contradiccion']}.",
            "",
            f"**Justificación humana:** {r['justificacion']}",
            "",
        ])
    lineas.extend([
        "## Para documentar los hallazgos",
        "",
        "Relacionar cada modo de falla observado con un caso "
        "y una nota concreta en el documento de límites. "
        "F1 por sí solo no demuestra corrección ni error.",
        "",
    ])
    return "\n".join(lineas)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    acciones = parser.add_mutually_exclusive_group(required=True)
    for accion in ("preparar", "revisar", "validar", "informe"):
        acciones.add_argument(f"--{accion}", action="store_true")
    args = parser.parse_args()

    base = construir_base(leer_json(ORIGEN_B15))
    resultados = validar_guardados(leer_json(DESTINO_CORE), base)
    registros = leer_o_preparar(
        DESTINO_REVISION, construir_muestra_core(resultados)
    )
    print(f"Corpus: 20/20; muestra 10; "
          f"juicios humanos: {contar_revisados(registros)}/10")
    print("Casos: " + ", ".join(str(r["caso"]) for r in registros))

    if args.preparar:
        print(f"Plantilla lista, no sobrescrita: {DESTINO_REVISION}")
        return

    if args.revisar:
        for i, registro in enumerate(registros):
            if registro["correccion_factual"] is not None:
                continue
            try:
                registros[i] = pedir_juicio(registro)
            except (KeyboardInterrupt, EOFError):
                print("\nInterrumpido. Se conservaron las revisiones previas.")
                raise SystemExit(1) from None
            guardar_json_atomico(DESTINO_REVISION, registros)
            print(f"Guardado: {contar_revisados(registros)}/10")
        print("Rúbrica terminada. Sigue con --validar y --informe.")
        return

    if contar_revisados(registros) != 10:
        raise SystemExit(
            f"INCOMPLETO: {contar_revisados(registros)}/10 revisiones humanas."
        )

    if args.validar:
        print("VÁLIDO: 20 respuestas reales y 10 revisiones humanas justificadas.")
        print("Pendiente: documentar modos de falla propios en límites de métrica.")
        return

    if args.informe:
        DESTINO_INFORME.parent.mkdir(parents=True, exist_ok=True)
        DESTINO_INFORME.write_text(
            redactar_informe(registros), encoding="utf-8"
        )
        print(f"Informe humano creado: {DESTINO_INFORME}")


if __name__ == "__main__":
    main()
