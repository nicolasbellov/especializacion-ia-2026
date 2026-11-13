"""Pruebas offline de U2.5/B24: no llaman a Gemini ni a Booking Core."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from langchain_core.documents import Document

from src.rag_b24_booking_core import (
    CORPUS_DEMO,
    MODELO_EMBEDDING,
    buscar_demo,
    clasificar_fallo,
    crear_documentos_demo,
    crear_embeddings,
    id_estable,
    indexar_demo,
)


class StoreFicticio:
    def __init__(self):
        self.registros = {}
        self.consultas = []

    def add_documents(self, documents, ids):
        for documento, identificador in zip(documents, ids):
            self.registros[identificador] = documento

    def similarity_search(self, query, k):
        self.consultas.append((query, k))
        return list(self.registros.values())[:k]


class TestRagBookingCoreB24(unittest.TestCase):
    def test_corpus_en_secciones_y_sin_secretos(self):
        self.assertTrue(CORPUS_DEMO.is_file())
        docs = crear_documentos_demo()
        self.assertEqual(len(docs), 5)
        for documento in docs:
            self.assertTrue(documento.page_content.startswith("## "))
            self.assertEqual(documento.metadata["origen"], "FICTICIO_ACADEMICO")
            self.assertEqual(documento.metadata["fuente"], CORPUS_DEMO.name)
            self.assertNotIn("GEMINI_API_KEY=", documento.page_content)
            self.assertNotIn("tenantId", documento.metadata)

    def test_titulos_y_ids_estables(self):
        docs = crear_documentos_demo()
        ids = [id_estable(d) for d in docs]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, [id_estable(d) for d in crear_documentos_demo()])

    def test_sin_secciones_falla(self):
        with tempfile.TemporaryDirectory() as temporal:
            p = Path(temporal) / "vacio.md"
            p.write_text("# Sin secciones", encoding="utf-8")
            with self.assertRaises(ValueError):
                crear_documentos_demo(p)

    def test_indexacion_repetida_no_duplica_ids(self):
        store = StoreFicticio()
        docs = crear_documentos_demo()
        self.assertEqual(indexar_demo(store, docs), len(docs))
        self.assertEqual(indexar_demo(store, docs), len(docs))
        self.assertEqual(len(store.registros), len(docs))

    def test_indexacion_sin_documentos(self):
        with self.assertRaises(ValueError):
            indexar_demo(StoreFicticio(), [])

    def test_recuperacion_reutiliza_store(self):
        store = StoreFicticio()
        indexar_demo(store, crear_documentos_demo())
        resultados = buscar_demo(store, "  ¿Puedo cambiar mi hora?  ", k=2)
        self.assertEqual(store.consultas, [("¿Puedo cambiar mi hora?", 2)])
        self.assertEqual(len(resultados), 2)
        self.assertTrue(all(isinstance(d, Document) for d in resultados))

    def test_preguntas_invalidas(self):
        with self.assertRaises(ValueError):
            buscar_demo(StoreFicticio(), "  ")
        with self.assertRaises(ValueError):
            buscar_demo(StoreFicticio(), "horarios", k=0)

    @patch("src.rag_b24_booking_core.load_dotenv")
    def test_sin_clave_no_hace_llamada(self, carga_ficticia):
        with patch.dict("os.environ", {"GEMINI_API_KEY": ""}):
            with self.assertRaisesRegex(RuntimeError, "GEMINI_API_KEY"):
                crear_embeddings()
        carga_ficticia.assert_called_once()

    def test_diagnostico_no_expone_error_completo(self):
        self.assertIn("429", clasificar_fallo(Exception("429 RESOURCE_EXHAUSTED")))
        self.assertIn("Autenticación", clasificar_fallo(Exception("API key incorrecta")))
        self.assertNotIn("secreto", clasificar_fallo(Exception("detalle secreto")))

    def test_modelo_oficial(self):
        self.assertEqual(MODELO_EMBEDDING, "models/gemini-embedding-001")


    def test_chroma_local_real_sin_red_si_instalado(self):
        """Comprueba persistencia y búsqueda reales con vectores ficticios."""
        try:
            from langchain_chroma import Chroma
        except ImportError:
            self.skipTest("Chroma es dependencia opcional: usar requirements-rag.txt")

        class EmbeddingsFicticios:
            def embed_documents(self, texts):
                return [self.embed_query(t) for t in texts]

            def embed_query(self, text):
                texto = text.lower()
                return [
                    float(texto.count("cita") + 1),
                    float(texto.count("servicio") + 1),
                    float(texto.count("reserva") + 1),
                ]

        with tempfile.TemporaryDirectory() as temporal:
            store = Chroma(
                collection_name="test_booking_core_b24",
                embedding_function=EmbeddingsFicticios(),
                persist_directory=temporal,
            )
            docs = crear_documentos_demo()
            indexar_demo(store, docs)
            indexar_demo(store, docs)
            self.assertEqual(len(store.get()["ids"]), len(docs))
            resultados = buscar_demo(store, "¿Cómo cambio mi cita?", k=2)
            self.assertEqual(len(resultados), 2)
            self.assertTrue(
                all(d.metadata["origen"] == "FICTICIO_ACADEMICO" for d in resultados)
            )


if __name__ == "__main__":
    unittest.main()
