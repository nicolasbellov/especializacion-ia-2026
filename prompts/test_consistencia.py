"""U1.5 · Prueba REAL de consistencia contra Gemini REST.

Ejecutar desde la raíz del repositorio:
    python -m prompts.test_consistencia

Requiere .env con GEMINI_API_KEY; no registrar claves en el repositorio.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from prompts.banco import BANCO_DE_PROMPTS
from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
)

DESTINO = Path(__file__).parent / "registro_resultados.json"
INTENTOS = 3
SEGUNDOS_ENTRE_PETICIONES = 2


def validar_contenido(datos, valores_esperados):
    """Control semántico adicional, separado del éxito estructural del curso."""
    diferencias = []
    for clave, esperado in valores_esperados.items():
        actual = datos.get(clave)
        if isinstance(esperado, list) and isinstance(actual, list):
            coincide = sorted(actual) == sorted(esperado)
        else:
            coincide = actual == esperado
        if not coincide:
            diferencias.append(clave)
    return diferencias


def ejecutar_pruebas():
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError(
            "Falta GEMINI_API_KEY en .env. No se ejecutaron llamadas a la API."
        )

    registro = {
        "fecha_ejecucion": datetime.now().astimezone().isoformat(timespec="seconds"),
        "modelo": os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        "repeticiones_por_prompt": INTENTOS,
        "prompts": {},
    }

    for indice, prompt in enumerate(BANCO_DE_PROMPTS):
        exitos_estructura = 0
        exitos_contenido = 0
        fallos = []
        for numero in range(1, INTENTOS + 1):
            try:
                url, headers, body = armar_peticion(
                    prompt["ejemplo_usuario"],
                    prompt["system_instruction"],
                    prompt.get("response_schema"),
                )
                respuesta = enviar_peticion(url, headers, body)
                texto = extraer_texto(respuesta)
                datos = parsear_respuesta_json(
                    texto, prompt.get("response_schema")
                )
                exitos_estructura += 1
                diferencias = validar_contenido(
                    datos, prompt.get("resultado_esperado", {})
                )
                if not diferencias:
                    exitos_contenido += 1
                else:
                    fallos.append({
                        "intento": numero,
                        "tipo": "contenido_no_esperado",
                        "detalle": "Campos con discrepancia: " + ", ".join(diferencias),
                    })
            except (ValueError, RuntimeError) as error:
                fallos.append({
                    "intento": numero,
                    "tipo": (
                        "api_cuota_429" if "HTTP 429" in str(error)
                        else "api_http" if isinstance(error, RuntimeError)
                        else "estructura_json_invalida"
                    ),
                    "detalle": str(error),
                })
                print(f"  {prompt['nombre']} · intento {numero}: {error}")

            if not (indice == len(BANCO_DE_PROMPTS) - 1 and numero == INTENTOS):
                time.sleep(SEGUNDOS_ENTRE_PETICIONES)

        registro["prompts"][prompt["nombre"]] = {
            "exitos_estructura": exitos_estructura,
            "exitos_contenido": exitos_contenido,
            "intentos": INTENTOS,
            "fallos": fallos,
        }
        print(
            f"{prompt['nombre']}: {exitos_estructura}/{INTENTOS} JSON estructuralmente "
            f"válidos; {exitos_contenido}/{INTENTOS} con contenido esperado"
        )

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    with DESTINO.open("w", encoding="utf-8") as archivo:
        json.dump(registro, archivo, indent=2, ensure_ascii=False)
    print(f"Resultados guardados en: {DESTINO}")
    return registro


if __name__ == "__main__":
    ejecutar_pruebas()
