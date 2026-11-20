"""B26/L2: pruebas offline de fuentes y citas con el corpus Skillnest."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import unittest

from langchain_core.documents import Document
import citas_demo as demo


@unittest.skipUnless(
    importlib.util.find_spec("langchain_text_splitters") is not None,
    "B26/L2 requiere langchain-text-splitters; ejecutar suite completa en job RAG",
)
class TestCitasDemoB26(unittest.TestCase):

    def test_dos_documentos_y_dos_metadatas_oficiales(self):
        self.assertEqual(len(demo.CORPUS), 2)
        self.assertEqual(demo.METADATAS, [
            {"fuente": "manual_cliente.md"},
            {"fuente": "manual_costos.md"},
        ])
        self.assertEqual((demo.CHUNK_SIZE, demo.CHUNK_OVERLAP), (90, 10))

    def test_cuatro_chunks_y_herencia_de_fuente(self):
        chunks = demo.crear_chunks()
        self.assertEqual(len(chunks), 4)
        self.assertEqual(
            [c.metadata["fuente"] for c in chunks],
            ["manual_cliente.md", "manual_cliente.md",
             "manual_costos.md", "manual_costos.md"],
        )
        self.assertTrue(chunks[0].page_content.startswith("El cliente reintenta"))
        self.assertTrue(chunks[1].page_content.startswith("errores de autenticacion"))
        self.assertTrue(chunks[2].page_content.startswith("El costo de cada llamada"))
        self.assertEqual(chunks[3].page_content, "por cada 1000 tokens.")

    def test_contexto_numerado_y_mapa_exactos(self):
        chunks = demo.crear_chunks()
        contexto, citas = demo.formatear_contexto(chunks)
        self.assertEqual(citas, {
            1: "manual_cliente.md", 2: "manual_cliente.md",
            3: "manual_costos.md", 4: "manual_costos.md",
        })
        secciones = contexto.split("\n\n")
        self.assertEqual(len(secciones), 4)
        for i, parte in enumerate(secciones, 1):
            self.assertEqual(parte, f"[{i}] {chunks[i-1].page_content}")

    def test_numeros_son_locales_al_contexto(self):
        chunks = demo.crear_chunks()
        contexto, citas = demo.formatear_contexto([chunks[2], chunks[0]])
        self.assertEqual(citas, {1: "manual_costos.md", 2: "manual_cliente.md"})
        self.assertTrue(contexto.startswith("[1] " + chunks[2].page_content))

    def test_fuente_desconocida_si_falta_metadata(self):
        contexto, citas = demo.formatear_contexto([
            Document(page_content="Prueba sin metadata", metadata={})
        ])
        self.assertEqual(contexto, "[1] Prueba sin metadata")
        self.assertEqual(citas, {1: "desconocida"})

    def test_prompt_exige_citar_y_abstenerse(self):
        contexto, citas = demo.formatear_contexto(demo.crear_chunks())
        prompt = demo.construir_prompt(contexto, demo.PREGUNTA_DEMO)
        self.assertIn("Responde la pregunta usando SOLO el contexto", prompt)
        self.assertIn("como [1]", prompt)
        self.assertIn("dilo explicitamente en vez de inventar", prompt)
        self.assertIn("manual_cliente", str(citas))
        self.assertIn("Pregunta: Que hace el cliente si hay un TimeoutError?", prompt)
        self.assertIn(contexto, prompt)
        with self.assertRaises(ValueError):
            demo.construir_prompt(contexto, "  ")

    def test_cita_valida_reconstruye_fuente(self):
        _, citas = demo.formatear_contexto(demo.crear_chunks())
        self.assertEqual(demo.mapear_citas(demo.RESPUESTA_DEMO, citas),
                         [(1, "manual_cliente.md")])

    def test_cita_inventada_99_no_lanza_error(self):
        _, citas = demo.formatear_contexto(demo.crear_chunks())
        self.assertEqual(
            demo.mapear_citas(demo.RESPUESTA_CITAS_MULTIPLES, citas),
            [(1, "manual_cliente.md"), (2, "manual_cliente.md"),
             (3, "manual_costos.md"), (99, demo.CITA_INVALIDA)],
        )

    def test_citas_agrupadas_reales_1_3_y_falsas(self):
        """Regresión B26/L3: Gemini escribió [1, 3], antes omitíamos ambos."""
        _, citas = demo.formatear_contexto(demo.crear_chunks())
        respuesta = (
            "El modelo reconoce falta de precios [1, 3] y no inventa [1]. "
            "Prueba una referencia inexistente [2, 99]."
        )
        self.assertEqual(
            demo.mapear_citas(respuesta, citas),
            [
                (1, "manual_cliente.md"),
                (3, "manual_costos.md"),
                (1, "manual_cliente.md"),
                (2, "manual_cliente.md"),
                (99, demo.CITA_INVALIDA),
            ],
        )

    def test_citas_combinadas_espacios_orden_y_sin_inventar_numeros(self):
        citas = {1: "uno.md", 3: "tres.md"}
        respuesta = "Texto [ 3 , 1 ] / [3] / [x, 2] / [1; 3] / [abc]."
        self.assertEqual(
            demo.mapear_citas(respuesta, citas),
            [(3, "tres.md"), (1, "uno.md"), (3, "tres.md")],
        )

    def test_rechaza_metadatas_incompletas_antes_splitter(self):
        with self.assertRaisesRegex(ValueError, "metadata"):
            demo.crear_chunks(demo.CORPUS, [{"fuente": "solo_uno.md"}])

    def test_sin_citas_y_contexto_vacio(self):
        self.assertEqual(demo.mapear_citas("Respuesta sin referencias", {}), [])
        self.assertEqual(demo.formatear_contexto([]), ("", {}))

    def test_cli_offline_no_necesita_clave_ni_vectorstore(self):
        env = os.environ.copy()
        env.pop("GEMINI_API_KEY", None)
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        resultado = subprocess.run(
            [sys.executable, "citas_demo.py"],
            cwd=str(Path(demo.__file__).resolve().parent),
            env=env, text=True, capture_output=True, encoding="utf-8",
            errors="replace", check=False, timeout=30,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("manual_cliente.md", resultado.stdout)
        self.assertIn("{1: 'manual_cliente.md', 2: 'manual_cliente.md'", resultado.stdout)
        self.assertIn("Cita [99]: Cita invalida / no encontrada", resultado.stdout)
        self.assertIn("sin Gemini, Chroma ni solicitud de API", resultado.stdout)


if __name__ == "__main__":
    unittest.main()
