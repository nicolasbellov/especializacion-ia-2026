"""Pruebas offline de U2.6 B29/L3: dataset de intenciones Booking Core AI."""

import json
import unittest

from google.genai import types

from dataset_tuning import (
    CLAVES_ESPERADAS,
    RUTA_POR_INTENCION,
    chequear_balance,
    construir_dataset,
    ejemplos_raw,
    validar_dataset,
)


class DatasetTuningBookingCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.examples = construir_dataset(ejemplos_raw)

    def test_minimo_diez_ejemplos_propios(self) -> None:
        self.assertGreaterEqual(len(self.examples), 10)
        self.assertEqual(len(self.examples), 20)

    def test_cinco_intenciones_con_variedad(self) -> None:
        balance = chequear_balance(ejemplos_raw, "intencion")
        self.assertEqual(set(balance), set(RUTA_POR_INTENCION))
        self.assertEqual(dict(balance), {intent: 4 for intent in RUTA_POR_INTENCION})

    def test_balance_maximo_minimo(self) -> None:
        balance = chequear_balance(ejemplos_raw, "intencion")
        self.assertEqual(max(balance.values()) / min(balance.values()), 1.0)

    def test_dataset_sin_problemas(self) -> None:
        self.assertEqual(validar_dataset(self.examples), [])

    def test_json_exacto_y_rutas_permitidas(self) -> None:
        for ejemplo in self.examples:
            with self.subTest(mensaje=ejemplo.text_input):
                salida = json.loads(ejemplo.output)
                self.assertEqual(set(salida), set(CLAVES_ESPERADAS))
                self.assertEqual(salida["ruta"], RUTA_POR_INTENCION[salida["intencion"]])

    def test_intencion_politica_no_ejecuta_transaccion(self) -> None:
        casos = [salida for _, salida in ejemplos_raw if salida["intencion"] == "consultar_politica"]
        self.assertEqual(len(casos), 4)
        self.assertTrue(all(s["ruta"] == "rag_documental" for s in casos))

    def test_transacciones_solo_clasificadas_como_supervisadas(self) -> None:
        transaccionales = {"crear_reserva", "reprogramar_reserva", "cancelar_reserva"}
        for _, salida in ejemplos_raw:
            if salida["intencion"] in transaccionales:
                self.assertEqual(salida["ruta"], "operacion_supervisada")

    def test_error_texto_vacio(self) -> None:
        rotos = self.examples + [
            types.TuningExample(
                text_input="", output='{"intencion":"cancelar_reserva","ruta":"operacion_supervisada"}'
            )
        ]
        self.assertTrue(any("text_input vacio" in p for p in validar_dataset(rotos)))

    def test_error_duplicado(self) -> None:
        rotos = self.examples + [self.examples[0]]
        self.assertTrue(any("text_input duplicado" in p for p in validar_dataset(rotos)))

    def test_error_json_invalido(self) -> None:
        rotos = self.examples + [
            types.TuningExample(text_input="Otro mensaje ficticio", output="no es json")
        ]
        self.assertTrue(any("no es JSON valido" in p for p in validar_dataset(rotos)))

    def test_error_clave_faltante(self) -> None:
        rotos = self.examples + [
            types.TuningExample(
                text_input="Otra cancelación ficticia",
                output='{"intencion":"cancelar_reserva"}',
            )
        ]
        self.assertTrue(any('falta la clave "ruta"' in p for p in validar_dataset(rotos)))

    def test_error_ruta_incompatible(self) -> None:
        rotos = self.examples + [
            types.TuningExample(
                text_input="Otra petición ficticia de anulación",
                output='{"intencion":"cancelar_reserva","ruta":"rag_documental"}',
            )
        ]
        self.assertTrue(any("ruta incompatible" in p for p in validar_dataset(rotos)))

    def test_error_intencion_desconocida(self) -> None:
        rotos = self.examples + [
            types.TuningExample(
                text_input="Consulta sobre una categoría no contemplada",
                output='{"intencion":"inventada","ruta":"rag_documental"}',
            )
        ]
        self.assertTrue(any("intencion desconocida" in p for p in validar_dataset(rotos)))

    def test_error_output_no_objeto(self) -> None:
        rotos = self.examples + [
            types.TuningExample(text_input="Ejemplo no objeto", output='["dato"]')
        ]
        self.assertTrue(any("objeto JSON" in p for p in validar_dataset(rotos)))

    def test_error_output_vacio(self) -> None:
        rotos = self.examples + [
            types.TuningExample(text_input="Ejemplo sin output", output="")
        ]
        self.assertTrue(any("output vacio" in p for p in validar_dataset(rotos)))

    def test_error_claves_extra(self) -> None:
        rotos = self.examples + [
            types.TuningExample(
                text_input="Ejemplo con campo extra",
                output='{"intencion":"crear_reserva","ruta":"operacion_supervisada","id_reserva":"123"}',
            )
        ]
        self.assertTrue(any("exactamente las claves" in p for p in validar_dataset(rotos)))


if __name__ == "__main__":
    unittest.main()
