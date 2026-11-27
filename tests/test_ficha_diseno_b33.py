"""Pruebas de la actividad B33/L3 en directorios temporales; sin tocar la ficha real."""
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FICHA = ROOT / "docs" / "ficha_diseno_funcional.md"
PNG = ROOT / "docs" / "diagrama_arquitectura.png"


class TestFichaB33(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = Path(self.tmp.name)
        self.ficha = self.cwd / "docs" / FICHA.name
        self.png = self.cwd / "docs" / PNG.name

    def ejecutar(self, script):
        return subprocess.run([sys.executable, str(ROOT / script)], cwd=self.cwd,
                              capture_output=True, text=True, encoding="utf-8",
                              env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})

    def copiar_ficha(self):
        self.ficha.parent.mkdir(exist_ok=True)
        shutil.copyfile(FICHA, self.ficha)

    def test_esqueleto_detecta_tres_marcas(self):
        creado = self.ejecutar("crear_ficha.py")
        self.assertEqual(creado.returncode, 0, creado.stderr)
        r = self.ejecutar("verificar_ficha.py")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout.count("ERROR:"), 3, r.stdout)
        self.assertIn("3 problema(s)", r.stdout)

    def test_generador_no_sobrescribe(self):
        self.copiar_ficha()
        antes = self.ficha.read_bytes()
        r = self.ejecutar("crear_ficha.py")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no se sobrescribe", r.stderr)
        self.assertEqual(self.ficha.read_bytes(), antes)

    def test_sin_diagrama(self):
        self.copiar_ficha()
        r = self.ejecutar("verificar_ficha.py")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout.count("ERROR:"), 1, r.stdout)
        self.assertIn("el diagrama docs/diagrama_arquitectura.png no existe", r.stdout)

    def test_ficha_completa(self):
        self.copiar_ficha()
        shutil.copyfile(PNG, self.png)
        r = self.ejecutar("verificar_ficha.py")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("AVISO:", r.stdout)
        self.assertNotIn("ERROR:", r.stdout)
        self.assertIn("Ficha verificada: secciones 1 a 3 completas", r.stdout)
        self.assertEqual(self.png.read_bytes()[:8], bytes.fromhex("89504e470d0a1a0a"))

    def test_rnf_sin_numero_y_rf_repetido(self):
        self.copiar_ficha()
        shutil.copyfile(PNG, self.png)
        texto = self.ficha.read_text(encoding="utf-8")
        texto = re.sub(r"(?m)^- RNF-01: .+$", "- RNF-01: El servicio es rapido.", texto)
        texto = texto.replace("Deseable: RF-05", "Deseable: RF-01, RF-05")
        self.ficha.write_text(texto, encoding="utf-8")
        r = self.ejecutar("verificar_ficha.py")
        self.assertEqual(r.returncode, 1)
        self.assertIn("RNF-01 no tiene ningun numero", r.stdout)
        self.assertIn("RF-01 debe estar en exactamente un cajon", r.stdout)

    def test_esqueleto_conserva_secciones_pendientes_b34(self):
        # La ficha real evoluciona en Core; probar el esqueleto histórico generado.
        creado = self.ejecutar("crear_ficha.py")
        self.assertEqual(creado.returncode, 0, creado.stderr)
        texto = self.ficha.read_text(encoding="utf-8")
        self.assertEqual(texto.count("[PENDIENTE: se completa en el Bloque 34]"), 2)
        self.assertIn("[COMPLETAR", texto)


if __name__ == "__main__":
    unittest.main()
