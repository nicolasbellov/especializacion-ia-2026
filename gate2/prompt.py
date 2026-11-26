"""Prompt activo de Gate 2: texto exacto versionado, no v2 propuesta de B32."""
from pathlib import Path
from src.versionado_supervision_b32 import cargar_registro

RUTA = Path(__file__).resolve().parents[1] / "prompts" / "booking_core_ai" / "registro_gate2.json"


def prompt_activo():
    return cargar_registro(RUTA).por_version("booking_core_ai_gate2", "v3-gate2")
