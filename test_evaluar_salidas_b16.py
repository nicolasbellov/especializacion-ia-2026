"""Pruebas offline de U2.2 / Bloque 16 L3. No consumen Gemini."""

import json
from pathlib import Path

import pytest

from evaluar_salidas_b16 import (
    calcular_metricas,
    evaluar_respuestas,
    guardar_resultados,
    peores_casos,
    resumir_metricas,
)
from metricas_texto import calcular_precision_cobertura_f1
from pipeline_texto import procesar_texto


def test_calcular_metricas_usa_pipeline_y_contador_existentes():
    referencia = "El gato duerme en el sofá."
    respuesta = "El gato duerme en el sillón todo el día."
    esperado = calcular_precision_cobertura_f1(
        procesar_texto(referencia), procesar_texto(respuesta)
    )
    assert calcular_metricas(referencia, respuesta) == esperado


def test_calcular_metricas_texto_vacio():
    assert calcular_metricas("", "Hola") == {
        "precision": 0.0, "cobertura": 0.0, "f1": 0.0
    }


def test_resumen_sin_casos_no_divide_por_cero():
    assert resumir_metricas([]) == {
        "precision_promedio": 0.0,
        "cobertura_promedio": 0.0,
        "f1_promedio": 0.0,
    }


def test_resumen_es_promedio_simple_de_casos():
    datos = [
        {"precision": 1.0, "cobertura": 0.5, "f1": 2 / 3},
        {"precision": 0.5, "cobertura": 1.0, "f1": 2 / 3},
    ]
    assert resumir_metricas(datos) == pytest.approx({
        "precision_promedio": 0.75,
        "cobertura_promedio": 0.75,
        "f1_promedio": 2 / 3,
    })


def test_ordenar_por_f1_ascendente_sin_modificar_entrada():
    datos = [{"f1": 0.8}, {"f1": 0.2}, {"f1": 0.5}]
    resultado = peores_casos(datos, 2)
    assert [item["f1"] for item in resultado] == [0.2, 0.5]
    assert [item["f1"] for item in datos] == [0.8, 0.2, 0.5]


def test_rechaza_cantidad_negativa():
    with pytest.raises(ValueError, match="negativa"):
        peores_casos([], -1)


def test_guardado_json_utf8_conserva_textos(tmp_path: Path):
    datos = [
        {"caso": 1, "consulta": "¿Qué es Python?",
         "referencia": "Programación", "respuesta": "Niño",
         "precision": 0.1, "cobertura": 0.2, "f1": 0.1333}
    ]
    destino = tmp_path / "resultados_metricas.json"
    guardar_resultados(datos, destino)
    assert "¿Qué" in destino.read_text(encoding="utf-8")
    assert json.loads(destino.read_text(encoding="utf-8")) == datos


def test_tres_respuestas_historicas_reales_con_metricas_y_orden():
    origen = Path(__file__).with_name("resultados_b15.json")
    casos = json.loads(origen.read_text(encoding="utf-8"))
    resultados = evaluar_respuestas(casos)
    assert len(resultados) == 3
    assert all(r["consulta"] and r["referencia"] and r["respuesta"]
               for r in resultados)
    assert [r["f1"] for r in resultados] == pytest.approx(
        [4 / 9, 1 / 3, 6 / 31]
    )
    assert [r["caso"] for r in peores_casos(resultados)] == [3, 2, 1]
    assert resumir_metricas(resultados)["f1_promedio"] == pytest.approx(
        (4 / 9 + 1 / 3 + 6 / 31) / 3
    )
