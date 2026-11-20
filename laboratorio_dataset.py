r"""Skillnest / Especializacion IA 2026 — U2.6, Bloque 29.

Laboratorio de preparacion de datos para PEFT.
Construye, valida y revisa el balance de un dataset de errores HTTP.
NO llama a la API ni inicia un trabajo de tuning.

Ejecutar desde la raiz del proyecto (PowerShell):
    .\.venv\Scripts\python.exe .\laboratorio_dataset.py
"""

import json
from collections import Counter

from google.genai import types


ejemplos_raw = [
    (
        "TimeoutError: la conexion tardo mas de 10 segundos en responder.",
        {"categoria": "red", "accion_sugerida": "reintentar con backoff exponencial"},
    ),
    (
        "ValueError: la clave de API no tiene el formato esperado.",
        {"categoria": "autenticacion", "accion_sugerida": "revisar GEMINI_API_KEY, no reintentar"},
    ),
    (
        "429 RESOURCE_EXHAUSTED: se supero el limite de peticiones por minuto.",
        {"categoria": "cuota", "accion_sugerida": "esperar y reintentar, con backoff"},
    ),
    (
        "API key not valid. Please pass a valid API key.",
        {"categoria": "autenticacion", "accion_sugerida": "revisar GEMINI_API_KEY, no reintentar"},
    ),
    (
        "RuntimeError: Your system has an unsupported version of sqlite3.",
        {"categoria": "entorno", "accion_sugerida": "instalar pysqlite3-binary"},
    ),
    (
        "ModuleNotFoundError: No module named langchain_chroma.",
        {"categoria": "entorno", "accion_sugerida": "instalar dependencia faltante"},
    ),
    (
        "PermissionError al crear la carpeta del vector store.",
        {"categoria": "entorno", "accion_sugerida": "revisar permisos de escritura"},
    ),
    (
        "InvalidArgumentError: Collection expecting embedding with dimension of 768, got 1536.",
        {
            "categoria": "consistencia_indice",
            "accion_sugerida": "reindexar con el mismo modelo de embeddings",
        },
    ),
]


def validar_dataset(examples, claves_esperadas=("categoria", "accion_sugerida")):
    """Valida entradas vacias, duplicados y estructura JSON de las salidas."""
    problemas = []
    vistos = set()
    for i, ejemplo in enumerate(examples):
        if not ejemplo.text_input or not ejemplo.text_input.strip():
            problemas.append(f"ejemplo {i}: text_input vacio")
        if not ejemplo.output or not ejemplo.output.strip():
            problemas.append(f"ejemplo {i}: output vacio")
            continue
        if ejemplo.text_input in vistos:
            problemas.append(f"ejemplo {i}: text_input duplicado")
        vistos.add(ejemplo.text_input)
        try:
            salida = json.loads(ejemplo.output)
        except json.JSONDecodeError:
            problemas.append(f"ejemplo {i}: output no es JSON valido")
            continue
        if not isinstance(salida, dict):
            problemas.append(f"ejemplo {i}: output debe ser un objeto JSON")
            continue
        for clave in claves_esperadas:
            if clave not in salida:
                problemas.append(f'ejemplo {i}: output no tiene la clave "{clave}"')
    return problemas


def chequear_balance(datos):
    return Counter(salida["categoria"] for _, salida in datos)


def main():
    # 1. Crear los ejemplos estructurados que entiende el SDK.
    examples = [
        types.TuningExample(
            text_input=texto,
            output=json.dumps(salida, ensure_ascii=False),
        )
        for texto, salida in ejemplos_raw
    ]
    print("=== 1. DATASET ===")
    print(len(examples), "ejemplos construidos")
    print(examples[0])

    # 2. Validar la calidad estructural localmente.
    print("\n=== 2. VALIDACION ===")
    problemas = validar_dataset(examples)
    print(f"{len(examples)} ejemplos, {len(problemas)} problemas encontrados")
    for problema in problemas:
        print(" -", problema)

    # 3. Examinar la representacion de cada categoria.
    print("\n=== 3. BALANCE ===")
    balance = chequear_balance(ejemplos_raw)
    for categoria, cuenta in balance.most_common():
        print(f"{categoria}: {cuenta}")
    maximo = max(balance.values())
    minimo = min(balance.values())
    print(f"categoria mas representada: {maximo} ejemplos")
    print(f"categoria menos representada: {minimo} ejemplos")
    print(f"razon max/min: {maximo / minimo:.1f}x")

    # 4. Ver los estados de entrenamiento; NO crear ningun trabajo.
    print("\n=== 4. ESTADOS DE UN TUNING JOB ===")
    for estado in types.JobState:
        print(" ", estado)

    # 5. Prueba negativa: confirmar que el validador detecta fallas.
    print("\n=== 5. TEST NEGATIVO DEL VALIDADOR ===")
    examples_rotos = examples + [
        types.TuningExample(text_input="", output='{"categoria": "red"}'),
        types.TuningExample(text_input=ejemplos_raw[0][0], output="no es json"),
    ]
    problemas_rotos = validar_dataset(examples_rotos)
    print(f"{len(examples_rotos)} ejemplos, {len(problemas_rotos)} problemas encontrados")
    for problema in problemas_rotos:
        print(" -", problema)

    # 6. Construir objetos del SDK en memoria. No llamar a client.tunings.tune().
    print("\n=== 6. CONFIGURACION PEFT (SOLO LOCAL) ===")
    dataset = types.TuningDataset(examples=examples)
    config = types.CreateTuningJobConfig(
        tuning_mode=types.TuningMode.TUNING_MODE_PEFT_ADAPTER,
        adapter_size=types.AdapterSize.ADAPTER_SIZE_FOUR,
        epoch_count=5,
        tuned_model_display_name="clasificador-errores-cliente",
    )
    print("Dataset SDK construido:", len(dataset.examples), "ejemplos")
    print("Modo:", config.tuning_mode)
    print("Adapter:", config.adapter_size)
    print("Epocas:", config.epoch_count)
    print("No se han realizado llamadas a la API ni iniciado entrenamientos.")

    assert len(examples) == 8
    assert len(problemas) == 0
    assert len(problemas_rotos) == 4
    print("\nLABORATORIO LOCAL: VALIDACIONES APROBADAS")


if __name__ == "__main__":
    main()
