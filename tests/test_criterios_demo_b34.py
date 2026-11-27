"""Regresiones del ejemplo oficial, no pruebas del futuro servicio HTTP."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestCriteriosDemoB34(unittest.TestCase):
    def ejecutar(self, nombre):
        r = subprocess.run([sys.executable, str(ROOT / "criterios" / nombre)],
                           cwd=ROOT / "criterios", capture_output=True,
                           text=True, encoding="utf-8", timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_demo_cuatro_criterios(self):
        salida = self.ejecutar("criterios_demo.py")
        self.assertIn("4 de 4 criterios cumplidos", salida)
        self.assertEqual(salida.count("PASA "), 4)
        self.assertNotIn("FALLA", salida)

    def test_variante_detecta_contrato_incompleto(self):
        salida = self.ejecutar("variante_rota.py")
        self.assertIn("1 de 4 criterios cumplidos", salida)
        for id_ in ("CA-01", "CA-02", "CA-03"):
            self.assertIn(f"FALLA {id_}", salida)
        self.assertIn("PASA  CA-05", salida)
        self.assertEqual(salida.count("error: KeyError"), 2)
        self.assertEqual(salida.count("FALLA"), 3)


if __name__ == "__main__":
    unittest.main()
