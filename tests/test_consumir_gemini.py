import unittest
import requests
from unittest.mock import patch

from src.consumir_gemini import extraer_texto, enviar_peticion



class TestExtraerTexto(unittest.TestCase):

    def test_respuesta_correcta(self):
        datos = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "Respuesta correcta"}
                        ]
                    }
                }
            ]
        }

        resultado = extraer_texto(datos)

        self.assertEqual(resultado, "Respuesta correcta")

    def test_campo_faltante(self):
        datos = {"error": "Respuesta simulada"}

        with self.assertRaisesRegex(
            RuntimeError, "candidates"
        ):
            extraer_texto(datos)

    def test_lista_vacia(self):
        datos = {"candidates": []}

        with self.assertRaisesRegex(
            RuntimeError, "lista vacía"
        ):
            extraer_texto(datos)





class TestEnviarPeticion(unittest.TestCase):

    @patch("src.consumir_gemini.requests.post")
    def test_error_conexion(self, post_simulado):
        post_simulado.side_effect = (
            requests.exceptions.ConnectionError("Red no disponible")
        )

        with self.assertRaisesRegex(
            RuntimeError, "No se pudo conectar"
        ):
            enviar_peticion("https://ejemplo.invalid", {}, {})

    @patch("src.consumir_gemini.requests.post")
    def test_timeout(self, post_simulado):
        post_simulado.side_effect = (
            requests.exceptions.ConnectTimeout("Tiempo agotado")
        )

        with self.assertRaisesRegex(
            RuntimeError, "tardó demasiado"
        ):
            enviar_peticion("https://ejemplo.invalid", {}, {})

    @patch("src.consumir_gemini.requests.post")
    def test_json_invalido(self, post_simulado):
        respuesta = post_simulado.return_value
        respuesta.json.side_effect = (
            requests.exceptions.JSONDecodeError(
                "JSON inválido", "contenido incorrecto", 0
            )
        )

        with self.assertRaisesRegex(
            RuntimeError, "no contiene JSON válido"
        ):
            enviar_peticion("https://ejemplo.invalid", {}, {})

    @patch("src.consumir_gemini.requests.post")
    def test_credencial_invalida(self, post_simulado):
        respuesta = post_simulado.return_value
        respuesta.status_code = 401
        respuesta.raise_for_status.side_effect = (
            requests.exceptions.HTTPError("401 Unauthorized")
        )

        with self.assertRaisesRegex(
            RuntimeError, "Error de autenticación"
        ):
            enviar_peticion("https://ejemplo.invalid", {}, {})

if __name__ == "__main__":
    unittest.main()