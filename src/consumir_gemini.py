
"""Cliente REST de Gemini utilizado durante el Módulo 1.

U1.5: incorpora instrucciones de sistema, esquema de respuesta y validación JSON
sin cambiar el contrato previo (url, headers, body) de armar_peticion().
"""

import json
import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()


def armar_peticion(pregunta, system_instruction=None, response_schema=None):
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta debe ser un texto no vacío")

    if system_instruction is not None and (
        not isinstance(system_instruction, str) or not system_instruction.strip()
    ):
        raise ValueError("La instrucción de sistema debe ser un texto no vacío")

    if response_schema is not None and not isinstance(response_schema, dict):
        raise ValueError("response_schema debe ser un diccionario")

    api_key = os.getenv("GEMINI_API_KEY")
    modelo = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{modelo}:generateContent"
    )
    headers = {"x-goog-api-key": api_key}
    body = {"contents": [{"parts": [{"text": pregunta}]}]}

    if system_instruction is not None:
        body["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }

    return url, headers, body


def enviar_peticion(url, headers, body):
    try:
        respuesta = requests.post(
            url,
            headers=headers,
            json=body,
            timeout=30,
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
        if respuesta.status_code == 429:
            raise RuntimeError(
                "La API devolvió HTTP 429: cuota o límite de solicitudes."
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
            "La respuesta de Gemini no contiene el campo esperado: "
            f"{error.args[0]}."
        ) from error
    except IndexError as error:
        raise RuntimeError(
            "La respuesta de Gemini contiene una lista vacía donde "
            "se esperaba texto generado."
        ) from error


def _validar_tipo(valor, especificacion, campo):
    tipo = especificacion.get("type")
    valido = {
        "STRING": lambda x: isinstance(x, str),
        "NUMBER": lambda x: isinstance(x, (int, float)) and not isinstance(x, bool),
        "INTEGER": lambda x: isinstance(x, int) and not isinstance(x, bool),
        "BOOLEAN": lambda x: isinstance(x, bool),
        "ARRAY": lambda x: isinstance(x, list),
        "OBJECT": lambda x: isinstance(x, dict),
    }

    if tipo not in valido or not valido[tipo](valor):
        raise ValueError(f"Tipo incorrecto en '{campo}': se esperaba {tipo}.")
    if "enum" in especificacion and valor not in especificacion["enum"]:
        raise ValueError(f"Valor no permitido en '{campo}'.")
    if tipo in ("NUMBER", "INTEGER"):
        if "minimum" in especificacion and valor < especificacion["minimum"]:
            raise ValueError(f"Valor inferior al mínimo en '{campo}'.")
        if "maximum" in especificacion and valor > especificacion["maximum"]:
            raise ValueError(f"Valor superior al máximo en '{campo}'.")
    if tipo == "ARRAY" and "items" in especificacion:
        for i, elemento in enumerate(valor):
            _validar_tipo(elemento, especificacion["items"], f"{campo}[{i}]")


def parsear_respuesta_json(texto, response_schema=None):
    """Limpia bloques Markdown, decodifica JSON y verifica el esquema básico.

    Acepta un esquema diferente para cada prompt; no presupone claves fijas.
    """
    if not isinstance(texto, str):
        raise ValueError("La respuesta del modelo debe ser texto.")

    texto_limpio = texto.strip()
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio, flags=re.I)
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio)

    try:
        datos = json.loads(texto_limpio)
    except json.JSONDecodeError as error:
        raise ValueError("La respuesta del modelo no es JSON válido.") from error

    if not isinstance(datos, dict):
        raise ValueError("Se esperaba un objeto JSON, no una lista u otro valor.")

    if response_schema is not None:
        obligatorias = response_schema.get("required", [])
        faltantes = [clave for clave in obligatorias if clave not in datos]

        if faltantes:
            raise ValueError(
                f"Faltan claves obligatorias: {', '.join(faltantes)}."
            )

        for clave, especificacion in response_schema.get("properties", {}).items():
            if clave in datos:
                _validar_tipo(datos[clave], especificacion, clave)

    return datos


def calcular_costo(datos, precio_entrada, precio_salida):
    uso = datos["usageMetadata"]
    tokens_entrada = uso["promptTokenCount"]
    tokens_salida = uso["candidatesTokenCount"]

    costo_entrada = tokens_entrada * precio_entrada
    costo_salida = tokens_salida * precio_salida

    return costo_entrada + costo_salida


def obtener_dato_de_prueba(pregunta):
    url, headers, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, headers, body)
    return extraer_texto(datos)


if __name__ == "__main__":
    import sys

    try:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()

        if not api_key or api_key == "tu_llave_aqui":
            raise RuntimeError(
                "Configura GEMINI_API_KEY en el archivo .env."
            )

        pregunta = (
            "Confirma en una frase corta que "
            "esta conexión funciona."
        )

        resultado = obtener_dato_de_prueba(pregunta)
        print("Resultado:", resultado)

    except (ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
