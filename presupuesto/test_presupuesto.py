import unittest
from unittest.mock import patch

import presupuesto_alcance as pa
import presupuesto_booking_core as bc


class TestEjemploOficial(unittest.TestCase):
    def test_pedido_y_mvp(self):
        self.assertEqual(sum(pa.horas_reales(f) for f in pa.funcionalidades), 71)
        self.assertEqual(pa.presupuesto(), 10)
        dentro, fuera, usado = pa.recortar(pa.funcionalidades)
        self.assertEqual([f["id"] for f in dentro], ["RF-02", "RF-01", "RF-03", "RF-05"])
        self.assertEqual(usado, 10)
        self.assertEqual({f["id"] for f, m in fuera if m == "requiere datos o sistemas reales"}, {"RF-04", "RF-07"})

    def test_sin_contenedor(self):
        lista = [f for f in pa.funcionalidades if f["id"] != "RF-03"]
        dentro, _, usado = pa.recortar(lista)
        self.assertEqual(sum(pa.horas_reales(f) for f in lista), 68)
        self.assertEqual(usado, 10)
        self.assertEqual(pa.CAPAS_OBLIGATORIAS - {f["capa"] for f in dentro}, {"contenedor"})
        self.assertIn("RF-06", {f["id"] for f in dentro})

    def test_quince_horas(self):
        with patch.object(pa, "HORAS_DISPONIBLES", 15):
            self.assertEqual(pa.presupuesto(), 7.5)
            dentro, _, usado = pa.recortar(pa.funcionalidades)
            self.assertEqual(usado, 7)
            self.assertEqual([f["id"] for f in dentro], ["RF-02", "RF-01", "RF-05"])


class TestBookingCore(unittest.TestCase):
    def test_veinte_no_viable(self):
        r = bc.evaluar(20)
        self.assertFalse(r["viable"])
        self.assertEqual(r["faltantes"], {"T-DOCKER"})

    def test_veintidos_minimo(self):
        r = bc.evaluar(22)
        self.assertTrue(r["viable"])
        self.assertEqual(r["usado"], 11)
        self.assertNotIn("RF-05", {f["id"] for f in r["dentro"]})

    def test_veinticuatro(self):
        r = bc.evaluar(24)
        self.assertTrue(r["viable"])
        self.assertEqual(r["neto"] - r["usado"], 1)

    def test_veintiocho_incluye_deseable(self):
        r = bc.evaluar(28)
        self.assertTrue(r["viable"])
        self.assertEqual(r["usado"], 14)
        self.assertIn("RF-05", {f["id"] for f in r["dentro"]})

    def test_exclusiones_y_configuracion(self):
        self.assertEqual(set(bc.EXCLUIDAS), {"RF-06", "RF-07"})
        self.assertEqual(pa.HORAS_DISPONIBLES, 20)
        for horas in (0, -1, float("nan"), float("inf"), 0.001):
            with self.subTest(horas=horas), self.assertRaises(ValueError):
                bc.evaluar(horas)


if __name__ == "__main__":
    unittest.main()
