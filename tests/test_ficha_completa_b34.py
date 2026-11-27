"""Pruebas Core B34. Registro sintético exclusivamente temporal, no evidencia real."""
import os
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

# Fixture de formato; no representa una persona ni revisión efectuada.
REVISION_FIXTURE = """# Revisión del alcance
Revisor: FIXTURE DE PRUEBA (no es una revisión)
Fecha: FECHA SINTÉTICA

- Hallazgo 1 (criterio 4): Texto sintético para probar el patrón.
  Decisión: aceptado. Cambio: ejemplo de formato.

- Hallazgo 2: Segundo texto sintético.
  Decisión: rechazado. Motivo: ejemplo de formato.
"""


class TestFichaCompletaB34(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = Path(self.tmp.name)
        self.docs = self.cwd / "docs"
        self.docs.mkdir()
        self.ficha = self.docs / FICHA.name
        self.revision = self.docs / "revision_alcance.md"
        shutil.copyfile(FICHA, self.ficha)
        shutil.copyfile(PNG, self.docs / PNG.name)

    def ejecutar(self):
        return subprocess.run(
            [sys.executable, str(ROOT / "verificar_ficha_completa.py")],
            cwd=self.cwd, capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=30,
        )

    def cambiar(self, anterior, nuevo):
        texto = self.ficha.read_text(encoding="utf-8")
        self.assertIn(anterior, texto)
        self.ficha.write_text(texto.replace(anterior, nuevo, 1), encoding="utf-8")

    def test_sin_revision_bloquea(self):
        r = self.ejecutar()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("falta docs/revision_alcance.md", r.stdout)
        self.assertEqual(r.stdout.count("ERROR:"), 1, r.stdout)
        self.assertNotIn("AVISO:", r.stdout)

    def test_formato_completo_con_fixture(self):
        self.revision.write_text(REVISION_FIXTURE, encoding="utf-8")
        r = self.ejecutar()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Ficha verificada: las cinco secciones son coherentes", r.stdout)
        self.assertNotIn("AVISO:", r.stdout)

    def test_pendientes_prioritarios(self):
        self.cambiar("## 4. Criterios de aceptación", "## 4. Criterios de aceptación\n[PENDIENTE]")
        r = self.ejecutar()
        self.assertEqual(r.returncode, 1)
        self.assertIn("la seccion 4 todavia tiene marcas", r.stdout)
        self.assertNotIn("falta docs/revision_alcance.md", r.stdout)

    def test_requerimiento_sin_criterio(self):
        texto = self.ficha.read_text(encoding="utf-8")
        texto = re.sub(r"(?m)^- CA-\d{2} \(RNF-05\): .+\n", "", texto)
        self.ficha.write_text(texto, encoding="utf-8")
        r = self.ejecutar()
        self.assertEqual(r.returncode, 1)
        self.assertIn("RNF-05 no tiene criterio de aceptacion", r.stdout)

    def test_exceso_horas(self):
        texto = self.ficha.read_text(encoding="utf-8")
        texto = re.sub(r"(?m)^- H5 \([\d.,]+ h\)", "- H5 (999 h)", texto)
        self.ficha.write_text(texto, encoding="utf-8")
        r = self.ejecutar()
        self.assertEqual(r.returncode, 1)
        self.assertIn("y el tope es", r.stdout)

    def test_hito_sin_criterio(self):
        texto = self.ficha.read_text(encoding="utf-8")
        texto = re.sub(r"(?m)^(- H4 .+?Se comprueba con:).+$", r"\1 pruebas manuales.", texto)
        self.ficha.write_text(texto, encoding="utf-8")
        r = self.ejecutar()
        self.assertEqual(r.returncode, 1)
        self.assertIn("H4 no tiene criterio de aceptacion", r.stdout)

    def test_revision_sangria_y_tilde(self):
        for sustitucion in (" Decisión:", "    Decisión:", "\tDecisión:", "  Decision:"):
            with self.subTest(sustitucion=sustitucion):
                self.revision.write_text(REVISION_FIXTURE.replace("  Decisión:", sustitucion, 1), encoding="utf-8")
                r = self.ejecutar()
                self.assertEqual(r.returncode, 1)
                self.assertIn("cada hallazgo necesita", r.stdout)

    def test_revision_un_hallazgo(self):
        self.revision.write_text(REVISION_FIXTURE.split("- Hallazgo 2:")[0], encoding="utf-8")
        r = self.ejecutar()
        self.assertEqual(r.returncode, 1)
        self.assertIn("hay 1 hallazgos y se piden 2", r.stdout)


if __name__ == "__main__":
    unittest.main()
