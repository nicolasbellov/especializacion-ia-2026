import os
from pathlib import Path

import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(
    dotenv_path=Path(__file__).with_name(".env"),
    override=True
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not GEMINI_API_KEY:
    raise RuntimeError("Falta configurar GEMINI_API_KEY")

URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    f"models/{GEMINI_MODEL}:generateContent"
)

headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": GEMINI_API_KEY,
}


def enviar_peticion(cuerpo):
    try:
        respuesta = requests.post(
            URL,
            json=cuerpo,
            headers=headers,
            timeout=10
        )

    except (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError
    ) as error:
        raise TimeoutError(
            "No se pudo contactar al proveedor."
        ) from error

    if respuesta.status_code in (401, 403):
        raise ValueError(
            "Credencial invalida o sin permiso."
        )

    # Gemini puede responder 400 API_KEY_INVALID
    if respuesta.status_code == 400:
        try:
            detalle = respuesta.json().get("error", {})
            razones = detalle.get("details", [])
            clave_invalida = any(
                isinstance(item, dict)
                and item.get("reason") == "API_KEY_INVALID"
                for item in razones
            )
            mensaje = str(detalle.get("message", "")).lower()

            if clave_invalida or "api key not valid" in mensaje:
                raise ValueError(
                    "Credencial invalida. Revisa GEMINI_API_KEY."
                )
        except requests.exceptions.JSONDecodeError:
            pass

    if respuesta.status_code == 429:
        raise TimeoutError(
            "Rate limit excedido. Reintentar mas tarde."
        )

    if respuesta.status_code >= 500:
        raise TimeoutError(
            "Error temporal del proveedor."
        )

    respuesta.raise_for_status()
    return respuesta.json()


if __name__ == "__main__":
    cuerpo = {
        "contents": [
            {
                "parts": [
                    {"text": "Di hola en una frase."}
                ]
            }
        ]
    }

    try:
        resultado = enviar_peticion(cuerpo)
        print("Respuesta:", resultado)

    except (
        ValueError,
        TimeoutError,
        requests.exceptions.RequestException
    ) as error:
        print(f"{type(error).__name__}: {error}")
