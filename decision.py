r"""B30 Core: decision fundamentada Booking Core AI, reproducible y offline.

Uso: .\.venv\Scripts\python.exe .\decision.py
Crea decision_personalizacion.md. No usa API, GPU ni reservas reales.
"""
from __future__ import annotations

from pathlib import Path

from comparar_estrategias import recomendar_estrategia

RESPUESTAS_MI_CASO: dict[str, bool] = {
    "informacion_cambia_seguido": False,
    "problema_de_formato_o_tono": False,
    "dataset_grande_y_de_calidad": False,
    "presupuesto_limitado_o_iterar_rapido": True,
    "necesita_multiples_variantes": False,
}

# El método usa los pesos EXACTOS de B30/L2, sin ocultar empates.
# La actividad Core agrega umbrales de evidencia más exigentes: NO se
# pueden trasladar sin revisar los supuestos del ejercicio anterior.
EVIDENCIAS: tuple[tuple[str, str], ...] = (
    (
        "informacion_cambia_seguido = False",
        "Las cinco fuentes ficticias fueron creadas el 13/11/2026 y no "
        "registran cambios posteriores hasta el 20/11. La historia disponible "
        "no acredita al menos una actualización mensual durante tres meses; "
        "no se afirma que las futuras políticas comerciales sean estáticas.",
    ),
    (
        "problema_de_formato_o_tono = False",
        "No se dispone de una auditoría de 20 respuestas reales de este "
        "componente con al menos tres fallos. Los 20 pares de dataset_tuning.py "
        "son ejemplos etiquetados, NO salidas observadas del modelo. "
        "False indica umbral sin demostrar, no tasa observada de fallos cero.",
    ),
    (
        "dataset_grande_y_de_calidad = False",
        "Existen 20 ejemplos sintéticos para el clasificador de intención, "
        "menos de los 200 del umbral y sin auditoría aleatoria de etiquetas. "
        "RAG no necesita ejemplos de entrenamiento para indexar documentos.",
    ),
    (
        "presupuesto_limitado_o_iterar_rapido = True",
        "El piloto académico ADOPTA como condición de diseño poder observar "
        "cambios de contenido en menos de un día; es coherente con las "
        "iteraciones dentro del mismo día ya registradas en GitHub y Windows. "
        "No equivale a un SLA de producción ni a un límite de dinero aprobado.",
    ),
    (
        "necesita_multiples_variantes = False",
        "La implementación académica evalúa un asistente Booking Core AI, "
        "sin requerimiento documentado de dos o más variantes ajustadas.",
    ),
)

PROBLEMA = (
    "Booking Core AI debe responder consultas sobre procedimientos de servicios, "
    "reprogramación, cancelación y privacidad con respaldo documental "
    "identificable, sin inventar condiciones comerciales ni ejecutar reservas "
    "por el solo hecho de generar una respuesta."
)

FUNDAMENTO = (
    "Elijo **RAG para el componente documental**, con contexto numerado, "
    "citas verificables y abstención cuando falta evidencia. El método lo "
    "sitúa primero bajo los supuestos explícitos (2 puntos frente a 1 de "
    "PEFT y 0 de fine-tuning completo). RAG permite actualizar documentos "
    "sin entrenar otro modelo y aprovecha el corpus/vectorstore ya preparado. "
    "No elijo PEFT ni fine-tuning para este problema: no está acreditada "
    "una falla sistemática de formato en 20 respuestas reales, y tampoco "
    "tenemos 200 ejemplos revisados. Para el **clasificador de intenciones** "
    "del Bloque 29 (20 ejemplos sintéticos), evaluaría primero prompting "
    "estructurado/JSON Schema; PEFT solo si un baseline medido falla. "
    "La puntuación del curso no incluye prompting ni soft-prompting. "
    "RAG no sustituye el backend: identidad, tenant, disponibilidad y "
    "operaciones de agenda requieren APIs autorizadas."
)

PLAN = (
    "Para la demostración ya existen **5 de 5 documentos ficticios** en "
    "data/corpus_b24_l3 y un índice Chroma local de **10 chunks**: "
    "**faltan 0 documentos para reproducir el alcance académico actual**. "
    "En B27 se prepararon **12 preguntas** (10 con relevancia etiquetada y "
    "2 sin respuesta factual) y se obtuvieron dos corridas reproducibles "
    "para k=3: precisión media **0,306** y recall medio **1,000** en "
    "los casos evaluables. Son métricas de recuperación de un corpus "
    "sintético, no resultados de producción ni verificación del texto final. "
    "Para uso real falta inventariar las fuentes oficiales de políticas y "
    "servicios de AES Barber; **todavía no existe una cifra verificable** "
    "de documentos faltantes para producción. También se requieren "
    "actualización/versionado del índice, controles de tenant, citas "
    "validadas, pruebas de abstención y acceso al backend autorizado. "
    "La disponibilidad y los precios vigentes nunca se extraerán de "
    "notas ficticias. Como alternativa futura, el clasificador tiene "
    "**20 ejemplos**, le faltan **180 para llegar a 200** según el "
    "umbral orientativo del curso, además de etiquetas revisadas y "
    "evaluación con respuestas reales: 200 no garantiza un tuning útil."
)

DESTINO = Path("decision_personalizacion.md")


def generar_esqueleto_decision(
    problema: str, puntos: dict[str, int], ganadoras: list[str]
) -> str:
    """Incluye exactamente las cuatro secciones obligatorias del curso."""
    lineas = [
        "# Decisión fundamentada de personalización — Booking Core AI",
        "",
        "## 1. El problema",
        problema,
        "",
        "## 2. Resultado del método de decisión",
        "Se aplicó la rúbrica de B30 Core al componente documental.",
        "",
    ]
    for tecnica, puntaje in sorted(puntos.items(), key=lambda x: -x[1]):
        lineas.append(f"- **{tecnica}: {puntaje} puntos**")
    lineas += ["", "**Candidatas mejor puntuadas:** " + ", ".join(ganadoras) + "."]
    if len(ganadoras) > 1:
        lineas.append("**Empate explícito:** " + ", ".join(ganadoras) + ".")
    lineas += ["", "**Evidencia por criterio (True/False):**", ""]
    for clave, descripcion in EVIDENCIAS:
        lineas.append(f"- **{clave}.** {descripcion}")
    lineas += [
        "",
        "[SENSIBILIDAD]",
        "",
        "## 3. Técnica elegida y por qué",
        "[COMPLETAR_FUNDAMENTO]",
        "",
        "## 4. Qué necesitarías para ejecutarla",
        "[COMPLETAR_PLAN]",
        "",
    ]
    return "\n".join(lineas)


def generar_documento() -> str:
    puntos, ganadoras = recomendar_estrategia(RESPUESTAS_MI_CASO)
    variante = dict(RESPUESTAS_MI_CASO)
    variante["presupuesto_limitado_o_iterar_rapido"] = False
    puntos_v, ganadoras_v = recomendar_estrategia(variante)
    sensibilidad = (
        "**Prueba de sensibilidad:** se invirtió SOLO "
        "§presupuesto_limitado_o_iterar_rapido§ de True a False. "
        f"Resultado: RAG {puntos_v['RAG']}, fine-tuning completo "
        f"{puntos_v['Fine-tuning completo']}, PEFT {puntos_v['PEFT']}; "
        "**empate entre " + ", ".join(ganadoras_v) + "**. "
        "En ese caso la heurística deja de decidir: RAG seguiría siendo "
        "una opción cualitativa para datos documentales, pero no una "
        "ganadora por puntaje. Hay que ratificar el objetivo de "
        "iteración menor a un día antes de una decisión productiva."
    ).replace("§", chr(96))
    documento = generar_esqueleto_decision(PROBLEMA, puntos, ganadoras)
    documento = documento.replace("[SENSIBILIDAD]", sensibilidad)
    documento = documento.replace("[COMPLETAR_FUNDAMENTO]", FUNDAMENTO)
    documento = documento.replace("[COMPLETAR_PLAN]", PLAN)
    return documento


def main() -> None:
    puntos, ganadoras = recomendar_estrategia(RESPUESTAS_MI_CASO)
    print("=== B30 CORE — BOOKING CORE DOCUMENTAL ===")
    print("Respuestas:", RESPUESTAS_MI_CASO)
    print("Puntajes:", puntos)
    print("Candidatas:", ganadoras)
    documento = generar_documento()
    assert documento.count("## ") == 4
    assert "[COMPLETAR" not in documento
    DESTINO.write_text(documento, encoding="utf-8")
    print("Documento creado: decision_personalizacion.md")
    print("B30 CORE: DOCUMENTO GENERADO SIN API")


if __name__ == "__main__":
    main()
