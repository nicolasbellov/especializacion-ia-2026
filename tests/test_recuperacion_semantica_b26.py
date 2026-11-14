"""B26/L1: pruebas de retrieval sin API; no se reindexa ninguna base real."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from src import recuperacion_semantica_b26 as r

RAIZ = Path(__file__).resolve().parents[1]


@unittest.skipUnless(
    importlib.util.find_spec("langchain_chroma") is not None,
    "Pruebas B26 de Chroma corren en job RAG con requirements-rag.txt",
)
class TestRecuperacionSemanticaB26(unittest.TestCase):
    def test_corpus_y_metadatos_oficiales(self):
        self.assertEqual(len(r.CORPUS_FAKE), 5)
        self.assertIn("TimeoutError", r.CORPUS_FAKE[0])
        self.assertIn("totalTokenCount", r.CORPUS_FAKE[2])
        self.assertEqual(r.PREGUNTA_CURSO, "que pasa si la conexion tarda demasiado")

    def test_similarity_search_k_y_metadata_fake(self):
        store = r.crear_demo_fake()
        resultados = r.recuperar_documentos(store, r.PREGUNTA_CURSO, 3)
        self.assertEqual(len(resultados), 3)
        for doc in resultados:
            self.assertIn(doc.page_content, r.CORPUS_FAKE)
            self.assertIn(doc.metadata.get("fuente"), {f"doc{i}.md" for i in range(5)})

    def test_fake_no_es_evaluacion_semantica(self):
        store = r.crear_demo_fake()
        resultados = r.recuperar_documentos(store, r.PREGUNTA_CURSO, 3)
        # No exigir que TimeoutError sea primero con embeddings hash; comprobar forma.
        self.assertEqual(len(resultados), 3)
        self.assertTrue(all(hasattr(d, "page_content") for d in resultados))

    def test_distancias_numericas_ordenadas_no_porcentajes(self):
        store = r.crear_demo_fake()
        puntuaciones = r.recuperar_con_distancia(store, r.PREGUNTA_CURSO, 3)
        self.assertEqual(len(puntuaciones), 3)
        self.assertTrue(all(isinstance(v, (int, float)) for _, v in puntuaciones))
        self.assertEqual(
            [valor for _, valor in puntuaciones],
            sorted(valor for _, valor in puntuaciones),
        )
        # No comparar con los números ilustrativos del curso: dependen de versión.
        self.assertTrue(any(score > 1.0 for _, score in puntuaciones))

    def test_as_retriever_invoke_k2(self):
        store = r.crear_demo_fake()
        documentos = r.crear_retriever(store, k=2).invoke(r.PREGUNTA_RETRIEVER)
        self.assertEqual(len(documentos), 2)
        self.assertTrue(all("fuente" in d.metadata for d in documentos))

    def test_k_superior_a_total_devuelve_todos(self):
        store = r.crear_demo_fake()
        self.assertEqual(len(r.recuperar_documentos(store, "cualquier consulta", 10)), 5)

    def test_pregunta_y_k_invalidos(self):
        for pregunta, k in [("", 3), ("  ", 3), ("hola", 0), ("hola", -2), ("hola", 2.3)]:
            with self.subTest(pregunta=pregunta, k=k):
                with self.assertRaises(ValueError):
                    r.validar_entrada(pregunta, k)
        with self.assertRaises(ValueError):
            r.crear_retriever(object(), k=0)

    def test_indice_real_faltante_no_crea_ni_pide_api(self):
        with tempfile.TemporaryDirectory() as tmp:
            ausente = Path(tmp) / "indice_inexistente"
            with patch.object(r, "DIRECTORIO_B25", ausente), patch.object(
                r, "crear_embeddings"
            ) as crear:
                with self.assertRaises(FileNotFoundError):
                    r.abrir_indice_real()
                crear.assert_not_called()
            self.assertFalse(ausente.exists())

    def test_demo_cli_sin_credenciales_gemini(self):
        env = os.environ.copy()
        env.pop("GEMINI_API_KEY", None)
        env["PYTHONUTF8"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        resultado = subprocess.run(
            [sys.executable, "-m", "src.recuperacion_semantica_b26", "--modo", "fake"],
            cwd=str(RAIZ), env=env, capture_output=True, text=True,
            encoding="utf-8", errors="replace", check=False, timeout=45,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("MODO FAKE", resultado.stdout)
        self.assertIn("Chunks en Chroma: 5", resultado.stdout)
        self.assertIn("as_retriever.invoke", resultado.stdout)
        self.assertIn("MENOR distancia", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
