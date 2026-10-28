import time
from typing import Callable, Any

# Mock: simula un proveedor que falla dos veces
intentos_previos = 0


def enviar_peticion(cuerpo: dict) -> dict:
    global intentos_previos

    intentos_previos += 1

    if intentos_previos < 3:
        raise TimeoutError(
            "Limite de peticiones excedido."
        )

    return {
        "contenido": "Respuesta simulada exitosa",
        "intento": intentos_previos
    }


def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_segundos: int = 2,
) -> Any:

    for intento in range(1, intentos + 1):
        try:
            return funcion()

        except TimeoutError:
            if intento == intentos:
                raise

            print(
                f"Intento {intento} de {intentos} "
                "fallo por limite de uso. "
                "Reintentando..."
            )

            time.sleep(espera_segundos)


if __name__ == "__main__":

    cuerpo = {
        "contents": [
            {
                "parts": [
                    {"text": "Hola"}
                ]
            }
        ]
    }

    respuesta = con_reintento(
        lambda: enviar_peticion(cuerpo)
    )

    print(respuesta)
