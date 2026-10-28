"""Suite Skillnest U2.1 / Bloque 14 (actividad core).

Pruebas de las cuatro funciones del cliente modular, sin consultas a Gemini.
"""

from unittest.mock import Mock, patch

import pytest

import cliente
from cliente_api import enviar_peticion
from cliente_reintento import con_reintento


@pytest.fixture(autouse=True)
def reiniciar_costo_total():
    """Evita que una prueba contamine el acumulado de la siguiente."""
    cliente.costo_total_sesion = 0.0
    yield
    cliente.costo_total_sesion = 0.0


# enviar_peticion: EP-01 a EP-05.
def test_enviar_peticion_credencial_invalida():
    respuesta_falsa = Mock(status_code=401)
    with patch("cliente_api.requests.post", return_value=respuesta_falsa) as post:
        with pytest.raises(ValueError, match="Credencial invalida"):
            enviar_peticion({"pregunta": "test"})
    post.assert_called_once()


def test_enviar_peticion_sin_permiso_403():
    respuesta_falsa = Mock(status_code=403)
    with patch("cliente_api.requests.post", return_value=respuesta_falsa) as post:
        with pytest.raises(ValueError, match="sin permiso"):
            enviar_peticion({"pregunta": "test"})
    post.assert_called_once()


def test_enviar_peticion_limite_de_uso():
    respuesta_falsa = Mock(status_code=429)
    with patch("cliente_api.requests.post", return_value=respuesta_falsa) as post:
        with pytest.raises(TimeoutError, match="Rate limit"):
            enviar_peticion({"pregunta": "test"})
    post.assert_called_once()


def test_enviar_peticion_error_500():
    respuesta_falsa = Mock(status_code=500)
    with patch("cliente_api.requests.post", return_value=respuesta_falsa) as post:
        with pytest.raises(TimeoutError, match="Error temporal"):
            enviar_peticion({"pregunta": "test"})
    post.assert_called_once()


def test_enviar_peticion_exito():
    respuesta_falsa = Mock(status_code=200)
    respuesta_falsa.json.return_value = {"texto": "respuesta simulada"}
    with patch("cliente_api.requests.post", return_value=respuesta_falsa) as post:
        resultado = enviar_peticion({"pregunta": "test"})
    assert resultado == {"texto": "respuesta simulada"}
    respuesta_falsa.raise_for_status.assert_called_once()
    respuesta_falsa.json.assert_called_once()
    post.assert_called_once()


# con_reintento: RI-01 a RI-03.
def test_con_reintento_recupera_timeout():
    llamadas = 0

    def fallar_una_vez():
        nonlocal llamadas
        llamadas += 1
        if llamadas == 1:
            raise TimeoutError("temporal")
        return "ok"

    with patch("cliente_reintento.time.sleep") as dormir:
        assert con_reintento(fallar_una_vez) == "ok"
    assert llamadas == 2
    dormir.assert_called_once()


def test_con_reintento_no_reintenta_value_error():
    error_original = ValueError("permanente")
    accion = Mock(side_effect=error_original)
    with patch("cliente_reintento.time.sleep") as dormir:
        with pytest.raises(ValueError) as captura:
            con_reintento(accion)
    assert captura.value is error_original
    accion.assert_called_once()
    dormir.assert_not_called()


def test_con_reintento_agota_intentos_y_propaga_error_original():
    error_original = TimeoutError("proveedor agotado")
    accion = Mock(side_effect=error_original)
    with patch("cliente_reintento.time.sleep") as dormir:
        with pytest.raises(TimeoutError) as captura:
            con_reintento(accion, intentos=3)
    assert captura.value is error_original
    assert accion.call_count == 3
    assert dormir.call_count == 2


# registrar_costo: CO-01 y CO-02.
def test_registrar_costo_calcula_tokens():
    respuesta = {"usageMetadata": {"totalTokenCount": 1000}}
    costo = cliente.registrar_costo(respuesta)
    assert costo == pytest.approx(cliente.COSTO_POR_1000_TOKENS)
    assert cliente.costo_total_sesion == pytest.approx(
        cliente.COSTO_POR_1000_TOKENS
    )


def test_registrar_costo_acumula():
    primera = cliente.registrar_costo(
        {"usageMetadata": {"totalTokenCount": 42}}
    )
    segunda = cliente.registrar_costo(
        {"usageMetadata": {"totalTokenCount": 57}}
    )
    assert primera == pytest.approx(0.000084)
    assert segunda == pytest.approx(0.000114)
    assert cliente.costo_total_sesion == pytest.approx(0.000198)


# consultar_modelo: CM-01 y CM-02.
def test_consultar_modelo_convierte_error():
    error_original = TimeoutError("agotado")
    with patch("cliente.con_reintento", side_effect=error_original) as reintento:
        with pytest.raises(RuntimeError, match="varios intentos") as captura:
            cliente.consultar_modelo("pregunta de prueba")
    assert captura.value.__cause__ is error_original
    reintento.assert_called_once()
    assert cliente.costo_total_sesion == 0.0


def test_consultar_modelo_propaga_value_error():
    error_original = ValueError("credencial invalida")
    with patch("cliente.con_reintento", side_effect=error_original) as reintento:
        with pytest.raises(ValueError) as captura:
            cliente.consultar_modelo("pregunta de prueba")
    assert captura.value is error_original
    reintento.assert_called_once()
    assert cliente.costo_total_sesion == 0.0


# Criterio adicional: metadatos ausentes no equivalen a costo cero auditado.
def test_registrar_costo_sin_metadata_no_inventa_precio():
    assert cliente.registrar_costo({}) is None
    assert cliente.costo_total_sesion == 0.0
