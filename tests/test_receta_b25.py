"""Bloque 25/L1 — pruebas de la receta reutilizable, sin Gemini real."""

import importlib.util
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from src.receta_indexacion_b25 import (
    CORPUS_EJEMPLO,
    DIRECTORIO_B25,
    preparar_chunks,
    _firma,
)

RAIZ = Path(__file__).resolve().parents[1]


def ejecutar_hijo(codigo: str, ruta: Path) -> subprocess.CompletedProcess[str]:
    """Subprocesos separados; forzar UTF-8 para evitar el error Windows B24-WIN-002."""
    env = os.environ.copy()
    env.pop("GEMINI_API_KEY", None)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-c", codigo, str(ruta)],
        cwd=str(RAIZ),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=90,
        check=False,
    )


class TestRecetaB25(unittest.TestCase):
    def test_ejemplo_oficial_tres_textos_tres_chunks(self):
        chunks = preparar_chunks(CORPUS_EJEMPLO)
        self.assertEqual(len(CORPUS_EJEMPLO), 3)
        self.assertEqual(len(chunks), 3)
        self.assertEqual([d.page_content for d in chunks], CORPUS_EJEMPLO)
        self.assertEqual(
            [d.metadata["fuente"] for d in chunks],
            ["ejemplo_skillnest_1", "ejemplo_skillnest_2", "ejemplo_skillnest_3"],
        )

    def test_tamano_overlap_son_parametros(self):
        fragmentos = preparar_chunks(["Primera idea en la documentación. " * 15],
                                     chunk_size=100, chunk_overlap=15)
        self.assertGreater(len(fragmentos), 1)
        self.assertTrue(all(len(d.page_content) <= 100 for d in fragmentos))

    def test_parametros_no_validos(self):
        for corpus, tam, overlap in [
            ([], 200, 30),
            ([""], 200, 30),
            (["abc"], 0, 0),
            (["abc"], 100, 100),
            (["abc"], 100, -1),
        ]:
            with self.subTest(corpus=corpus, tam=tam, overlap=overlap):
                with self.assertRaises(ValueError):
                    preparar_chunks(corpus, tam, overlap)

    def test_firma_determinista_y_sensible_al_texto(self):
        originales = preparar_chunks(CORPUS_EJEMPLO)
        firma, ids = _firma(originales, 200, 30)
        self.assertEqual((firma, ids), _firma(preparar_chunks(CORPUS_EJEMPLO), 200, 30))
        cambiados = preparar_chunks([CORPUS_EJEMPLO[0] + " nuevo"] + CORPUS_EJEMPLO[1:])
        firma2, ids2 = _firma(cambiados, 200, 30)
        self.assertNotEqual(firma, firma2)
        self.assertNotEqual(ids, ids2)
        self.assertEqual(len(ids), len(set(ids)))

    def test_ruta_diferente_de_los_indices_B24(self):
        self.assertIn(".local", DIRECTORIO_B25.parts)
        self.assertNotEqual(DIRECTORIO_B25, RAIZ / "vectorstore")
        self.assertNotEqual(DIRECTORIO_B25, RAIZ / ".local" / "chroma_b24")

    def test_preparar_es_offline_sin_credencial(self):
        env = os.environ.copy()
        env.pop("GEMINI_API_KEY", None)
        env["PYTHONIOENCODING"] = "utf-8"
        resultado = subprocess.run(
            [sys.executable, "-m", "src.receta_indexacion_b25", "--modo", "preparar"],
            cwd=str(RAIZ), env=env, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=20, check=False,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Chunking local: 3 chunks", resultado.stdout)

    def test_chroma_persistente_reutilizado_sin_llamadas_gemini(self):
        if importlib.util.find_spec("langchain_chroma") is None:
            self.skipTest("Falta chromadb/langchain-chroma de requirements-rag.txt")

        generar = textwrap.dedent(
            """
            import sys
            from pathlib import Path
            from src.receta_indexacion_b25 import indexar_corpus, CORPUS_EJEMPLO

            class FakeEmbeddings:
                def embed_query(self, text):
                    return [float(len(text) % 19), 1.0, 2.0]
                def embed_documents(self, texts):
                    return [self.embed_query(t) for t in texts]

            store, estado, n = indexar_corpus(
                CORPUS_EJEMPLO, Path(sys.argv[1]), embeddings=FakeEmbeddings()
            )
            assert estado == "indexado con embeddings"
            assert n == store._collection.count() == 3
            print("INDICE_FAKE_3_OK")
            """
        )
        comprobar = textwrap.dedent(
            """
            import sys
            from pathlib import Path
            from src.receta_indexacion_b25 import (
                CORPUS_EJEMPLO, verificar_indice, indexar_corpus
            )

            destino = Path(sys.argv[1])
            assert verificar_indice(CORPUS_EJEMPLO, destino) == 3
            # No hay API key ni embeddings inyectados: jamás debe crearlos de nuevo.
            _, estado, n = indexar_corpus(CORPUS_EJEMPLO, destino)
            assert estado == "reutilizado sin re-embedding" and n == 3

            try:
                indexar_corpus(CORPUS_EJEMPLO + ["Texto nuevo"], destino)
                raise AssertionError("Debió rechazar un corpus alterado")
            except ValueError as error:
                assert "cambiaron" in str(error)
            print("PERSISTENCIA_3_OK")
            """
        )
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / "indice_b25"
            for codigo, marca in [
                (generar, "INDICE_FAKE_3_OK"),
                (comprobar, "PERSISTENCIA_3_OK"),
            ]:
                p = ejecutar_hijo(codigo, destino)
                self.assertEqual(p.returncode, 0, p.stderr[-2500:])
                self.assertIn(marca, p.stdout)
            self.assertTrue((destino / "chroma.sqlite3").is_file())
            self.assertTrue((destino / "manifiesto_b25_receta.json").is_file())


if __name__ == "__main__":
    unittest.main()
