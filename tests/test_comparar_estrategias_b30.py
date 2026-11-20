"""Pruebas B30/L2: función oficial, empate, sensibilidad y aplicación propia."""

import unittest

from comparar_estrategias import (
    CLAVES,
    RESPUESTAS_BOOKING_CORE_CLASIFICADOR,
    RESPUESTAS_BOOKING_CORE_COMPLETO,
    RESPUESTAS_CASO1,
    RESPUESTAS_CASO2,
    TECNICAS,
    analizar_sensibilidad,
    recomendar_estrategia,
)


class CompararEstrategiasTests(unittest.TestCase):
    def test_caso_2_puntajes_oficiales(self) -> None:
        puntos, _ = recomendar_estrategia(RESPUESTAS_CASO2)
        self.assertEqual(puntos, {"RAG": 0, "Fine-tuning completo": 3, "PEFT": 3})

    def test_caso_2_empate_visible(self) -> None:
        _, ganadoras = recomendar_estrategia(RESPUESTAS_CASO2)
        self.assertEqual(ganadoras, ["Fine-tuning completo", "PEFT"])

    def test_items_y_maximo_del_ejemplo(self) -> None:
        puntos, _ = recomendar_estrategia(RESPUESTAS_CASO2)
        self.assertEqual(
            list(puntos.items()),
            [("RAG", 0), ("Fine-tuning completo", 3), ("PEFT", 3)],
        )
        self.assertEqual(max(puntos.values()), 3)

    def test_caso_1_puntajes_oficiales(self) -> None:
        puntos, _ = recomendar_estrategia(RESPUESTAS_CASO1)
        self.assertEqual(puntos, {"RAG": 5, "Fine-tuning completo": 1, "PEFT": 3})

    def test_caso_1_ganador_unico(self) -> None:
        _, ganadoras = recomendar_estrategia(RESPUESTAS_CASO1)
        self.assertEqual(ganadoras, ["RAG"])

    def test_sensibilidad_cambia_todas_las_respuestas(self) -> None:
        cambios = analizar_sensibilidad(RESPUESTAS_CASO2)
        self.assertEqual(len(cambios), 5)
        self.assertEqual([c[0] for c in cambios], list(CLAVES))
        self.assertTrue(all(c[4] for c in cambios))

    def test_sensibilidad_info_cambiante_empate_triple(self) -> None:
        cambios = analizar_sensibilidad(RESPUESTAS_CASO2)
        self.assertEqual(cambios[0][3], ["RAG", "Fine-tuning completo", "PEFT"])

    def test_sensibilidad_formato_false_gana_finetuning(self) -> None:
        cambios = analizar_sensibilidad(RESPUESTAS_CASO2)
        self.assertEqual(cambios[1][3], ["Fine-tuning completo"])

    def test_sensibilidad_dataset_false_gana_peft(self) -> None:
        cambios = analizar_sensibilidad(RESPUESTAS_CASO2)
        self.assertEqual(cambios[2][3], ["PEFT"])

    def test_sensibilidad_presupuesto_true_gana_peft(self) -> None:
        cambios = analizar_sensibilidad(RESPUESTAS_CASO2)
        self.assertEqual(cambios[3][3], ["PEFT"])

    def test_sensibilidad_variantes_true_gana_peft(self) -> None:
        cambios = analizar_sensibilidad(RESPUESTAS_CASO2)
        self.assertEqual(cambios[4][3], ["PEFT"])

    def test_todas_false_empate_triple_de_cero(self) -> None:
        puntos, ganadoras = recomendar_estrategia(dict.fromkeys(CLAVES, False))
        self.assertEqual(puntos, dict.fromkeys(TECNICAS, 0))
        self.assertEqual(ganadoras, list(TECNICAS))

    def test_no_muta_respuestas(self) -> None:
        entrada = dict(RESPUESTAS_CASO2)
        recomendar_estrategia(entrada)
        analizar_sensibilidad(entrada)
        self.assertEqual(entrada, RESPUESTAS_CASO2)

    def test_rechaza_bool_como_texto(self) -> None:
        respuestas = dict(RESPUESTAS_CASO2)
        respuestas["informacion_cambia_seguido"] = "False"
        with self.assertRaisesRegex(TypeError, "debe ser bool"):
            recomendar_estrategia(respuestas)

    def test_rechaza_numeros_en_lugar_de_bool(self) -> None:
        respuestas = dict(RESPUESTAS_CASO2)
        respuestas["necesita_multiples_variantes"] = 1
        with self.assertRaises(TypeError):
            recomendar_estrategia(respuestas)

    def test_rechaza_clave_faltante(self) -> None:
        respuestas = dict(RESPUESTAS_CASO2)
        del respuestas["necesita_multiples_variantes"]
        with self.assertRaisesRegex(ValueError, "faltan"):
            recomendar_estrategia(respuestas)

    def test_rechaza_clave_extra(self) -> None:
        respuestas = {**RESPUESTAS_CASO2, "otro_criterio": True}
        with self.assertRaisesRegex(ValueError, "extras"):
            recomendar_estrategia(respuestas)

    def test_booking_core_completo_hace_explicito_rag(self) -> None:
        puntos, ganadoras = recomendar_estrategia(RESPUESTAS_BOOKING_CORE_COMPLETO)
        self.assertEqual(puntos, {"RAG": 5, "Fine-tuning completo": 1, "PEFT": 3})
        self.assertEqual(ganadoras, ["RAG"])

    def test_booking_core_clasificador_aislado_peft(self) -> None:
        puntos, ganadoras = recomendar_estrategia(RESPUESTAS_BOOKING_CORE_CLASIFICADOR)
        self.assertEqual(puntos, {"RAG": 2, "Fine-tuning completo": 1, "PEFT": 3})
        self.assertEqual(ganadoras, ["PEFT"])


if __name__ == "__main__":
    unittest.main()
