"""Autoevaluación basada en la rúbrica S1 y evidencia Windows del 26/11/2026; no es nota oficial."""
PESOS = {
    "pipeline_funcional": .25, "recuperacion_citacion": .15,
    "costo_latencia": .10, "personalizacion": .15,
    "observabilidad": .15, "seguridad_gobernanza": .20,
}
# Estimaciones conservadoras mantenidas tras validar Windows y Gemini; no son notas oficiales.
PUNTAJES = {
    "pipeline_funcional": 75, "recuperacion_citacion": 75,
    "costo_latencia": 80, "personalizacion": 95,
    "observabilidad": 85, "seguridad_gobernanza": 80,
}
# Cuatro pruebas PASS en Windows, corrida real exit 0, cita contrastada y rechazo interactivo.
NO_COMPENSABLES = {
    "pipeline_corre_de_punta_a_punta": True,
    "respuestas_citan_fuente": True,
    "logs_sin_contenido_crudo": True,
    "supervision_humana_funciona": True,
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
    print("Autoevaluación propia (no calificación):", f"{promedio:.1f}%")
    for criterio, estado in NO_COMPENSABLES.items():
        print(criterio, "PASS" if estado is True else "FAIL" if estado is False else "PENDIENTE")
    print("LISTO PARA ENTREGAR SEGÚN AUTOCHEQUEO:", listo)
