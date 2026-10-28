from cliente_api import enviar_peticion
from cliente_reintento import con_reintento


def armar_peticion(
    pregunta: str,
    system_instruction: str = ""
) -> dict:

    cuerpo = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": pregunta}]
            }
        ]
    }

    if system_instruction:
        cuerpo["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    return cuerpo


def extraer_texto(respuesta: dict) -> str:

    try:
        partes = respuesta["candidates"][0]["content"]["parts"]

        texto = "".join(
            parte.get("text", "")
            for parte in partes
            if isinstance(parte, dict)
        ).strip()

        if not texto:
            raise KeyError("Sin contenido de texto")

        return texto

    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError(
            "La API no devolvio una respuesta de texto valida."
        ) from error


def consultar_modelo(
    pregunta: str,
    system_instruction: str = ""
) -> str:

    cuerpo = armar_peticion(
        pregunta,
        system_instruction
    )

    try:
        respuesta = con_reintento(
            lambda: enviar_peticion(cuerpo)
        )

    except TimeoutError as error:
        raise RuntimeError(
            "El servicio no respondio tras varios intentos. "
            "Intenta mas tarde."
        ) from error

    return extraer_texto(respuesta)
