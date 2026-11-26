"""Gate2 E2E: corpus REAL ficticio -> CHROMA REAL -> retriever -> RAG -> respuesta.

Los embeddings y el LLM se simulan deliberadamente; no se usa Gemini.
El índice se crea en un directorio TEMPORAL, nunca en vectorstore/
persistido del alumno. Se ejecuta en SUBPROCESO para evitar bloqueos de
SQLite en Windows al limpiar el directorio temporal.
"""

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


RAIZ = Path(__file__).resolve().parents[1]


@unittest.skipUnless(
    importlib.util.find_spec("langchain_chroma") is not None
    and importlib.util.find_spec("langchain_text_splitters") is not None,
    "La prueba E2E Chroma requiere requirements-rag.txt",
)
class TestGate2E2EChroma(unittest.TestCase):
    def test_indexar_persistir_reabrir_recuperar_y_responder_en_chroma_real(self):
        codigo = textwrap.dedent(
            """
            import sys
            from pathlib import Path
            from langchain_core.messages import AIMessage

            from indexar_corpus import indexar_corpus, comprobar_indice
            from recuperacion import abrir_vectorstore
            from gate2.servicio import ServicioRAG, RESPONDIDA
            from logging_rag import configurar_logger

            class EmbeddingsDeterministas:
                def _vector(self, texto):
                    palabras = texto.casefold()
                    return [
                        1.0 + float(palabras.count("cita")),
                        1.0 + float(palabras.count("reprogram")),
                        1.0 + float(palabras.count("privacidad")),
                        1.0 + float(palabras.count("disponibilidad")),
                        1.0 + float(palabras.count("cancel")),
                        1.0,
                    ]

                def embed_query(self, text):
                    return self._vector(text)

                def embed_documents(self, texts):
                    return [self._vector(t) for t in texts]

            ruta = Path(sys.argv[1])
            modelo_embeddings = EmbeddingsDeterministas()

            # INDEXACIÓN de corpus académico real en Chroma temporal, sin Gemini.
            creado = indexar_corpus(
                directorio_vectorstore=ruta,
                embeddings=modelo_embeddings,
            )
            assert creado["estado"] == "creado con embeddings", creado
            assert creado["documentos"] == 5, creado
            assert creado["chunks"] == 10, creado

            # Persistencia + integridad de manifiesto, IDs y fuente en Chroma.
            verificado = comprobar_indice(ruta)
            assert verificado["chunks"] == 10
            print("CHROMA_TEMP_INDEXADO", creado["documentos"], creado["chunks"])

            # Reutilización sin rehacer embeddings.
            segundo = indexar_corpus(directorio_vectorstore=ruta)
            assert segundo["estado"] == "existente; sin re-embedding"
            print("CHROMA_SIN_REEMBEDDING", segundo["chunks"])

            # Reapertura, recuperación semántica con vector fake y 1 respuesta.
            store = abrir_vectorstore(directorio=ruta, embeddings=modelo_embeddings)
            retriever = store.as_retriever(search_kwargs={"k": 3})

            def generar_respuesta(mensajes):
                assert "<contexto_recuperado>" in mensajes[1].content
                return AIMessage(
                    content="La información procede de una política ficticia [1].",
                    usage_metadata={
                        "input_tokens": 60,
                        "output_tokens": 12,
                        "total_tokens": 72,
                    },
                )

            resultado = ServicioRAG(
                retriever.invoke,
                generar_respuesta,
                logger=configurar_logger(),
                simulado=True,
                k=3,
            ).consultar("¿Cómo reprogramar una cita de prueba?")
            assert resultado.estado == RESPONDIDA, resultado.estado
            assert 1 <= resultado.documentos_recuperados <= 3
            assert resultado.documentos_descartados == 0
            assert resultado.citas_utilizadas == (1,)
            assert resultado.fuentes[1].endswith(".md")
            assert resultado.consumo["total_tokens"] == 72
            print("GATE2_E2E_CHROMA_PASS", resultado.fuentes[1])
            print("SIN_GEMINI_SIN_RESERVAS_REALES")
            """
        )
        with tempfile.TemporaryDirectory() as temporal:
            indice_temporal = str(Path(temporal) / "chroma_gate2")
            entorno = os.environ.copy()
            entorno.pop("GEMINI_API_KEY", None)
            entorno.pop("GOOGLE_API_KEY", None)
            entorno["PYTHONIOENCODING"] = "utf-8"
            entorno["PYTHONUTF8"] = "1"
            proceso = subprocess.run(
                [sys.executable, "-c", codigo, indice_temporal],
                cwd=str(RAIZ),
                env=entorno,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
                check=False,
            )
            self.assertEqual(proceso.returncode, 0, proceso.stderr[-3500:])
            self.assertIn("CHROMA_TEMP_INDEXADO 5 10", proceso.stdout)
            self.assertIn("CHROMA_SIN_REEMBEDDING 10", proceso.stdout)
            self.assertIn("GATE2_E2E_CHROMA_PASS", proceso.stdout)
            self.assertIn("SIN_GEMINI_SIN_RESERVAS_REALES", proceso.stdout)


if __name__ == "__main__":
    unittest.main()
