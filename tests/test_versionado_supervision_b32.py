"""U2.7/B32/L1: versionado y supervisión humana LangGraph SIN APIs reales."""

import hashlib
from pathlib import Path
import unittest

from src.mitigacion_inyeccion_b31_booking_core import PROMPT_SISTEMA
from src.versionado_supervision_b32 import (
    ARCHIVO_REGISTRO,
    NOMBRE_PROMPT,
    RegistroDePrompts,
    cargar_registro,
    construir_grafo,
    diff_prompts,
    huella_prompt,
    inspeccionar_pendiente,
    proponer_cambio,
    resolver_solicitud,
)


class TestVersionadoSupervisionB32(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registro = cargar_registro()
        cls.v1 = cls.registro.por_version(NOMBRE_PROMPT, "v1-b31-l2")
        cls.v2 = cls.registro.por_version(NOMBRE_PROMPT, "v2-b32-l1")

    def nueva_solicitud(self, app=None):
        app = construir_grafo() if app is None else app
        solicitud = proponer_cambio(
            app,
            version_actual=self.v1["version"],
            version_nueva=self.v2["version"],
            huella_nueva=self.v2["huella"],
        )
        return app, solicitud

    def test_version_v1_es_texto_original_b31_l2(self):
        self.assertEqual(self.v1["texto"], PROMPT_SISTEMA)

    def test_versiones_diferentes_y_hash_reproducible(self):
        self.assertNotEqual(self.v1["texto"], self.v2["texto"])
        self.assertNotEqual(self.v1["huella"], self.v2["huella"])
        for version in [self.v1, self.v2]:
            esperado = hashlib.sha256(version["texto"].encode("utf-8")).hexdigest()[:12]
            self.assertEqual(version["huella"], esperado)
            self.assertEqual(len(huella_prompt(version["texto"])), 12)

    def test_metadata_registrada_sin_inventar_modelo_validado(self):
        for version in [self.v1, self.v2]:
            self.assertTrue(version["autor"])
            self.assertEqual(version["fecha"], "2026-11-26")
            self.assertTrue(version["nota"])
            self.assertIsNone(version["modelo_probado"])
            self.assertIsNone(version["parametros_probados"])

    def test_diff_muestra_instrucciones_nuevas(self):
        diferencias = diff_prompts(self.v1["texto"], self.v2["texto"])
        self.assertTrue(diferencias[0].startswith("---"))
        self.assertTrue(diferencias[1].startswith("+++"))
        self.assertTrue(any(linea.startswith("+Si") for linea in diferencias))
        self.assertTrue(any("autorizacion" in linea for linea in diferencias))

    def test_registro_ultima_por_nombre(self):
        self.assertEqual(self.registro.ultima(NOMBRE_PROMPT)["version"], "v2-b32-l1")
        self.assertIsNone(self.registro.ultima("inexistente"))
        with self.assertRaises(KeyError):
            self.registro.por_version(NOMBRE_PROMPT, "inexistente")

    def test_registro_rechaza_duplicados(self):
        registro = RegistroDePrompts()
        campos = dict(
            nombre=NOMBRE_PROMPT,
            version="v1",
            texto="Prompt ejemplo",
            autor="autor-academico",
            fecha="2026-11-26",
            nota="primera version",
        )
        registro.registrar(**campos)
        with self.assertRaises(ValueError):
            registro.registrar(**campos)

    def test_registro_rechaza_texto_vacio(self):
        with self.assertRaises(ValueError):
            huella_prompt("")
        with self.assertRaises(ValueError):
            RegistroDePrompts().registrar(
                NOMBRE_PROMPT, "v1", "", "autor", "2026-11-26", "nota"
            )

    def test_registro_se_lee_desde_archivos_git(self):
        self.assertTrue(ARCHIVO_REGISTRO.is_file())
        self.assertEqual(len(self.registro.versiones), 2)
        for nombre in ("sistema_v1.txt", "sistema_v2.txt"):
            self.assertTrue((ARCHIVO_REGISTRO.parent / nombre).is_file())
        self.assertIsNotNone(cargar_registro().ultima(NOMBRE_PROMPT))

    def test_interrupt_deja_solicitud_pendiente_sin_desplegar(self):
        app, solicitud = self.nueva_solicitud()
        pendiente = inspeccionar_pendiente(app, solicitud)
        estado = app.get_state(solicitud.config)
        self.assertIn("punto_supervision", estado.next)
        self.assertTrue(estado.interrupts)
        self.assertEqual(estado.values["resultado"], "pendiente")
        self.assertEqual(estado.values["version_activa"], self.v1["version"])
        self.assertEqual(pendiente["version_propuesta"], self.v2["version"])
        self.assertEqual(pendiente["huella_propuesta"], self.v2["huella"])

    def test_aprobacion_reanuda_solo_version_revisada(self):
        app, solicitud = self.nueva_solicitud()
        pendiente = inspeccionar_pendiente(app, solicitud)
        final = resolver_solicitud(
            app, solicitud, aprobar=True,
            version_revisada=pendiente["version_propuesta"],
            huella_revisada=pendiente["huella_propuesta"],
        )
        self.assertTrue(final["aprobado"])
        self.assertEqual(final["version_activa"], self.v2["version"])
        self.assertEqual(final["resultado"], "aprobado_en_simulacion")
        self.assertFalse(app.get_state(solicitud.config).next)

    def test_rechazo_conserva_version_anterior(self):
        app, solicitud = self.nueva_solicitud()
        final = resolver_solicitud(
            app, solicitud, aprobar=False,
            version_revisada=self.v2["version"],
            huella_revisada=self.v2["huella"],
        )
        self.assertFalse(final["aprobado"])
        self.assertEqual(final["version_activa"], self.v1["version"])
        self.assertEqual(final["resultado"], "rechazado_en_simulacion")

    def test_version_o_huella_distintas_bloquean_aprobacion(self):
        app, solicitud = self.nueva_solicitud()
        for version, huella in [
            ("otra-version", self.v2["huella"]),
            (self.v2["version"], "huella-distinta"),
        ]:
            with self.subTest(version=version):
                with self.assertRaises(ValueError):
                    resolver_solicitud(
                        app, solicitud, aprobar=True,
                        version_revisada=version, huella_revisada=huella,
                    )
        self.assertEqual(
            inspeccionar_pendiente(app, solicitud)["version_propuesta"],
            self.v2["version"],
        )

    def test_rechaza_segunda_aprobacion_del_mismo_hilo(self):
        app, solicitud = self.nueva_solicitud()
        resolver_solicitud(
            app, solicitud, aprobar=True,
            version_revisada=self.v2["version"],
            huella_revisada=self.v2["huella"],
        )
        with self.assertRaisesRegex(ValueError, "no tiene aprobacion pendiente"):
            resolver_solicitud(
                app, solicitud, aprobar=True,
                version_revisada=self.v2["version"],
                huella_revisada=self.v2["huella"],
            )

    def test_thread_ids_unicos_y_solicitudes_aisladas(self):
        app = construir_grafo()
        _, a = self.nueva_solicitud(app)
        _, b = self.nueva_solicitud(app)
        self.assertNotEqual(
            a.config["configurable"]["thread_id"],
            b.config["configurable"]["thread_id"],
        )
        resolver_solicitud(
            app, a, aprobar=True,
            version_revisada=self.v2["version"], huella_revisada=self.v2["huella"],
        )
        self.assertEqual(
            inspeccionar_pendiente(app, b)["version_propuesta"],
            self.v2["version"],
        )

    def test_no_se_puede_aprobar_con_decision_no_booleana(self):
        app, solicitud = self.nueva_solicitud()
        with self.assertRaises(ValueError):
            resolver_solicitud(
                app, solicitud, aprobar="si",
                version_revisada=self.v2["version"],
                huella_revisada=self.v2["huella"],
            )
        self.assertTrue(app.get_state(solicitud.config).next)

    def test_no_se_produce_ninguna_reserva_ni_despliegue_real(self):
        # El nombre de resultado declara que el efecto es solo un estado simulado.
        app, solicitud = self.nueva_solicitud()
        final = resolver_solicitud(
            app, solicitud, aprobar=True,
            version_revisada=self.v2["version"],
            huella_revisada=self.v2["huella"],
        )
        self.assertIn("simulacion", final["resultado"])
        self.assertEqual(self.registro.ultima(NOMBRE_PROMPT)["version"], "v2-b32-l1")
        self.assertNotIn("GEMINI_API_KEY", final)


if __name__ == "__main__":
    unittest.main()
