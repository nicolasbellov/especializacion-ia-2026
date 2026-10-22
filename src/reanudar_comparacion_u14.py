r"""U1.4 Bloque 9: reanudar pruebas pendientes sin repetir ni borrar resultados.

Ejecutar desde la raíz del repositorio:
    & .\venv\Scripts\python.exe -m src.reanudar_comparacion_u14

Lee docs/mediciones_modelos_u14.csv (generado por comparar_modelos_u14.py).
Reutiliza su función medir(), conservando exactamente prompts, modelos y tarifas.
Aplica reintentos acotados solo para incidencias transitorias 429/503/timeout.
No altera consumir_gemini.py ni realiza cambios en la configuración de la API.
"""

import csv
import json
import os
import statistics
import tempfile
import time
from pathlib import Path

from src.comparar_modelos_u14 import CAMPOS, CASOS, MODELOS, medir

DESTINO = Path("docs") / "mediciones_modelos_u14.csv"
MAX_INTENTOS = 3  # Incluye el primer intento; nunca hace bucles infinitos.


def clave(fila):
    return (fila["modelo"], fila["caso"], int(fila["repeticion"]))


def leer_existentes():
    if not DESTINO.is_file():
        raise FileNotFoundError(
            f"No existe {DESTINO}. Conserva el CSV de la prueba inicial "
            "y ejecuta este script desde la raíz del repositorio."
        )
    with DESTINO.open("r", encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames != CAMPOS:
            raise ValueError(
                "El CSV tiene columnas diferentes a las esperadas. "
                "No se modificará para evitar pérdida de datos."
            )
        filas = list(lector)

    claves = [clave(fila) for fila in filas]
    if len(claves) != len(set(claves)):
        raise ValueError("El CSV contiene pruebas duplicadas; revisar antes de continuar.")
    return filas, set(claves)


def guardar_seguro(filas):
    """Reemplazo atómico: no trunca el CSV original durante su escritura."""
    temporal = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8-sig", newline="",
            dir=DESTINO.parent, prefix="mediciones_u14_", suffix=".tmp", delete=False,
        ) as archivo:
            temporal = Path(archivo.name)
            escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
            escritor.writeheader()
            escritor.writerows(filas)
        os.replace(temporal, DESTINO)
    finally:
        if temporal is not None:
            temporal.unlink(missing_ok=True)


def medir_con_reintentos(modelo, tarifas, caso, pregunta, repeticion):
    for numero_intento in range(1, MAX_INTENTOS + 1):
        try:
            return medir(modelo, tarifas, caso, pregunta, repeticion)
        except RuntimeError as error:
            mensaje = str(error)
            transitorio = (
                "HTTP 503" in mensaje
                or "HTTP 429" in mensaje
                or "tardó demasiado" in mensaje
            )
            if not transitorio or numero_intento == MAX_INTENTOS:
                raise
            espera = (5 if "HTTP 503" in mensaje else 20) * (2 ** (numero_intento - 1))
            print(f"  {mensaje} | Reintento {numero_intento + 1}/{MAX_INTENTOS} en {espera}s")
            time.sleep(espera)
    raise AssertionError("No se debería llegar a esta línea")


def resumen(filas):
    print("\n=== RESUMEN ACTUAL ===")
    for modelo in MODELOS:
        propias = [f for f in filas if f["modelo"] == modelo]
        principal = [f for f in propias if f["caso"] == "reserva_completa"]
        print(f"{modelo}: {len(propias)}/6 casos/repeticiones registradas")
        if principal:
            latencias = [float(f["latencia_s"]) for f in principal]
            tipo = "promedio comparable" if len(principal) == 4 else "promedio provisional"
            print(f"  {tipo} reserva_completa ({len(principal)}/4): "
                  f"{statistics.mean(latencias):.2f}s")
            print(f"  costo medio registrado reserva_completa: USD "
                  f"{statistics.mean(float(f['costo_estimado_usd']) for f in principal):.8f}")
        if propias:
            estrictas = 0
            for f in propias:
                try:
                    objeto = json.loads(f["respuesta"])
                    estrictas += int(isinstance(objeto, dict))
                except (json.JSONDecodeError, TypeError):
                    pass
            print(f"  respuestas JSON estrictas (sin Markdown): {estrictas}/{len(propias)}")
    print(f"Archivo: {DESTINO}")


def main():
    filas, hechas = leer_existentes()
    esperadas = [
        (modelo, tarifas, caso, pregunta, n)
        for modelo, tarifas in MODELOS.items()
        for caso, pregunta, repeticiones in CASOS
        for n in range(1, repeticiones + 1)
    ]
    pendientes = [x for x in esperadas if (x[0], x[2], x[4]) not in hechas]
    print(f"Filas existentes: {len(filas)} | Pendientes: {len(pendientes)}")

    if not pendientes:
        print("No faltan peticiones. No se modificó el CSV.")
        resumen(filas)
        return

    for modelo, tarifas, caso, pregunta, repeticion in pendientes:
        print(f"Ejecutando {modelo} | {caso} #{repeticion}")
        try:
            fila = medir_con_reintentos(modelo, tarifas, caso, pregunta, repeticion)
        except (RuntimeError, KeyError, ValueError) as error:
            print(f"PRUEBA DETENIDA: {error}")
            print("Se conservó el CSV con todas las mediciones válidas previas.")
            resumen(filas)
            return
        filas.append(fila)
        hechas.add(clave(fila))
        guardar_seguro(filas)  # Persiste cada resultado inmediatamente.
        print(f"  OK {float(fila['latencia_s']):.2f}s | "
              f"USD {float(fila['costo_estimado_usd']):.8f} | "
              f"CSV actualizado ({len(filas)}/12)")
        time.sleep(2)

    print("\nTodas las peticiones pendientes completadas.")
    resumen(filas)


if __name__ == "__main__":
    main()
