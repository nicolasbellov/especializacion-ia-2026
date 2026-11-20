"""Pruebas offline del ejercicio de costos de personalizacion U2.6/B30-L1."""

import math
import unittest

from costos_personalizacion import (
    estimar_con_segunda_revision,
    estimar_costo_de_etiquetar,
)
from dataset_tuning import ejemplos_raw


class CostosPersonalizacionTests(unittest.TestCase):
    def test_curso_8_ejemplos(self) -> None:
        horas, costo = estimar_costo_de_etiquetar(8, 5, 25)
        self.assertAlmostEqual(horas, 2 / 3)
        self.assertAlmostEqual(costo, 50 / 3)

    def test_curso_200_ejemplos(self) -> None:
        horas, costo = estimar_costo_de_etiquetar(200, 5, 25)
        self.assertAlmostEqual(horas, 50 / 3)
        self.assertAlmostEqual(costo, 1250 / 3)

    def test_crecimiento_lineal_25_veces(self) -> None:
        horas8, _ = estimar_costo_de_etiquetar(8, 5, 25)
        horas200, _ = estimar_costo_de_etiquetar(200, 5, 25)
        self.assertAlmostEqual(horas200 / horas8, 25)

    def test_mini_ejercicio_500_base(self) -> None:
        curso = estimar_con_segunda_revision(500, 4, 20, 0.2, 2)
        self.assertAlmostEqual(curso.horas_base, 2000 / 60)
        self.assertAlmostEqual(curso.costo_base_usd, 2000 / 60 * 20)

    def test_mini_ejercicio_500_revision(self) -> None:
        curso = estimar_con_segunda_revision(500, 4, 20, 0.2, 2)
        self.assertEqual(curso.ejemplos_revisados, 100)
        self.assertAlmostEqual(curso.horas_revision, 200 / 60)
        self.assertAlmostEqual(curso.costo_revision_usd, 200 / 60 * 20)

    def test_mini_ejercicio_500_totales(self) -> None:
        curso = estimar_con_segunda_revision(500, 4, 20, 0.2, 2)
        self.assertEqual(round(curso.horas_totales, 2), 36.67)
        self.assertEqual(round(curso.costo_total_usd, 2), 733.33)
        self.assertEqual(round(curso.jornadas_ocho_horas, 1), 4.6)

    def test_booking_core_usa_cantidad_actual(self) -> None:
        self.assertEqual(len(ejemplos_raw), 20)
        caso = estimar_con_segunda_revision(len(ejemplos_raw), 4, 20, 0.2, 2)
        self.assertEqual(caso.ejemplos_revisados, 4)
        self.assertEqual(round(caso.horas_totales, 2), 1.47)
        self.assertEqual(round(caso.costo_total_usd, 2), 29.33)

    def test_revision_cero(self) -> None:
        caso = estimar_con_segunda_revision(10, 4, 20, 0, 2)
        self.assertEqual(caso.ejemplos_revisados, 0)
        self.assertEqual(caso.horas_revision, 0)
        self.assertEqual(caso.costo_revision_usd, 0)

    def test_etiquetado_cero(self) -> None:
        self.assertEqual(estimar_costo_de_etiquetar(0, 4, 20), (0, 0))

    def test_rechaza_valores_negativos(self) -> None:
        with self.assertRaises(ValueError):
            estimar_costo_de_etiquetar(-1, 4, 20)
        with self.assertRaises(ValueError):
            estimar_costo_de_etiquetar(10, -4, 20)
        with self.assertRaises(ValueError):
            estimar_costo_de_etiquetar(10, 4, -20)

    def test_rechaza_porcentaje_fuera_de_rango(self) -> None:
        for fraccion in (-0.01, 1.01):
            with self.subTest(fraccion=fraccion):
                with self.assertRaises(ValueError):
                    estimar_con_segunda_revision(10, 4, 20, fraccion, 2)

    def test_rechaza_cantidad_no_entera(self) -> None:
        with self.assertRaises(ValueError):
            estimar_con_segunda_revision(10.5, 4, 20, 0.2, 2)


if __name__ == "__main__":
    unittest.main()
