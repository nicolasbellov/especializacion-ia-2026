"""Ensayo controlado del Bloque 13 (Skillnest).

Hace como maximo 10 operaciones reales con el cliente existente.
Observa los codigos HTTP *reales*, incluido 429, sin alterar cliente_api.py.
Detiene el ensayo al primer 429 observado, incluso si el reintento se recupera.

ATENCION: ejecutar este archivo hace llamadas reales y puede consumir cuota.
Los precios mostrados por cliente.py son REFERENCIALES, no facturacion real.
"""

from collections import Counter
from unittest.mock import patch

import requests

import cliente
import cliente_api
import cliente_reintento


MAX_OPERACIONES = 10


def ejecutar_ensayo(
    max_operaciones: int = MAX_OPERACIONES, *, simulacion: bool = False
) -> dict:
    if type(max_operaciones) is not int or not 1 <= max_operaciones <= MAX_OPERACIONES:
        raise ValueError("max_operaciones debe estar entre 1 y 10")

    # El contador es local al proceso y a este ensayo.
    cliente.costo_total_sesion = 0.0
    codigos_http = Counter()
    llamadas_http = 0
    operaciones_ok = 0
    operaciones_fallidas = 0
    primera_operacion_429 = None
    primera_llamada_429 = None
    esperas = []

    # Guardar las funciones originales antes de instrumentarlas.
    post_original = cliente_api.requests.post
    dormir_original = cliente_reintento.time.sleep
    operacion_actual = -1

    def observar_http(*args, **kwargs):
        nonlocal llamadas_http, primera_operacion_429, primera_llamada_429
        llamadas_http += 1
        try:
            respuesta = post_original(*args, **kwargs)
        except requests.exceptions.RequestException as error:
            codigos_http["error_red"] += 1
            print(f"HTTP #{llamadas_http}: error de red ({type(error).__name__})")
            raise

        codigo = respuesta.status_code
        codigos_http[codigo] += 1
        print(f"HTTP #{llamadas_http}: {codigo}")

        if codigo == 429 and primera_llamada_429 is None:
            primera_llamada_429 = llamadas_http
            primera_operacion_429 = operacion_actual
            print(
                f"HTTP 429 {'SIMULADO' if simulacion else 'REAL'} OBSERVADO "
                f"en operacion {operacion_actual}, llamada HTTP #{llamadas_http}."
            )
        return respuesta

    def observar_espera(segundos):
        esperas.append(round(segundos, 3))
        return dormir_original(segundos)

    print(
        f"Inicio del ensayo: maximo {max_operaciones} operaciones, "
        "hasta 3 intentos HTTP cada una."
    )
    print(f"Tipo de ensayo: {'SIMULADO' if simulacion else 'REAL CON GEMINI'}")
    print("No se aumentara automaticamente el limite si no aparece HTTP 429.")

    # Solo el ensayo usa estos parches: la logica de produccion no cambia.
    with (
        patch("cliente_api.requests.post", side_effect=observar_http),
        patch("cliente_reintento.time.sleep", side_effect=observar_espera),
    ):
        for operacion_actual in range(max_operaciones):
            print(f"\n--- Operacion {operacion_actual} ---")
            try:
                texto = cliente.consultar_modelo(
                    f"Responde solamente OK. Prueba {operacion_actual}."
                )
                operaciones_ok += 1
                print(f"Respuesta {operacion_actual}: {texto[:60]}")
            except (ValueError, requests.exceptions.RequestException) as error:
                operaciones_fallidas += 1
                print(
                    "Ensayo detenido por error no reintentable: "
                    f"{type(error).__name__}: {error}"
                )
                break
            except RuntimeError as error:
                operaciones_fallidas += 1
                print(f"Operacion fallida tras reintentos: {error}")
                break

            # No continuar presionando la cuota tras observar un 429.
            if primera_llamada_429 is not None:
                print("Se detecto HTTP 429; no se enviaran mas operaciones.")
                break

            # Detener tambien si el proveedor ha respondido 5xx.
            if any(isinstance(c, int) and c >= 500 for c in codigos_http):
                print("Se observo error 5xx; ensayo detenido por precaucion.")
                break

    hubo_429 = primera_llamada_429 is not None
    resumen = {
        "operaciones_maximas": max_operaciones,
        "operaciones_exitosas": operaciones_ok,
        "operaciones_fallidas": operaciones_fallidas,
        "llamadas_http": llamadas_http,
        "codigos_http": dict(codigos_http),
        "primer_429_operacion": primera_operacion_429,
        "primer_429_llamada_http": primera_llamada_429,
        "esperas_segundos": esperas,
        "costo_referencial_usd": round(cliente.costo_total_sesion, 8),
        "tipo_ensayo": "simulado" if simulacion else "real_gemini",
        "http_429_observado": hubo_429,
    }

    print("\n===== RESUMEN DEL ENSAYO B13 =====")
    for clave, valor in resumen.items():
        print(f"{clave}: {valor}")
    if not hubo_429:
        if simulacion:
            print("RESULTADO: ningun HTTP 429 en las respuestas simuladas.")
        else:
            print(
                "RESULTADO: ningun HTTP 429 real en el ensayo. "
                "No se demostro el limite del proveedor."
            )
    else:
        print(
            "RESULTADO: HTTP 429 simulado verificado."
            if simulacion
            else "RESULTADO: HTTP 429 real confirmado."
        )
    print("Costo USD: solo calculo didactico del curso, no factura del proveedor.")
    return resumen


if __name__ == "__main__":
    ejecutar_ensayo()
