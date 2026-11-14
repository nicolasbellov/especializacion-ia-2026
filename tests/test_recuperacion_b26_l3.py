"""B26/L3: pruebas sin red de recuperación citada sobre el corpus propio.

La indexación con Gemini real queda EXCLUSIVAMENTE para PowerShell del alumno.
Estos tests no alteran vectorstore/ y nunca usan credenciales reales.
"""

from __future__ import annotations

import importlib.util
from io import StringIO
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from langchain_core.documents import Document
import recuperacion as rag


class FakeRetriever:
    def __init__(self, store, k: int):
        self.store = store
        self.k = k

    def invoke(self, pregunta: str):
        self.store.preguntas.append(pregunta)
        texto = pregunta.lower()
        if "empresas" in texto or "datos" in texto or "privacidad" in texto:
            return self.store.docs_privacidad[:self.k]
        return self.store.docs_cambio[:self.k]


class FakeStore:
    def __init__(self):
        self.preguntas = []
        self.docs_cambio = [
            Document(
                page_content="EJEMPLO FICTICIO. Para cambiar una cita se necesita autorización.",
                metadata={"fuente": "03_reprogramacion.md", "origen": "FICTICIO_ACADEMICO"},
            ),
            Document(
                page_content="EJEMPLO FICTICIO. Consultar disponibilidad en backend.",
                metadata={"fuente": "02_disponibilidad.md", "origen": "FICTICIO_ACADEMICO"},
            ),
            Document(
                page_content="EJEMPLO FICTICIO. El catálogo contiene corte de cabello.",
                metadata={"fuente": "01_servicios.md", "origen": "FICTICIO_ACADEMICO"},
            ),
        ]
        self.docs_privacidad = [
            Document(
                page_content="EJEMPLO FICTICIO. Los tenants se aislan en backend.",
                metadata={"fuente": "05_privacidad.md", "origen": "FICTICIO_ACADEMICO"},
            ),
            self.docs_cambio[1],
            self.docs_cambio[0],
        ]

    def as_retriever(self, search_kwargs):
        return FakeRetriever(self, search_kwargs["k"])


@unittest.skipUnless(
    importlib.util.find_spec("langchain_chroma") is not None
    and importlib.util.find_spec("langchain_text_splitters") is not None,
    "B26/L3 se prueba en job RAG con requirements-rag.txt",
)
class TestRecuperacionPropiaB26(unittest.TestCase):
    def test_b24_ya_incluye_metadata_ids_y_5_fuentes(self):
        from indexar_corpus import (
            cargar_documentos, crear_chunks, ids_estables, COLECCION
        )
        documentos = cargar_documentos()
        chunks = crear_chunks(documentos)
        ids = ids_estables(chunks)
        self.assertEqual(COLECCION, "booking_core_b24_l3")
        self.assertEqual(len(documentos), 5)
        self.assertEqual(len(chunks), 10)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 10)
        self.assertEqual(len({doc.metadata["fuente"] for doc in chunks}), 5)
        self.assertTrue(all(
            doc.metadata.get("origen") == "FICTICIO_ACADEMICO"
            and doc.metadata.get("fuente") and "indice_chunk" in doc.metadata
            for doc in chunks
        ))

    def test_prompt_cita_tres_fuentes_propias_y_pregunta_exacta(self):
        store = FakeStore()
        pregunta = " ¿Cómo solicito otro horario? "
        resultado = rag.construir_resultado(pregunta, k=3, store=store)
        self.assertEqual(resultado.pregunta, pregunta)
        self.assertIn(f"Pregunta: {pregunta}", resultado.prompt)
        self.assertEqual(len(resultado.documentos), 3)
        self.assertEqual(resultado.citas, {
            1: "03_reprogramacion.md",
            2: "02_disponibilidad.md",
            3: "01_servicios.md",
        })
        self.assertEqual(store.preguntas, [pregunta])
        for i, doc in enumerate(resultado.documentos, 1):
            self.assertIn(f"[{i}] {doc.page_content}", resultado.prompt)
        self.assertIn("dilo explicitamente en vez de inventar", resultado.prompt)

    def test_construir_prompt_devuelve_tupla_oficial(self):
        prompt, citas = rag.construir_prompt("Puedo mover mi cita?", store=FakeStore())
        self.assertIsInstance(prompt, str)
        self.assertEqual(list(citas), [1, 2, 3])
        self.assertTrue(all(fuente.endswith(".md") for fuente in citas.values()))

    def test_dos_preguntas_cambian_contextos_y_fuente_principal(self):
        store = FakeStore()
        cambio = rag.construir_resultado(rag.PREGUNTA_CAMBIO, store=store)
        privacidad = rag.construir_resultado(rag.PREGUNTA_PRIVACIDAD, store=store)
        self.assertNotEqual(cambio.citas[1], privacidad.citas[1])
        self.assertNotEqual(cambio.prompt, privacidad.prompt)
        self.assertEqual(len(store.preguntas), 2)
        self.assertEqual(privacidad.citas[1], "05_privacidad.md")

    def test_k_dos_y_k_superior_al_corpus(self):
        store = FakeStore()
        dos = rag.construir_resultado("cambiar", k=2, store=store)
        diez = rag.construir_resultado("cambiar", k=10, store=store)
        self.assertEqual(len(dos.citas), 2)
        self.assertEqual(len(diez.citas), 3)  # k es máximo, no rellena.

    def test_rechaza_preguntas_y_k_invalidos(self):
        for pregunta, k in [("", 3), ("   ", 3), (None, 3),
                            ("válida", 0), ("válida", -1),
                            ("válida", 1.5), ("válida", True)]:
            with self.subTest(pregunta=pregunta, k=k):
                with self.assertRaises(ValueError):
                    rag.construir_resultado(pregunta, k=k, store=FakeStore())

    def test_sin_fragmentos_no_crea_prompt_engañoso(self):
        class StoreVacio(FakeStore):
            def as_retriever(self, search_kwargs):
                return type("R", (), {"invoke": lambda self, q: []})()
        with self.assertRaisesRegex(ValueError, "No se recuperaron"):
            rag.construir_resultado("consulta", store=StoreVacio())

    def test_rechaza_fuente_faltante_en_un_chunk(self):
        store = FakeStore()
        store.docs_cambio[0].metadata.clear()
        with self.assertRaisesRegex(ValueError, "metadata.fuente"):
            rag.construir_resultado("cambiar", store=store)

    def test_verifica_citas_validas_invalidas_y_ausentes(self):
        citas = {1: "03_reprogramacion.md", 2: "02_disponibilidad.md"}
        with redirect_stdout(StringIO()) as salida:
            self.assertTrue(rag.mostrar_citas_respuesta("Debe consultar [1].", citas))
            self.assertFalse(rag.mostrar_citas_respuesta("Confirma [99].", citas))
            self.assertFalse(rag.mostrar_citas_respuesta("No hay evidencia.", citas))
        self.assertIn("Cita [99] -> Cita invalida", salida.getvalue())
        self.assertIn("Sin citas numeradas", salida.getvalue())

    def test_indice_ausente_es_bloqueado_antes_de_crear_chroma(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "no_existe"
            with self.assertRaises(FileNotFoundError):
                rag.comprobar_fuentes(ruta)
            self.assertFalse(ruta.exists())

    def test_mostrar_resultado_incluye_numeros_y_evidencia(self):
        resultado = rag.construir_resultado("cambiar", store=FakeStore())
        out = StringIO()
        with redirect_stdout(out):
            rag.mostrar_resultado(resultado)
        texto = out.getvalue()
        self.assertIn("Mapa de citas:", texto)
        self.assertIn("[1] 03_reprogramacion.md", texto)
        self.assertIn("ADVERTENCIA: son documentos ficticios", texto)

    def test_reutiliza_api_sin_modelo_real_en_tests(self):
        # El cuerpo del método contiene una sola invocación inyectable.
        # No llamamos respuesta_llm aquí ni a la API de Gemini.
        fake = FakeStore()
        with patch.object(rag, "abrir_vectorstore", return_value=fake) as abrir:
            res = rag.construir_resultado("cambiar", k=3)
            abrir.assert_called_once()
        self.assertEqual(res.citas[1], "03_reprogramacion.md")


if __name__ == "__main__":
    unittest.main()
