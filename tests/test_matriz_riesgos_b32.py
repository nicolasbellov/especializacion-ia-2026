"""B32/L2: pruebas sin red de la matriz oficial y la propuesta Booking Core AI."""

from copy import deepcopy
from contextlib import redirect_stdout
from io import StringIO
import unittest

from matriz_riesgos import (
    RIESGOS_CURSO,
    cargar_matriz_booking_core,
    categoria_riesgo,
    esta_en_el_limite,
    main,
    ordenar_y_evaluar,
    puntaje_riesgo,
    validar_matriz_booking_core,
)


class TestMatrizRiesgosB32(unittest.TestCase):
    def test_cinco_puntajes_oficiales_en_orden(self):
        filas = ordenar_y_evaluar(RIESGOS_CURSO)
        self.assertEqual([r["puntaje"] for r in filas], [16, 15, 9, 8, 6])

    def test_cinco_categorias_oficiales(self):
        filas = ordenar_y_evaluar(RIESGOS_CURSO)
        self.assertEqual(
            [r["categoria"] for r in filas],
            ["CRITICO", "CRITICO", "ALTO", "MEDIO", "MEDIO"],
        )

    def test_cinco_riesgos_oficiales_estan_al_limite(self):
        filas = ordenar_y_evaluar(RIESGOS_CURSO)
        self.assertTrue(all(r["al_limite"] for r in filas))

    def test_contraste_uno_por_uno_no_esta_al_limite(self):
        self.assertEqual(puntaje_riesgo(1, 1), 1)
        self.assertEqual(categoria_riesgo(1), "BAJO")
        self.assertFalse(esta_en_el_limite(1, 1))

    def test_categorias_en_cada_umbral(self):
        casos = {
            1: "BAJO", 3: "BAJO", 4: "MEDIO", 8: "MEDIO",
            9: "ALTO", 14: "ALTO", 15: "CRITICO", 25: "CRITICO",
        }
        for puntaje, categoria in casos.items():
            with self.subTest(puntaje=puntaje):
                self.assertEqual(categoria_riesgo(puntaje), categoria)

    def test_sensibilidad_no_sale_de_escala_1_a_5(self):
        self.assertFalse(esta_en_el_limite(5, 5))
        self.assertTrue(esta_en_el_limite(4, 4))
        self.assertTrue(esta_en_el_limite(3, 3))

    def test_entradas_invalidas_no_producen_puntajes_engañosos(self):
        for p, i in [(0, 2), (6, 2), ("4", 3), (True, 5), (2.5, 4)]:
            with self.subTest(p=p, i=i), self.assertRaises(ValueError):
                puntaje_riesgo(p, i)
        for puntaje in (0, 26, "15", True, 5.5):
            with self.subTest(puntaje=puntaje), self.assertRaises(ValueError):
                categoria_riesgo(puntaje)

    def test_evaluar_no_modifica_diccionarios_originales(self):
        original = deepcopy(RIESGOS_CURSO)
        ordenar_y_evaluar(RIESGOS_CURSO)
        self.assertEqual(RIESGOS_CURSO, original)

    def test_matriz_booking_core_contiene_seis_riesgos_priorizados(self):
        matriz = cargar_matriz_booking_core()
        filas = matriz["riesgos"]
        self.assertEqual(len(filas), 6)
        self.assertEqual(
            [r["id"] for r in filas],
            ["BC-01", "BC-02", "BC-03", "BC-04", "BC-06", "BC-05"],
        )
        self.assertEqual(
            [r["puntaje"] for r in filas],
            [20, 16, 15, 12, 8, 6],
        )

    def test_book_core_estimaciones_se_identifican_como_no_auditadas(self):
        matriz = cargar_matriz_booking_core()
        self.assertIn("NO mediciones", matriz["fuente"])
        self.assertIn("académico", matriz["fuente"].lower())
        self.assertEqual(matriz["fecha_revision"], "2026-11-26")

    def test_alto_critico_tienen_supervision_propuesta_no_productiva(self):
        for fila in cargar_matriz_booking_core()["riesgos"]:
            if fila["categoria"] in ("ALTO", "CRITICO"):
                self.assertTrue(fila["punto_supervision"])
                self.assertEqual(
                    fila["estado_supervision"], "PROPUESTO_NO_IMPLEMENTADO"
                )
            else:
                self.assertEqual(
                    fila["estado_supervision"], "NO_REQUERIDO_POR_UMBRAL"
                )

    def test_falla_si_alto_no_tiene_punto_supervision(self):
        filas = deepcopy(cargar_matriz_booking_core()["riesgos"])
        filas[0]["punto_supervision"] = None
        with self.assertRaisesRegex(ValueError, "requiere un punto"):
            validar_matriz_booking_core(filas)

    def test_falla_si_se_declara_implementacion_no_verificada(self):
        filas = deepcopy(cargar_matriz_booking_core()["riesgos"])
        filas[0]["estado_supervision"] = "IMPLEMENTADO_EN_PRODUCCION"
        with self.assertRaisesRegex(ValueError, "no puede declarar"):
            validar_matriz_booking_core(filas)

    def test_detecta_ids_duplicados_y_falta_de_mitigacion(self):
        filas = deepcopy(cargar_matriz_booking_core()["riesgos"])
        filas[1]["id"] = filas[0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicado"):
            validar_matriz_booking_core(filas)
        filas = deepcopy(cargar_matriz_booking_core()["riesgos"])
        filas[0]["mitigacion_pendiente"] = ""
        with self.assertRaisesRegex(ValueError, "mitigacion_pendiente"):
            validar_matriz_booking_core(filas)

    def test_compara_controles_existentes_con_pendientes(self):
        matriz = {r["id"]: r for r in cargar_matriz_booking_core()["riesgos"]}
        self.assertIn("B31/L2", matriz["BC-02"]["mitigacion_existente"])
        self.assertIn("detener", matriz["BC-02"]["mitigacion_pendiente"])
        self.assertIn("no se comunica", matriz["BC-04"]["mitigacion_existente"])
        self.assertIn("tenant", matriz["BC-04"]["mitigacion_pendiente"])

    def test_script_imprime_curso_sensibilidad_y_adaptacion_sin_api(self):
        salida = StringIO()
        with redirect_stdout(salida):
            self.assertEqual(main(), 0)
        texto = salida.getvalue()
        self.assertIn("EJEMPLO OFICIAL SKILLNEST", texto)
        self.assertIn("CRITICO  (16)", texto)
        self.assertIn("no al limite", texto)
        self.assertIn("BOOKING CORE AI: PROPUESTA", texto)
        self.assertIn("BC-01: supervision PROPUESTO_NO_IMPLEMENTADO", texto)
        self.assertIn("ningun punto de supervision productivo se ha implementado", texto)
        self.assertIn("No se consulto Gemini ni se altero la agenda", texto)


if __name__ == "__main__":
    unittest.main()
