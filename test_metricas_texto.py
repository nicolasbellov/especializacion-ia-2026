"""Pruebas offline para Skillnest U2.2 / Bloque 16."""

import json
from pathlib import Path

import pytest

from metricas_texto import (
    calcular_metricas_casos,
    calcular_precision_cobertura_f1,
    contar_coincidencias,
)
from pipeline_texto import procesar_texto


def test_interseccion_counter_considera_repeticiones():
    assert contar_coincidencias(
        ["el", "gato"], ["el", "gato", "el", "gato"]
    ) == 2


def test_ejemplo_oficial_precision_cobertura_f1():
    referencia = procesar_texto("El gato duerme en el sofá.")
    respuesta = procesar_texto("El gato duerme en el sillón todo el día.")
    assert contar_coincidencias(referencia, respuesta) == 5
    resultado = calcular_precision_cobertura_f1(referencia, respuesta)
    assert resultado["precision"] == pytest.approx(5 / 9)
    assert resultado["cobertura"] == pytest.approx(5 / 6)
    assert resultado["f1"] == pytest.approx(2 / 3)


def test_listas_vacias_no_dividen_por_cero():
    esperado = {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}
    assert calcular_precision_cobertura_f1([], []) == esperado
    assert calcular_precision_cobertura_f1(["hola"], []) == esperado
    assert calcular_precision_cobertura_f1([], ["hola"]) == esperado


def test_cero_coincidencias():
    assert calcular_precision_cobertura_f1(
        ["perro"], ["gato"]
    ) == {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}


def test_coincidencia_total():
    assert calcular_precision_cobertura_f1(
        ["a", "a", "b"], ["a", "a", "b"]
    ) == {"precision": 1.0, "cobertura": 1.0, "f1": 1.0}


def test_rechaza_texto_crudo_no_tokenizado():
    with pytest.raises(TypeError, match="tokens_referencia"):
        contar_coincidencias("hola mundo", ["hola"])
    with pytest.raises(TypeError, match="tokens_respuesta"):
        contar_coincidencias(["hola"], "hola mundo")


def test_rechaza_listas_con_elementos_no_textuales():
    with pytest.raises(TypeError, match="tokens_referencia"):
        contar_coincidencias([None], ["hola"])


def test_tres_respuestas_reales_guardadas():
    ruta = Path(__file__).with_name("resultados_b15.json")
    casos = json.loads(ruta.read_text(encoding="utf-8"))
    resultados = calcular_metricas_casos(casos)
    assert [r["coincidencias"] for r in resultados] == [6, 5, 3]
    assert [(r["tokens_referencia"], r["tokens_respuesta"]) for r in resultados] == [
        (6, 21), (7, 23), (6, 25)
    ]
    for resultado, f1_esperado in zip(
        resultados, [4 / 9, 1 / 3, 6 / 31]
    ):
        assert resultado["f1"] == pytest.approx(f1_esperado)
