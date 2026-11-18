"""B27/L2: validar conjunto de evaluación y promedios SIN red ni API."""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
import subprocess
import sys
import unittest

import evaluacion_rag as e


class RetrieverFalso:
    def __init__(self, resultados: dict[str, list[str]]):
        self.resultados = resultados
        self.consultas: list[str] = []

    def invoke(self, pregunta: str):
        self.consultas.append(pregunta)
        return [
            SimpleNamespace(id=identificador)
            for identificador in self.resultados[pregunta]
        ]


class TestEvaluacionRagB27(unittest.TestCase):

    def test_cuatro_preguntas_etiquetadas_exactamente_como_curso(self):
        self.assertEqual(len(e.casos_evaluacion), 4)
        self.assertEqual(
            [c["pregunta"] for c in e.casos_evaluacion],
            [
                "que hace el cliente si una llamada tarda demasiado",
                "que pasa si la clave de api es invalida",
                "como se calcula el costo de una llamada",
                "como decide el agente que herramienta usar",
            ],
        )
        self.assertEqual(
            [c["ids_relevantes"] for c in e.casos_evaluacion],
            [{"doc0"}, {"doc1"}, {"doc2"}, {"doc3"}],
        )

    def test_ranking_simulado_del_material_oficial(self):
        self.assertEqual(
            list(e.ids_recuperados_por_pregunta.values()),
            [
                ["doc0", "doc4", "doc2"],
                ["doc2", "doc4", "doc3"],
                ["doc2", "doc0", "doc4"],
                ["doc4", "doc3", "doc1"],
            ],
        )

    def test_precision_promedio_oficial_025(self):
        resultados, p_prom, _ = e.evaluar_recuperacion_simulada(e.casos_evaluacion)
        self.assertEqual([r["precision"] for r in resultados], [0.333, 0.0, 0.333, 0.333])
        self.assertEqual(p_prom, 0.25)

    def test_recall_promedio_oficial_075(self):
        resultados, _, r_prom = e.evaluar_recuperacion_simulada(e.casos_evaluacion)
        self.assertEqual([r["recall"] for r in resultados], [1.0, 0.0, 1.0, 1.0])
        self.assertEqual(r_prom, 0.75)

    def test_preguntas_truncadas_a_40_caracteres_como_curso(self):
        resultados, _, _ = e.evaluar_recuperacion_simulada(e.casos_evaluacion)
        self.assertEqual(resultados[0]["pregunta"], e.casos_evaluacion[0]["pregunta"][:40])
        self.assertEqual(resultados[3]["pregunta"], e.casos_evaluacion[3]["pregunta"][:40])
        self.assertLessEqual(max(len(x["pregunta"]) for x in resultados), 40)

    def test_segundo_caso_falla_pese_a_tres_documentos_recuperados(self):
        c = e.casos_evaluacion[1]
        recuperados = e.ids_recuperados_por_pregunta[c["pregunta"]]
        self.assertNotIn("doc1", recuperados)
        self.assertEqual(e.precision_at_k(recuperados, c["ids_relevantes"]), 0.0)
        self.assertEqual(e.recall_at_k(recuperados, c["ids_relevantes"]), 0.0)

    def test_precision_vacia_cero_recall_vacio_con_relevantes_cero(self):
        self.assertEqual(e.precision_at_k([], {"doc0"}), 0.0)
        self.assertEqual(e.recall_at_k([], {"doc0"}), 0.0)

    def test_recall_sin_relevantes_es_none(self):
        self.assertIsNone(e.recall_at_k(["doc0"], set()))
        self.assertIsNone(e.recall_at_k([], set()))
        self.assertEqual(e.precision_at_k(["doc0"], set()), 0.0)

    def test_promedio_ignora_none_y_maneja_todos_none(self):
        self.assertEqual(e.promediar([1.0, None, 0.0]), 0.5)
        self.assertEqual(e.promediar([None, None]), 0.0)
        self.assertEqual(e.promediar([]), 0.0)
        self.assertEqual(e.promediar(v for v in [0.5, None, 1.0]), 0.75)

    def test_multiple_relevantes_precision_y_recall(self):
        self.assertAlmostEqual(
            e.precision_at_k(["doc0", "doc2", "doc4"], {"doc0", "doc4"}),
            2 / 3,
        )
        self.assertEqual(
            e.recall_at_k(["doc0", "doc2", "doc4"], {"doc0", "doc4"}),
            1.0,
        )

    def test_k_modifica_recuperaciones_y_agregados(self):
        res, p, r = e.evaluar_recuperacion_simulada(e.casos_evaluacion, k=1)
        self.assertEqual([row["precision"] for row in res], [1.0, 0.0, 1.0, 0.0])
        self.assertEqual([row["recall"] for row in res], [1.0, 0.0, 1.0, 0.0])
        self.assertEqual((p, r), (0.5, 0.5))

    def test_evaluar_retriever_inyectado_usa_document_id(self):
        fake = RetrieverFalso(e.ids_recuperados_por_pregunta)
        resultados, p, r = e.evaluar_recuperacion(fake, e.casos_evaluacion)
        self.assertEqual(fake.consultas, [c["pregunta"] for c in e.casos_evaluacion])
        self.assertEqual(len(resultados), 4)
        self.assertAlmostEqual(p, 0.25)
        self.assertEqual(r, 0.75)
        self.assertEqual(resultados[0]["pregunta"], e.casos_evaluacion[0]["pregunta"])

    def test_evaluar_retriever_sin_documentos_calcula_ceros(self):
        fake = RetrieverFalso({"consulta": []})
        resultados, p, r = e.evaluar_recuperacion(
            fake, [{"pregunta": "consulta", "ids_relevantes": {"doc0"}}]
        )
        self.assertEqual(resultados[0]["precision"], 0)
        self.assertEqual(resultados[0]["recall"], 0)
        self.assertEqual((p, r), (0, 0))

    def test_caso_sin_relevantes_no_distorsiona_recall_medio(self):
        fake = RetrieverFalso({"a": ["doc0"], "fuera": ["doc2"]})
        resultados, p, r = e.evaluar_recuperacion(
            fake, [
                {"pregunta": "a", "ids_relevantes": {"doc0"}},
                {"pregunta": "fuera", "ids_relevantes": set()},
            ],
        )
        self.assertIsNone(resultados[1]["recall"])
        self.assertEqual(p, 0.5)
        self.assertEqual(r, 1.0)

    def test_retriever_sin_ids_explicitos_falla_en_lugar_de_falsos_ceros(self):
        fake = RetrieverFalso({"consulta": [None]})
        with self.assertRaisesRegex(ValueError, "Document.id explícito"):
            e.evaluar_recuperacion(
                fake, [{"pregunta": "consulta", "ids_relevantes": {"doc0"}}]
            )

    def test_retriever_con_ids_duplicados_falla(self):
        fake = RetrieverFalso({"consulta": ["doc0", "doc0"]})
        with self.assertRaisesRegex(ValueError, "duplicados"):
            e.evaluar_recuperacion(
                fake, [{"pregunta": "consulta", "ids_relevantes": {"doc0"}}]
            )

    def test_rechaza_k_y_formato_invalido_de_etiquetas(self):
        with self.assertRaisesRegex(ValueError, "entero positivo"):
            e.evaluar_recuperacion_simulada(e.casos_evaluacion, k=0)
        with self.assertRaisesRegex(ValueError, "entero positivo"):
            e.evaluar_recuperacion_simulada(e.casos_evaluacion, k=True)
        with self.assertRaisesRegex(ValueError, "ids_relevantes"):
            e.evaluar_recuperacion(
                RetrieverFalso({"pregunta": ["doc0"]}),
                [{"pregunta": "pregunta", "ids_relevantes": "doc0"}],
            )

    def test_cli_reproduce_cifras_oficiales_sin_credenciales(self):
        env = os.environ.copy()
        env.pop("GEMINI_API_KEY", None)
        env.pop("GOOGLE_API_KEY", None)
        env["PYTHONUTF8"] = "1"
        res = subprocess.run(
            [sys.executable, "evaluacion_rag.py"],
            cwd=Path(__file__).resolve().parents[1],
            env=env, text=True, capture_output=True,
            encoding="utf-8", errors="replace", check=False, timeout=20,
        )
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("Casos: 4", res.stdout)
        self.assertIn("'precision': 0.333, 'recall': 1.0", res.stdout)
        self.assertIn("'precision': 0.0, 'recall': 0.0", res.stdout)
        self.assertIn("precision promedio: 0.25", res.stdout)
        self.assertIn("recall promedio: 0.75", res.stdout)
        self.assertIn("\n0.0\nNone\n", res.stdout)
        self.assertIn("no evalúan el índice real de Booking Core AI", res.stdout)


if __name__ == "__main__":
    unittest.main()
