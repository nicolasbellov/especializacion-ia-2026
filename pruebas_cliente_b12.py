from types import SimpleNamespace
from unittest.mock import patch

from cliente import consultar_modelo

respuesta_simulada = {
    "candidates": [
        {
            "content": {
                "parts": [
                    {"text": "Santiago es la capital de Chile."}
                ]
            }
        }
    ]
}


def prueba_normal():
    with patch(
        "cliente.enviar_peticion",
        return_value=respuesta_simulada
    ) as mock:
        resultado = consultar_modelo(
            "Cual es la capital de Chile?"
        )

    assert resultado == "Santiago es la capital de Chile."
    assert mock.call_count == 1
    print("OK: consulta normal")


def prueba_autenticacion():
    respuesta_401 = SimpleNamespace(status_code=401)

    with patch(
        "cliente_api.requests.post",
        return_value=respuesta_401
    ) as mock:
        try:
            consultar_modelo("Hola")
        except ValueError:
            pass
        else:
            raise AssertionError("Se esperaba ValueError")

    assert mock.call_count == 1
    print("OK: autenticacion invalida sin reintentos")


def prueba_recuperacion():
    efectos = [
        TimeoutError("Error temporal 1"),
        TimeoutError("Error temporal 2"),
        respuesta_simulada
    ]

    with patch(
        "cliente.enviar_peticion",
        side_effect=efectos
    ) as mock:
        with patch("cliente_reintento.time.sleep") as sleep:
            resultado = consultar_modelo("Hola")

    assert resultado == "Santiago es la capital de Chile."
    assert mock.call_count == 3
    assert sleep.call_count == 2
    print("OK: recuperacion en tercer intento")


def prueba_agotamiento():
    with patch(
        "cliente.enviar_peticion",
        side_effect=TimeoutError("Error persistente")
    ) as mock:
        with patch("cliente_reintento.time.sleep") as sleep:
            try:
                consultar_modelo("Hola")
            except RuntimeError as error:
                assert "varios intentos" in str(error)
            else:
                raise AssertionError("Se esperaba RuntimeError")

    assert mock.call_count == 3
    assert sleep.call_count == 2
    print("OK: reintentos agotados")


if __name__ == "__main__":
    prueba_normal()
    prueba_autenticacion()
    prueba_recuperacion()
    prueba_agotamiento()

    print("\nTODAS LAS PRUEBAS SUPERADAS")
