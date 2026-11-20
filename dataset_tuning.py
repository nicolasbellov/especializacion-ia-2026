r"""U2.6 / Bloque 29, actividad practica: dataset propio de personalizacion.

Caso: clasificar mensajes ficticios de Booking Core AI con salida JSON consistente.
No consulta agendas, no reserva citas y no llama a Gemini ni a la API de tuning.

Uso:
    .\.venv\Scripts\python.exe .\dataset_tuning.py
"""

import json
from collections import Counter

from google.genai import types


# Contrato de salida: clasifica intencion y ruta, sin ejecutar la ruta.
RUTA_POR_INTENCION = {
    "consultar_disponibilidad": "consulta_agenda",
    "crear_reserva": "operacion_supervisada",
    "reprogramar_reserva": "operacion_supervisada",
    "cancelar_reserva": "operacion_supervisada",
    "consultar_politica": "rag_documental",
}
CLAVES_ESPERADAS = ("intencion", "ruta")

# Dataset 100 % sintetico para el proyecto academico Booking Core AI.
# No representa reglas comerciales reales ni incluye datos de pacientes/clientes.
ejemplos_raw: list[tuple[str, dict[str, str]]] = [
    # Consultas de disponibilidad (lectura, sin reserva).
    ("¿Qué horarios libres tienen el viernes por la tarde?",
     {"intencion": "consultar_disponibilidad", "ruta": "consulta_agenda"}),
    ("¿Hay cupos para corte de pelo el miércoles después de las seis?",
     {"intencion": "consultar_disponibilidad", "ruta": "consulta_agenda"}),
    ("Muéstrame las horas disponibles para mañana por la mañana.",
     {"intencion": "consultar_disponibilidad", "ruta": "consulta_agenda"}),
    ("Antes de decidir, quiero ver la disponibilidad del próximo sábado.",
     {"intencion": "consultar_disponibilidad", "ruta": "consulta_agenda"}),

    # Peticiones para crear una reserva: requieren autorización/confirmación backend.
    ("Quiero reservar un corte para el sábado a las 11:00.",
     {"intencion": "crear_reserva", "ruta": "operacion_supervisada"}),
    ("Agéndame una atención para el martes a las 17:00, por favor.",
     {"intencion": "crear_reserva", "ruta": "operacion_supervisada"}),
    ("Me gustaría sacar una hora para corte de pelo el jueves.",
     {"intencion": "crear_reserva", "ruta": "operacion_supervisada"}),
    ("Necesito que me apartes un cupo para el lunes a primera hora.",
     {"intencion": "crear_reserva", "ruta": "operacion_supervisada"}),

    # Cambio explícito de una reserva ya existente.
    ("Tengo una reserva mañana; cámbiala al lunes a las 17:00.",
     {"intencion": "reprogramar_reserva", "ruta": "operacion_supervisada"}),
    ("¿Puedes mover mi cita del martes al jueves?",
     {"intencion": "reprogramar_reserva", "ruta": "operacion_supervisada"}),
    ("No alcanzo a llegar a mi hora de hoy; reprogramémosla para el viernes.",
     {"intencion": "reprogramar_reserva", "ruta": "operacion_supervisada"}),
    ("Pasa la reserva que ya tengo de las 15:00 a las 18:00.",
     {"intencion": "reprogramar_reserva", "ruta": "operacion_supervisada"}),

    # Cancelación explícita de la reserva, distinta de preguntar por la política.
    ("Cancela mi reserva del próximo martes, por favor.",
     {"intencion": "cancelar_reserva", "ruta": "operacion_supervisada"}),
    ("Ya no podré asistir, quiero anular la cita del sábado.",
     {"intencion": "cancelar_reserva", "ruta": "operacion_supervisada"}),
    ("Elimina mi hora agendada para mañana.",
     {"intencion": "cancelar_reserva", "ruta": "operacion_supervisada"}),
    ("Necesito dar de baja la reserva que hice para el viernes.",
     {"intencion": "cancelar_reserva", "ruta": "operacion_supervisada"}),

    # Preguntas de políticas: RAG documental; no se inventa la respuesta.
    ("¿Con cuánta anticipación se puede cancelar una reserva?",
     {"intencion": "consultar_politica", "ruta": "rag_documental"}),
    ("¿Qué condiciones aplican si llego tarde a mi cita?",
     {"intencion": "consultar_politica", "ruta": "rag_documental"}),
    ("¿Cuál es el procedimiento para cambiar una reserva?",
     {"intencion": "consultar_politica", "ruta": "rag_documental"}),
    ("¿Existe alguna regla sobre reprogramaciones de última hora?",
     {"intencion": "consultar_politica", "ruta": "rag_documental"}),
]


def construir_dataset(datos: list[tuple[str, dict[str, str]]]) -> list[types.TuningExample]:
    """Convierte pares entrada/salida en objetos TuningExample del SDK."""
    return [
        types.TuningExample(
            text_input=texto,
            output=json.dumps(salida, ensure_ascii=False),
        )
        for texto, salida in datos
    ]


def chequear_balance(
    datos: list[tuple[str, dict[str, str]]], clave: str
) -> Counter[str]:
    """Cuenta la representación de cada categoría elegida."""
    return Counter(salida[clave] for _, salida in datos)


def validar_dataset(
    examples: list[types.TuningExample],
    claves_esperadas: tuple[str, ...] = CLAVES_ESPERADAS,
) -> list[str]:
    """Verifica texto, unicidad, JSON exacto y correspondencia intención/ruta."""
    problemas: list[str] = []
    vistos: set[str] = set()
    for i, ejemplo in enumerate(examples):
        texto = (ejemplo.text_input or "").strip()
        if not texto:
            problemas.append(f"ejemplo {i}: text_input vacio")
        if texto in vistos:
            problemas.append(f"ejemplo {i}: text_input duplicado")
        vistos.add(texto)

        output = ejemplo.output or ""
        if not output.strip():
            problemas.append(f"ejemplo {i}: output vacio")
            continue
        try:
            salida = json.loads(output)
        except json.JSONDecodeError:
            problemas.append(f"ejemplo {i}: output no es JSON valido")
            continue
        if not isinstance(salida, dict):
            problemas.append(f"ejemplo {i}: output debe ser un objeto JSON")
            continue

        for clave in claves_esperadas:
            if clave not in salida:
                problemas.append(f'ejemplo {i}: falta la clave "{clave}"')
        if set(salida) != set(claves_esperadas):
            problemas.append(f"ejemplo {i}: el JSON no tiene exactamente las claves esperadas")

        intencion = salida.get("intencion")
        ruta = salida.get("ruta")
        if intencion is not None and intencion not in RUTA_POR_INTENCION:
            problemas.append(f"ejemplo {i}: intencion desconocida")
        elif intencion in RUTA_POR_INTENCION and ruta is not None:
            if ruta != RUTA_POR_INTENCION[intencion]:
                problemas.append(f"ejemplo {i}: ruta incompatible con intencion")
        if ruta is not None and not isinstance(ruta, str):
            problemas.append(f"ejemplo {i}: ruta debe ser texto")
    return problemas


def main() -> None:
    examples = construir_dataset(ejemplos_raw)
    print("=== 1. DATASET BOOKING CORE AI ===")
    print(f"{len(examples)} ejemplos construidos")
    print("Ejemplo:", examples[0])

    print("\n=== 2. BALANCE POR INTENCION ===")
    balance = chequear_balance(ejemplos_raw, "intencion")
    for categoria, cuenta in sorted(balance.items()):
        print(f"{categoria}: {cuenta}")
    minimo, maximo = min(balance.values()), max(balance.values())
    print(f"razon max/min: {maximo / minimo:.1f}x")

    print("\n=== 3. VALIDACION ===")
    problemas = validar_dataset(examples)
    print(f"{len(examples)} ejemplos, {len(problemas)} problemas encontrados")
    for problema in problemas:
        print(" -", problema)

    print("\n=== 4. PRUEBA NEGATIVA DEL VALIDADOR ===")
    rotos = examples + [
        types.TuningExample(text_input="", output='{"intencion": "cancelar_reserva"}'),
        types.TuningExample(text_input=ejemplos_raw[0][0], output="no es json"),
    ]
    problemas_rotos = validar_dataset(rotos)
    print(f"{len(rotos)} ejemplos, {len(problemas_rotos)} problemas encontrados")
    for problema in problemas_rotos:
        print(" -", problema)

    assert len(examples) >= 10, "El curso exige al menos 10 ejemplos"
    assert len(balance) >= 2, "Debe haber mas de una categoria"
    assert set(balance) == set(RUTA_POR_INTENCION), "Faltan categorias"
    assert not problemas, "El dataset original no supera la validacion"
    assert len(problemas_rotos) >= 4, "El validador no detecto los defectos sembrados"
    print("\nDATASET PROPIO: VALIDACIONES APROBADAS")
    print("No se ha entrenado un modelo ni llamado a la API.")


if __name__ == "__main__":
    main()
