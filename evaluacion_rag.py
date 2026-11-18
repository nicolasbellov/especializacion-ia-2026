"""U2.5/B27/L2: evaluar un conjunto de preguntas mediante precision y recall.

Ejemplo OFICIAL Skillnest con cuatro preguntas y resultados SIMULADOS.
Python 3.10+ estándar; no instala paquetes ni llama a Gemini/Chroma.
Ejecución desde la raíz: python evaluacion_rag.py

evaluar_recuperacion(retriever, casos, k=3) queda preparada para recibir
un retriever REAL más adelante. Esta demostración no lo conecta ni inventa
etiquetas de relevancia para el índice propio de Booking Core AI.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

# Casos e IDs relevantes etiquetados en el MATERIAL OFICIAL, no en el índice propio.
casos_evaluacion = [
    {"pregunta": "que hace el cliente si una llamada tarda demasiado",
     "ids_relevantes": {"doc0"}},
    {"pregunta": "que pasa si la clave de api es invalida",
     "ids_relevantes": {"doc1"}},
    {"pregunta": "como se calcula el costo de una llamada",
     "ids_relevantes": {"doc2"}},
    {"pregunta": "como decide el agente que herramienta usar",
     "ids_relevantes": {"doc3"}},
]

# Simulación determinada por Skillnest: no hay llamada a retriever.invoke real.
ids_recuperados_por_pregunta = {
    "que hace el cliente si una llamada tarda demasiado": ["doc0", "doc4", "doc2"],
    "que pasa si la clave de api es invalida": ["doc2", "doc4", "doc3"],
    "como se calcula el costo de una llamada": ["doc2", "doc0", "doc4"],
    "como decide el agente que herramienta usar": ["doc4", "doc3", "doc1"],
}


def precision_at_k(ids_recuperados: list[str], ids_relevantes: set[str]) -> float:
    """Fracción recuperada relevante; 0.0 para resultado vacío, según B27/L2."""
    if not ids_recuperados:
        return 0.0
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_recuperados)


def recall_at_k(
    ids_recuperados: list[str],
    ids_relevantes: set[str],
) -> float | None:
    """Fracción de todos los relevantes recuperados; None si no hay relevantes."""
    if not ids_relevantes:
        return None
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_relevantes)


def promediar(valores: Iterable[float | None]) -> float:
    """Media aritmética solo de valores definidos; 0.0 si ninguno es válido."""
    validos = [valor for valor in valores if valor is not None]
    return sum(validos) / len(validos) if validos else 0.0


def _validar_caso(caso: dict[str, Any]) -> None:
    """Extensión: detectar etiquetas mal formadas antes de calcular promedios."""
    if (
        not isinstance(caso, dict)
        or not isinstance(caso.get("pregunta"), str)
        or not caso["pregunta"].strip()
        or not isinstance(caso.get("ids_relevantes"), set)
        or any(
            not isinstance(i, str) or not i
            for i in caso["ids_relevantes"]
        )
    ):
        raise ValueError("Caso inválido: pregunta no vacía e ids_relevantes set[str].")


def _validar_k(k: int) -> None:
    if type(k) is not int or k <= 0:
        raise ValueError("k debe ser un entero positivo.")


def evaluar_recuperacion(
    retriever: Any,
    casos: list[dict[str, Any]],
    k: int = 3,
) -> tuple[list[dict[str, Any]], float, float]:
    """Evaluación con retriever inyectado (NO se llama en el main).

    El curso lee c.id de cada Document. Comprobamos que sea un ID explícito
    no vacío para evitar que una divergencia de ID produzca falsos ceros.
    No normalizar ni cambiar IDs: deben coincidir con etiquetas humanas.
    """
    _validar_k(k)
    resultados: list[dict[str, Any]] = []
    for caso in casos:
        _validar_caso(caso)
        chunks = retriever.invoke(caso["pregunta"])
        ids_recuperados = [getattr(c, "id", None) for c in chunks][:k]
        if any(not isinstance(i, str) or not i for i in ids_recuperados):
            raise ValueError("Retrieval sin Document.id explícito: comprobar indexación.")
        if len(set(ids_recuperados)) != len(ids_recuperados):
            raise ValueError("Retriever devolvió IDs duplicados; revisar evaluación.")
        p = precision_at_k(ids_recuperados, caso["ids_relevantes"])
        r = recall_at_k(ids_recuperados, caso["ids_relevantes"])
        resultados.append(
            {"pregunta": caso["pregunta"], "precision": p, "recall": r}
        )
    return (
        resultados,
        promediar(fila["precision"] for fila in resultados),
        promediar(fila["recall"] for fila in resultados),
    )


def evaluar_recuperacion_simulada(
    casos: list[dict[str, Any]],
    k: int = 3,
) -> tuple[list[dict[str, Any]], float, float]:
    """Ejemplo del curso: recuperaciones FIJAS y media de resultados por caso."""
    _validar_k(k)
    resultados: list[dict[str, Any]] = []
    for caso in casos:
        _validar_caso(caso)
        # Acceso por pregunta exacta, tal como aparece en la lección.
        ids_recuperados = ids_recuperados_por_pregunta[caso["pregunta"]][:k]
        p = precision_at_k(ids_recuperados, caso["ids_relevantes"])
        r = recall_at_k(ids_recuperados, caso["ids_relevantes"])
        resultados.append({
            "pregunta": caso["pregunta"][:40],
            "precision": round(p, 3),
            "recall": r,
        })
    return (
        resultados,
        round(promediar(x["precision"] for x in resultados), 3),
        round(promediar(x["recall"] for x in resultados), 3),
    )


def main() -> int:
    print("B27/L2 - Conjunto de evaluación SIMULADO del curso, sin Gemini.")
    print("Casos:", len(casos_evaluacion))
    resultados, p_prom, r_prom = evaluar_recuperacion_simulada(casos_evaluacion)
    for fila in resultados:
        print(fila)
    print("precision promedio:", p_prom)
    print("recall promedio:", r_prom)
    print()
    print(precision_at_k([], {"doc0"}))
    print(recall_at_k(["doc0"], set()))
    print("AVISO: estos promedios no evalúan el índice real de Booking Core AI.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
