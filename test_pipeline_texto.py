"""Bloque 15: pruebas sin API ni credenciales."""

import pytest

from pipeline_texto import (
    coincidencia_palabras,
    limpiar_texto,
    procesar_texto,
    tokenizar,
)


def test_procesar_texto_normaliza_mayusculas_y_puntuacion():
    assert procesar_texto("El Cielo, es AZUL!") == ["el", "cielo", "es", "azul"]


def test_procesar_texto_solo_puntuacion_devuelve_lista_vacia():
    assert procesar_texto("¡¡¡...!!!") == []


def test_limpiar_texto_conserva_tildes_y_enie():
    assert limpiar_texto("NIÑO, acción!") == "niño acción"


def test_procesar_texto_colapsa_espacios():
    assert procesar_texto("  Hola   mundo\n  ") == ["hola", "mundo"]


def test_tokenizar_devuelve_lista_vacia_con_texto_vacio():
    assert tokenizar("") == []


def test_limpiar_texto_rechaza_valor_que_no_sea_str():
    with pytest.raises(TypeError, match="limpiar_texto espera str"):
        limpiar_texto(None)


def test_comparacion_antes_y_despues_del_pipeline():
    referencia = "El cielo es azul."
    respuesta = "el cielo es azul"
    assert coincidencia_palabras(referencia, respuesta, normalizar=False) == 0.5
    assert coincidencia_palabras(referencia, respuesta, normalizar=True) == 1.0


def test_metrica_no_identifica_el_cambio_de_orden():
    assert coincidencia_palabras(
        "El perro persiguió al gato.",
        "El gato persiguió al perro.",
        normalizar=True,
    ) == 1.0


def test_metrica_maneja_referencia_vacia_sin_division_por_cero():
    assert coincidencia_palabras("¡¡¡...!!!", "texto", normalizar=True) == 0.0
    assert coincidencia_palabras("", "texto", normalizar=False) == 0.0
