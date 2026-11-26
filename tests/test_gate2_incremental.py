"""Prueba incremental en Chroma real, corpus COPIADO y embeddings sintéticos."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

RAIZ = Path(__file__).resolve().parents[1]


@unittest.skipUnless(importlib.util.find_spec("langchain_chroma") is not None,
                     "Requiere Chroma")
class TestGate2Incremental(unittest.TestCase):
    def test_incremental_conserva_vectores_y_sin_duplicados(self):
        codigo = textwrap.dedent("""
            import sys
            import shutil
            from pathlib import Path
            from servicio_rag import CORPUS, EmbeddingsEnsayo, abrir_preparado
            from gate2.indice import preparar_indice
            from indexar_corpus import comprobar_indice

            base = Path(sys.argv[1])
            corpus = base / "corpus"
            shutil.copytree(CORPUS, corpus)
            ruta = base / "indice"
            emb = EmbeddingsEnsayo()
            _, info = abrir_preparado(ruta, corpus, emb)
            assert info["chunks"] == 10
            assert emb.documentos_embebidos == 10
            # Cambiar un documento conservando el ID de fuente; añadir otro
            # y eliminar otro (se mantienen cinco fuentes académicas).
            mod = corpus / "03_reprogramacion.md"
            mod.write_text(mod.read_text(encoding="utf-8") + "\\nNota ficticia de actualización.", encoding="utf-8")
            (corpus / "05_privacidad.md").unlink()
            (corpus / "06_revision.md").write_text("# Revision\\nEJEMPLO FICTICIO. Revision de prueba.", encoding="utf-8")
            n = emb.documentos_embebidos
            r = preparar_indice(ruta, corpus, emb, actualizar=True)
            assert r["upserts"] > 0 and r["eliminados"] > 0 and r["conservados"] > 0, r
            assert emb.documentos_embebidos - n == r["upserts"], r
            assert comprobar_indice(ruta)["chunks"] == r["chunks"]
            n = emb.documentos_embebidos
            segundo = preparar_indice(ruta, corpus, emb, actualizar=True)
            assert segundo["estado"] == "sin_cambios"
            assert emb.documentos_embebidos == n
            print("GATE2_INCREMENTAL_PASS", r)
        """)
        with tempfile.TemporaryDirectory() as tmp:
            p = subprocess.run([sys.executable, "-c", codigo, tmp],
                               cwd=str(RAIZ), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=120)
            self.assertEqual(p.returncode, 0, p.stderr[-4000:])
            self.assertIn("GATE2_INCREMENTAL_PASS", p.stdout)


if __name__ == "__main__":
    unittest.main()
