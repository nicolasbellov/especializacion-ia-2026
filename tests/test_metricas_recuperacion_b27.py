"""U2.5/B27/L1: sin red y sin bibliotecas externas, verificar métricas oficiales."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest

import metricas_recuperacion as m

RAIZ = Path(__file__).resolve().parents[1]


class TestMetricasRecuperacionB27(unittest.TestCase):
    def test_corpus_e_ids_fieles_a_skillnest(self):
        self.assertEqual(list(m.CORPUS), ["doc0", "doc1", "doc2", "doc3", "doc4"])
        self.assertIn("TimeoutError", m.CORPUS["doc0"])
        self.assertIn("totalTokenCount", m.CORPUS["doc2"])
        self.assertEqual(m.IDS_RELEVANTES, {"doc0"})
        self.assertEqual(m.IDS_RECUPERADOS, ["doc2", "doc0", "doc4"])
        self.assertEqual(m.RANKED, ["doc2", "doc4", "doc0", "doc1", "doc3"])

    def test_ejemplo_oficial_precision_recall_top3(self):
        self.assertAlmostEqual(
            m.precision_at_k(m.IDS_RECUPERADOS, m.IDS_RELEVANTES), 1 / 3
        )
        self.assertEqual(m.recall_at_k(m.IDS_RECUPERADOS, m.IDS_RELEVANTES), 1)

    def test_tabla_oficial_precisiones(self):
        filas = m.evaluar_ranking(m.RANKED, m.IDS_RELEVANTES)
        self.assertEqual(
            [round(f["precision"], 6) for f in filas],
            [0, 0, round(1 / 3, 6), 0.25, 0.2],
        )
        self.assertEqual([f["k"] for f in filas], [1, 2, 3, 4, 5])
        self.assertEqual([f["ids"] for f in filas], [
            ["doc2"], ["doc2", "doc4"],
            ["doc2", "doc4", "doc0"],
            ["doc2", "doc4", "doc0", "doc1"],
            ["doc2", "doc4", "doc0", "doc1", "doc3"],
        ])

    def test_tabla_oficial_recall(self):
        filas = m.evaluar_ranking(m.RANKED, m.IDS_RELEVANTES)
        self.assertEqual([f["recall"] for f in filas], [0, 0, 1, 1, 1])

    def test_tabla_oficial_f1(self):
        filas = m.evaluar_ranking(m.RANKED, m.IDS_RELEVANTES)
        self.assertEqual(
            [round(f["f1"], 3) for f in filas],
            [0, 0, 0.5, 0.4, 0.333],
        )

    def test_mejor_f1_ocurre_en_k3(self):
        filas = m.evaluar_ranking(m.RANKED, m.IDS_RELEVANTES)
        mejor = max(filas, key=lambda x: x["f1"])
        self.assertEqual(mejor["k"], 3)
        self.assertEqual(mejor["f1"], 0.5)

    def test_f1_cero_y_media_armonica(self):
        self.assertEqual(m.f1(0, 0), 0)
        self.assertEqual(m.f1(0, 1), 0)
        self.assertEqual(m.f1(1, 1), 1)
        self.assertEqual(m.f1(1 / 3, 1), 0.5)

    def test_prec_recall_independientes_del_orden_dentro_top_k(self):
        # Fuente: el curso distingue IDS_RECUPERADOS y ranked[:3].
        a = ["doc2", "doc0", "doc4"]
        b = ["doc2", "doc4", "doc0"]
        self.assertEqual(
            m.precision_at_k(a, {"doc0"}), m.precision_at_k(b, {"doc0"})
        )
        self.assertEqual(
            m.recall_at_k(a, {"doc0"}), m.recall_at_k(b, {"doc0"})
        )

    def test_varios_relevantes_y_top_k_incompleto(self):
        recuperados = ["doc0", "doc1", "doc3"]
        relevantes = {"doc0", "doc3", "doc4"}
        self.assertAlmostEqual(m.precision_at_k(recuperados, relevantes), 2 / 3)
        self.assertAlmostEqual(m.recall_at_k(recuperados, relevantes), 2 / 3)
        self.assertAlmostEqual(m.f1(2 / 3, 2 / 3), 2 / 3)

    def test_sin_aciertos_con_resultados_no_vacios(self):
        self.assertEqual(m.precision_at_k(["doc2"], {"doc0"}), 0)
        self.assertEqual(m.recall_at_k(["doc2"], {"doc0"}), 0)

    def test_casos_sin_denominador_rechazados_explicitamente(self):
        with self.assertRaisesRegex(ValueError, "recuperados vacío"):
            m.precision_at_k([], {"doc0"})
        with self.assertRaisesRegex(ValueError, "relevantes vacío"):
            m.recall_at_k(["doc0"], set())
        with self.assertRaisesRegex(ValueError, "relevantes vacío"):
            m.evaluar_ranking(["doc0"], set())
        with self.assertRaisesRegex(ValueError, "Ranking vacío"):
            m.evaluar_ranking([], {"doc0"})

    def test_ids_duplicados_rechazados(self):
        with self.assertRaisesRegex(ValueError, "recuperados duplicados"):
            m.precision_at_k(["doc0", "doc0"], {"doc0"})
        with self.assertRaisesRegex(ValueError, "relevantes duplicados"):
            m.recall_at_k(["doc0"], ["doc0", "doc0"])

    def test_ids_y_k_invalidos_rechazados(self):
        with self.assertRaises(ValueError):
            m.precision_at_k(["doc0", None], {"doc0"})
        with self.assertRaises(ValueError):
            m.recall_at_k(["doc0"], {""})
        with self.assertRaises(ValueError):
            m.evaluar_ranking(m.RANKED, m.IDS_RELEVANTES, 0)
        with self.assertRaises(ValueError):
            m.evaluar_ranking(m.RANKED, m.IDS_RELEVANTES, 6)
        with self.assertRaises(ValueError):
            m.evaluar_ranking(m.RANKED, m.IDS_RELEVANTES, True)

    def test_limite_k_parcial_sin_reordenamiento(self):
        filas = m.evaluar_ranking(m.RANKED, {"doc0"}, max_k=3)
        self.assertEqual(len(filas), 3)
        self.assertEqual(filas[2]["ids"], ["doc2", "doc4", "doc0"])

    def test_cli_reproduce_numeros_sin_clave_api(self):
        env = os.environ.copy()
        env.pop("GEMINI_API_KEY", None)
        env.pop("GOOGLE_API_KEY", None)
        env["PYTHONUTF8"] = "1"
        result = subprocess.run(
            [sys.executable, "metricas_recuperacion.py"],
            cwd=RAIZ, env=env, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=15, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("precision@3: 0.3333333333333333", result.stdout)
        self.assertIn("recall@3: 1.0", result.stdout)
        self.assertIn("k=3: F1=0.500", result.stdout)
        self.assertIn("k=5: F1=0.333", result.stdout)
        self.assertIn("Máximo F1 en este ejemplo: k=3, F1=0.500", result.stdout)
        self.assertIn("no son métricas del RAG Booking Core", result.stdout)


if __name__ == "__main__":
    unittest.main()
