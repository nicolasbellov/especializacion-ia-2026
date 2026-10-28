"""Bloque 14, leccion 1 (Skillnest): pruebas unitarias con pytest y Mock.

Mockea el punto de salida HTTP de cliente_api.enviar_peticion.
No realiza consultas reales ni requiere una clave valida de Gemini.
"""

from unittest.mock import Mock, patch

import pytest

from cliente_api import enviar_peticion


def test_enviar_peticion_credencial_invalida():
    """401: una credencial invalida debe levantar ValueError."""
    respuesta_falsa = Mock(status_code=401)

    with patch("cliente_api.requests.post", return_value=respuesta_falsa) as post:
        with pytest.raises(ValueError, match="Credencial invalida"):
            enviar_peticion({"pregunta": "test"})

    post.assert_called_once()


def test_enviar_peticion_limite_de_uso():
    """429: limite de uso debe convertirse en TimeoutError."""
    respuesta_falsa = Mock(status_code=429)

    with patch("cliente_api.requests.post", return_value=respuesta_falsa) as post:
        with pytest.raises(TimeoutError, match="Rate limit"):
            enviar_peticion({"pregunta": "test"})

    post.assert_called_once()


def test_enviar_peticion_exito():
    """200: se devuelve exactamente el JSON del proveedor."""
    respuesta_falsa = Mock(status_code=200)
    respuesta_falsa.json.return_value = {"texto": "respuesta simulada"}

    with patch("cliente_api.requests.post", return_value=respuesta_falsa) as post:
        resultado = enviar_peticion({"pregunta": "test"})

    assert resultado == {"texto": "respuesta simulada"}
    respuesta_falsa.raise_for_status.assert_called_once()
    respuesta_falsa.json.assert_called_once()
    post.assert_called_once()
