"""Estimación didáctica B28: no constituye tarifa ni facturación Gemini."""
from __future__ import annotations

# Valores ficticios usados por costos_rag.py (B28), USD por mil tokens.
TARIFA_ENTRADA_X1000 = 0.0001
TARIFA_SALIDA_X1000 = 0.0004


def estimar_costo_generacion(uso):
    """Usa tokens observados o simulados, explícitos; no inventa valores faltantes."""
    if not uso:
        return None
    entrada, salida = uso.get("input_tokens"), uso.get("output_tokens")
    if type(entrada) is not int or type(salida) is not int or min(entrada, salida) < 0:
        return None
    return {
        "usd_estimado_chat": round((entrada * TARIFA_ENTRADA_X1000
                                    + salida * TARIFA_SALIDA_X1000) / 1000, 9),
        "tipo_tarifa": "FICTICIA_B28_NO_FACTURACION",
        "simulado": bool(uso.get("simulado")),
        "incluye_embeddings": False,
    }
