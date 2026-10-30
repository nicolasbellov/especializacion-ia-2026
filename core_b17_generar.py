"""U2.2 / Bloque 17 Core: 20 respuestas REALES con métricas.

Conserva las tres respuestas verificadas del Bloque 15 y genera 17 nuevas
mediante cliente.consultar_modelo, con guardado después de cada petición.

Vista previa (sin API):
    python core_b17_generar.py --plan

Generación REAL (usa la API key local; puede consumir cuota):
    python core_b17_generar.py --generar --max-nuevas 17

Si una llamada falla, conserva las anteriores y permite reanudar con el
mismo comando. Nunca fabrica respuestas ni sobrescribe registros ya obtenidos.
"""

import argparse
import json
import os
from pathlib import Path

from evaluar_salidas_b16 import calcular_metricas


RAIZ = Path(__file__).resolve().parent
ORIGEN_B15 = RAIZ / "resultados_b15.json"
DESTINO_CORE = RAIZ / "resultados_core_b17.json"

# 17 consultas nuevas, distintas de los 3 casos reales del Bloque 15.
# Las referencias son hipótesis de comparación académica, NO un patrón
# de verdad absoluta ni un certificado de corrección factual.
PREGUNTAS_NUEVAS = (
    ("¿Qué es una variable en Python? Responde en una sola oración breve.",
     "Una variable permite asociar un nombre a un valor en Python."),
    ("¿Qué es una lista en Python? Responde en una sola oración breve.",
     "Una lista de Python es una colección ordenada y modificable de elementos."),
    ("¿Qué es un diccionario en Python? Responde en una sola oración breve.",
     "Un diccionario de Python almacena pares de clave y valor."),
    ("¿Qué hace len() en Python? Responde en una sola oración breve.",
     "len devuelve la cantidad de elementos de una colección."),
    ("¿Qué es una función en Python? Responde en una sola oración breve.",
     "Una función es un bloque de código reutilizable que puede recibir argumentos y devolver resultados."),
    ("¿Qué significa un error de sintaxis en Python? Responde en una sola oración breve.",
     "Un error de sintaxis aparece cuando el código no sigue las reglas del lenguaje."),
    ("¿Qué es JSON? Responde en una sola oración breve.",
     "JSON es un formato de texto para representar datos estructurados."),
    ("¿Para qué sirve HTTP? Responde en una sola oración breve.",
     "HTTP es un protocolo para intercambiar solicitudes y respuestas entre clientes y servidores."),
    ("¿Qué significa el código HTTP 404? Responde en una sola oración breve.",
     "HTTP 404 indica que el servidor no encontró el recurso solicitado."),
    ("¿Qué significa el código HTTP 429? Responde en una sola oración breve.",
     "HTTP 429 indica que el cliente envió demasiadas solicitudes en un periodo de tiempo."),
    ("¿Qué es una API REST? Responde en una sola oración breve.",
     "Una API REST expone recursos que se consultan y modifican mediante peticiones HTTP."),
    ("¿Qué es un commit de Git? Responde en una sola oración breve.",
     "Un commit registra una instantánea de cambios en un repositorio Git."),
    ("¿Para qué sirve git clone? Responde en una sola oración breve.",
     "git clone crea una copia local de un repositorio."),
    ("¿Qué es una prueba unitaria? Responde en una sola oración breve.",
     "Una prueba unitaria verifica el comportamiento de una parte pequeña del programa."),
    ("¿Qué es un entorno virtual de Python? Responde en una sola oración breve.",
     "Un entorno virtual aísla las dependencias de un proyecto Python."),
    ("¿Qué significa UTF-8? Responde en una sola oración breve.",
     "UTF-8 es una codificación de caracteres compatible con Unicode."),
    ("¿Qué es un token en procesamiento de texto? Responde en una sola oración breve.",
     "Un token es una unidad de texto obtenida al segmentar una entrada."),
)


def leer_json(ruta: Path) -> list[dict]:
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    if not isinstance(datos, list):
        raise ValueError(f"Se esperaba una lista JSON: {ruta}")
    return datos


def construir_base(casos_b15: list[dict]) -> list[dict]:
    """Usa SOLO las tres respuestas reales B15 y recalcula sus métricas."""
    if len(casos_b15) != 3 or {c["caso"] for c in casos_b15} != {1, 2, 3}:
        raise ValueError("Se esperaban exactamente 3 casos originales B15")

    resultados = []
    for caso in sorted(casos_b15, key=lambda c: c["caso"]):
        respuesta = caso["respuesta_real"]
        if not isinstance(respuesta, str) or not respuesta.strip():
            raise ValueError("El corpus original carece de respuesta real")
        resultados.append({
            "caso": caso["caso"], "consulta": caso["consulta"],
            "referencia": caso["referencia"], "respuesta": respuesta,
            "origen": "Bloque 15: Gemini real",
            **calcular_metricas(caso["referencia"], respuesta),
        })
    return resultados


def catalogo_completo(base: list[dict]) -> dict[int, dict]:
    esperado = {c["caso"]: c for c in base}
    for indice, (consulta, referencia) in enumerate(PREGUNTAS_NUEVAS, start=4):
        esperado[indice] = {
            "caso": indice, "consulta": consulta, "referencia": referencia,
            "origen": "Bloque 17 Core: Gemini real",
        }
    if len(esperado) != 20:
        raise ValueError("El catálogo no contiene 20 casos distintos")
    return esperado


def validar_guardados(
    existentes: list[dict], base: list[dict]
) -> list[dict]:
    """Evita atribuir a Gemini textos ficticios, alterados o sin procedencia."""
    esperados = catalogo_completo(base)
    ids = [r["caso"] for r in existentes]
    if len(ids) != len(set(ids)) or not {1, 2, 3}.issubset(ids):
        raise ValueError("Los registros existentes deben contener B15 sin duplicados")
    for caso in existentes:
        original = esperados.get(caso["caso"])
        if original is None:
            raise ValueError(f"Identificador inesperado: {caso['caso']}")
        for campo in ("consulta", "referencia", "origen"):
            if caso.get(campo) != original[campo]:
                raise ValueError(f"Caso {caso['caso']}: campo {campo} alterado")
        texto = caso.get("respuesta")
        if not isinstance(texto, str) or not texto.strip():
            raise ValueError(f"Caso {caso['caso']}: respuesta vacía")
        if caso["caso"] <= 3 and texto != original["respuesta"]:
            raise ValueError("No cambiar las respuestas originales del Bloque 15")
        metricas = calcular_metricas(original["referencia"], texto)
        if any(caso.get(clave) != valor for clave, valor in metricas.items()):
            raise ValueError(f"Caso {caso['caso']}: métricas inconsistentes")
    return sorted(existentes, key=lambda c: c["caso"])


def guardar_json_atomico(ruta: Path, registros: list[dict]) -> None:
    temporal = ruta.with_name(ruta.name + ".tmp")
    temporal.write_text(
        json.dumps(registros, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporal, ruta)


def ejecutar_consultas(
    registros: list[dict], destino: Path, consultar, max_nuevas: int
) -> list[dict]:
    """Realiza un máximo de max_nuevas llamadas, guardando cada éxito."""
    if not 1 <= max_nuevas <= 17:
        raise ValueError("max_nuevas debe estar entre 1 y 17")
    base = [r for r in registros if r["caso"] <= 3]
    esperados = catalogo_completo(base)
    completados = {r["caso"] for r in registros}
    nuevas = 0
    for id_caso in range(4, 21):
        if id_caso in completados:
            continue
        if nuevas >= max_nuevas:
            break
        caso = esperados[id_caso]
        print(f"Consultando caso {id_caso}/20: {caso['consulta']}", flush=True)
        respuesta = consultar(caso["consulta"])
        if not isinstance(respuesta, str) or not respuesta.strip():
            raise ValueError(f"Caso {id_caso}: Gemini no devolvió texto válido")
        registro = {
            **caso, "respuesta": respuesta,
            **calcular_metricas(caso["referencia"], respuesta),
        }
        registros.append(registro)
        registros.sort(key=lambda r: r["caso"])
        guardar_json_atomico(destino, registros)
        nuevas += 1
        completados.add(id_caso)
        print(f"  Guardado. Total real: {len(registros)}/20")
    return registros


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--plan", action="store_true", help="Sin API ni escrituras")
    grupo.add_argument("--generar", action="store_true", help="Consume API Gemini real")
    parser.add_argument("--max-nuevas", type=int, default=17)
    args = parser.parse_args()

    base = construir_base(leer_json(ORIGEN_B15))
    guardados = validar_guardados(
        leer_json(DESTINO_CORE) if DESTINO_CORE.exists() else base, base
    )
    pendientes = [n for n in range(4, 21) if n not in {
        c["caso"] for c in guardados
    }]
    print(f"Casos reales: {len(guardados)}/20; nuevos pendientes: {len(pendientes)}")
    print(f"Destino: {DESTINO_CORE}")
    if args.plan:
        print("Modo plan: ninguna llamada API ni cambio de archivos.")
        return
    if not 1 <= args.max_nuevas <= 17:
        parser.error("--max-nuevas debe estar entre 1 y 17")
    if not pendientes:
        print("Corpus de 20 completo. No se llama a Gemini.")
        return

    # Persistir B15 antes de iniciar; así se conserva evidencia ante fallas.
    if not DESTINO_CORE.exists():
        guardar_json_atomico(DESTINO_CORE, guardados)

    # Importación diferida: --plan y pruebas offline NO cargan el cliente ni .env.
    from cliente import consultar_modelo

    try:
        ejecutar_consultas(guardados, DESTINO_CORE, consultar_modelo, args.max_nuevas)
    except Exception as error:
        print(f"Generación detenida: {type(error).__name__}: {error}")
        print("Las respuestas ya guardadas permanecen. Reejecutar para reanudar.")
        raise SystemExit(1) from error

    print(f"Resultado: {len(guardados)}/20 respuestas REALES.")
    if len(guardados) < 20:
        print("Actividad Core todavía incompleta; reanudar después.")


if __name__ == "__main__":
    main()
