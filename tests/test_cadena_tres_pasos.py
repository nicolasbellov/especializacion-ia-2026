"""Pruebas de actividad 20344; no hacen llamadas reales a Gemini."""

from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage

from src.cadena_tres_pasos import construir_cadena


def test_encadena_tres_pasos_y_entrega_texto():
    modelo_falso = MagicMock(
        side_effect=[
            AIMessage(content="Categoría: diferencia de indicadores. Hechos: 36 vs 42."),
            AIMessage(content="Plan: verificar filtros, fechas y actualización del cubo."),
            AIMessage(content="# Informe\n- Revisar filtros\n- Revisar fechas\n- Revisar cubo"),
        ]
    )

    cadena = construir_cadena(modelo_falso)
    resultado = cadena.invoke({"incidencia": "Datos ficticios: tablero 36, fuente 42."})

    assert modelo_falso.call_count == 3
    assert isinstance(resultado, str)
    assert "# Informe" in resultado
    # Confirma dependencia REAL entre pasos, además de contar invocaciones.
    segundo_prompt = modelo_falso.call_args_list[1].args[0].to_string()
    tercer_prompt = modelo_falso.call_args_list[2].args[0].to_string()
    assert "Categoría: diferencia de indicadores" in segundo_prompt
    assert "Plan: verificar filtros, fechas" in tercer_prompt


def test_falta_variable_obligatoria_sin_llamar_al_modelo():
    modelo_falso = MagicMock()
    cadena = construir_cadena(modelo_falso)

    with pytest.raises(KeyError, match="incidencia"):
        cadena.invoke({"otra_clave": "valor"})

    assert modelo_falso.call_count == 0
