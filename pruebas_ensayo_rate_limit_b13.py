"""Pruebas offline del ensayo de rate limit (sin enviar HTTP real)."""

import json
from unittest.mock import patch

import requests

import cliente
from ensayo_rate_limit_b13 import ejecutar_ensayo


def respuesta_http(codigo: int, tokens: int = 30) -> requests.Response:
    respuesta = requests.Response()
    respuesta.status_code = codigo
    if codigo == 200:
        datos = {
            "candidates": [{"content": {"parts": [{"text": "OK"}]}}],
            "usageMetadata": {"totalTokenCount": tokens},
        }
    else:
        datos = {"error": {"code": codigo, "message": "Error simulado"}}
    respuesta._content = json.dumps(datos).encode("utf-8")
    respuesta.encoding = "utf-8"
    respuesta.url = "https://ejemplo.invalid/prueba"
    return respuesta


def probar_429_recuperado():
    con_respuestas = [respuesta_http(429), respuesta_http(200, 25)]
    with (
        patch("cliente_api.requests.post", side_effect=con_respuestas) as post,
        patch("cliente_reintento.time.sleep") as dormir,
    ):
        resumen = ejecutar_ensayo(10)

    assert resumen["http_429_real_observado"] is True
    assert resumen["primer_429_operacion"] == 0
    assert resumen["primer_429_llamada_http"] == 1
    assert resumen["llamadas_http"] == 2
    assert resumen["operaciones_exitosas"] == 1
    assert resumen["operaciones_fallidas"] == 0
    assert abs(resumen["costo_referencial_usd"] - 0.00005) < 1e-12
    assert len(resumen["esperas_segundos"]) == 1
    assert post.call_count == 2
    assert dormir.call_count == 1
    print("OK: codigo 429 real del HTTP simulado, reintento y parada")


def probar_sin_429():
    con_respuestas = [respuesta_http(200) for _ in range(3)]
    with patch("cliente_api.requests.post", side_effect=con_respuestas) as post:
        resumen = ejecutar_ensayo(3)
    assert resumen["http_429_real_observado"] is False
    assert resumen["llamadas_http"] == 3
    assert resumen["operaciones_exitosas"] == 3
    assert post.call_count == 3
    print("OK: tres respuestas 200, no se inventa un 429")


def probar_auth_no_reintentable():
    with (
        patch("cliente_api.requests.post", return_value=respuesta_http(401)) as post,
        patch("cliente_reintento.time.sleep") as dormir,
    ):
        resumen = ejecutar_ensayo(10)
    assert resumen["operaciones_fallidas"] == 1
    assert resumen["llamadas_http"] == 1
    assert resumen["http_429_real_observado"] is False
    assert post.call_count == 1
    dormir.assert_not_called()
    print("OK: HTTP 401 detiene ensayo, sin reintento")


def probar_limite_estricto():
    try:
        ejecutar_ensayo(11)
    except ValueError:
        pass
    else:
        raise AssertionError("El ensayo deberia limitar a 10 operaciones")
    print("OK: no permite mas de 10 operaciones")


if __name__ == "__main__":
    probar_429_recuperado()
    probar_sin_429()
    probar_auth_no_reintentable()
    probar_limite_estricto()
    cliente.costo_total_sesion = 0.0
    print("\nTODAS LAS PRUEBAS DEL ENSAYO B13 SUPERADAS")
