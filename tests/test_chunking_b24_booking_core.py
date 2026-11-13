"""U2.5/B24/L2 — pruebas offline de chunking fijo y recursivo."""

import subprocess
import sys
import unittest
from pathlib import Path

from langchain_core.documents import Document

from src.comparar_chunking_b24_booking_core import (
    dividir_documentos,
    resumir_fragmentos,
)
from src.rag_b24_booking_core import crear_documentos_demo


RAIZ = Path(__file__).resolve().parents[1]


class TestChunkingBloque24(unittest.TestCase):
    def test_ejemplo_oficial_reproducible(self):
        """Ejecuta el script CONTINUO de Skillnest, sin llamadas externas."""
        resultado = subprocess.run(
            [sys.executable, "test_chunking.py"],
            cwd=str(RAIZ),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            check=False,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr[-2000:])
        self.assertIn(
            "Fijo: 3 chunks; longitudes: [110, 110, 93]",
            resultado.stdout,
        )
        self.assertIn(
            "Recursivo: 3 chunks; longitudes: [102, 108, 99]",
            resultado.stdout,
        )
        self.assertIn("Los er", resultado.stdout)
        self.assertIn("rores de autenticacion", resultado.stdout)

    def test_corpus_ficticio_mantiene_secciones(self):
        originales = crear_documentos_demo()
        self.assertEqual(len(originales), 5)
        for estrategia in ("fijo", "recursivo"):
            partes = dividir_documentos(originales, estrategia)
            self.assertGreater(len(partes), len(originales))
            self.assertEqual(
                set(d.metadata["seccion"] for d in partes),
                set(d.metadata["seccion"] for d in originales),
            )
            self.assertTrue(
                all(d.metadata["origen"] == "FICTICIO_ACADEMICO" for d in partes)
            )
            self.assertTrue(
                all(d.metadata["fuente"] == originales[0].metadata["fuente"] for d in partes)
            )
            self.assertTrue(
                all(d.metadata["estrategia"] == estrategia for d in partes)
            )
            self.assertTrue(
                all(len(d.page_content) <= 110 for d in partes)
            )

    def test_indices_se_reinician_por_seccion(self):
        partes = dividir_documentos(crear_documentos_demo(), "recursivo")
        for seccion, cantidad in resumir_fragmentos(partes).items():
            indices = [
                d.metadata["indice_chunk"]
                for d in partes
                if d.metadata["seccion"] == seccion
            ]
            self.assertEqual(indices, list(range(cantidad)))

    def test_fijo_corta_palabra(self):
        doc = Document(
            page_content="Los errores de autenticacion",
            metadata={"fuente": "prueba.md", "seccion": "Demo", "origen": "FICTICIO_ACADEMICO"},
        )
        partes = dividir_documentos([doc], "fijo", chunk_size=6, chunk_overlap=0)
        self.assertEqual(partes[0].page_content, "Los er")
        self.assertEqual(partes[1].page_content, "rores ")

    def test_recursivo_prioriza_parrafos_cortos(self):
        doc = Document(
            page_content="Uno.\n\nDos.\n\nTres.",
            metadata={"fuente": "prueba.md", "seccion": "Demo", "origen": "FICTICIO_ACADEMICO"},
        )
        partes = dividir_documentos([doc], "recursivo", chunk_size=8, chunk_overlap=2)
        self.assertEqual([d.page_content for d in partes], ["Uno.", "Dos.", "Tres."])

    def test_validaciones_parametros(self):
        documentos = crear_documentos_demo()
        for estrategia, tam, overlap in [
            ("fijo", 0, 0),
            ("recursivo", 110, 110),
            ("recursivo", 110, -1),
            ("desconocida", 110, 20),
        ]:
            with self.subTest(estrategia=estrategia, tam=tam, overlap=overlap):
                with self.assertRaises(ValueError):
                    dividir_documentos(documentos, estrategia, tam, overlap)

    def test_no_modifica_documentos_originales(self):
        documentos = crear_documentos_demo()
        copia = [(d.page_content, dict(d.metadata)) for d in documentos]
        dividir_documentos(documentos, "fijo")
        dividir_documentos(documentos, "recursivo")
        self.assertEqual(
            [(d.page_content, d.metadata) for d in documentos],
            copia,
        )


if __name__ == "__main__":
    unittest.main()
