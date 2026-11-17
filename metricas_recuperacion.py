"""U2.5/B27/L1: precisión@k, exhaustividad (recall@k) y F1.

Ejemplo oficial Skillnest (5 textos ficticios, IDs doc0..doc4).
Python estándar: SIN Gemini, Chroma, otras bibliotecas, API ni reindexación.

Ejecutar desde la raíz:
    python metricas_recuperacion.py
    python -m unittest discover -s tests -p "test_metricas_recuperacion_b27.py" -v

IMPORTANTE: ranking fijo del curso, NO resultados medidos en Booking Core.
"""

from __future__ import annotations

from collections.abc import Collection, Sequence

# Datos, orden y relevancia proporcionados por Skillnest B27/L1.
CORPUS = {
    "doc0": "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente.",
    "doc1": "Los errores de autenticacion nunca se reintentan: fallan de inmediato con un ValueError.",
    "doc2": "El costo de cada llamada se calcula a partir de totalTokenCount y la tarifa vigente por cada 1000 tokens.",
    "doc3": "El agente de la Unidad 2.4 decide por si mismo que herramienta usar, segun la descripcion de cada una.",
    "doc4": "Las pruebas unitarias del cliente usan mocks, de forma que la suite completa corre en menos de un segundo.",
}
PREGUNTA = "que hace el cliente si una llamada tarda demasiado?"
IDS_RELEVANTES = {"doc0"}  # Etiquetado humano del ejemplo, no automático.
IDS_RECUPERADOS = ["doc2", "doc0", "doc4"]  # Ejemplo independiente de top-3.
RANKED = ["doc2", "doc4", "doc0", "doc1", "doc3"]  # Ranking fijo para variar k.


def _validar_ids(
    ids_recuperados: Sequence[str],
    ids_relevantes: Collection[str],
) -> tuple[set[str], set[str]]:
    """Extensión de robustez: evita métricas indefinidas o recall > 1.

    En el curso se presupone IDs únicos, top-k no vacío y al menos un relevante;
    cuando faltan se produce ZeroDivisionError. En el proyecto reportamos un
    ValueError explícito para no ocultar datos de evaluación mal etiquetados.
    """
    if not ids_recuperados:
        raise ValueError("No se puede medir precision@k: recuperados vacío.")
    if not ids_relevantes:
        raise ValueError("No se puede medir recall@k: relevantes vacío.")
    if any(not isinstance(i, str) or not i for i in ids_recuperados):
        raise ValueError("Los ids recuperados deben ser strings no vacíos.")
    if any(not isinstance(i, str) or not i for i in ids_relevantes):
        raise ValueError("Los ids relevantes deben ser strings no vacíos.")
    vistos = set(ids_recuperados)
    if len(vistos) != len(ids_recuperados):
        raise ValueError("Hay IDs recuperados duplicados: revisar el ranking.")
    relevantes = set(ids_relevantes)
    if len(relevantes) != len(ids_relevantes):
        raise ValueError("Hay IDs relevantes duplicados: revisar las etiquetas.")
    return vistos, relevantes


def precision_at_k(
    ids_recuperados: Sequence[str],
    ids_relevantes: Collection[str],
) -> float:
    """De lo recuperado, fracción realmente relevante."""
    _validar_ids(ids_recuperados, ids_relevantes)
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_recuperados)


def recall_at_k(
    ids_recuperados: Sequence[str],
    ids_relevantes: Collection[str],
) -> float:
    """De todos los relevantes, fracción que entró en los recuperados."""
    _validar_ids(ids_recuperados, ids_relevantes)
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_relevantes)


def f1(precision: float, recall: float) -> float:
    """Media armónica de precisión y recall (cero cuando ambos son cero)."""
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def evaluar_ranking(
    ranked: Sequence[str],
    ids_relevantes: Collection[str],
    max_k: int | None = None,
) -> list[dict[str, object]]:
    """Calcular trade-off para cada k sobre UN MISMO ranking fijo.

    El argumento max_k solo restringe la longitud; no recalcula embeddings.
    """
    if not ranked:
        raise ValueError("Ranking vacío.")
    limite = len(ranked) if max_k is None else max_k
    if type(limite) is not int or not 1 <= limite <= len(ranked):
        raise ValueError("max_k debe estar entre 1 y el tamaño del ranking.")
    resultados: list[dict[str, object]] = []
    for k in range(1, limite + 1):
        sub = list(ranked[:k])
        p = precision_at_k(sub, ids_relevantes)
        r = recall_at_k(sub, ids_relevantes)
        resultados.append({
            "k": k, "ids": sub, "precision": p, "recall": r, "f1": f1(p, r),
        })
    return resultados


def main() -> int:
    print("Bloque 27/L1 - Evaluación offline del ranking FIJO del curso.")
    print("Pregunta:", PREGUNTA)
    print("Relevantes (etiquetado del curso):", sorted(IDS_RELEVANTES))
    print("IDs recuperados @3:", IDS_RECUPERADOS)
    print("precision@3:", precision_at_k(IDS_RECUPERADOS, IDS_RELEVANTES))
    print("recall@3:", recall_at_k(IDS_RECUPERADOS, IDS_RELEVANTES))

    resultados = evaluar_ranking(RANKED, IDS_RELEVANTES)
    print("\n--- Trade-off precision/recall por k ---")
    for fila in resultados:
        print(
            f"k={fila['k']}: precision={fila['precision']:.3f}  "
            f"recall={fila['recall']:.3f}  recuperados={fila['ids']}"
        )
    print("\n--- F1 por k ---")
    for fila in resultados:
        print(f"k={fila['k']}: F1={fila['f1']:.3f}")
    mejor = max(resultados, key=lambda x: x["f1"])
    print(f"\nMáximo F1 en este ejemplo: k={mejor['k']}, F1={mejor['f1']:.3f}")
    print("AVISO: números hipotéticos del curso; no son métricas del RAG Booking Core.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
