"""Pruebas offline para la réplica oficial Skillnest B25/L3; nunca usar Gemini real."""

from __future__ import annotations

import copy
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest.mock import patch

import replica_ejemplo as replica

RAIZ = Path(__file__).resolve().parents[1]


def ejecutar(codigo, ruta):
    env = os.environ.copy()
    env.pop("GEMINI_API_KEY", None)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    return subprocess.run(
        [sys.executable, "-c", codigo, str(ruta)],
        cwd=str(RAIZ), env=env, text=True, capture_output=True,
        encoding="utf-8", errors="replace", timeout=100, check=False,
    )


class TestReplicaEjemploB25(unittest.TestCase):
    def test_corpus_oficial_cinco_textos_490_caracteres(self):
        self.assertEqual(len(replica.CORPUS_EJEMPLO), 5)
        self.assertEqual(list(map(len, replica.CORPUS_EJEMPLO)),
                         [106, 103, 99, 85, 97])
        self.assertEqual(sum(map(len, replica.CORPUS_EJEMPLO)), 490)

    def test_chunking_150_20_sin_perdida_ni_duplicados(self):
        chunks = replica.preparar_chunks()
        textos = [c.page_content for c in chunks]
        self.assertEqual(replica.CHUNK_SIZE, 150)
        self.assertEqual(replica.CHUNK_OVERLAP, 20)
        self.assertEqual(textos, replica.CORPUS_EJEMPLO)
        self.assertEqual(len(textos), len(set(textos)))
        self.assertEqual(sum(map(len, textos)), 490)

    def test_ids_y_huella_estables_y_sensibles_a_cambios(self):
        chunks = replica.preparar_chunks()
        huella, ids = replica._identidad(chunks)
        self.assertEqual((huella, ids), replica._identidad(replica.preparar_chunks()))
        self.assertEqual(len(ids), len(set(ids)))
        cambiado = copy.deepcopy(chunks)
        cambiado[0].page_content += " otro"
        huella2, ids2 = replica._identidad(cambiado)
        self.assertNotEqual(huella, huella2)
        self.assertNotEqual(ids, ids2)

    def test_ruta_local_distinta_de_indices_b24_y_b25_l1(self):
        self.assertEqual(replica.INDICE, RAIZ / ".local" / "chroma_b25_tienda_ejemplo")
        self.assertNotEqual(replica.INDICE, RAIZ / "vectorstore")
        self.assertNotEqual(replica.INDICE, RAIZ / ".local" / "chroma_b24")
        self.assertNotEqual(replica.INDICE, RAIZ / ".local" / "chroma_b25_receta")
        self.assertEqual(replica.COLECCION, "tienda_ficticia_b25_replica")

    def test_cli_preparar_no_exige_credencial(self):
        env = os.environ.copy()
        env.pop("GEMINI_API_KEY", None)
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        p = subprocess.run(
            [sys.executable, "replica_ejemplo.py", "--modo", "preparar"],
            cwd=str(RAIZ), env=env, text=True, capture_output=True,
            encoding="utf-8", errors="replace", timeout=25, check=False,
        )
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("5 chunks generados", p.stdout)
        self.assertIn("PREFLIGHT OK: 5 chunks, 490 caracteres", p.stdout)

    def test_verificacion_sin_indice_no_crea_carpeta(self):
        if importlib.util.find_spec("langchain_chroma") is None:
            self.skipTest("langchain-chroma no instalado; usar requirements-rag.txt")
        with tempfile.TemporaryDirectory() as temp:
            ruta = Path(temp) / "indice_inexistente"
            with patch.object(replica, "INDICE", ruta):
                with self.assertRaises(FileNotFoundError):
                    replica.verificar(replica.preparar_chunks())
            self.assertFalse(ruta.exists())

    def test_sin_clave_no_intenta_embeddings(self):
        if importlib.util.find_spec("langchain_chroma") is None:
            self.skipTest("langchain-chroma no instalado")
        with tempfile.TemporaryDirectory() as temp:
            ruta = Path(temp) / "nuevo"
            with patch.object(replica, "INDICE", ruta), patch.dict(
                os.environ, {"GEMINI_API_KEY": ""}
            ), patch("dotenv.load_dotenv", return_value=False):
                with self.assertRaisesRegex(RuntimeError, "Falta GEMINI_API_KEY"):
                    replica.indexar(replica.preparar_chunks())
            self.assertFalse(ruta.exists())

    def test_persistencia_entre_procesos_sin_gemini_y_reuso(self):
        if importlib.util.find_spec("langchain_chroma") is None:
            self.skipTest("langchain-chroma no instalado")
        indexar = textwrap.dedent(
            """
            import os, sys
            from pathlib import Path
            from unittest.mock import patch
            import replica_ejemplo as r

            class FakeEmbeddings:
                def embed_query(self, text):
                    return [float(len(text) % 23), 1.0, 2.0]
                def embed_documents(self, textos):
                    return [self.embed_query(t) for t in textos]

            os.environ["GEMINI_API_KEY"] = "fake-test-only"
            with patch.object(r, "INDICE", Path(sys.argv[1])), patch(
                "langchain_google_genai.GoogleGenerativeAIEmbeddings",
                return_value=FakeEmbeddings()
            ):
                r.indexar(r.preparar_chunks())
            assert (Path(sys.argv[1]) / "chroma.sqlite3").is_file()
            print("CINCO_CHUNKS_SIMULADOS_OK")
            """
        )
        comprobar = textwrap.dedent(
            """
            import sys
            from pathlib import Path
            from unittest.mock import patch
            import replica_ejemplo as r

            with patch.object(r, "INDICE", Path(sys.argv[1])):
                chunks = r.preparar_chunks()
                assert r.verificar(chunks) == 5
                # No API key: la reejecución debe reutilizar lo persistido.
                r.indexar(chunks)
            print("PERSISTENCIA_5_REUSO_OK")
            """
        )
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "indice_prueba"
            for codigo, marca in [
                (indexar, "CINCO_CHUNKS_SIMULADOS_OK"),
                (comprobar, "PERSISTENCIA_5_REUSO_OK"),
            ]:
                p = ejecutar(codigo, ruta)
                self.assertEqual(p.returncode, 0, p.stderr[-2500:])
                self.assertIn(marca, p.stdout)
            self.assertTrue((ruta / replica.MANIFIESTO).is_file())


if __name__ == "__main__":
    unittest.main()
