"""Autoevaluación preliminar basada en la rúbrica S1; no es nota oficial."""
PESOS = {
    "pipeline_funcional": .25, "recuperacion_citacion": .15,
    "costo_latencia": .10, "personalizacion": .15,
    "observabilidad": .15, "seguridad_gobernanza": .20,
}
# Estimaciones conservadoras del diseño y evidencia histórica; revisar al cerrar Windows.
PUNTAJES = {
    "pipeline_funcional": 75, "recuperacion_citacion": 75,
    "costo_latencia": 80, "personalizacion": 95,
    "observabilidad": 85, "seguridad_gobernanza": 80,
}
# None = evidencia final Windows/manual todavía pendiente; nunca convertirlo en PASS.
NO_COMPENSABLES = {
    "pipeline_corre_de_punta_a_punta": None,
    "respuestas_citan_fuente": None,
    "logs_sin_contenido_crudo": None,
    "supervision_humana_funciona": None,
}


def promedio_ponderado(puntajes, pesos=PESOS):
    if set(puntajes) != set(pesos) or any(not 0 <= v <= 100 for v in puntajes.values()):
        raise ValueError("Puntajes inválidos.")
    return sum(puntajes[d] * pesos[d] for d in pesos)


def evaluar_gate(puntajes, no_compensables, umbral=80):
    promedio = promedio_ponderado(puntajes)
    return promedio, promedio >= umbral and all(
        no_compensables.get(k) is True for k in NO_COMPENSABLES
    )


if __name__ == "__main__":
    promedio, listo = evaluar_gate(PUNTAJES, NO_COMPENSABLES)
    print("Autoevaluación PROVISIONAL (no calificación):", f"{promedio:.1f}%")
    for criterio, estado in NO_COMPENSABLES.items():
        print(criterio, "PASS" if estado is True else "FAIL" if estado is False else "PENDIENTE")
    print("LISTO PARA ENTREGAR SEGÚN AUTOCHEQUEO:", listo)
