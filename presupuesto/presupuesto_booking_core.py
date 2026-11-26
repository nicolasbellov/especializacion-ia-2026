"""Adaptacion academica del presupuesto; sin APIs, redes ni datos reales."""
import argparse
import math

import presupuesto_alcance as pa


def tarea(id_, nombre, horas, capa, tipo, novedad=False):
    return dict(id=id_, nombre=nombre, horas=horas, capa=capa,
                tipo=tipo, novedad=novedad, sistema_real=False)


# Estimaciones provisionales de construccion, no horas medidas.
# T-DOCKER contabiliza RNF-05; no es un nuevo RF.
TAREAS = [
    tarea("RF-01", "Endpoint JSON y contrato", 2, "api", "imprescindible", True),
    tarea("RF-02", "Integrar RAG, fuentes y trace_id", 2, "rag", "imprescindible"),
    tarea("RF-03", "Integrar abstencion y controles existentes", 1, "rag", "imprescindible"),
    tarea("RF-04", "Disponibilidad ficticia, datos y enrutamiento", 2, "otra", "imprescindible"),
    tarea("T-DOCKER", "Contenedor y configuracion reproducible", 2, "contenedor", "imprescindible", True),
    tarea("RF-05", "Exponer supervision de cancelacion ficticia", 2, "otra", "deseable", True),
]
EXCLUIDAS = {
    "RF-06": "requiere sistemas y datos reales",
    "RF-07": "frontend propio fuera del alcance acordado",
}


def evaluar(horas):
    if not math.isfinite(horas) or horas <= 0 or round(horas * 0.5, 2) <= 0:
        raise ValueError("Las horas deben ser positivas, finitas y suficientes para un presupuesto no nulo")
    # Reutilizar heuristica del curso sin dejar su configuracion modificada.
    anterior = pa.HORAS_DISPONIBLES
    try:
        pa.HORAS_DISPONIBLES = horas
        neto = pa.presupuesto()
        dentro, fuera, usado = pa.recortar(TAREAS)
    finally:
        pa.HORAS_DISPONIBLES = anterior
    ids = {f["id"] for f in dentro}
    requeridas = {f["id"] for f in TAREAS if f["tipo"] == "imprescindible"}
    faltantes = requeridas - ids
    capas_faltantes = pa.CAPAS_OBLIGATORIAS - {f["capa"] for f in dentro}
    return dict(neto=neto, usado=usado, dentro=dentro, fuera=fuera,
                faltantes=faltantes, capas_faltantes=capas_faltantes,
                viable=not faltantes and not capas_faltantes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--horas", type=float, required=True,
                        help="Horas efectivas disponibles para laboratorio y evidencia")
    args = parser.parse_args()
    try:
        r = evaluar(args.horas)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"Horas disponibles (escenario): {args.horas:g}")
    print(f"Construccion: {r['neto']:.1f} h | Pruebas/docs/defensa: {args.horas * pa.RESERVA_PRUEBAS_DOCS:.1f} h | Imprevistos: {args.horas * pa.MARGEN_IMPREVISTOS:.1f} h")
    print(f"Seleccion heuristica: {r['usado']:.1f} h")
    for f in r["dentro"]:
        print(f"  {f['id']} {f['nombre']}: {pa.horas_reales(f):.1f} h ({f['tipo']})")
    for f, motivo in r["fuera"]:
        print(f"  NO {f['id']}: {motivo}")
    for id_, motivo in EXCLUIDAS.items():
        print(f"  EXCLUIDA {id_}: {motivo}")
    if not r["viable"]:
        print("NO VIABLE: renegociar; no aprobar una seleccion parcial.")
        print("Imprescindibles faltantes:", ", ".join(sorted(r["faltantes"])) or "ninguno")
        print("Capas faltantes:", ", ".join(sorted(r["capas_faltantes"])) or "ninguna")
        return 2
    print("VIABLE SEGUN ESTIMACIONES: no equivale a validacion tecnica.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
