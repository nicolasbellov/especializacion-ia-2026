"""U2.3 / 20346: pruebas de cada ruta sin llamadas a Gemini.

Complemento al curso: tambien verificamos la ruta de sugerencia.
"""

from unittest.mock import MagicMock

from langchain_core.messages import AIMessage

from src.bloque19_01_enrutamiento import (
    construir_cadena_con_enrutamiento,
    construir_paso_clasificacion,
)


def test_enrutamiento_va_a_queja():
    clasificador = MagicMock(return_value="queja")
    ruta_queja = MagicMock(return_value="respuesta de queja")
    ruta_sugerencia = MagicMock(return_value="respuesta de sugerencia")
    ruta_pregunta = MagicMock(return_value="respuesta de pregunta")
    cadena = construir_cadena_con_enrutamiento(
        clasificador, ruta_queja, ruta_sugerencia, ruta_pregunta
    )

    resultado = cadena.invoke({"mensaje": "El tablero ficticio no funciona."})

    assert resultado == "respuesta de queja"
    clasificador.assert_called_once()
    ruta_queja.assert_called_once()
    ruta_sugerencia.assert_not_called()
    ruta_pregunta.assert_not_called()
    assert ruta_queja.call_args.args[0]["categoria"] == "queja"
    assert ruta_queja.call_args.args[0]["mensaje"] == "El tablero ficticio no funciona."


def test_enrutamiento_va_a_sugerencia():
    clasificador = MagicMock(return_value="sugerencia")
    ruta_queja = MagicMock(return_value="respuesta de queja")
    ruta_sugerencia = MagicMock(return_value="respuesta de sugerencia")
    ruta_pregunta = MagicMock(return_value="respuesta de pregunta")
    cadena = construir_cadena_con_enrutamiento(
        clasificador, ruta_queja, ruta_sugerencia, ruta_pregunta
    )

    resultado = cadena.invoke({"mensaje": "Sería útil una alerta en el tablero simulado."})

    assert resultado == "respuesta de sugerencia"
    clasificador.assert_called_once()
    ruta_sugerencia.assert_called_once()
    ruta_queja.assert_not_called()
    ruta_pregunta.assert_not_called()


def test_enrutamiento_va_a_pregunta():
    clasificador = MagicMock(return_value="pregunta")
    ruta_pregunta = MagicMock(return_value="respuesta de pregunta")
    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificador,
        cadena_pregunta=ruta_pregunta,
    )

    resultado = cadena.invoke({"mensaje": "¿Qué indica este KPI ficticio?"})

    assert resultado == "respuesta de pregunta"
    clasificador.assert_called_once()
    ruta_pregunta.assert_called_once()
    assert ruta_pregunta.call_args.args[0]["categoria"] == "pregunta"


def test_enrutamiento_usa_default_ante_categoria_desconocida():
    clasificador = MagicMock(return_value="categoria_inventada")
    ruta_queja = MagicMock(return_value="respuesta de queja")
    ruta_sugerencia = MagicMock(return_value="respuesta de sugerencia")
    ruta_pregunta = MagicMock(return_value="respuesta por defecto")
    cadena = construir_cadena_con_enrutamiento(
        clasificador, ruta_queja, ruta_sugerencia, ruta_pregunta
    )

    resultado = cadena.invoke({"mensaje": "Mensaje ambiguo ficticio."})

    assert resultado == "respuesta por defecto"
    clasificador.assert_called_once()
    ruta_pregunta.assert_called_once()
    ruta_queja.assert_not_called()
    ruta_sugerencia.assert_not_called()


def test_paso_clasificacion_normaliza_respuesta_del_modelo():
    modelo_falso = MagicMock(return_value=AIMessage(content=" Queja \n"))

    resultado = construir_paso_clasificacion(modelo_falso).invoke(
        {"mensaje": "Algo salió mal en el tablero simulado."}
    )

    assert resultado == "queja"
    modelo_falso.assert_called_once()
