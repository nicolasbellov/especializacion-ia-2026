"""Checklist operativo Gate 2; jamás imprime la clave Gemini."""
import argparse
from importlib.metadata import version, PackageNotFoundError
import os
from pathlib import Path
import subprocess
import sys

RAIZ = Path(__file__).resolve().parent
PAQUETES = ["langchain-core", "langchain-chroma", "chromadb", "langgraph",
            "langchain-google-genai", "langchain-text-splitters", "python-dotenv", "pytest"]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--modo", choices=("simulado", "real"), default="real")
    p.add_argument("--permitir-indice-nuevo", action="store_true")
    a = p.parse_args()
    problemas = []
    print("Python:", sys.version.split()[0])
    if sys.version_info < (3, 10):
        problemas.append("Python >=3.10")
    for paquete in PAQUETES:
        try:
            print(paquete + ":", version(paquete))
        except PackageNotFoundError:
            problemas.append("instalar " + paquete)
    try:
        from dotenv import load_dotenv
        load_dotenv(RAIZ / ".env")
    except ImportError:
        pass
    definida = bool(os.getenv("GEMINI_API_KEY"))
    print("GEMINI_API_KEY:", "definida" if definida else "FALTA")
    if a.modo == "real" and not definida:
        problemas.append("definir GEMINI_API_KEY localmente")
    git = subprocess.run(["git", "check-ignore", ".env"], cwd=RAIZ,
                         capture_output=True, text=True)
    print(".env ignorado:", git.returncode == 0)
    if git.returncode != 0:
        problemas.append(".env debe estar ignorado por Git")
    ruta = RAIZ / ("vectorstore" if a.modo == "real" else ".local/gate2_simulado")
    if (ruta / "manifiesto_b24_l3.json").is_file():
        try:
            from gate2.indice import verificar_bloqueo
            from recuperacion import comprobar_fuentes
            verificar_bloqueo(ruta)
            info = comprobar_fuentes(ruta)
            print("Índice:", info["documentos"], "fuentes,", info["chunks"], "chunks")
        except Exception as exc:
            problemas.append("índice no válido: " + type(exc).__name__)
    elif a.permitir_indice_nuevo:
        print("Índice ausente; se creará en la primera corrida explícita.")
    else:
        problemas.append("indexar el corpus primero")
    if problemas:
        print("Pendiente:", "; ".join(problemas))
        return 1
    print("Entorno listo para la corrida final")
    return 0


if __name__ == "__main__":
    sys.exit(main())
