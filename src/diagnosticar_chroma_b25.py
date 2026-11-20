"""U2.5/Bloque 25/L2: diagnóstico de vector stores sin API ni reindexación.

La guía oficial de Skillnest agrupa fallos de instalación, Gemini, Chroma y
colecciones. Esta herramienta complementaria inspecciona SOLO archivos locales
y usa SQLite en modo de lectura: no importa Chroma, no crea colecciones, no
lee .env ni imprime claves, no genera embeddings y no modifica índices.

    python -m src.diagnosticar_chroma_b25 --indice todos
    python -m src.diagnosticar_chroma_b25 --indice b25_receta
"""

from __future__ import annotations

import argparse
from contextlib import closing
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
from typing import Any, Callable, TypeVar

RAIZ = Path(__file__).resolve().parents[1]

INDICES = {
    "b24_l1": (RAIZ / ".local" / "chroma_b24", "booking_core_rag_demo_b24", None),
    "b24_l3": (
        RAIZ / "vectorstore", "booking_core_b24_l3", "manifiesto_b24_l3.json",
    ),
    "b25_receta": (
        RAIZ / ".local" / "chroma_b25_receta",
        "receta_b25_ejemplo",
        "manifiesto_b25_receta.json",
    ),
}

DEPENDENCIAS = {
    "langchain_google_genai": "langchain-google-genai",
    "langchain_text_splitters": "langchain-text-splitters",
    "langchain_chroma": "langchain-chroma",
    "chromadb": "chromadb",
    "dotenv": "python-dotenv",
}

T = TypeVar("T")


def es_error_cuota(error: Exception) -> bool:
    """Heurística de la lección: solo reintentar errores que parezcan 429."""
    mensaje = str(error).casefold()
    return "429" in mensaje or "resource_exhausted" in mensaje


def con_reintentos_cuota(
    operacion: Callable[[], T],
    max_intentos: int = 4,
    espera_inicial: float = 5,
    dormir: Callable[[float], None] = time.sleep,
    registrar: Callable[[str], None] | None = None,
) -> T:
    """Patrón del curso 5/10/20 s, comprobable con mocks sin esperas reales.

    Solo para operaciones idempotentes: repetir una indexación parcial puede
    causar duplicados si se usan IDs aleatorios o si quedaron escrituras a medias.
    """
    if max_intentos < 1 or espera_inicial < 0:
        raise ValueError("max_intentos >= 1 y espera_inicial >= 0 son obligatorios.")
    espera = espera_inicial
    for intento in range(1, max_intentos + 1):
        try:
            return operacion()
        except Exception as error:
            if not es_error_cuota(error) or intento == max_intentos:
                raise
            if registrar is not None:
                registrar(
                    f"Límite de peticiones. Reintento {intento} "
                    f"de {max_intentos - 1} en {espera:g} s."
                )
            dormir(espera)
            espera *= 2
    raise AssertionError("El bucle de reintentos debe retornar o lanzar excepción.")


def inspeccionar_indice(
    directorio: Path,
    coleccion: str,
    manifiesto: str | None = None,
) -> dict[str, Any]:
    """Comprobar ruta y SQLite con mode=ro. No crear directorios ni colecciones."""
    ruta = Path(directorio).resolve()
    resultado: dict[str, Any] = {
        "ruta": str(ruta),
        "coleccion_configurada": coleccion,
        "existe": ruta.is_dir(),
        "sqlite_existe": False,
        "sqlite_integridad": "no comprobada",
        "manifiesto_estado": "no requerido" if manifiesto is None else "no encontrado",
    }
    archivo_db = ruta / "chroma.sqlite3"
    if not archivo_db.is_file():
        return resultado
    resultado["sqlite_existe"] = True

    # as_uri produce file:///C:/... en Windows y file:///... en Linux.
    # ?mode=ro evita crear la base y mantiene esta comprobación en solo lectura.
    try:
        with closing(sqlite3.connect(archivo_db.as_uri() + "?mode=ro", uri=True, timeout=2)) as db:
            fila = db.execute("PRAGMA quick_check").fetchone()
            resultado["sqlite_integridad"] = str(fila[0]) if fila else "sin respuesta"
    except sqlite3.Error:
        resultado["sqlite_integridad"] = "no legible; revisar permisos/corrupción"

    if manifiesto is not None:
        archivo_meta = ruta / manifiesto
        if archivo_meta.is_file():
            try:
                datos = json.loads(archivo_meta.read_text(encoding="utf-8"))
                if datos.get("coleccion") != coleccion:
                    resultado["manifiesto_estado"] = "colección diferente a la esperada"
                else:
                    resultado["manifiesto_estado"] = "coincide"
                    # Este recuento NO es count() de Chroma. Es solo metadata.
                    if "total_chunks" in datos:
                        resultado["chunks_segun_manifiesto"] = datos["total_chunks"]
                    elif isinstance(datos.get("ids"), list):
                        resultado["chunks_segun_manifiesto"] = len(datos["ids"])
            except (OSError, UnicodeError, ValueError):
                resultado["manifiesto_estado"] = "ilegible o JSON inválido"
    return resultado


def entorno_sin_secretos() -> dict[str, Any]:
    """Informar disponibilidad de imports y clave en el proceso; jamás su valor."""
    return {
        "python": ".".join(str(x) for x in sys.version_info[:3]),
        "entorno_virtual": sys.prefix != sys.base_prefix,
        "sqlite_version": sqlite3.sqlite_version,
        "gemini_key_en_proceso": bool(os.environ.get("GEMINI_API_KEY")),
        "paquetes": {paquete: importlib.util.find_spec(paquete) is not None
                     for paquete in DEPENDENCIAS},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnóstico seguro B25/L2, solo lectura")
    parser.add_argument("--indice", choices=["todos", *INDICES], default="todos")
    args = parser.parse_args()

    entorno = entorno_sin_secretos()
    print("Python:", entorno["python"])
    print("Entorno virtual activo:", entorno["entorno_virtual"])
    print("SQLite:", entorno["sqlite_version"])
    print("GEMINI_API_KEY presente en el proceso:", entorno["gemini_key_en_proceso"])
    print("Nota: no se lee .env; 'False' no descarta una clave allí.")
    for modulo, disponible in entorno["paquetes"].items():
        print("Dependencia", DEPENDENCIAS[modulo] + ":", "OK" if disponible else "FALTA")

    indices = INDICES if args.indice == "todos" else {args.indice: INDICES[args.indice]}
    for nombre, (ruta, coleccion, manifiesto) in indices.items():
        estado = inspeccionar_indice(ruta, coleccion, manifiesto)
        print(f"\nÍndice {nombre}")
        print("Ruta absoluta:", estado["ruta"])
        print("Colección prevista:", estado["coleccion_configurada"])
        print("Directorio existente:", estado["existe"])
        print("Base SQLite existente:", estado["sqlite_existe"])
        print("SQLite quick_check:", estado["sqlite_integridad"])
        print("Manifiesto:", estado["manifiesto_estado"])
        if "chunks_segun_manifiesto" in estado:
            print("Chunks declarados en manifiesto:", estado["chunks_segun_manifiesto"])
        print("Para validar el conteo real usar el verificador de B24 o B25.")

    print("\nDiagnóstico local completado. Sin API, sin cambios en los índices.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
