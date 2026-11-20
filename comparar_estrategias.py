r"""U2.6/B30-L2: puntuacion reproducible de estrategias de personalizacion.

Reproduce los dos casos de Skillnest, el empate corregido y la sensibilidad.
Agrega dos escenarios DIDACTICOS de Booking Core AI: sistema completo y
clasificador de intenciones aislado. El score no es un estudio economico
ni autoriza operaciones transaccionales o entrenamiento real.

Ejecucion en Windows:
    .\.venv\Scripts\python.exe .\comparar_estrategias.py

Solo utiliza Python estandar; no consume API ni depende de Gemini.
"""

from __future__ import annotations

import sys
from collections.abc import Mapping

CLAVES = (
    "informacion_cambia_seguido",
    "problema_de_formato_o_tono",
    "dataset_grande_y_de_calidad",
    "presupuesto_limitado_o_iterar_rapido",
    "necesita_multiples_variantes",
)

# Ponderaciones literales de Skillnest, B30/L2.
PESOS = {
    "informacion_cambia_seguido": {"RAG": 3},
    "problema_de_formato_o_tono": {"PEFT": 2, "Fine-tuning completo": 1},
    "dataset_grande_y_de_calidad": {"Fine-tuning completo": 2, "PEFT": 1},
    "presupuesto_limitado_o_iterar_rapido": {"RAG": 2, "PEFT": 1},
    "necesita_multiples_variantes": {"PEFT": 2},
}

TECNICAS = ("RAG", "Fine-tuning completo", "PEFT")


def recomendar_estrategia(
    respuestas: Mapping[str, bool],
) -> tuple[dict[str, int], list[str]]:
    """Aplica los pesos del curso; informa TODAS las técnicas empatadas."""
    faltantes = set(CLAVES) - set(respuestas)
    extras = set(respuestas) - set(CLAVES)
    if faltantes or extras:
        raise ValueError(
            f"Claves incorrectas; faltan: {sorted(faltantes)}; extras: {sorted(extras)}"
        )
    for clave in CLAVES:
        if type(respuestas[clave]) is not bool:
            raise TypeError(f"{clave} debe ser bool (True/False), no texto ni número")

    puntos = {tecnica: 0 for tecnica in TECNICAS}
    for clave in CLAVES:
        if respuestas[clave]:
            for tecnica, cantidad in PESOS[clave].items():
                puntos[tecnica] += cantidad

    maximo = max(puntos.values())
    ganadoras = [tecnica for tecnica, puntaje in puntos.items() if puntaje == maximo]
    return puntos, ganadoras


def analizar_sensibilidad(
    respuestas: Mapping[str, bool],
) -> list[tuple[str, bool, dict[str, int], list[str], bool]]:
    """Cambia una sola respuesta por vez y detecta cambios en el ganador."""
    _, originales = recomendar_estrategia(respuestas)
    resultados = []
    for clave in CLAVES:
        variante = dict(respuestas)
        variante[clave] = not variante[clave]
        puntos, ganadoras = recomendar_estrategia(variante)
        cambia = set(ganadoras) != set(originales)
        resultados.append((clave, variante[clave], puntos, ganadoras, cambia))
    return resultados


# Caso 2, oficial Skillnest: clasificación con gran dataset y empate 3 a 3.
RESPUESTAS_CASO2 = {
    "informacion_cambia_seguido": False,
    "problema_de_formato_o_tono": True,
    "dataset_grande_y_de_calidad": True,
    "presupuesto_limitado_o_iterar_rapido": False,
    "necesita_multiples_variantes": False,
}

# Caso 1, oficial Skillnest: políticas cambiantes y tono consistente.
RESPUESTAS_CASO1 = {
    "informacion_cambia_seguido": True,
    "problema_de_formato_o_tono": True,
    "dataset_grande_y_de_calidad": False,
    "presupuesto_limitado_o_iterar_rapido": True,
    "necesita_multiples_variantes": False,
}

# Inferencia de proyecto: Booking Core completo, políticas/documentos cambiantes,
# clasificación JSON, 20 ejemplos sintéticos (NO dataset grande de calidad probado),
# iteración rápida y sin requisito declarado de múltiples adapters.
RESPUESTAS_BOOKING_CORE_COMPLETO = dict(RESPUESTAS_CASO1)

# Separar subproblemas es clave: si SOLO clasificamos intención y ruta,
# la información documental actualizable no forma parte de esa tarea.
RESPUESTAS_BOOKING_CORE_CLASIFICADOR = {
    "informacion_cambia_seguido": False,
    "problema_de_formato_o_tono": True,
    "dataset_grande_y_de_calidad": False,
    "presupuesto_limitado_o_iterar_rapido": True,
    "necesita_multiples_variantes": False,
}


def main() -> None:
    if sys.version_info < (3, 10):
        raise SystemExit("Necesitas Python 3.10 o superior.")
    print("Python", sys.version.split()[0])
    print("Entorno listo")

    puntos2, ganadoras2 = recomendar_estrategia(RESPUESTAS_CASO2)
    print("\n=== CASO 2 OFICIAL: EMPATE ===")
    print("caso 2:", puntos2)
    print("candidatas empatadas:", ganadoras2)
    print("items:", list(puntos2.items()))
    print("maximo:", max(puntos2.values()))

    print("\n=== SENSIBILIDAD CASO 2 ===")
    for clave, valor, _puntos, ganadoras, cambia in analizar_sensibilidad(
        RESPUESTAS_CASO2
    ):
        print(f"{clave} -> {valor}: {ganadoras}  [{'CAMBIA' if cambia else 'igual'}]")

    puntos1, ganadoras1 = recomendar_estrategia(RESPUESTAS_CASO1)
    print("\n=== CASO 1 OFICIAL: POLITICAS CAMBIANTES ===")
    print("caso 1:", puntos1)
    print("candidatas empatadas:", ganadoras1)

    print("\n=== BOOKING CORE AI: SISTEMA COMPLETO (SUPUESTOS) ===")
    puntos_full, ganadoras_full = recomendar_estrategia(
        RESPUESTAS_BOOKING_CORE_COMPLETO
    )
    print("puntajes:", puntos_full)
    print("candidatas:", ganadoras_full)
    print("La ruta RAG aplica a conocimiento documental; reservas usan backend autorizado.")

    print("\n=== BOOKING CORE AI: SOLO CLASIFICADOR (SUPUESTOS) ===")
    puntos_cls, ganadoras_cls = recomendar_estrategia(
        RESPUESTAS_BOOKING_CORE_CLASIFICADOR
    )
    print("puntajes:", puntos_cls)
    print("candidatas:", ganadoras_cls)
    print("Primero evaluar prompting/JSON Schema como baseline, antes de PEFT.")

    assert puntos2 == {"RAG": 0, "Fine-tuning completo": 3, "PEFT": 3}
    assert ganadoras2 == ["Fine-tuning completo", "PEFT"]
    assert all(cambia for _, _, _, _, cambia in analizar_sensibilidad(RESPUESTAS_CASO2))
    assert puntos1 == {"RAG": 5, "Fine-tuning completo": 1, "PEFT": 3}
    assert ganadoras1 == ["RAG"]
    assert puntos_cls == {"RAG": 2, "Fine-tuning completo": 1, "PEFT": 3}
    assert ganadoras_cls == ["PEFT"]
    print("\nB30/L2: COMPARACION Y EMPATES VALIDADOS (SIN API)")


if __name__ == "__main__":
    main()
