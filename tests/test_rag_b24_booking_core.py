"""Pruebas offline de U2.5/B24: no llaman a Gemini ni a Booking Core."""

import importlib.util
import subprocess
import sys
import tempfile
import textwrap
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
        """Persiste y recupera datos entre procesos, liberando handles en Windows.

        El índice se escribe y consulta desde procesos Python independientes.
        Al finalizar cada proceso, Windows puede cerrar los archivos de Chroma
        ANTES de que TemporaryDirectory intente eliminar data_level0.bin.
        No se llama a Gemini, ni se accede a Booking Core o Supabase.
        """
        if importlib.util.find_spec("langchain_chroma") is None:
            self.skipTest("Chroma opcional: instalar requirements-rag.txt")

        trabajador = textwrap.dedent(
            """
            import sys
            from langchain_chroma import Chroma
            from src.rag_b24_booking_core import (
                buscar_demo,
                crear_documentos_demo,
                indexar_demo,
            )

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

            store = Chroma(
                collection_name="test_booking_core_b24",
                embedding_function=EmbeddingsFicticios(),
                persist_directory=sys.argv[1],
            )

            if sys.argv[2] == "indexar":
                documentos = crear_documentos_demo()
                indexar_demo(store, documentos)
                indexar_demo(store, documentos)
                assert len(store.get()["ids"]) == len(documentos)
            elif sys.argv[2] == "recuperar":
                assert len(store.get()["ids"]) == 5
                resultados = buscar_demo(store, "¿Cómo cambio mi cita?", k=2)
                assert len(resultados) == 2
                assert all(
                    d.metadata["origen"] == "FICTICIO_ACADEMICO"
                    for d in resultados
                )
            else:
                raise ValueError("Modo de prueba desconocido")
            """
        )

        with tempfile.TemporaryDirectory() as temporal:
            for modo in ("indexar", "recuperar"):
                resultado = subprocess.run(
                    [sys.executable, "-c", trabajador, temporal, modo],
                    cwd=str(CORPUS_DEMO.parent.parent),
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=90,
                    check=False,
                )
                self.assertEqual(
                    resultado.returncode, 0,
                    msg=f"Falló proceso Chroma ({modo}):\n"
                    f"{resultado.stderr[-3000:]}",
                )


if __name__ == "__main__":
    unittest.main()
