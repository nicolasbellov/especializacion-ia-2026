
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def armar_peticion(pregunta):
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta debe ser un texto no vacío")

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

    return url, headers, body



def enviar_peticion(url, headers, body):
    try:
        respuesta = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=30
        )

    except requests.exceptions.Timeout as error:
        raise RuntimeError(
            "El servicio tardó demasiado en responder."
        ) from error

    except requests.exceptions.ConnectionError as error:
            raise RuntimeError(
                "No se pudo conectar con el servicio."
            ) from error

    try:
        respuesta.raise_for_status()

    except requests.exceptions.HTTPError as error:
        if respuesta.status_code in (401, 403):
            raise RuntimeError(
                "Error de autenticación. Revisa GEMINI_API_KEY."
            ) from error

        if respuesta.status_code == 400:
            raise RuntimeError(
                "El servicio rechazó la solicitud (HTTP 400). "
                "Revisa la credencial y los datos enviados."
            ) from error

        raise RuntimeError(
            f"El servicio devolvió HTTP {respuesta.status_code}."
        ) from error

    try:
        return respuesta.json()

    except requests.exceptions.JSONDecodeError as error:
        raise RuntimeError(
            "La respuesta del servicio no contiene JSON válido."
        ) from error




def extraer_texto(datos):
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]

    except KeyError as error:
        raise RuntimeError(
            f"La respuesta de Gemini no contiene el campo esperado: {error.args[0]}."
        ) from error

    except IndexError as error:
        raise RuntimeError(
            "La respuesta de Gemini contiene una lista vacía donde se esperaba texto generado."
        ) from error



def obtener_dato_de_prueba(pregunta):
    url, headers, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, headers, body)
    return extraer_texto(datos)


if __name__ == "__main__":
    preguntas = [
        "",
        "Confirma en una frase corta que esta conexión funciona"
    ]

    for pregunta in preguntas:
        try:
            resultado = obtener_dato_de_prueba(pregunta)
            print("Resultado:", resultado)

        except (ValueError, RuntimeError) as error:
            print("No se pudo completar la operación:", error)
