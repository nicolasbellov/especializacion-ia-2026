"""Skillnest | U2.7 / Bloque 32 / Actividad CORE | PASO 1.

Registro reproducible de DOS versiones de un prompt REAL DEL PROYECTO:
- v1-b31-l2: prompt usado por el laboratorio RAG de Booking Core AI.
- v2-b32-l1: propuesta versionada que NO ha sido desplegada.

Reutiliza el registro existente y sus archivos Git, no inventa prompts.
Uso (desde la raiz): python registro_prompts.py
No llama a Gemini ni altera la agenda real.
"""

from __future__ import annotations

from src.versionado_supervision_b32 import (
    NOMBRE_PROMPT,
    RegistroDePrompts,
    cargar_registro,
    diff_prompts,
    huella_prompt,
)

VERSION_ANTERIOR = "v1-b31-l2"
VERSION_PROPUESTA = "v2-b32-l1"


def validar_registro(registro: RegistroDePrompts) -> tuple[dict, dict]:
    """Dos versiones propias, con huellas distintas y latest = la propuesta."""
    anterior = registro.por_version(NOMBRE_PROMPT, VERSION_ANTERIOR)
    nueva = registro.por_version(NOMBRE_PROMPT, VERSION_PROPUESTA)
    if len(registro.versiones) < 2:
        raise ValueError("La entrega requiere al menos dos versiones.")
    if anterior["huella"] != huella_prompt(anterior["texto"]):
        raise ValueError("Huella v1 inconsistente.")
    if nueva["huella"] != huella_prompt(nueva["texto"]):
        raise ValueError("Huella v2 inconsistente.")
    if anterior["huella"] == nueva["huella"]:
        raise ValueError("Los prompts deben tener huellas diferentes.")
    if registro.ultima(NOMBRE_PROMPT)["version"] != VERSION_PROPUESTA:
        raise ValueError("ultima(...) no corresponde a la ultima version registrada.")
    if not diff_prompts(anterior["texto"], nueva["texto"]):
        raise ValueError("No se encontro diferencia entre las versiones.")
    return anterior, nueva


def main() -> int:
    registro = cargar_registro()  # registro.json + sistema_v1.txt + sistema_v2.txt
    anterior, nueva = validar_registro(registro)

    print("=== BOOKING CORE AI | PASO 1: VERSIONADO DE PROMPTS ===")
    print("Registro del sistema:", NOMBRE_PROMPT)
    for version in (anterior, nueva):
        print(
            f"{version['version']} | sha256_12={version['huella']} "
            f"| autor={version['autor']} | fecha={version['fecha']}"
        )
        print("  motivo:", version["nota"])
        print("  modelo_probado:", version["modelo_probado"])
    print(
        "ultima(...):", registro.ultima(NOMBRE_PROMPT)["version"],
        registro.ultima(NOMBRE_PROMPT)["huella"],
    )
    print("--- diff version anterior vs version propuesta ---")
    for linea in diff_prompts(anterior["texto"], nueva["texto"]):
        print(linea)
    print("Version v1 usada en B31; v2 es propuesta NO desplegada.")
    print("PASS: dos prompts propios versionados, huellas y diff verificables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
