"""Pruebas educativas para los límites del F1 de tokens (sin API)."""

import pytest

from ejemplos_limites_b16 import CASOS, evaluar


@pytest.mark.parametrize(
    "indice,precision,cobertura,f1",
    [
        (0, 0.5, 0.5, 0.5),
        (1, 0.8, 0.8, 0.8),
        (2, 1.0, 5 / 6, 10 / 11),
        (3, 10 / 11, 1.0, 20 / 21),
    ],
)
def test_limites_lexicos_reproducen_valores_del_curso(
    indice: int, precision: float, cobertura: float, f1: float
):
    resultado = evaluar(CASOS[indice])
    assert resultado["precision"] == pytest.approx(precision)
    assert resultado["cobertura"] == pytest.approx(cobertura)
    assert resultado["f1"] == pytest.approx(f1)
