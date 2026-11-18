"""B27/L3: etiquetas humanas congeladas y evaluación real inyectable (OFFLINE).

No se usan credenciales, embeddings Gemini ni índice productivo en CI.
"""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
from types import SimpleNamespace
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import evaluacion_recuperacion as a


class RecuperadorFalso:
    def __init__(self, casos, conocidos, k: int):
        self.k = k
        self.preguntas = []
        self.relevantes = {c["pregunta"]: c["ids_relevantes"] for c in casos}
        self.conocidos = sorted(conocidos)

    def invoke(self, pregunta):
        self.preguntas.append(pregunta)
        relevantes = sorted(self.relevantes[pregunta])
        resto = [i for i in self.conocidos if i not in relevantes]
        elegidos = (relevantes + resto)[: self.k]
        return [SimpleNamespace(id=i) for i in elegidos]


class StoreFalso:
    def __init__(self, casos, conocidos):
        self.casos = casos
        self.conocidos = conocidos
        self.retrievers = []

    def as_retriever(self, search_kwargs):
        fake = RecuperadorFalso(
            self.casos, self.conocidos, search_kwargs["k"]
        )
        self.retrievers.append(fake)
        return fake


class TestEvaluacionRecuperacionB27L3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config, cls.casos = a.cargar_etiquetas()
        cls.ids = {a.id_estable(f, o) for f in a.FUENTES for o in (0, 1)}

    def test_ids_sha256_coinciden_con_el_algoritmo_b24_l3(self):
        self.assertEqual(
            a.id_estable("01_servicios.md", 0),
            "11961cd9d91b41dc59dfab4888d5ddd1d1f66b0dbcff37e8d8dbfb9fbd6c6688",
        )
        self.assertEqual(
            a.id_estable("05_privacidad.md", 1),
            "211a65372bec79df5eebac3391ee84d5b1e50d43186209760a4c34e1f25f9dd7",
        )
        self.assertEqual(len(self.ids), 10)

    def test_etiquetas_son_12_con_10_positivos_y_dos_sin_respuesta(self):
        self.assertEqual(len(self.casos), 12)
        self.assertEqual(sum(bool(c["ids_relevantes"]) for c in self.casos), 10)
        self.assertEqual(sum(not c["ids_relevantes"] for c in self.casos), 2)
        self.assertEqual(self.config["estado"], "ETIQUETAS_FIJADAS_PREVIAS_A_RETRIEVAL")
        self.assertEqual(self.config["coleccion"], a.COLECCION)
        self.assertEqual((self.config["chunk_size"], self.config["chunk_overlap"]),
                         (550, 80))

    def test_cinco_temas_y_chunks_ordinales_sin_ids_ajenos(self):
        cubiertos = set().union(*(c["ids_relevantes"] for c in self.casos))
        self.assertEqual(cubiertos, self.ids)
        self.assertTrue(all(c["ids_relevantes"] <= self.ids for c in self.casos))

    def test_una_pregunta_tiene_dos_chunks_relevantes(self):
        c = next(c for c in self.casos if c["id"] == "SERV-02")
        self.assertEqual(
            c["ids_relevantes"],
            {a.id_estable("01_servicios.md", 0),
             a.id_estable("01_servicios.md", 1)},
        )

    def test_casos_sin_relevantes_corresponden_a_precio_y_telefono_actuales(self):
        preguntas = [c["pregunta"] for c in self.casos if not c["ids_relevantes"]]
        self.assertEqual(len(preguntas), 2)
        self.assertIn("precio vigente hoy", preguntas[0])
        self.assertIn("número de teléfono", preguntas[1])

    def test_no_permite_corregir_etiquetas_usando_ids_desconocidos(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads(a.RUTA_ETIQUETAS.read_text(encoding="utf-8"))
            data["casos"][0]["ids_relevantes"] = ["doc0"]
            ruta = Path(tmp) / "labels.json"
            ruta.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ID etiquetado inexistente"):
                a.cargar_etiquetas(ruta)

    def test_rechaza_numero_de_preguntas_menor_que_ocho(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads(a.RUTA_ETIQUETAS.read_text(encoding="utf-8"))
            data["casos"] = data["casos"][:7]
            ruta = Path(tmp) / "labels.json"
            ruta.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "entre 8 y 15"):
                a.cargar_etiquetas(ruta)

    def test_retriever_falso_calcula_precision_y_recall_sin_api(self):
        fake = RecuperadorFalso(self.casos, self.ids, k=3)
        resultados, p, r = a.evaluar_una_pasada(fake, self.casos, 3, self.ids)
        self.assertEqual(len(resultados), 12)
        self.assertEqual(len(fake.preguntas), 12)
        self.assertTrue(0 <= p <= 1 and 0 <= r <= 1)
        self.assertEqual(resultados[0]["recall"], 1)
        self.assertIsNone(resultados[-1]["recall"])

    def test_recall_none_para_dos_casos_sin_respuesta(self):
        fake = RecuperadorFalso(self.casos, self.ids, k=5)
        resultados, _, promedio = a.evaluar_una_pasada(
            fake, self.casos, 5, self.ids
        )
        self.assertIsNone(resultados[-1]["recall"])
        self.assertIsNone(resultados[-2]["recall"])
        self.assertEqual(promedio, 1.0)

    def test_duplicado_de_document_id_rechazado(self):
        bad = SimpleNamespace(
            invoke=lambda p: [SimpleNamespace(id=next(iter(self.ids)))] * 3
        )
        with self.assertRaisesRegex(ValueError, "duplicado"):
            a.evaluar_una_pasada(bad, self.casos[:1], 3, self.ids)

    def test_document_id_ausente_o_inventado_se_rechaza(self):
        for bad_ids in [[None, "x", "y"], ["doc0", "doc1", "doc2"]]:
            with self.subTest(ids=bad_ids):
                bad = SimpleNamespace(
                    invoke=lambda p: [SimpleNamespace(id=i) for i in bad_ids]
                )
                with self.assertRaisesRegex(ValueError, "inválido"):
                    a.evaluar_una_pasada(bad, self.casos[:1], 3, self.ids)

    def test_k_3_versus_k_5_aplica_top_k_reales(self):
        tres = RecuperadorFalso(self.casos, self.ids, 3)
        cinco = RecuperadorFalso(self.casos, self.ids, 5)
        a3, _, r3 = a.evaluar_una_pasada(tres, self.casos, 3, self.ids)
        a5, _, r5 = a.evaluar_una_pasada(cinco, self.casos, 5, self.ids)
        self.assertEqual(len(a3[0]["ids_recuperados"]), 3)
        self.assertEqual(len(a5[0]["ids_recuperados"]), 5)
        self.assertGreaterEqual(r5, r3)
        self.assertTrue(all(
            len(row["ids_recuperados"]) == 5 for row in a5
        ))

    def test_repetibilidad_compara_ids_y_no_solo_promedios(self):
        fake1 = RecuperadorFalso(self.casos, self.ids, 3)
        fake2 = RecuperadorFalso(self.casos, self.ids, 3)
        a1 = a.evaluar_una_pasada(fake1, self.casos, 3, self.ids)
        a2 = a.evaluar_una_pasada(fake2, self.casos, 3, self.ids)
        self.assertTrue(a.verificar_repetibilidad(a1, a2))
        # Mismos promedios aunque cambia el orden del primer caso.
        a2[0][0]["ids_recuperados"].reverse()
        self.assertFalse(a.verificar_repetibilidad(a1, a2))

    def test_informe_tiene_formato_skillnest_fecha_chunking_k_promedios(self):
        fake = RecuperadorFalso(self.casos, self.ids, 3)
        v = a.evaluar_una_pasada(fake, self.casos, 3, self.ids)
        txt = a.formatear_informe(
            self.config, v, v, 3, "huella-de-ejemplo", "2026-11-18"
        )
        self.assertIn("Fecha: 2026-11-18", txt)
        self.assertIn("Configuracion: k=3, chunk_size=550, chunk_overlap=80", txt)
        self.assertIn("Corrida 1:", txt)
        self.assertIn("Corrida 2:", txt)
        self.assertIn("Repetibilidad de secuencias de IDs y métricas: PASS", txt)
        self.assertIn("recall: ", txt)
        self.assertIn("n/a", txt)

    def test_archivo_nunca_sobrescribe_resultados_anteriores(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "resultados_evaluacion.txt"
            p1 = a.guardar_sin_sobrescribir("primera\n", dest)
            p2 = a.guardar_sin_sobrescribir("segunda\n", dest)
            self.assertEqual(p1, dest)
            self.assertNotEqual(p2, dest)
            self.assertEqual(p1.read_text(encoding="utf-8"), "primera\n")
            self.assertEqual(p2.read_text(encoding="utf-8"), "segunda\n")

    def test_flujo_completo_mock_no_genera_consultas_externas(self):
        inventario = {
            "estado": {"huella": "h-ficticia"},
            "chunks": [{"id": i} for i in sorted(self.ids)],
        }
        fake = StoreFalso(self.casos, self.ids)
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(StringIO()):
            ruta, res = a.ejecutar_evaluacion(
                3, store=fake, inventario=inventario,
                salida=Path(tmp) / "resultados_evaluacion.txt",
            )
            self.assertTrue(ruta.exists())
        self.assertEqual(len(fake.retrievers), 1)
        self.assertEqual(len(fake.retrievers[0].preguntas), 24)
        self.assertEqual(len(res[0]), 12)

    def test_modo_etiquetas_cli_sin_claves_ni_indice(self):
        env = os.environ.copy()
        env.pop("GEMINI_API_KEY", None)
        env.pop("GOOGLE_API_KEY", None)
        env["PYTHONUTF8"] = "1"
        p = subprocess.run(
            [sys.executable, "evaluacion_recuperacion.py", "--modo", "etiquetas"],
            cwd=a.RAIZ, env=env, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=15, check=False,
        )
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("sin API: 12", p.stdout)
        self.assertIn("Positivos: 10", p.stdout)
        self.assertIn("Sin respuesta factual: 2", p.stdout)
        # La CI debe seguir verde incluso DESPUÉS de publicar la primera corrida
        # real en resultados_evaluacion.txt; solo se verifica el modo sin API.
        self.assertIn("SERV-01", p.stdout)

    def test_sin_llamadas_reales_ni_escrituras_al_vectorstore_en_tests(self):
        # Pasar modo etiquetas no abre Chroma, no instancia embeddings.
        with patch("evaluacion_recuperacion.preflight_indice") as preflight:
            with patch("evaluacion_recuperacion.ejecutar_evaluacion") as evaluar:
                with patch("sys.argv", ["evaluacion_recuperacion.py", "--modo", "etiquetas"]):
                    with redirect_stdout(StringIO()):
                        self.assertEqual(a.main(), 0)
                preflight.assert_not_called()
                evaluar.assert_not_called()


if __name__ == "__main__":
    unittest.main()
