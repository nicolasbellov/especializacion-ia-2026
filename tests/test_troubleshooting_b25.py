"""U2.5/B25/L2 — errores y reintentos de Chroma, siempre sin red ni Gemini."""

from __future__ import annotations

from contextlib import closing
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.diagnosticar_chroma_b25 import (
    INDICES,
    con_reintentos_cuota,
    entorno_sin_secretos,
    es_error_cuota,
    inspeccionar_indice,
)

RAIZ = Path(__file__).resolve().parents[1]


class TestTroubleshootingB25(unittest.TestCase):
    def test_identifica_429_y_resource_exhausted(self):
        self.assertTrue(es_error_cuota(RuntimeError("429 RESOURCE_EXHAUSTED")))
        self.assertTrue(es_error_cuota(RuntimeError("resource_exhausted")))
        self.assertFalse(es_error_cuota(ValueError("API key not valid")))
        self.assertFalse(es_error_cuota(ValueError("401 UNAUTHENTICATED")))
        self.assertFalse(es_error_cuota(PermissionError("readonly database")))

    def test_reintentos_429_5_10_y_exito(self):
        esperas = []
        mensajes = []
        intentos = []

        def api_simulada():
            intentos.append("intento")
            if len(intentos) <= 2:
                raise RuntimeError("429 RESOURCE_EXHAUSTED")
            return "OK"

        resultado = con_reintentos_cuota(
            api_simulada, dormir=esperas.append, registrar=mensajes.append
        )
        self.assertEqual(resultado, "OK")
        self.assertEqual(len(intentos), 3)
        self.assertEqual(esperas, [5, 10])
        self.assertEqual(len(mensajes), 2)

    def test_cuota_persistente_propagada_tras_cuatro_intentos(self):
        esperas = []
        contador = []

        def siempre_429():
            contador.append(1)
            raise RuntimeError("429 RESOURCE_EXHAUSTED")

        with self.assertRaisesRegex(RuntimeError, "RESOURCE_EXHAUSTED"):
            con_reintentos_cuota(siempre_429, dormir=esperas.append)
        self.assertEqual(len(contador), 4)
        self.assertEqual(esperas, [5, 10, 20])

    def test_errores_401_403_y_sqlite_no_se_reintentan(self):
        for excepcion in (
            ValueError("401 INVALID_API_KEY"),
            RuntimeError("403 PERMISSION_DENIED"),
            PermissionError("attempt to write a readonly database"),
        ):
            with self.subTest(error=str(excepcion)):
                intentos = []
                esperas = []

                def fallo():
                    intentos.append(True)
                    raise excepcion

                with self.assertRaises(type(excepcion)):
                    con_reintentos_cuota(fallo, dormir=esperas.append)
                self.assertEqual(len(intentos), 1)
                self.assertEqual(esperas, [])

    def test_parmetros_de_retry(self):
        with self.assertRaises(ValueError):
            con_reintentos_cuota(lambda: "ok", max_intentos=0)
        with self.assertRaises(ValueError):
            con_reintentos_cuota(lambda: "ok", espera_inicial=-2)
        self.assertEqual(
            con_reintentos_cuota(lambda: 12, max_intentos=1, dormir=lambda _: None),
            12,
        )

    def test_indice_inexistente_no_crea_archivos(self):
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "no_existe"
            resultado = inspeccionar_indice(ruta, "prueba")
            self.assertFalse(resultado["existe"])
            self.assertFalse(resultado["sqlite_existe"])
            self.assertFalse(ruta.exists())

    def test_comprobacion_sqlite_lectura_sin_mutaciones(self):
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "indice"
            ruta.mkdir()
            dbfile = ruta / "chroma.sqlite3"
            with closing(sqlite3.connect(dbfile)) as conexion:
                conexion.execute("CREATE TABLE prueba (id INTEGER)")
                conexion.execute("INSERT INTO prueba VALUES (5)")
                conexion.commit()
            meta = ruta / "manifiesto_b24_l3.json"
            meta.write_text(
                json.dumps({"coleccion": "coleccion_academica", "total_chunks": 3}),
                encoding="utf-8",
            )
            before = dbfile.read_bytes()
            meta_before = meta.read_bytes()
            result = inspeccionar_indice(ruta, "coleccion_academica", meta.name)
            self.assertTrue(result["existe"])
            self.assertTrue(result["sqlite_existe"])
            self.assertEqual(result["sqlite_integridad"], "ok")
            self.assertEqual(result["manifiesto_estado"], "coincide")
            self.assertEqual(result["chunks_segun_manifiesto"], 3)
            self.assertEqual(dbfile.read_bytes(), before)
            self.assertEqual(meta.read_bytes(), meta_before)

    def test_coleccion_distinta_detectada_por_manifiesto(self):
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal)
            dbfile = ruta / "chroma.sqlite3"
            with closing(sqlite3.connect(dbfile)) as conexion:
                conexion.execute("CREATE TABLE t (id INTEGER)")
                conexion.commit()
            (ruta / "manifiesto_b25_receta.json").write_text(
                json.dumps({"coleccion": "otra", "ids": ["a", "b"]}),
                encoding="utf-8",
            )
            result = inspeccionar_indice(ruta, "esperada", "manifiesto_b25_receta.json")
            self.assertEqual(result["manifiesto_estado"], "colección diferente a la esperada")
            self.assertNotIn("chunks_segun_manifiesto", result)

    def test_clave_no_se_imprime_ni_carga_dotenv(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "SECRETO_DE_TEST"}, clear=False):
            info = entorno_sin_secretos()
            self.assertTrue(info["gemini_key_en_proceso"])
            self.assertNotIn("SECRETO_DE_TEST", str(info))
        self.assertIn("sqlite_version", info)

    def test_rutas_independientes_y_colecciones_explicitas(self):
        self.assertEqual(set(INDICES), {"b24_l1", "b24_l3", "b25_receta"})
        rutas = [str(fila[0]) for fila in INDICES.values()]
        nombres = [fila[1] for fila in INDICES.values()]
        self.assertEqual(len(set(rutas)), 3)
        self.assertEqual(len(set(nombres)), 3)
        self.assertTrue(all(len(nombre) >= 3 for nombre in nombres))

    def test_cli_sin_llamadas_gemini(self):
        env = os.environ.copy()
        env.pop("GEMINI_API_KEY", None)
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        proceso = subprocess.run(
            [sys.executable, "-m", "src.diagnosticar_chroma_b25", "--indice", "b25_receta"],
            cwd=str(RAIZ),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            check=False,
        )
        self.assertEqual(proceso.returncode, 0, proceso.stderr[-1000:])
        self.assertIn("Diagnóstico local completado. Sin API", proceso.stdout)
        self.assertIn("Colección prevista: receta_b25_ejemplo", proceso.stdout)
        self.assertNotIn("SECRETO_DE_TEST", proceso.stdout)


if __name__ == "__main__":
    unittest.main()
