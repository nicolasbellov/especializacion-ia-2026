"""U2.3 - Bloque 20: recuperacion de fallos por paso.

Demostracion 100 % offline. No configura Gemini, no lee .env y no consume API.
Reutiliza el enrutador del Bloque 19 sin modificar su implementacion.

Desde la raiz del repositorio:
    python -m src.bloque20_01_fallbacks
"""

import logging

from langchain_core.runnables import RunnableLambda

from src.bloque19_01_enrutamiento import construir_cadena_con_enrutamiento


logger = logging.getLogger(__name__)

RESPUESTA_GENERICA = (
    "No fue posible responder esta consulta en el ejercicio simulado. "
    "Intenta nuevamente mas tarde."
)
RESPUESTA_ERROR_GLOBAL = (
    "No pudimos procesar tu mensaje en este momento. "
    "Intenta nuevamente mas tarde."
)


def fallar_a_proposito(_entrada):
    """Simula una excepcion sin conectarse a ningun servicio."""
    raise ConnectionError("Error de red simulado")


def construir_fallback_generico():
    """Alternativa final local: no llama a un modelo ni promete contacto humano."""
    return RunnableLambda(lambda _entrada: RESPUESTA_GENERICA)


def proteger_cadena_queja(
    cadena_queja,
    *,
    cadena_secundaria=None,
    respuesta_generica=None,
):
    """Prueba alternativas en orden y termina en una respuesta local.

    Una cadena secundaria es opcional. En un sistema real podria usar otro
    proveedor/modelo; en este ejercicio se simula siempre sin llamadas de red.
    """
    alternativas = []
    if cadena_secundaria is not None:
        alternativas.append(cadena_secundaria)
    if respuesta_generica is None:
        respuesta_generica = construir_fallback_generico()
    alternativas.append(respuesta_generica)
    return cadena_queja.with_fallbacks(alternativas)


def construir_flujo_con_respaldo(
    *,
    paso_clasificacion,
    cadena_queja,
    cadena_sugerencia,
    cadena_pregunta,
    cadena_queja_secundaria=None,
    respuesta_generica=None,
):
    """Agrega respaldo a la ruta de quejas; conserva las otras dos rutas."""
    cadena_queja_segura = proteger_cadena_queja(
        cadena_queja,
        cadena_secundaria=cadena_queja_secundaria,
        respuesta_generica=respuesta_generica,
    )
    return construir_cadena_con_enrutamiento(
        paso_clasificacion=paso_clasificacion,
        cadena_queja=cadena_queja_segura,
        cadena_sugerencia=cadena_sugerencia,
        cadena_pregunta=cadena_pregunta,
    )


def procesar_mensaje_seguro(cadena, mensaje: str) -> str:
    """Red de seguridad global si la clasificacion u otra ruta falla.

    Se registra el tipo de excepcion, nunca el mensaje original ni tokens.
    Durante depuracion local es preferible inspeccionar el fallo original.
    """
    try:
        return cadena.invoke({"mensaje": mensaje})
    except Exception as error:
        logger.error("Fallo no recuperado en la cadena: %s", type(error).__name__)
        return RESPUESTA_ERROR_GLOBAL


def main() -> None:
    """Muestra fallback simple, fallback en orden y captura global sin API."""
    logging.basicConfig(level=logging.INFO)

    rota = RunnableLambda(fallar_a_proposito)
    generica = construir_fallback_generico()
    entrada = {"mensaje": "El tablero ficticio no responde."}

    print("Bloque 20: demostracion offline de tolerancia a fallos")
    print("\n1. Falla la cadena principal; responde el fallback:")
    print(rota.with_fallbacks([generica]).invoke(entrada))

    print("\n2. Fallan la principal y la secundaria; responde el fallback final:")
    print(rota.with_fallbacks([RunnableLambda(fallar_a_proposito), generica]).invoke(entrada))

    print("\n3. El clasificador falla; responde la proteccion global:")
    flujo = construir_flujo_con_respaldo(
        paso_clasificacion=RunnableLambda(fallar_a_proposito),
        cadena_queja=rota,
        cadena_sugerencia=RunnableLambda(lambda _x: "Ruta sugerencia"),
        cadena_pregunta=RunnableLambda(lambda _x: "Ruta pregunta"),
    )
    print(procesar_mensaje_seguro(flujo, entrada["mensaje"]))


if __name__ == "__main__":
    main()
