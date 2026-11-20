"""Pruebas offline U2.6/B30 Core — decisión documental Booking Core AI."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import decision
from comparar_estrategias import recomendar_estrategia as metodo_b30_l2


class DecisionCoreB30Tests(unittest.TestCase):
    def test_cinco_respuestas_booleanas_validas(self) -> None:
        self.assertEqual(len(decision.RESPUESTAS_MI_CASO), 5)
        self.assertTrue(all(type(x) is bool for x in decision.RESPUESTAS_MI_CASO.values()))

    def test_puntuacion_core_reproducible(self) -> None:
        puntos, candidatas = decision.recomendar_estrategia(decision.RESPUESTAS_MI_CASO)
        self.assertEqual(puntos, {"RAG": 2, "Fine-tuning completo": 0, "PEFT": 1})
        self.assertEqual(candidatas, ["RAG"])

    def test_reutiliza_exactamente_metodo_del_bloque_anterior(self) -> None:
        esperado = metodo_b30_l2(decision.RESPUESTAS_MI_CASO)
        observado = decision.recomendar_estrategia(decision.RESPUESTAS_MI_CASO)
        self.assertEqual(observado, esperado)

    def test_fuentes_y_ausencia_de_metrica_no_se_confunden(self) -> None:
        evidencia = "\n".join(descripcion for _, descripcion in decision.EVIDENCIAS)
        self.assertIn("13/11/2026", evidencia)
        self.assertIn("20 respuestas reales", evidencia)
        self.assertIn("NO salidas observadas", evidencia)
        self.assertIn("200", evidencia)

    def test_cinco_evidencias_una_por_clave(self) -> None:
        self.assertEqual(len(decision.EVIDENCIAS), 5)
        claves = [titulo.split(" = ")[0] for titulo, _ in decision.EVIDENCIAS]
        self.assertEqual(set(claves), set(decision.RESPUESTAS_MI_CASO))

    def test_prohibido_inventar_promedio_fallos_del_clasificador(self) -> None:
        documento = decision.generar_documento()
        self.assertIn("umbral sin demostrar", documento)
        self.assertNotIn("0 de 20 respuestas fallaron", documento)

    def test_sensibilidad_al_invertir_una_respuesta(self) -> None:
        variante = dict(decision.RESPUESTAS_MI_CASO)
        variante["presupuesto_limitado_o_iterar_rapido"] = False
        puntos, candidatas = decision.recomendar_estrategia(variante)
        self.assertEqual(puntos, {"RAG": 0, "Fine-tuning completo": 0, "PEFT": 0})
        self.assertEqual(candidatas, ["RAG", "Fine-tuning completo", "PEFT"])

    def test_no_muta_respuestas_al_recalcular(self) -> None:
        antes = dict(decision.RESPUESTAS_MI_CASO)
        decision.generar_documento()
        self.assertEqual(antes, decision.RESPUESTAS_MI_CASO)

    def test_esqueleto_contiene_cuatro_secciones(self) -> None:
        puntos, candidatas = decision.recomendar_estrategia(decision.RESPUESTAS_MI_CASO)
        doc = decision.generar_esqueleto_decision(decision.PROBLEMA, puntos, candidatas)
        self.assertEqual(doc.count("## "), 4)
        self.assertIn("[COMPLETAR_FUNDAMENTO]", doc)
        self.assertIn("[COMPLETAR_PLAN]", doc)

    def test_empate_aparece_explicitamente_en_esqueleto(self) -> None:
        puntos, candidatas = decision.recomendar_estrategia(
            dict.fromkeys(decision.RESPUESTAS_MI_CASO, False)
        )
        doc = decision.generar_esqueleto_decision(decision.PROBLEMA, puntos, candidatas)
        self.assertIn("Empate explícito", doc)
        self.assertIn("RAG, Fine-tuning completo, PEFT", doc)

    def test_documento_final_sin_marcadores(self) -> None:
        doc = decision.generar_documento()
        self.assertNotIn("[COMPLETAR", doc)
        self.assertNotIn("[SENSIBILIDAD]", doc)
        self.assertEqual(doc.count("## "), 4)

    def test_secciones_en_orden_correcto(self) -> None:
        doc = decision.generar_documento()
        headers = [
            "## 1. El problema",
            "## 2. Resultado del método de decisión",
            "## 3. Técnica elegida y por qué",
            "## 4. Qué necesitarías para ejecutarla",
        ]
        self.assertEqual([doc.find(h) for h in headers], sorted(doc.find(h) for h in headers))
        self.assertTrue(all(h in doc for h in headers))

    def test_hay_cifras_de_planificacion(self) -> None:
        doc = decision.generar_documento()
        for dato in ("5 de 5", "10 chunks", "faltan 0", "12 preguntas", "180", "0,306"):
            with self.subTest(dato=dato):
                self.assertIn(dato, doc)

    def test_no_presenta_la_heuristica_como_validacion_real(self) -> None:
        doc = decision.generar_documento()
        self.assertIn("SLA de producción", doc)
        self.assertIn("no resultados de producción", doc)
        self.assertIn("inventariar las fuentes oficiales", doc)

    def test_decision_recomienda_rag_solo_para_documentos(self) -> None:
        doc = decision.generar_documento()
        self.assertIn("RAG para el componente documental", doc)
        self.assertIn("API", doc)

    def test_version_generada_igual_a_entregable_versionado(self) -> None:
        path = Path(__file__).resolve().parents[1] / "decision_personalizacion.md"
        self.assertEqual(decision.generar_documento(), path.read_text(encoding="utf-8"))

    def test_main_genera_archivo_sin_api(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            salida = Path(temporal) / "decision_personalizacion.md"
            with patch.object(decision, "DESTINO", salida):
                with contextlib.redirect_stdout(io.StringIO()) as stdout:
                    decision.main()
            self.assertTrue(salida.is_file())
            self.assertEqual(salida.read_text(encoding="utf-8"), decision.generar_documento())
            self.assertIn("SIN API", stdout.getvalue())

    def test_booleans_en_texto_no_son_validos(self) -> None:
        variantes = dict(decision.RESPUESTAS_MI_CASO)
        variantes["informacion_cambia_seguido"] = "False"
        with self.assertRaises(TypeError):
            decision.recomendar_estrategia(variantes)


if __name__ == "__main__":
    unittest.main()
