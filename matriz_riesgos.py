"""U2.7/B32/L2: matriz de riesgos Skillnest y análisis preliminar Booking Core AI.

Estándar de la LECCIÓN: probabilidad 1..5 x impacto 1..5;
CRITICO >=15, ALTO >=9, MEDIO >=4, BAJO el resto.
El primer reporte reproduce cinco ejemplos del curso; el segundo usa
estimaciones PROPIAS, no observaciones de incidentes productivos.

100 % biblioteca estándar, sin llamadas a Gemini, Chroma o Booking Core.
Ejecutar desde la raíz: python matriz_riesgos.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


RAIZ = Path(__file__).resolve().parent
ARCHIVO_BOOKING_CORE = RAIZ / "data" / "matriz_riesgos_booking_core_b32.json"

# Cinco ejemplos OFICIALES de la lección, con valores preservados.
RIESGOS_CURSO = [
    {
        "riesgo": "Inyeccion de prompt via documento recuperado",
        "probabilidad": 4, "impacto": 4,
        "mitigacion": "Filtro de patrones + delimitacion de contexto (Bloque 31)",
    },
    {
        "riesgo": "Filtracion de PII en logs sin redactar",
        "probabilidad": 3, "impacto": 5,
        "mitigacion": "Registrar huella/longitud en vez de contenido (Bloque 31)",
    },
    {
        "riesgo": "Dataset de tuning desbalanceado produce sesgo",
        "probabilidad": 3, "impacto": 3,
        "mitigacion": "Chequeo de balance por categoria antes de enviar (Bloque 29)",
    },
    {
        "riesgo": "Modelo de embeddings usado queda deprecado sin aviso",
        "probabilidad": 2, "impacto": 4,
        "mitigacion": "Revision periodica de la documentacion oficial (Bloque 28)",
    },
    {
        "riesgo": "Respuesta con informacion vieja por chunk no reindexado",
        "probabilidad": 3, "impacto": 2,
        "mitigacion": "Actualizacion incremental del indice con ids explicitos (Bloque 25)",
    },
]


def validar_nivel(valor: int, nombre: str) -> None:
    if type(valor) is not int or not 1 <= valor <= 5:
        raise ValueError(f"{nombre} debe ser un entero entre 1 y 5.")


def puntaje_riesgo(probabilidad: int, impacto: int) -> int:
    """P × I: misma regla que Skillnest; valida entradas para evitar errores."""
    validar_nivel(probabilidad, "probabilidad")
    validar_nivel(impacto, "impacto")
    return probabilidad * impacto


def categoria_riesgo(puntaje: int) -> str:
    """Cortes DIDÁCTICOS Skillnest, no estándar universal."""
    if type(puntaje) is not int or not 1 <= puntaje <= 25:
        raise ValueError("El puntaje debe ser un entero entre 1 y 25.")
    if puntaje >= 15:
        return "CRITICO"
    if puntaje >= 9:
        return "ALTO"
    if puntaje >= 4:
        return "MEDIO"
    return "BAJO"


def esta_en_el_limite(probabilidad: int, impacto: int) -> bool:
    """¿Alterar UN punto válido en P o I cambiaría la categoría?"""
    actual = categoria_riesgo(puntaje_riesgo(probabilidad, impacto))
    vecinos = [
        (probabilidad + 1, impacto),
        (probabilidad - 1, impacto),
        (probabilidad, impacto + 1),
        (probabilidad, impacto - 1),
    ]
    return any(
        categoria_riesgo(puntaje_riesgo(p, i)) != actual
        for p, i in vecinos if 1 <= p <= 5 and 1 <= i <= 5
    )


def ordenar_y_evaluar(riesgos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Anota puntaje, categoría y sensibilidad SIN modificar el inventario."""
    evaluados = []
    for fila in riesgos:
        if not isinstance(fila, dict) or not isinstance(fila.get("riesgo"), str) or not fila["riesgo"].strip():
            raise ValueError("Cada riesgo necesita una descripción concreta.")
        probabilidad = fila.get("probabilidad")
        impacto = fila.get("impacto")
        puntaje = puntaje_riesgo(probabilidad, impacto)
        evaluados.append({
            **fila,
            "puntaje": puntaje,
            "categoria": categoria_riesgo(puntaje),
            "al_limite": esta_en_el_limite(probabilidad, impacto),
        })
    return sorted(evaluados, key=lambda fila: -fila["puntaje"])


def validar_matriz_booking_core(riesgos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """El ALTO/CRITICO debe tener supervisor definido y estado HONESTO.

    Un punto de supervisión anotado en JSON es un CONTROL PROPUESTO, NO
    prueba de que el guard humano esté implementado en Booking Core.
    """
    if not isinstance(riesgos, list) or not riesgos:
        raise ValueError("Se requiere una matriz de riesgos no vacía.")
    ids = set()
    for fila in riesgos:
        if not isinstance(fila, dict):
            raise ValueError("Cada fila de riesgo debe ser un diccionario.")
        identificador = fila.get("id")
        if not isinstance(identificador, str) or not identificador.strip() or identificador in ids:
            raise ValueError("Falta ID o existe un ID duplicado.")
        ids.add(identificador)
        for campo in ("mitigacion", "mitigacion_existente", "mitigacion_pendiente", "justificacion"):
            if not isinstance(fila.get(campo), str) or not fila[campo].strip():
                raise ValueError(f"Falta {campo} para {identificador}.")
        categoria = categoria_riesgo(
            puntaje_riesgo(fila.get("probabilidad"), fila.get("impacto"))
        )
        if categoria in {"ALTO", "CRITICO"}:
            supervision = fila.get("punto_supervision")
            if not isinstance(supervision, str) or not supervision.strip():
                raise ValueError(f"{identificador} requiere un punto de supervisión.")
            if fila.get("estado_supervision") != "PROPUESTO_NO_IMPLEMENTADO":
                raise ValueError(
                    "Esta matriz académica no puede declarar supervisiones productivas implementadas."
                )
        else:
            if fila.get("estado_supervision") != "NO_REQUERIDO_POR_UMBRAL":
                raise ValueError(
                    f"{identificador}: categoría MEDIA/BAJA no necesita gate en este ejercicio."
                )
    return ordenar_y_evaluar(riesgos)


def cargar_matriz_booking_core(ruta: Path = ARCHIVO_BOOKING_CORE) -> dict[str, Any]:
    """Lee la matriz del repositorio, sin llamar a servicios externos."""
    contenido = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if contenido.get("proyecto") != "Booking Core AI (agenda de barbería)":
        raise ValueError("El archivo no corresponde al laboratorio Booking Core AI.")
    contenido["riesgos"] = validar_matriz_booking_core(contenido["riesgos"])
    return contenido


def mostrar_riesgos(riesgos: list[dict[str, Any]]) -> None:
    for r in riesgos:
        marca = " [AL LIMITE]" if r["al_limite"] else ""
        print(f"{r['categoria']:8} ({r['puntaje']:2}) - {r['riesgo']}{marca}")


def main() -> int:
    print("=== EJEMPLO OFICIAL SKILLNEST: CINCO RIESGOS ===")
    curso = ordenar_y_evaluar(RIESGOS_CURSO)
    for r in curso:
        print(f"{r['categoria']:8} ({r['puntaje']:2}) - {r['riesgo']}")
    print("\n=== SENSIBILIDAD DEL EJEMPLO OFICIAL ===")
    mostrar_riesgos(curso)
    contraste = puntaje_riesgo(1, 1)
    print(
        "\nContraste 1x1:",
        "AL LIMITE" if esta_en_el_limite(1, 1) else "no al limite",
        "| puntaje", contraste, categoria_riesgo(contraste),
    )

    print("\n=== BOOKING CORE AI: PROPUESTA DE RIESGOS, NO AUDITORIA ===")
    matriz = cargar_matriz_booking_core()
    print("Fuente/estado:", matriz["fuente"])
    mostrar_riesgos(matriz["riesgos"])
    for r in matriz["riesgos"]:
        print(f"  {r['id']}: mitigacion: {r['mitigacion']}")
        if r["al_limite"]:
            print(f"  revisar con otra persona: {r['id']} ({r['categoria']})")
        if r["categoria"] in ("ALTO", "CRITICO"):
            print(
                f"  {r['id']}: supervision {r['estado_supervision']} "
                f"| punto: {r['punto_supervision']}"
            )
    print("\nAVISO: ningun punto de supervision productivo se ha implementado.")
    print("No se consulto Gemini ni se altero la agenda real de Booking Core.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
