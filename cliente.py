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


# Tarifa didactica de Skillnest; NO representa facturacion real de Gemini.
COSTO_POR_1000_TOKENS = 0.002
costo_total_sesion = 0.0


def registrar_costo(respuesta: dict) -> float | None:
    global costo_total_sesion

    uso = respuesta.get("usageMetadata", {})
    tokens = uso.get("totalTokenCount") if isinstance(uso, dict) else None

    if type(tokens) is not int or tokens < 0:
        print("Operacion sin uso de tokens: costo no estimable.")
        return None

    costo = tokens / 1000 * COSTO_POR_1000_TOKENS
    costo_total_sesion += costo
    print(
        f"Operacion: {tokens} tokens | "
        f"USD referencial: {costo:.6f} | "
        f"Acumulado: {costo_total_sesion:.6f}"
    )
    return costo


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

    registrar_costo(respuesta)
    return extraer_texto(respuesta)
