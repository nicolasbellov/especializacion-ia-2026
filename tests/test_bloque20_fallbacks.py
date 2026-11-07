"""Pruebas offline del Bloque 20: fallos reales simulados por excepcion."""

import logging

from langchain_core.runnables import RunnableLambda

from src.bloque20_01_fallbacks import (
    RESPUESTA_ERROR_GLOBAL,
    RESPUESTA_GENERICA,
    construir_fallback_generico,
    construir_flujo_con_respaldo,
    fallar_a_proposito,
    procesar_mensaje_seguro,
    proteger_cadena_queja,
)


def test_fallback_reemplaza_excepcion_del_paso_principal():
    cadena = RunnableLambda(fallar_a_proposito).with_fallbacks(
        [construir_fallback_generico()]
    )
    assert cadena.invoke({"mensaje": "Fallo simulado."}) == RESPUESTA_GENERICA


def test_fallbacks_se_ejecutan_en_orden_hasta_el_primero_que_funciona():
    llamadas = []

    def principal(_entrada):
        llamadas.append("principal")
        raise ConnectionError("Red simulada")

    def secundaria(_entrada):
        llamadas.append("secundaria")
        raise TimeoutError("Tiempo de espera simulado")

    def generica(_entrada):
        llamadas.append("generica")
        return RESPUESTA_GENERICA

    cadena = RunnableLambda(principal).with_fallbacks(
        [RunnableLambda(secundaria), RunnableLambda(generica)]
    )
    assert cadena.invoke({"mensaje": "Caso ficticio"}) == RESPUESTA_GENERICA
    assert llamadas == ["principal", "secundaria", "generica"]


def test_fallback_exitoso_evita_cadena_generica():
    llamadas = []

    def principal(_entrada):
        llamadas.append("principal")
        raise ConnectionError("Simulado")

    def secundaria(_entrada):
        llamadas.append("secundaria")
        return "Respuesta secundaria"

    def generica(_entrada):
        llamadas.append("generica")
        return RESPUESTA_GENERICA

    cadena = proteger_cadena_queja(
        RunnableLambda(principal),
        cadena_secundaria=RunnableLambda(secundaria),
        respuesta_generica=RunnableLambda(generica),
    )
    assert cadena.invoke({"mensaje": "Caso ficticio"}) == "Respuesta secundaria"
    assert llamadas == ["principal", "secundaria"]


def test_si_el_paso_principal_funciona_no_se_invoca_ningun_fallback():
    llamadas = []

    def principal(_entrada):
        llamadas.append("principal")
        return "Respuesta principal"

    def secundaria(_entrada):
        llamadas.append("secundaria")
        return "Respuesta secundaria"

    cadena = proteger_cadena_queja(
        RunnableLambda(principal),
        cadena_secundaria=RunnableLambda(secundaria),
    )
    assert cadena.invoke({"mensaje": "Caso ficticio"}) == "Respuesta principal"
    assert llamadas == ["principal"]


def test_integracion_queja_caida_entrega_respuesta_generica():
    llamadas = []

    def sugerencia(_entrada):
        llamadas.append("sugerencia")
        return "Respuesta sugerencia"

    def pregunta(_entrada):
        llamadas.append("pregunta")
        return "Respuesta pregunta"

    cadena = construir_flujo_con_respaldo(
        paso_clasificacion=RunnableLambda(lambda _datos: "queja"),
        cadena_queja=RunnableLambda(fallar_a_proposito),
        cadena_sugerencia=RunnableLambda(sugerencia),
        cadena_pregunta=RunnableLambda(pregunta),
    )
    respuesta = procesar_mensaje_seguro(cadena, "Falla ficticia en el tablero")
    assert respuesta == RESPUESTA_GENERICA
    assert llamadas == []  # No paso por otras rutas


def test_integracion_sugerencia_sigue_su_ruta_sin_fallback():
    cadena = construir_flujo_con_respaldo(
        paso_clasificacion=RunnableLambda(lambda _datos: "sugerencia"),
        cadena_queja=RunnableLambda(fallar_a_proposito),
        cadena_sugerencia=RunnableLambda(lambda datos: "Respuesta: " + datos["mensaje"]),
        cadena_pregunta=RunnableLambda(lambda _datos: "Pregunta"),
    )
    respuesta = procesar_mensaje_seguro(cadena, "Agregar alerta ficticia")
    assert respuesta == "Respuesta: Agregar alerta ficticia"


def test_try_except_global_cubre_fallo_en_clasificacion(caplog):
    cadena = construir_flujo_con_respaldo(
        paso_clasificacion=RunnableLambda(fallar_a_proposito),
        cadena_queja=RunnableLambda(lambda _datos: "Queja"),
        cadena_sugerencia=RunnableLambda(lambda _datos: "Sugerencia"),
        cadena_pregunta=RunnableLambda(lambda _datos: "Pregunta"),
    )
    mensaje = "Mensaje ficticio que no debe aparecer en el log"
    with caplog.at_level(logging.ERROR):
        respuesta = procesar_mensaje_seguro(cadena, mensaje)
    assert respuesta == RESPUESTA_ERROR_GLOBAL
    assert "ConnectionError" in caplog.text
    assert mensaje not in caplog.text


def test_try_except_global_cubre_fallo_de_ruta_sin_fallback():
    cadena = construir_flujo_con_respaldo(
        paso_clasificacion=RunnableLambda(lambda _datos: "pregunta"),
        cadena_queja=RunnableLambda(lambda _datos: "Queja"),
        cadena_sugerencia=RunnableLambda(lambda _datos: "Sugerencia"),
        cadena_pregunta=RunnableLambda(fallar_a_proposito),
    )
    assert (
        procesar_mensaje_seguro(cadena, "Pregunta ficticia")
        == RESPUESTA_ERROR_GLOBAL
    )
