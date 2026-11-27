import time


def consultar(pregunta):
    """Simulacro del servicio, sin modelo ni red."""
    time.sleep(0.01)
    if "devol" in pregunta.lower():
        return {
            "respuesta": "Tienes 30 dias desde la compra para devolver.",
            "fuentes": ["manual.pdf"],
        }
    return {
        "respuesta": "No encuentro esa informacion en el manual.",
        "fuentes": [],
    }


def ca_01():
    r = consultar("Cual es el plazo para devolver un producto?")
    return set(r) == {"respuesta", "fuentes"}, f"campos: {sorted(r)}"


def ca_02():
    r = consultar("Cual es el plazo para devolver un producto?")
    ok = "manual.pdf" in r["fuentes"] and "30 dias" in r["respuesta"]
    return ok, f"fuentes: {r['fuentes']}"


def ca_03():
    r = consultar("Venden gift cards?")
    ok = r["fuentes"] == [] and r["respuesta"].startswith("No encuentro")
    return ok, f"fuentes: {r['fuentes']}"


def ca_05():
    tiempos = []
    for _ in range(10):
        inicio = time.perf_counter()
        consultar("Cual es el plazo para devolver un producto?")
        tiempos.append(time.perf_counter() - inicio)
    rapidas = sum(1 for t in tiempos if t < 5)
    return rapidas >= 9, f"{rapidas} de 10 en menos de 5 s"


CRITERIOS = [
    ("CA-01", "RF-01", "respuesta JSON con respuesta y fuentes", ca_01),
    ("CA-02", "RF-02", "fuente manual.pdf y menciona 30 dias", ca_02),
    ("CA-03", "RF-02", "sin informacion en el manual: no inventa", ca_03),
    ("CA-05", "RNF-01", "9 de 10 consultas en menos de 5 s", ca_05),
]


def ejecutar(criterios):
    fallidos = 0
    for id_, cubre, descripcion, prueba in criterios:
        try:
            ok, evidencia = prueba()
        except Exception as error:
            ok = False
            evidencia = f"error: {type(error).__name__}({error})"
        estado = "PASA " if ok else "FALLA"
        print(f"{estado} {id_} ({cubre}) {descripcion} -> {evidencia}")
        fallidos += 0 if ok else 1
    cumplidos = len(criterios) - fallidos
    print(f"\n{cumplidos} de {len(criterios)} criterios cumplidos")


if __name__ == "__main__":
    ejecutar(CRITERIOS)
