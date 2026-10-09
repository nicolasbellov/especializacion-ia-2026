
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def obtener_dato_de_prueba(pregunta):
    api_key = os.getenv("GEMINI_API_KEY")
    modelo = "gemini-3.5-flash"

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{modelo}:generateContent"
    )

    headers = {
        "x-goog-api-key": api_key
    }

    body = {
        "contents": [
            {"parts": [{"text": pregunta}]}
        ]
    }

    respuesta = requests.post(
        url,
        headers=headers,
        json=body,
        timeout=30
    )

    datos = respuesta.json()

    return datos["candidates"][0]["content"]["parts"][0]["text"]


print(
    obtener_dato_de_prueba(
        "Confirma en una frase corta que esta conexión funciona"
    )
)
