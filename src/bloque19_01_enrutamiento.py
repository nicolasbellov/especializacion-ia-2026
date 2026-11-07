"""U2.3 - Bloque 19 - Leccion 20345: enrutamiento condicional.

Ejemplos ficticios de soporte para TrakCare Analytics: pregunta, queja
o sugerencia. No consulta sistemas ni datos reales.

Desde la raiz del repositorio (con .venv activo):
    python -m src.bloque19_01_enrutamiento
    python -m src.bloque19_01_enrutamiento --ejemplo pregunta
    python -m src.bloque19_01_enrutamiento --ejemplo sugerencia

Cada ejecucion hace DOS llamadas reales a Gemini y puede consumir cuota:
una para clasificar y otra para la ruta seleccionada.
"""

import argparse
import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnablePassthrough,
)
from langchain_google_genai import ChatGoogleGenerativeAI


EJEMPLOS_FICTICIOS = {
    "pregunta": (
        "En un tablero simulado de TrakCare Analytics, ¿qué verificaciones "
        "de solo lectura ayudan a comparar la cantidad de atenciones "
        "de urgencias del tablero con una extracción de origen?"
    ),
    "queja": (
        "Estoy molesto porque en nuestro ejercicio ficticio el tablero "
        "de urgencias muestra 36 atenciones, pero la extracción simulada "
        "muestra 42. Esta discrepancia está impidiendo validar el "
        "indicador y necesito que se reconozca e investigue el problema."
    ),
    "sugerencia": (
        "Sería útil agregar al tablero ficticio una alerta que señale "
        "cuándo la última construcción del cubo analítico no se completó."
    ),
}


def normalizar_categoria(texto: str) -> str:
    """Adapta el texto del LLM para comparar las rutas.

    Extension al curso: tambien elimina puntuacion final simple.
    Una categoria desconocida continua a la ruta por defecto 'pregunta',
    igual que en el ejemplo de Skillnest.
    """
    return texto.strip().lower().strip(" .!?¡¿:;\n\t")


def _mostrar_categoria(datos: dict) -> dict:
    """Diagnostico optativo: registra solo la categoria, no el mensaje."""
    categoria = datos["categoria"]
    print(f"Categoria detectada: {categoria!r}")
    if categoria not in {"pregunta", "queja", "sugerencia"}:
        print("Categoria no reconocida: se usara la ruta por defecto (pregunta).")
    return datos


def construir_paso_clasificacion(modelo):
    """Compone el clasificador inyectable; no ejecuta llamadas al modelo."""
    plantilla_clasificacion = PromptTemplate.from_template(
        "Clasifica la INTENCION principal del siguiente mensaje de soporte "
        "de Analytics. Selecciona EXACTAMENTE una categoria:\n"
        "- queja: reporta un fallo, discrepancia, incumplimiento o "
        "insatisfaccion actual, aunque tambien pida ayuda.\n"
        "- sugerencia: propone una mejora futura sin reportar un fallo.\n"
        "- pregunta: solicita informacion o explicaciones sin reportar "
        "un problema actual.\n"
        "Prioridad: si describe un problema presente, clasifica como queja; "
        "si propone una mejora, como sugerencia; en los demas casos, pregunta. "
        "Responde solo una palabra en minusculas: pregunta, queja o "
        "sugerencia.\n\nMensaje:\n{mensaje}"
    )

    return (
        plantilla_clasificacion
        | modelo
        | StrOutputParser()
        | normalizar_categoria
    )


def construir_cadena_con_enrutamiento(
    paso_clasificacion,
    cadena_queja=None,
    cadena_sugerencia=None,
    cadena_pregunta=None,
    *,
    diagnostico: bool = False,
):
    """Construye rutas inyectables para pruebas offline y su uso real."""
    # Los defaults se usan solo si esa ruta resulta seleccionada.
    if cadena_queja is None:
        cadena_queja = RunnablePassthrough()
    if cadena_sugerencia is None:
        cadena_sugerencia = RunnablePassthrough()
    if cadena_pregunta is None:
        cadena_pregunta = RunnablePassthrough()

    bifurcacion = RunnableBranch(
        (lambda datos: datos["categoria"] == "queja", cadena_queja),
        (lambda datos: datos["categoria"] == "sugerencia", cadena_sugerencia),
        cadena_pregunta,  # Ruta por defecto.
    )

    entrada_clasificada = RunnablePassthrough.assign(
        categoria=paso_clasificacion
    )
    if diagnostico:
        entrada_clasificada = entrada_clasificada | RunnableLambda(
            _mostrar_categoria
        )

    return entrada_clasificada | bifurcacion


def construir_cadena(modelo, *, diagnostico: bool = False):
    """Conserva la interfaz del Bloque 19 con tres rutas y un solo modelo."""
    paso_clasificacion = construir_paso_clasificacion(modelo)

    cadena_pregunta = (
        PromptTemplate.from_template(
            "Responde la siguiente pregunta tecnica sobre Analytics con "
            "precision. Propone solo verificaciones, sin afirmar que "
            "accediste a sistemas o ejecutaste consultas.\n\n{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )

    cadena_queja = (
        PromptTemplate.from_template(
            "Responde a la siguiente queja sobre un escenario ficticio "
            "de Analytics con empatia y claridad. Reconoce el problema "
            "antes de proponer verificaciones de solo lectura. "
            "No atribuyas una causa raiz ni prometas una solucion "
            "no confirmada.\n\n{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )

    cadena_sugerencia = (
        PromptTemplate.from_template(
            "Agradece esta sugerencia de mejora para un tablero ficticio "
            "de Analytics. Explica como podria evaluarse su factibilidad "
            "sin asegurar que se implementara.\n\n{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )

    return construir_cadena_con_enrutamiento(
        paso_clasificacion=paso_clasificacion,
        cadena_queja=cadena_queja,
        cadena_sugerencia=cadena_sugerencia,
        cadena_pregunta=cadena_pregunta,
        diagnostico=diagnostico,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ejemplo",
        choices=tuple(EJEMPLOS_FICTICIOS),
        default="queja",
        help="Selecciona un mensaje ficticio, una ejecucion por vez.",
    )
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "tu_llave_aqui":
        raise SystemExit("Configura GEMINI_API_KEY en .env; no la subas a GitHub.")

    nombre_modelo = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    modelo = ChatGoogleGenerativeAI(model=nombre_modelo)
    cadena = construir_cadena(modelo, diagnostico=True)

    mensaje = EJEMPLOS_FICTICIOS[args.ejemplo]
    print("Bloque 19 - Enrutamiento condicional (datos ficticios)")
    print(f"Modelo: {nombre_modelo} | llamadas previstas: 2")
    print(f"Ejemplo elegido: {args.ejemplo}")
    print("\nProcesando mensaje ficticio...")
    respuesta = cadena.invoke({"mensaje": mensaje})
    assert isinstance(respuesta, str), "Se esperaba texto final."
    print("\nRESPUESTA FINAL:\n")
    print(respuesta)
    print(f"\nSalida compatible con str: {isinstance(respuesta, str)}")


if __name__ == "__main__":
    main()
