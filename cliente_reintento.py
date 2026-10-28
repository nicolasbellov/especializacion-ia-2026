import time
import random
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
    espera_base: float = 2,
    espera_maxima: float = 30,
) -> Any:
    if intentos < 1:
        raise ValueError("intentos debe ser mayor que cero")
    if espera_base < 0 or espera_maxima < 0:
        raise ValueError("Las esperas no pueden ser negativas")

    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise

            espera = min(
                espera_base * (2 ** (intento - 1)),
                espera_maxima,
            )
            espera_jitter = min(
                espera + random.uniform(0, espera * 0.1),
                espera_maxima,
            )
            print(
                f"Intento {intento} de {intentos} fallo. "
                f"Reintentando en {espera_jitter:.1f}s..."
            )
            time.sleep(espera_jitter)


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
