"""Banco U1.5: solicitudes ficticias de agenda de servicios.

Los prompts solo interpretan información: no crean ni modifican reservas reales.
"""

BANCO_DE_PROMPTS = [
    {
        "nombre": "interpretar_intencion_agenda",
        "system_instruction": (
            "Eres el componente que clasifica solicitudes de una agenda de servicios. "
            "Responde únicamente con un objeto JSON válido, sin Markdown. "
            "Usa la intención crear, reprogramar, cancelar, consultar u otro. "
            "La confianza debe ser un número entre 0 y 1. "
            "No confirmes reservas ni afirmes haber consultado disponibilidad."
        ),
        "ejemplo_usuario": (
            "Quiero reservar un corte de cabello el 29 de octubre de 2026 a las 15:30."
        ),
        "claves_esperadas": ["intencion", "confianza"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "intencion": {
                    "type": "STRING",
                    "enum": ["crear", "reprogramar", "cancelar", "consultar", "otro"],
                },
                "confianza": {"type": "NUMBER", "minimum": 0, "maximum": 1},
            },
            "required": ["intencion", "confianza"],
        },
        "resultado_esperado": {"intencion": "crear"},
    },
    {
        "nombre": "extraer_datos_cita",
        "system_instruction": (
            "Extraes datos de solicitudes para una agenda de servicios. "
            "Devuelve únicamente un objeto JSON, sin Markdown, con las claves: "
            "fecha, hora, duracion_minutos, servicio y profesional. "
            "Normaliza fechas explícitas a AAAA-MM-DD y horas a HH:MM (24 horas). "
            "Si no aparece un dato, no lo inventes: usa cadena vacía para "
            "campos de texto y 0 para duracion_minutos. "
            "No crees eventos ni verifiques disponibilidad."
        ),
        "ejemplo_usuario": (
            "Agenda un corte de cabello para el 29/10/2026 a las 15:30, "
            "con Ana, duración 45 minutos."
        ),
        "claves_esperadas": [
            "fecha", "hora", "duracion_minutos", "servicio", "profesional"
        ],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "fecha": {"type": "STRING"},
                "hora": {"type": "STRING"},
                "duracion_minutos": {"type": "INTEGER"},
                "servicio": {"type": "STRING"},
                "profesional": {"type": "STRING"},
            },
            "required": [
                "fecha", "hora", "duracion_minutos", "servicio", "profesional"
            ],
        },
        "resultado_esperado": {
            "fecha": "2026-10-29",
            "hora": "15:30",
            "duracion_minutos": 45,
            "profesional": "Ana",
        },
    },
    {
        "nombre": "detectar_datos_faltantes",
        "system_instruction": (
            "Validas solicitudes de una agenda de servicios. "
            "Los datos mínimos para solicitar una cita son servicio, fecha y hora. "
            "Responde solo con un objeto JSON, sin Markdown. "
            "datos_completos debe ser true únicamente si los tres datos "
            "están presentes explícitamente; de lo contrario false. "
            "campos_faltantes debe ser una lista de nombres exactos entre "
            "servicio, fecha y hora que no aparecen. "
            "No inventes fechas ni horarios y no confirmes reservas."
        ),
        "ejemplo_usuario": "Quiero agendar una limpieza facial.",
        "claves_esperadas": ["datos_completos", "campos_faltantes"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "datos_completos": {"type": "BOOLEAN"},
                "campos_faltantes": {
                    "type": "ARRAY",
                    "items": {
                        "type": "STRING",
                        "enum": ["servicio", "fecha", "hora"],
                    },
                },
            },
            "required": ["datos_completos", "campos_faltantes"],
        },
        "resultado_esperado": {
            "datos_completos": False,
            "campos_faltantes": ["fecha", "hora"],
        },
    },
]
