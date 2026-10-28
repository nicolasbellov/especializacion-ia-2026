"""Pruebas de integracion B13. Todos los estados HTTP son simulados."""

import json
import unittest
from unittest.mock import patch

import requests
import cliente


def respuesta_http(codigo, tokens=25):
    r = requests.Response()
    r.status_code = codigo
    r.url = "https://ejemplo.invalid/ensayo"
    if codigo == 200:
        data = {
            "candidates": [{"content": {"parts": [{"text": "OK"}]}}],
            "usageMetadata": {"totalTokenCount": tokens},
        }
    else:
        data = {"error": {"code": codigo, "message": "Fallo simulado"}}
    r._content = json.dumps(data).encode("utf-8")
    r.encoding = "utf-8"
    return r


class CierreBloque13(unittest.TestCase):
    def setUp(self):
        cliente.costo_total_sesion = 0.0

    def tearDown(self):
        cliente.costo_total_sesion = 0.0

    def test_429_se_recupera_y_costo_una_sola_vez(self):
        with (
            patch("cliente_api.requests.post", side_effect=[
                respuesta_http(429), respuesta_http(200, 42)
            ]) as post,
            patch("cliente_reintento.random.uniform", return_value=0),
            patch("cliente_reintento.time.sleep") as dormir,
        ):
            texto = cliente.consultar_modelo(
                "Di OK", system_instruction="Responde solo OK"
            )
        self.assertEqual(texto, "OK")
        self.assertEqual(post.call_count, 2)
        self.assertEqual([x.args[0] for x in dormir.call_args_list], [2])
        self.assertAlmostEqual(cliente.costo_total_sesion, 0.000084)
        cuerpo = post.call_args_list[0].kwargs["json"]
        self.assertEqual(
            cuerpo["systemInstruction"]["parts"][0]["text"],
            "Responde solo OK",
        )

    def test_tres_429_llevan_a_runtimeerror_sin_costo(self):
        with (
            patch("cliente_api.requests.post", side_effect=[
                respuesta_http(429) for _ in range(3)
            ]) as post,
            patch("cliente_reintento.random.uniform", return_value=0),
            patch("cliente_reintento.time.sleep") as dormir,
        ):
            with self.assertRaisesRegex(RuntimeError, "varios intentos"):
                cliente.consultar_modelo("Di OK")
        self.assertEqual(post.call_count, 3)
        self.assertEqual([x.args[0] for x in dormir.call_args_list], [2, 4])
        self.assertEqual(cliente.costo_total_sesion, 0.0)

    def test_401_no_reintenta(self):
        with (
            patch("cliente_api.requests.post", return_value=respuesta_http(401)) as post,
            patch("cliente_reintento.time.sleep") as dormir,
        ):
            with self.assertRaises(ValueError):
                cliente.consultar_modelo("Di OK")
        post.assert_called_once()
        dormir.assert_not_called()
        self.assertEqual(cliente.costo_total_sesion, 0.0)

    def test_500_se_recupera_y_costo_unico(self):
        with (
            patch("cliente_api.requests.post", side_effect=[
                respuesta_http(500), respuesta_http(200, 11)
            ]) as post,
            patch("cliente_reintento.random.uniform", return_value=0),
            patch("cliente_reintento.time.sleep") as dormir,
        ):
            self.assertEqual(cliente.consultar_modelo("Di OK"), "OK")
        self.assertEqual(post.call_count, 2)
        self.assertEqual([x.args[0] for x in dormir.call_args_list], [2])
        self.assertAlmostEqual(cliente.costo_total_sesion, 0.000022)


if __name__ == "__main__":
    unittest.main(verbosity=2)
