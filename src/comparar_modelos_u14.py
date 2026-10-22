r"""U1.4 Bloque 9 - Comparacion reproducible de modelos Gemini.

Ejecutar desde la raiz del repositorio:
    .\venv\Scripts\python.exe -m src.comparar_modelos_u14

Requiere GEMINI_API_KEY en .env. No modifica consumir_gemini.py.
Precios: tarifa Standard de pago por uso, verificada el 2026-10-20.
Fuente: https://ai.google.dev/gemini-api/docs/pricing
"""

import csv
import os
import statistics
import time
from datetime import datetime
from pathlib import Path

from src.consumir_gemini import armar_peticion, enviar_peticion, extraer_texto

MODELOS = {
    "gemini-3.5-flash-lite": {
        "entrada_por_millon": 0.30,
        "salida_por_millon": 2.50,
        "cache_por_millon": 0.03,
    },
    "gemini-3.8-flash": {
        "entrada_por_millon": 0.75,
        "salida_por_millon": 3.75,
        "cache_por_millon": 0.075,
    },
}

INSTRUCCION = (
    "Interpreta la solicitud de reserva de un usuario. Devuelve exclusivamente "
    "un objeto JSON con las claves: intencion, fecha, hora, personas y "
    "requiere_aclaracion. Usa fecha ISO AAAA-MM-DD, hora HH:MM en formato 24 h "
    "y null cuando falte un dato. Intencion: crear_reserva o cancelar_reserva. "
    "Marca requiere_aclaracion como true si falta un dato esencial para "
    "tramitar la solicitud, incluido el identificador al cancelar. "
    "No inventes información ni confirmes disponibilidad.\nSolicitud: "
)

CASOS = [
    (
        "reserva_completa",
        "Quiero reservar para 2 personas el 24 de octubre de 2026 a las 19:30.",
        4,  # Cuatro mediciones idénticas de latencia por modelo.
    ),
    (
        "hora_imprecisa",
        "Necesito reservar para 3 personas el 25 de octubre de 2026 por la tarde.",
        1,
    ),
    (
        "cancelacion_sin_id",
        "Quiero cancelar mi reserva.",
        1,
    ),
]

CAMPOS = [
    "fecha_medicion", "modelo", "caso", "repeticion", "latencia_s",
    "tokens_entrada", "tokens_salida_visible", "tokens_razonamiento",
    "tokens_cache", "costo_estimado_usd", "respuesta",
]


def medir(modelo, tarifas, caso, pregunta, repeticion):
    """Reutiliza las funciones existentes y cambia solo el endpoint del modelo."""
    url_base, headers, body = armar_peticion(INSTRUCCION + pregunta)
    if "/models/" not in url_base:
        raise RuntimeError("No se pudo identificar el endpoint de modelos Gemini.")

    url = url_base.rsplit("/models/", 1)[0] + f"/models/{modelo}:generateContent"
    inicio = time.perf_counter()
    respuesta_json = enviar_peticion(url, headers, body)
    latencia = time.perf_counter() - inicio

    respuesta = extraer_texto(respuesta_json)
    uso = respuesta_json["usageMetadata"]
    entrada = uso["promptTokenCount"]
    salida = uso.get("candidatesTokenCount", 0)
    razonamiento = uso.get("thoughtsTokenCount", 0)
    cache = uso.get("cachedContentTokenCount", 0)

    # La tarifa de salida incluye tokens de razonamiento. Los tokens
    # de entrada servidos desde cache pueden tener un precio distinto.
    costo = (
        (entrada - cache) * tarifas["entrada_por_millon"]
        + cache * tarifas["cache_por_millon"]
        + (salida + razonamiento) * tarifas["salida_por_millon"]
    ) / 1_000_000

    return {
        "fecha_medicion": datetime.now().astimezone().isoformat(timespec="seconds"),
        "modelo": modelo,
        "caso": caso,
        "repeticion": repeticion,
        "latencia_s": round(latencia, 4),
        "tokens_entrada": entrada,
        "tokens_salida_visible": salida,
        "tokens_razonamiento": razonamiento,
        "tokens_cache": cache,
        "costo_estimado_usd": round(costo, 10),
        "respuesta": respuesta.strip(),
    }


def guardar_csv(filas):
    destino = Path("docs") / "mediciones_modelos_u14.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(filas)
    print(f"\nEvidencia guardada en: {destino}")


def main():
    if not os.getenv("GEMINI_API_KEY"):
        print("Falta GEMINI_API_KEY en el archivo .env del proyecto.")
        return

    filas = []
    try:
        for modelo, tarifas in MODELOS.items():
            print(f"\n=== MODELO: {modelo} ===")
            for caso, pregunta, repeticiones in CASOS:
                for numero in range(1, repeticiones + 1):
                    fila = medir(modelo, tarifas, caso, pregunta, numero)
                    filas.append(fila)
                    print(
                        f"{caso} #{numero}: {fila['latencia_s']:.2f}s | "
                        f"USD {fila['costo_estimado_usd']:.8f}"
                    )
                    print("Respuesta:", fila["respuesta"])
                    time.sleep(2)  # Reducir la frecuencia de solicitudes.

            tiempos = [
                f["latencia_s"] for f in filas
                if f["modelo"] == modelo and f["caso"] == "reserva_completa"
            ]
            if len(tiempos) == 4:
                print(f"Latencia promedio ({modelo}): {statistics.mean(tiempos):.2f}s")
    except (RuntimeError, KeyError, ValueError) as error:
        print(f"\nPrueba interrumpida: {error}")
        print("No reintentes inmediatamente si recibiste HTTP 429.")
    finally:
        if filas:
            guardar_csv(filas)
        else:
            print("No se obtuvieron respuestas válidas; no se creó CSV.")


if __name__ == "__main__":
    main()
