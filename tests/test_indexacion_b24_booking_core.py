"""Pruebas B24/L3: corpus propio, chunking e índice persistente sin Gemini."""

import importlib.util
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from langchain_core.documents import Document

from indexar_corpus import (
    DIRECTORIO_CORPUS,
    TAMANO_CHUNK,
    OVERLAP_CHUNK,
    cargar_documentos,
    crear_chunks,
    huella_corpus,
    ids_estables,
)

RAIZ = Path(__file__).resolve().parents[1]


class TestIndexacionB24L3(unittest.TestCase):
    def test_corpus_cinco_archivos_ficticios(self):
        documentos = cargar_documentos()
        self.assertEqual(len(documentos), 5)
        self.assertEqual(len({d.metadata["fuente"] for d in documentos}), 5)
        for doc in documentos:
            self.assertEqual(doc.metadata["origen"], "FICTICIO_ACADEMICO")
            self.assertIn("EJEMPLO FICTICIO", doc.page_content)
            self.assertNotIn("GEMINI_API_KEY=", doc.page_content)
            self.assertGreater(len(doc.page_content), 150)

    def test_recursivo_antes_de_embeddings_y_titulos_sin_aislar(self):
        docs = cargar_documentos()
        chunks = crear_chunks(docs)
        self.assertGreater(len(chunks), len(docs))
        self.assertTrue(all(1 <= len(d.page_content) <= TAMANO_CHUNK for d in chunks))
        self.assertEqual(OVERLAP_CHUNK, 80)
        self.assertEqual(
            {d.metadata["fuente"] for d in chunks},
            {d.metadata["fuente"] for d in docs},
        )
        self.assertTrue(
            all(d.metadata["metodo_chunking"] == "recursivo" for d in chunks)
        )
        for doc in docs:
            primeros = [
                p for p in chunks
                if p.metadata["fuente"] == doc.metadata["fuente"]
                and p.metadata["indice_chunk"] == 0
            ]
            self.assertEqual(len(primeros), 1)
            self.assertTrue(primeros[0].page_content.startswith(doc.metadata["titulo"]))
            self.assertGreater(
                len(primeros[0].page_content),
                len(doc.metadata["titulo"]) + 20,
            )

    def test_ids_estables_y_sin_duplicados(self):
        chunks = crear_chunks(cargar_documentos())
        a, b = ids_estables(chunks), ids_estables(crear_chunks(cargar_documentos()))
        self.assertEqual(a, b)
        self.assertEqual(len(set(a)), len(chunks))

    def test_huella_detecta_cambio(self):
        documentos = cargar_documentos()
        original = huella_corpus(documentos)
        cambiado = list(documentos)
        copia = documentos[0]
        cambiado[0] = Document(
            page_content=copia.page_content + " CAMBIO DE PRUEBA",
            metadata=dict(copia.metadata),
        )
        self.assertNotEqual(original, huella_corpus(cambiado))

    def test_faltan_documentos(self):
        with tempfile.TemporaryDirectory() as temporal:
            destino = Path(temporal)
            for i in range(4):
                (destino / f"doc_{i}.md").write_text(
                    "# Título\nEJEMPLO FICTICIO. Contenido.", encoding="utf-8"
                )
            with self.assertRaisesRegex(ValueError, "cinco"):
                cargar_documentos(destino)

    def test_documento_sin_marca_ficticia_rechazado(self):
        with tempfile.TemporaryDirectory() as temporal:
            destino = Path(temporal)
            for i in range(5):
                (destino / f"doc_{i}.md").write_text(
                    "# Título\nEJEMPLO FICTICIO. Contenido.", encoding="utf-8"
                )
            (destino / "doc_3.md").write_text(
                "# Título\nTexto sin advertencia.", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "FICTICIO"):
                cargar_documentos(destino)

    def test_directorio_corpus_en_raiz(self):
        self.assertTrue(DIRECTORIO_CORPUS.is_dir())
        self.assertEqual(DIRECTORIO_CORPUS.parent.name, "data")

    def test_chroma_persistente_otro_proceso_no_reindexa(self):
        """Indexar Chroma real con vectores falsos; reabrir sin ninguna API."""
        if importlib.util.find_spec("langchain_chroma") is None:
            self.skipTest("Chroma opcional: instalar requirements-rag.txt")

        generador = textwrap.dedent(
            """
            import sys
            from pathlib import Path
            from indexar_corpus import indexar_corpus

            class EmbeddingsFicticios:
                def embed_query(self, text):
                    return [float(len(text) % 11), 1.0, 2.0]
                def embed_documents(self, texts):
                    return [self.embed_query(t) for t in texts]

            r = indexar_corpus(
                directorio_vectorstore=Path(sys.argv[1]),
                embeddings=EmbeddingsFicticios(),
            )
            assert r["estado"] == "creado con embeddings"
            assert r["documentos"] == 5
            assert r["chunks"] >= 5
            print("INDEXACION_FAKE_OK", r["chunks"])
            """
        )
        reutilizador = textwrap.dedent(
            """
            import sys
            from pathlib import Path
            from indexar_corpus import indexar_corpus
            # Sin inyectar embeddings ni credencial: debe DETECTAR índice existente.
            r = indexar_corpus(directorio_vectorstore=Path(sys.argv[1]))
            assert r["estado"] == "existente; sin re-embedding"
            print("SIN_REEMBEDDING_OK", r["chunks"])
            """
        )
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "vectorstore"
            env = os.environ.copy()
            env.pop("GEMINI_API_KEY", None)
            for script, marca in (
                (generador, "INDEXACION_FAKE_OK"),
                (reutilizador, "SIN_REEMBEDDING_OK"),
            ):
                proceso = subprocess.run(
                    [sys.executable, "-c", script, str(ruta)],
                    cwd=str(RAIZ),
                    env=env,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=90,
                    check=False,
                )
                self.assertEqual(proceso.returncode, 0, proceso.stderr[-3000:])
                self.assertIn(marca, proceso.stdout)

            self.assertTrue((ruta / "chroma.sqlite3").is_file())
            self.assertTrue((ruta / "manifiesto_b24_l3.json").is_file())

            # Proceso completamente nuevo de lectura: NO inicializa Gemini.
            p = subprocess.run(
                [sys.executable, "verificar_vectorstore_b24.py", "--ruta", str(ruta)],
                cwd=str(RAIZ),
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=90,
                check=False,
            )
            self.assertEqual(p.returncode, 0, p.stderr[-3000:])
            self.assertIn("Persistencia confirmada", p.stdout)
            self.assertIn("Documentos de origen: 5", p.stdout)
            # Los subprocesos finalizaron: evita WinError 32 en Windows.


if __name__ == "__main__":
    unittest.main()
