"""Fixture de práctica temporal: no crear ni versionar practica_revision/docs."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ficha_datos import cargar

# Ejemplo de tienda Skillnest B34/L2, conservando los defectos de trazabilidad y horas.
DEFECTUOSA = """# Ficha de Diseño Funcional

## 1. Problema de negocio
El equipo de soporte de una tienda en línea ficticia responde unas 60 consultas semanales (estimación) sobre devoluciones y envíos buscando a mano en un PDF de 40 páginas. Cada consulta toma cerca de 8 minutos y las respuestas varían según quién conteste. Se espera que cualquier integrante del equipo obtenga una respuesta con su fuente en menos de un minuto.

## 2. Requerimientos y alcance (MVP)
### Requerimientos funcionales
- RF-01: El usuario envía una pregunta de texto a un endpoint de consulta y recibe una respuesta en JSON.
- RF-02: Cada respuesta incluye al menos una fuente citada con el nombre del documento.
- RF-03: El servicio consulta el estado de un envío por número de pedido usando datos simulados.
- RF-04: Una persona aprueba o rechaza antes de que se genere un reembolso.
- RF-05: Una interfaz web muestra el historial de conversaciones.
- RF-06: El servicio consulta el sistema de pedidos real de la empresa.
### Requerimientos no funcionales
- RNF-01: El endpoint de consulta responde en menos de 5 segundos en al menos 9 de cada 10 consultas de prueba.
- RNF-02: En los registros de las 10 consultas de prueba, ninguna línea contiene el texto completo de la pregunta ni de los documentos, solo longitudes y conteos.
- RNF-03: El servicio levanta desde cero en un contenedor, siguiendo el README, en menos de 10 minutos.
### Alcance
Imprescindible: RF-01, RF-02, RF-03
Deseable: RF-04
Fuera de alcance: RF-05 (no hay frontend en el programa), RF-06 (requiere sistemas y datos reales)

## 3. Arquitectura de la solución
Diagrama: docs/diagrama_arquitectura.png
- Modelo: Gemini mediante API, con la clave en el archivo .env.
- Vector store: Chroma persistido en la carpeta indice/.
- Orquestación: recuperación, filtro de inyección y generación con citas; aprobación humana con LangGraph.
- Exposición: servicio FastAPI con un endpoint de consulta.
- Empaquetado: imagen Docker con el índice montado como volumen.

## 4. Criterios de aceptación
- CA-01 (RF-01): Al enviar la pregunta "¿Cuál es el plazo para devolver un producto?" al endpoint de consulta, la respuesta es un JSON con los campos "respuesta" y "fuentes".
- CA-02 (RF-02): Para esa misma pregunta, "fuentes" contiene "manual.pdf" y la respuesta menciona 30 días.
- CA-03 (RF-02): Ante la pregunta "¿Venden gift cards?", que el manual no cubre, la respuesta dice que no encuentra la información y "fuentes" va vacía.
- CA-05 (RNF-01): En las 10 consultas de prueba, al menos 9 responden en menos de 5 segundos.
- CA-06 (RNF-02): Tras ejecutar las 10 consultas de prueba, ninguna línea del registro contiene el texto completo de una pregunta.
- CA-07 (RNF-03): Siguiendo solo el README en un equipo limpio, el servicio responde a CA-01 a los 10 minutos o antes desde el inicio.

## 5. Plan de construcción por hitos
Horas disponibles: 20 h
Margen de imprevistos: 4 h
- H1 (3 h): Servicio FastAPI con el endpoint de consulta. Cubre: RF-01. Se comprueba con: CA-01.
- H2 (2 h): Respuestas con fuente desde el índice persistido. Cubre: RF-02. Se comprueba con: CA-02, CA-03.
- H3 (3 h): Servicio empaquetado en un contenedor. Cubre: RNF-03. Se comprueba con: CA-07.
- H4 (2 h): Consulta de estado de envío con datos simulados. Cubre: RF-03. Se comprueba con: pruebas manuales.
- H5 (8 h): Pruebas, documentación y ensayo de la defensa. Cubre: RNF-01, RNF-02. Se comprueba con: CA-05.
"""

CORREGIDA = (DEFECTUOSA
    .replace("- CA-05 (RNF-01)", "- CA-04 (RF-03): El pedido simulado PED-1001 devuelve su estado registrado.\n- CA-05 (RNF-01)")
    .replace("Se comprueba con: pruebas manuales.", "Se comprueba con: CA-04.")
    .replace("H5 (8 h)", "H5 (6 h)")
    .replace("Se comprueba con: CA-05.", "Se comprueba con: CA-05, CA-06."))


def ejecutar_en_temporal(texto):
    with tempfile.TemporaryDirectory() as tmp:
        docs = Path(tmp) / "docs"
        docs.mkdir()
        ruta = docs / "ficha_diseno_funcional.md"
        ruta.write_text(texto, encoding="utf-8")
        datos = cargar(ruta)
        r = subprocess.run([sys.executable, str(ROOT / "resumen_ficha.py")],
                           cwd=tmp, capture_output=True, text=True,
                           encoding="utf-8", timeout=30)
        if r.returncode:
            raise RuntimeError(r.stderr)
        return datos, r.stdout


class TestRevisionFichaB34(unittest.TestCase):
    def test_defectuosa(self):
        d, s = ejecutar_en_temporal(DEFECTUOSA)
        for linea in (
            "RF: 6 | RNF: 3",
            "Alcance: imprescindibles 3, deseables 1, fuera de alcance 2",
            "Criterios de aceptacion: 6",
            "Imprescindibles y RNF sin criterio: RF-03",
            "Hitos: 5 | Horas planificadas: 18.0 h de 16.0 h posibles",
            "Criterios que ningun hito comprueba: CA-06",
            "Hitos sin criterio: H4",
        ):
            self.assertIn(linea, s)
        self.assertEqual(len(d["hitos"]), 5)

    def test_corregida(self):
        d, s = ejecutar_en_temporal(CORREGIDA)
        self.assertEqual(len(d["criterios"]), 7)
        for linea in (
            "Imprescindibles y RNF sin criterio: ninguno",
            "Horas planificadas: 16.0 h de 16.0 h posibles",
            "Criterios que ningun hito comprueba: ninguno",
            "Hitos sin criterio: ninguno",
        ):
            self.assertIn(linea, s)

    def test_decimales_y_referencias(self):
        texto = CORREGIDA.replace("Horas disponibles: 20 h", "Horas disponibles: 24 h").replace(
            "Margen de imprevistos: 4 h", "Margen de imprevistos: 4,8 h").replace(
            "H5 (6 h)", "H5 (7,2 h)")
        d, s = ejecutar_en_temporal(texto)
        self.assertEqual(d["margen"], 4.8)
        self.assertEqual(d["hitos"][-1]["horas"], 7.2)
        self.assertEqual(d["hitos"][-1]["cubre"], ["RNF-01", "RNF-02"])
        self.assertEqual(d["hitos"][-1]["criterios"], ["CA-05", "CA-06"])
        self.assertIn("de 19.2 h posibles", s)

    def test_ficha_real_pendiente_sin_sobrescribir(self):
        # Usar una versión temporal con secciones pendientes; válida incluso tras Core.
        texto = DEFECTUOSA.split("## 4. Criterios de aceptación")[0] + (
            "## 4. Criterios de aceptación\n[PENDIENTE]\n\n"
            "## 5. Plan de construcción por hitos\n[PENDIENTE]\n")
        d, s = ejecutar_en_temporal(texto)
        self.assertEqual(d["criterios"], [])
        self.assertEqual(d["hitos"], [])
        self.assertIsNone(d["disponibles"])
        self.assertIn("Criterios de aceptacion: 0", s)


if __name__ == "__main__":
    if sys.argv[1:] == ["--demo"]:
        print("=== FICHA DEFECTUOSA (practica temporal) ===")
        print(ejecutar_en_temporal(DEFECTUOSA)[1], end="")
        print("\n=== FICHA CORREGIDA (practica temporal) ===")
        print(ejecutar_en_temporal(CORREGIDA)[1], end="")
    else:
        unittest.main()
