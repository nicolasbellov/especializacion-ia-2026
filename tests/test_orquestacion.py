"""Actividad Core U2.3 / Bloque 20: checklist integral de orquestacion.

Todas las pruebas son offline: no necesitan .env ni ejecutan Gemini.
Desde la raiz: python -m pytest tests/test_orquestacion.py -v
"""

import logging
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from src.bloque19_01_enrutamiento import construir_cadena, construir_paso_clasificacion
from src.bloque20_01_fallbacks import (
    RESPUESTA_ERROR_GLOBAL,
    RESPUESTA_GENERICA,
    construir_cadena_queja_segura,
    construir_flujo_con_respaldo,
    fallar_a_proposito,
    procesar_mensaje_seguro,
)


def test_core_clasificacion_normaliza_antes_de_comparar():
    modelo_falso = MagicMock(return_value=AIMessage(content=" QUEJA! \\n"))
    resultado = construir_paso_clasificacion(modelo_falso).invoke(
        {"mensaje": "El tablero ficticio presenta una discrepancia"}
    )
    assert resultado == "queja"
    modelo_falso.assert_called_once()


@pytest.mark.parametrize(
    ("categoria", "mensaje", "respuesta_esperada"),
    [
        ("queja", "Falla el tablero ficticio", "Respuesta de queja"),
        ("sugerencia", "Propongo una alerta", "Respuesta de sugerencia"),
        ("pregunta", "Que representa el KPI", "Respuesta de pregunta"),
        ("categoria_desconocida", "Entrada ambigua", "Respuesta de pregunta"),
        ("", "", "Respuesta de pregunta"),
    ],
)
def test_core_enrutamiento_y_ruta_default(categoria, mensaje, respuesta_esperada):
    clasificador = MagicMock(return_value=categoria)
    llamadas = []

    def ruta(nombre):
        def responder(datos):
            llamadas.append(nombre)
            assert datos["mensaje"] == mensaje
            assert datos["categoria"] == categoria
            return f"Respuesta de {nombre}"
        return RunnableLambda(responder)

    flujo = construir_flujo_con_respaldo(
        paso_clasificacion=clasificador,
        cadena_queja=ruta("queja"),
        cadena_sugerencia=ruta("sugerencia"),
        cadena_pregunta=ruta("pregunta"),
    )

    resultado = procesar_mensaje_seguro(flujo, mensaje)

    assert resultado == respuesta_esperada
    clasificador.assert_called_once()
    assert len(llamadas) == 1
    assert llamadas == [respuesta_esperada.replace("Respuesta de ", "")]


def test_core_cada_ruta_usa_un_prompt_distinto():
    mensaje = "Ejercicio ficticio de soporte"
    prompts = {}

    for categoria in ("queja", "sugerencia", "pregunta"):
        modelo_falso = MagicMock(
            side_effect=[AIMessage(content=categoria), AIMessage(content="Respuesta")]
        )
        resultado = construir_cadena(modelo_falso).invoke({"mensaje": mensaje})
        assert resultado == "Respuesta"
        assert modelo_falso.call_count == 2
        prompt_respuesta = modelo_falso.call_args_list[1].args[0].to_string()
        assert mensaje in prompt_respuesta
        prompts[categoria] = prompt_respuesta

    assert len(set(prompts.values())) == 3
    assert "Responde a la siguiente queja" in prompts["queja"]
    assert "Agradece esta sugerencia" in prompts["sugerencia"]
    assert "Responde la siguiente pregunta tecnica" in prompts["pregunta"]


def test_core_cadena_queja_usa_fallback_ante_fallo():
    cadena_segura = construir_cadena_queja_segura(
        RunnableLambda(fallar_a_proposito)
    )

    resultado = cadena_segura.invoke({"mensaje": "Esto no funciona"})

    assert resultado == RESPUESTA_GENERICA
    assert "no fue posible" in resultado.lower()


def test_core_flujo_completo_recupera_queja_sin_ejecutar_otras_rutas():
    llamadas = []

    def otra_ruta(_datos):
        llamadas.append("otra")
        return "Respuesta inesperada"

    flujo = construir_flujo_con_respaldo(
        paso_clasificacion=RunnableLambda(lambda _datos: "queja"),
        cadena_queja=RunnableLambda(fallar_a_proposito),
        cadena_sugerencia=RunnableLambda(otra_ruta),
        cadena_pregunta=RunnableLambda(otra_ruta),
    )

    assert procesar_mensaje_seguro(flujo, "Queja ficticia") == RESPUESTA_GENERICA
    assert llamadas == []


def test_core_try_except_cubre_error_del_clasificador_y_registra_evento(caplog):
    flujo = construir_flujo_con_respaldo(
        paso_clasificacion=RunnableLambda(fallar_a_proposito),
        cadena_queja=RunnableLambda(lambda _datos: "Queja"),
        cadena_sugerencia=RunnableLambda(lambda _datos: "Sugerencia"),
        cadena_pregunta=RunnableLambda(lambda _datos: "Pregunta"),
    )
    mensaje = "Contenido privado ficticio del mensaje"
    with caplog.at_level(logging.ERROR):
        resultado = procesar_mensaje_seguro(flujo, mensaje)

    assert resultado == RESPUESTA_ERROR_GLOBAL
    assert "ConnectionError" in caplog.text
    assert mensaje not in caplog.text


@pytest.mark.parametrize("salida", ["", "   ", None, 123])
def test_core_resultado_vacio_o_invalido_activa_red_de_seguridad(salida, caplog):
    flujo = RunnableLambda(lambda _datos: salida)
    with caplog.at_level(logging.ERROR):
        resultado = procesar_mensaje_seguro(flujo, "Prueba ficticia")

    assert resultado == RESPUESTA_ERROR_GLOBAL
    assert "ValueError" in caplog.text
