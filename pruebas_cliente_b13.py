from unittest.mock import patch
import cliente
from cliente_reintento import con_reintento


def respuesta(tokens):
    return {
        "candidates": [{"content": {"parts": [{"text": "Santiago"}]}}],
        "usageMetadata": {"totalTokenCount": tokens},
    }


def prueba_backoff():
    contador = 0

    def tarea():
        nonlocal contador
        contador += 1
        if contador < 3:
            raise TimeoutError("Error temporal")
        return "OK"

    with patch("cliente_reintento.random.uniform", return_value=0):
        with patch("cliente_reintento.time.sleep") as dormir:
            assert con_reintento(tarea) == "OK"
    assert contador == 3
    assert [c.args[0] for c in dormir.call_args_list] == [2, 4]
    print("OK: backoff 2s, 4s")


def prueba_jitter_y_tope():
    contador = 0

    def tarea():
        nonlocal contador
        contador += 1
        if contador < 3:
            raise TimeoutError("Error temporal")
        return "OK"

    with patch("cliente_reintento.random.uniform", side_effect=[0.2, 0.3]):
        with patch("cliente_reintento.time.sleep") as dormir:
            assert con_reintento(tarea, espera_maxima=3) == "OK"
    valores = [c.args[0] for c in dormir.call_args_list]
    assert valores == [2.2, 3.0], valores
    print("OK: jitter y tope de 3 segundos")


def prueba_autenticacion():
    contador = 0

    def tarea():
        nonlocal contador
        contador += 1
        raise ValueError("Clave invalida")

    with patch("cliente_reintento.time.sleep") as dormir:
        try:
            con_reintento(tarea)
        except ValueError:
            pass
        else:
            raise AssertionError("No se propago ValueError")
    assert contador == 1
    dormir.assert_not_called()
    print("OK: ValueError no se reintenta")


def prueba_costos():
    cliente.costo_total_sesion = 0.0
    try:
        with patch("cliente.enviar_peticion", side_effect=[respuesta(42), respuesta(57)]) as enviar:
            assert cliente.consultar_modelo("Pregunta 1") == "Santiago"
            assert cliente.consultar_modelo("Pregunta 2") == "Santiago"
        assert enviar.call_count == 2
        assert abs(cliente.costo_total_sesion - 0.000198) < 1e-12
        print("OK: costo individual y acumulado")
    finally:
        cliente.costo_total_sesion = 0.0


def prueba_metadata_ausente():
    assert cliente.registrar_costo({}) is None
    assert cliente.costo_total_sesion == 0.0
    print("OK: metadata ausente no cuenta como cero USD")


if __name__ == "__main__":
    prueba_backoff()
    prueba_jitter_y_tope()
    prueba_autenticacion()
    prueba_costos()
    prueba_metadata_ausente()
    print("\nTODAS LAS PRUEBAS B13 SUPERADAS")
