"""Pruebas iniciales del Bloque 19: sin consumir API ni exponer datos."""

from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage

from src.bloque19_01_enrutamiento import (
    construir_cadena,
    normalizar_categoria,
)


@pytest.mark.parametrize(
    ("entrada", "esperada"),
    [
        (" Queja \n", "queja"),
        ("Queja.", "queja"),
        ("SUGERENCIA!", "sugerencia"),
        (" pregunta ", "pregunta"),
    ],
)
def test_normaliza_respuesta_del_clasificador(entrada, esperada):
    assert normalizar_categoria(entrada) == esperada


def test_queja_va_a_su_ruta_y_conserva_mensaje():
    modelo_falso = MagicMock(
        side_effect=[
            AIMessage(content="Queja.\n"),
            AIMessage(content="Lamento la discrepancia. Podemos revisar filtros."),
        ]
    )
    cadena = construir_cadena(modelo_falso)
    mensaje = "Ejercicio ficticio: el tablero no coincide con la extracción."
    respuesta = cadena.invoke({"mensaje": mensaje})

    assert modelo_falso.call_count == 2
    assert "Lamento" in respuesta
    prompt_clasificacion = modelo_falso.call_args_list[0].args[0].to_string()
    prompt_respuesta = modelo_falso.call_args_list[1].args[0].to_string()
    assert mensaje in prompt_clasificacion
    assert mensaje in prompt_respuesta
    assert "Responde a la siguiente queja" in prompt_respuesta
    assert "Responde la siguiente pregunta tecnica" not in prompt_respuesta


def test_falta_mensaje_no_invoca_modelo():
    modelo_falso = MagicMock()
    cadena = construir_cadena(modelo_falso)

    with pytest.raises(KeyError, match="mensaje"):
        cadena.invoke({"entrada_erronea": "texto"})

    assert modelo_falso.call_count == 0
