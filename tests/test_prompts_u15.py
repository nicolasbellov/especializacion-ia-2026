"""Pruebas locales U1.5, sin consumo de la API ni credenciales."""
import unittest

from prompts.banco import BANCO_DE_PROMPTS
from prompts.test_consistencia import validar_contenido
from src.consumir_gemini import armar_peticion, parsear_respuesta_json


class TestAgendaU15(unittest.TestCase):
    def test_banco_tiene_tres_prompts(self):
        self.assertGreaterEqual(len(BANCO_DE_PROMPTS), 3)
        for prompt in BANCO_DE_PROMPTS:
            self.assertTrue(prompt["nombre"])
            self.assertTrue(prompt["system_instruction"])
            self.assertTrue(prompt["ejemplo_usuario"])
            self.assertTrue(prompt["response_schema"])

    def test_compatibilidad_anterior(self):
        _, headers, body = armar_peticion("¿Qué es una API?")
        self.assertIn("x-goog-api-key", headers)
        self.assertNotIn("systemInstruction", body)
        self.assertNotIn("generationConfig", body)

    def test_peticion_con_esquema(self):
        p = BANCO_DE_PROMPTS[0]
        _, _, body = armar_peticion(
            p["ejemplo_usuario"], p["system_instruction"], p["response_schema"]
        )
        self.assertIn("systemInstruction", body)
        self.assertEqual(
            body["generationConfig"]["responseMimeType"], "application/json"
        )
        self.assertEqual(body["generationConfig"]["responseSchema"], p["response_schema"])

    def test_limpia_markdown_y_valida(self):
        p = BANCO_DE_PROMPTS[0]
        texto = '```json\n{"intencion":"crear","confianza":0.9}\n```'
        datos = parsear_respuesta_json(texto, p["response_schema"])
        self.assertEqual(datos["intencion"], "crear")

    def test_json_invalido(self):
        with self.assertRaisesRegex(ValueError, "no es JSON válido"):
            parsear_respuesta_json('{"intencion":')

    def test_rechaza_lista(self):
        with self.assertRaisesRegex(ValueError, "Se esperaba un objeto"):
            parsear_respuesta_json("[]")

    def test_rechaza_clave_faltante(self):
        p = BANCO_DE_PROMPTS[0]
        with self.assertRaisesRegex(ValueError, "Faltan claves"):
            parsear_respuesta_json('{"intencion":"crear"}', p["response_schema"])

    def test_rechaza_tipo_incorrecto(self):
        p = BANCO_DE_PROMPTS[0]
        with self.assertRaisesRegex(ValueError, "Tipo incorrecto"):
            parsear_respuesta_json(
                '{"intencion":"crear","confianza":"alta"}', p["response_schema"]
            )

    def test_rechaza_confianza_fuera_de_rango(self):
        p = BANCO_DE_PROMPTS[0]
        with self.assertRaisesRegex(ValueError, "superior al máximo"):
            parsear_respuesta_json(
                '{"intencion":"crear","confianza":1.9}', p["response_schema"]
            )

    def test_rechaza_enum_invalido(self):
        p = BANCO_DE_PROMPTS[0]
        with self.assertRaisesRegex(ValueError, "Valor no permitido"):
            parsear_respuesta_json(
                '{"intencion":"inventar","confianza":0.9}', p["response_schema"]
            )

    def test_valida_lista_faltantes(self):
        p = BANCO_DE_PROMPTS[2]
        datos = parsear_respuesta_json(
            '{"datos_completos":false,"campos_faltantes":["hora","fecha"]}',
            p["response_schema"],
        )
        self.assertEqual(validar_contenido(datos, p["resultado_esperado"]), [])

    def test_rechaza_tipo_array_item(self):
        p = BANCO_DE_PROMPTS[2]
        with self.assertRaisesRegex(ValueError, "Tipo incorrecto"):
            parsear_respuesta_json(
                '{"datos_completos":false,"campos_faltantes":[4]}',
                p["response_schema"],
            )


if __name__ == "__main__":
    unittest.main()
