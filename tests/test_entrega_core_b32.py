"""Pruebas offline de integración de la entrega CORE U2.7/B32/L3."""

from contextlib import redirect_stdout
from io import StringIO
import unittest
from unittest.mock import patch

from grafo_supervision import (
    crear_grafo,
    ejecutar,
    iniciar_solicitud,
    obtener_pendiente,
    resolver,
)
from matriz_riesgos import cargar_matriz_booking_core
from registro_prompts import (
    VERSION_ANTERIOR,
    VERSION_PROPUESTA,
    main as main_registro,
    validar_registro,
)
from src.mitigacion_inyeccion_b31_booking_core import PROMPT_SISTEMA
from src.versionado_supervision_b32 import NOMBRE_PROMPT, cargar_registro


class TestEntregaCoreB32(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registro = cargar_registro()
        cls.v1, cls.v2 = validar_registro(cls.registro)

    def solicitud(self, app=None):
        app = app or crear_grafo()
        solicitud = iniciar_solicitud(
            app, self.v1["version"], self.v2["version"], self.v2["huella"]
        )
        return app, solicitud

    def test_prompt_v1_es_el_prompt_del_laboratorio_real(self):
        self.assertEqual(self.v1["texto"], PROMPT_SISTEMA)
        self.assertEqual(self.v1["version"], VERSION_ANTERIOR)
        self.assertEqual(self.v2["version"], VERSION_PROPUESTA)
        self.assertEqual(self.registro.ultima(NOMBRE_PROMPT)["huella"], self.v2["huella"])

    def test_dos_huellas_y_diff_en_script_paso_1(self):
        salida = StringIO()
        with redirect_stdout(salida):
            self.assertEqual(main_registro(), 0)
        txt = salida.getvalue()
        self.assertIn(self.v1["huella"], txt)
        self.assertIn(self.v2["huella"], txt)
        self.assertNotEqual(self.v1["huella"], self.v2["huella"])
        self.assertIn("--- version_anterior", txt)
        self.assertIn("+++ version_nueva", txt)
        self.assertIn("PASS: dos prompts propios", txt)

    def test_interrupt_espera_y_no_aplica_version(self):
        app, solicitud = self.solicitud()
        pendiente = obtener_pendiente(app, solicitud)
        estado = app.get_state(solicitud.config)
        self.assertIn("supervisar", estado.next)
        self.assertTrue(estado.interrupts)
        self.assertEqual(estado.values["resultado"], "PENDIENTE")
        self.assertEqual(estado.values["version_activa_simulada"], self.v1["version"])
        self.assertEqual(pendiente["huella_propuesta"], self.v2["huella"])

    def test_command_resume_true_aprueba_y_termina_sin_desplegar(self):
        app, solicitud = self.solicitud()
        final = resolver(app, solicitud, True, huella_revisada=self.v2["huella"])
        self.assertTrue(final["aprobado"])
        self.assertEqual(final["version_activa_simulada"], self.v2["version"])
        self.assertEqual(final["resultado"], "APROBADA_SOLO_EN_SIMULACION")
        self.assertFalse(app.get_state(solicitud.config).next)

    def test_command_resume_false_rechaza_y_conserva_version(self):
        app, solicitud = self.solicitud()
        final = resolver(app, solicitud, False, huella_revisada=self.v2["huella"])
        self.assertFalse(final["aprobado"])
        self.assertEqual(final["version_activa_simulada"], self.v1["version"])
        self.assertEqual(final["resultado"], "RECHAZADA_VERSION_ORIGINAL_CONSERVADA")

    def test_thread_ids_aislados(self):
        app = crear_grafo()
        _, solicitud1 = self.solicitud(app)
        _, solicitud2 = self.solicitud(app)
        self.assertNotEqual(solicitud1.config, solicitud2.config)
        resolver(app, solicitud1, False, huella_revisada=self.v2["huella"])
        self.assertEqual(
            obtener_pendiente(app, solicitud2)["version_propuesta"],
            self.v2["version"],
        )

    def test_hash_distinto_o_decision_no_booleana_bloquea(self):
        app, solicitud = self.solicitud()
        with self.assertRaises(ValueError):
            resolver(app, solicitud, True, huella_revisada="hash-diferente")
        with self.assertRaises(ValueError):
            resolver(app, solicitud, "no", huella_revisada=self.v2["huella"])
        self.assertEqual(obtener_pendiente(app, solicitud)["huella_propuesta"], self.v2["huella"])

    def test_no_se_puede_resolver_el_mismo_hilo_dos_veces(self):
        app, solicitud = self.solicitud()
        resolver(app, solicitud, False, huella_revisada=self.v2["huella"])
        with self.assertRaises(ValueError):
            resolver(app, solicitud, True, huella_revisada=self.v2["huella"])

    def test_script_paso_2_ensaya_aprobacion_y_rechazo(self):
        salida = StringIO()
        with redirect_stdout(salida):
            ejecutar(interactivo=False)
        texto = salida.getvalue()
        self.assertIn("__interrupt__ pendiente", texto)
        self.assertIn("APROBADA_SOLO_EN_SIMULACION", texto)
        self.assertIn("RECHAZADA_VERSION_ORIGINAL_CONSERVADA", texto)
        self.assertIn("PASS: interrupt real", texto)

    def test_modo_interactivo_con_rechazo_ficticio(self):
        salida = StringIO()
        with patch("builtins.input", return_value="n"), redirect_stdout(salida):
            ejecutar(interactivo=True)
        self.assertIn("RECHAZADA_VERSION_ORIGINAL_CONSERVADA", salida.getvalue())

    def test_matriz_seis_riesgos_con_mitigacion_expresa(self):
        riesgos = cargar_matriz_booking_core()["riesgos"]
        self.assertGreaterEqual(len(riesgos), 5)
        self.assertEqual(len(riesgos), 6)
        self.assertTrue(all(r["mitigacion"].strip() for r in riesgos))
        self.assertEqual([r["puntaje"] for r in riesgos], [20, 16, 15, 12, 8, 6])

    def test_al_menos_dos_mitigaciones_referencian_bloque_implementado(self):
        riesgos = cargar_matriz_booking_core()["riesgos"]
        n = sum(
            "Bloque 31" in r["mitigacion"] or "Bloques 24 y 26" in r["mitigacion"]
            for r in riesgos
        )
        self.assertGreaterEqual(n, 2)

    def test_alto_critico_incluye_punto_humano_no_implementado(self):
        riesgos = cargar_matriz_booking_core()["riesgos"]
        prioritarios = [r for r in riesgos if r["categoria"] in ("ALTO", "CRITICO")]
        self.assertEqual(len(prioritarios), 4)
        for r in prioritarios:
            self.assertTrue(r["punto_supervision"])
            self.assertEqual(r["estado_supervision"], "PROPUESTO_NO_IMPLEMENTADO")

    def test_matriz_indica_estimaciones_no_auditoria(self):
        matriz = cargar_matriz_booking_core()
        self.assertIn("NO mediciones", matriz["fuente"])
        self.assertIn("NO_REQUERIDO_POR_UMBRAL",
                      {r["estado_supervision"] for r in matriz["riesgos"]})


if __name__ == "__main__":
    unittest.main()
