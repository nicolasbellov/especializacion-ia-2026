"""U2.2 / Bloque 15: pipeline de texto y comparaciones con el cliente real.

Ejecutar desde la raiz del repositorio:
    python pipeline_texto.py

Las funciones de procesamiento no dependen de la red. Solo main()
importa consultar_modelo del cliente construido en U2.1.
"""

import json
import re
from pathlib import Path


def limpiar_texto(texto: str) -> str:
    """Normaliza mayusculas, puntuacion y espacios (ejercicio Skillnest)."""
    if not isinstance(texto, str):
        tipo = type(texto).__name__
        raise TypeError(f"limpiar_texto espera str, no {tipo}")

    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)
    return re.sub(r"\s+", " ", texto).strip()


def tokenizar(texto_limpio: str) -> list[str]:
    """Separa en palabras un texto ya normalizado."""
    return texto_limpio.split()


def procesar_texto(texto: str) -> list[str]:
    """Centraliza limpieza y tokenizacion."""
    return tokenizar(limpiar_texto(texto))


def coincidencia_palabras(
    referencia: str, respuesta: str, *, normalizar: bool
) -> float:
    """Proporcion de palabras UNICAS de referencia presentes en respuesta.

    No mide calidad semantica, orden ni repeticiones. La referencia vacia
    devuelve 0.0, evitando ZeroDivisionError.
    """
    if normalizar:
        tokens_ref = procesar_texto(referencia)
        tokens_resp = procesar_texto(respuesta)
    else:
        tokens_ref = referencia.split()
        tokens_resp = respuesta.split()

    palabras_ref = set(tokens_ref)
    if not palabras_ref:
        return 0.0
    return len(palabras_ref & set(tokens_resp)) / len(palabras_ref)


def main() -> None:
    # Importacion diferida: los tests de limpieza no requieren credenciales.
    from cliente import consultar_modelo

    # Revisar las referencias personales antes de entregar la actividad.
    casos = [
        {
            "consulta": "¿Qué es Python? Responde en una sola oración breve.",
            "referencia": "Python es un lenguaje de programación.",
        },
        {
            "consulta": "¿Qué es una API? Responde en una sola oración breve.",
            "referencia": "Una API permite la comunicación entre aplicaciones.",
        },
        {
            "consulta": "¿Para qué sirve Git? Responde en una sola oración breve.",
            "referencia": "Git permite controlar versiones del código.",
        },
    ]

    resultados = []
    ruta_evidencia = Path(__file__).with_name("resultados_b15.json")

    for indice, caso in enumerate(casos, start=1):
        # Debe realizarse en el equipo con GEMINI_API_KEY configurada.
        respuesta = consultar_modelo(caso["consulta"])
        if not isinstance(respuesta, str):
            raise TypeError(
                f"El caso {indice} esperaba str de consultar_modelo, "
                f"recibio {type(respuesta).__name__}"
            )

        pct_crudo = coincidencia_palabras(
            caso["referencia"], respuesta, normalizar=False
        )
        pct_procesado = coincidencia_palabras(
            caso["referencia"], respuesta, normalizar=True
        )

        resultado = {
            "caso": indice,
            "consulta": caso["consulta"],
            "referencia": caso["referencia"],
            "respuesta_real": respuesta,
            "coincidencia_cruda": pct_crudo,
            "coincidencia_procesada": pct_procesado,
        }
        resultados.append(resultado)

        print(f"\n[Caso {indice}] Consulta: {caso['consulta']}")
        print(f"[Caso {indice}] Respuesta real: {respuesta}")
        print(f"[Caso {indice}] Coincidencia texto crudo: {pct_crudo:.1%}")
        print(f"[Caso {indice}] Coincidencia texto procesado: {pct_procesado:.1%}")

        # Guardado incremental si una llamada posterior falla.
        ruta_evidencia.write_text(
            json.dumps(resultados, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(f"\nEvidencia guardada en: {ruta_evidencia}")


if __name__ == "__main__":
    main()
