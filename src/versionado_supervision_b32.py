"""Skillnest U2.7/B32/L1 — versionado de prompts y supervision humana.

Caso: Booking Core AI, exclusivamente laboratorio academico OFFLINE.
- Conserva versiones de prompt como archivos Git con registro de cambios.
- Demuestra interrupt, get_state y Command(resume=...) de LangGraph.
- El nodo final SOLO cambia estado simulado: no despliega prompts reales,
  no invoca Gemini y no modifica reservas de Booking Core.

Uso:
    python -m src.versionado_supervision_b32 --modo demo
    python -m src.versionado_supervision_b32 --modo interactivo
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
import difflib
import hashlib
import json
from pathlib import Path
from typing import Any, TypedDict
import uuid

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


DIRECTORIO_PROMPTS = Path(__file__).resolve().parents[1] / "prompts" / "booking_core_ai"
ARCHIVO_REGISTRO = DIRECTORIO_PROMPTS / "registro.json"
NOMBRE_PROMPT = "booking_core_ai_sistema"


def huella_prompt(texto: str) -> str:
    """Huella didactica del texto exacto (12 caracteres de SHA-256)."""
    if not isinstance(texto, str) or not texto:
        raise ValueError("El prompt debe ser texto no vacio.")
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:12]


def diff_prompts(anterior: str, nueva: str) -> list[str]:
    """Compara las palabras de dos versiones, como en la leccion oficial."""
    return list(difflib.unified_diff(
        anterior.split(), nueva.split(),
        fromfile="version_anterior",
        tofile="version_nueva",
        lineterm="",
    ))


class RegistroDePrompts:
    """Conserva la metadata de versiones leidas desde archivos bajo Git."""

    def __init__(self) -> None:
        self.versiones: list[dict[str, Any]] = []

    def registrar(
        self, nombre: str, version: str, texto: str,
        autor: str, fecha: str, nota: str,
        modelo_probado: str | None = None,
        parametros_probados: dict | None = None,
    ) -> dict[str, Any]:
        if not all(isinstance(c, str) and c.strip() for c in
                   (nombre, version, texto, autor, fecha, nota)):
            raise ValueError("El registro requiere nombre, version, texto, autor, fecha y nota.")
        date.fromisoformat(fecha)
        if any(
            v["nombre"] == nombre and v["version"] == version
            for v in self.versiones
        ):
            raise ValueError("Una version de prompt no puede registrarse dos veces.")
        dato = {
            "nombre": nombre,
            "version": version,
            "texto": texto,
            "huella": huella_prompt(texto),
            "autor": autor,
            "fecha": fecha,
            "nota": nota,
            "modelo_probado": modelo_probado,
            "parametros_probados": parametros_probados,
        }
        self.versiones.append(dato)
        return dato

    def ultima(self, nombre: str) -> dict[str, Any] | None:
        versiones = [v for v in self.versiones if v["nombre"] == nombre]
        return versiones[-1] if versiones else None

    def por_version(self, nombre: str, version: str) -> dict[str, Any]:
        for dato in self.versiones:
            if dato["nombre"] == nombre and dato["version"] == version:
                return dato
        raise KeyError("Version no registrada.")


def cargar_registro(ruta: Path = ARCHIVO_REGISTRO) -> RegistroDePrompts:
    """Lee Git como fuente de verdad; no sobrescribe prompts ni manifiesto."""
    ruta = Path(ruta)
    manifiesto = json.loads(ruta.read_text(encoding="utf-8"))
    nombre = manifiesto["nombre"]
    registro = RegistroDePrompts()
    for fila in manifiesto["versiones"]:
        archivo = fila["archivo"]
        if Path(archivo).name != archivo or archivo.startswith("."):
            raise ValueError("Ruta de prompt no permitida en registro.json")
        texto = (ruta.parent / archivo).read_text(encoding="utf-8").rstrip("\r\n")
        registro.registrar(
            nombre=nombre,
            version=fila["version"],
            texto=texto,
            autor=fila["autor"],
            fecha=fila["fecha"],
            nota=fila["nota"],
            modelo_probado=fila.get("modelo_probado"),
            parametros_probados=fila.get("parametros_probados"),
        )
    return registro


class EstadoSupervision(TypedDict):
    version_actual: str
    version_nueva: str
    huella_nueva: str
    aprobado: bool
    version_activa: str
    resultado: str


def proponer_version(estado: EstadoSupervision) -> dict:
    """Nodo inicial sin efectos externos."""
    return {}


def punto_supervision(estado: EstadoSupervision) -> dict:
    """Interrupcion REAL de LangGraph; solo una decision explicita reanuda."""
    decision = interrupt({
        "motivo": "revisar cambio de prompt de Booking Core AI (SIMULACION)",
        "version_propuesta": estado["version_nueva"],
        "huella_propuesta": estado["huella_nueva"],
        "version_actual": estado["version_actual"],
    })
    if type(decision) is not bool:
        raise ValueError("La decision del revisor debe ser True o False.")
    return {"aprobado": decision}


def aplicar_simulacion(estado: EstadoSupervision) -> dict:
    """NUNCA escribe a disco, modifica el prompt activo ni llama a Booking Core."""
    if estado["aprobado"]:
        return {
            "version_activa": estado["version_nueva"],
            "resultado": "aprobado_en_simulacion",
        }
    return {
        "version_activa": estado["version_actual"],
        "resultado": "rechazado_en_simulacion",
    }


def construir_grafo():
    grafo = StateGraph(EstadoSupervision)
    grafo.add_node("proponer_version", proponer_version)
    grafo.add_node("punto_supervision", punto_supervision)
    grafo.add_node("aplicar_simulacion", aplicar_simulacion)
    grafo.add_edge(START, "proponer_version")
    grafo.add_edge("proponer_version", "punto_supervision")
    grafo.add_edge("punto_supervision", "aplicar_simulacion")
    grafo.add_edge("aplicar_simulacion", END)
    return grafo.compile(checkpointer=InMemorySaver())


@dataclass(frozen=True)
class SolicitudRevision:
    config: dict
    version_nueva: str
    huella_nueva: str


def proponer_cambio(
    app, *, version_actual: str, version_nueva: str, huella_nueva: str
) -> SolicitudRevision:
    """Genera thread_id UNICO y deja la solicitud interrumpida."""
    if not version_actual or not version_nueva or not huella_nueva:
        raise ValueError("Versiones y huella deben ser no vacias.")
    config = {
        "configurable": {
            "thread_id": "revision-booking-core-" + uuid.uuid4().hex
        }
    }
    estado: EstadoSupervision = {
        "version_actual": version_actual,
        "version_nueva": version_nueva,
        "huella_nueva": huella_nueva,
        "aprobado": False,
        "version_activa": version_actual,
        "resultado": "pendiente",
    }
    respuesta = app.invoke(estado, config=config)
    if "__interrupt__" not in respuesta:
        raise RuntimeError("El grafo no se detuvo para supervision humana.")
    return SolicitudRevision(config, version_nueva, huella_nueva)


def inspeccionar_pendiente(app, solicitud: SolicitudRevision) -> dict[str, Any]:
    """Verifica estado conservado antes de mostrarlo a quien revisa."""
    snapshot = app.get_state(solicitud.config)
    if "punto_supervision" not in snapshot.next or not snapshot.interrupts:
        raise ValueError("Este thread_id no tiene aprobacion pendiente.")
    valores = snapshot.values
    if (
        valores.get("version_nueva") != solicitud.version_nueva
        or valores.get("huella_nueva") != solicitud.huella_nueva
    ):
        raise ValueError("La version pendiente no coincide con la solicitada.")
    return {
        "thread_id": solicitud.config["configurable"]["thread_id"],
        "version_actual": valores["version_actual"],
        "version_propuesta": valores["version_nueva"],
        "huella_propuesta": valores["huella_nueva"],
        "motivo": snapshot.interrupts[0].value["motivo"],
    }


def resolver_solicitud(
    app, solicitud: SolicitudRevision, *, aprobar: bool,
    version_revisada: str, huella_revisada: str,
) -> dict:
    """Reanuda una sola vez tras comparar version Y huella vistas por el revisor.

    ATENCION: no implementa autenticacion o autorizacion de un humano real.
    En produccion se necesita verificar identidad/rol en el backend.
    """
    if type(aprobar) is not bool:
        raise ValueError("aprobar debe ser bool.")
    pendiente = inspeccionar_pendiente(app, solicitud)
    if (
        pendiente["version_propuesta"] != version_revisada
        or pendiente["huella_propuesta"] != huella_revisada
    ):
        raise ValueError("No se puede aprobar una version diferente de la revisada.")
    return app.invoke(Command(resume=aprobar), config=solicitud.config)


def ejecutar_demo(interactivo: bool = False) -> None:
    registro = cargar_registro()
    anterior = registro.por_version(NOMBRE_PROMPT, "v1-b31-l2")
    nueva = registro.por_version(NOMBRE_PROMPT, "v2-b32-l1")
    print("Booking Core AI | control de prompts SOLO ACADEMICO")
    print("version anterior:", anterior["version"], "sha256_12:", anterior["huella"])
    print("version propuesta:", nueva["version"], "sha256_12:", nueva["huella"])
    print("modelo probado:", nueva["modelo_probado"])  # None: no validado con Gemini
    print("motivo:", nueva["nota"])
    print("Diferencias de texto:")
    for linea in diff_prompts(anterior["texto"], nueva["texto"]):
        print(linea)

    app = construir_grafo()
    solicitud = proponer_cambio(
        app,
        version_actual=anterior["version"],
        version_nueva=nueva["version"],
        huella_nueva=nueva["huella"],
    )
    pendiente = inspeccionar_pendiente(app, solicitud)
    print("pendiente:", json.dumps(pendiente, ensure_ascii=False))

    if interactivo:
        entrada = input("¿Aprobar propuesta ficticia? [s/n]: ").strip().lower()
        if entrada not in ("s", "n"):
            raise ValueError("Responde s o n, no se toma ninguna decision.")
        aprobacion = entrada == "s"
    else:
        print("DECISION SIMULADA: aprobar=True (no autentica a un revisor).")
        aprobacion = True

    final = resolver_solicitud(
        app, solicitud,
        aprobar=aprobacion,
        version_revisada=pendiente["version_propuesta"],
        huella_revisada=pendiente["huella_propuesta"],
    )
    print("resultado:", final["resultado"], "| version simulada:", final["version_activa"])
    assert final["version_activa"] == (
        nueva["version"] if aprobacion else anterior["version"]
    )
    assert final["resultado"] in ("aprobado_en_simulacion", "rechazado_en_simulacion")

    if not interactivo:
        segunda = proponer_cambio(
            app,
            version_actual=anterior["version"],
            version_nueva=nueva["version"],
            huella_nueva=nueva["huella"],
        )
        pendiente2 = inspeccionar_pendiente(app, segunda)
        rechazado = resolver_solicitud(
            app, segunda, aprobar=False,
            version_revisada=pendiente2["version_propuesta"],
            huella_revisada=pendiente2["huella_propuesta"],
        )
        assert rechazado["version_activa"] == anterior["version"]
        assert rechazado["resultado"] == "rechazado_en_simulacion"
        assert solicitud.config != segunda.config
        print("RECHAZO SIMULADO: version anterior conservada.")
    print("PASS: registro, diff, interrupt, estado pendiente y decision.")
    print("Sin despliegues, sin reservas reales, sin API Gemini.")


def main() -> int:
    parser = argparse.ArgumentParser(description="U2.7/B32/L1 Booking Core AI")
    parser.add_argument("--modo", choices=("demo", "interactivo"), default="demo")
    args = parser.parse_args()
    try:
        ejecutar_demo(interactivo=args.modo == "interactivo")
        return 0
    except Exception as error:
        # Nunca imprimir contenido sensible ni texto completo de excepciones.
        print(f"ERROR: {type(error).__name__}; revisar pruebas y entorno.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
