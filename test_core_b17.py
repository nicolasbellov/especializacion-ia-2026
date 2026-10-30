"""Pruebas OFFLINE: ninguna respuesta simulada es evidencia Core."""

import json
from pathlib import Path

import pytest

from core_b17_generar import (
    ORIGEN_B15, PREGUNTAS_NUEVAS, catalogo_completo,
    construir_base, ejecutar_consultas, leer_json,
    validar_guardados,
)
from core_b17_revisar import (
    construir_muestra_core, leer_o_preparar,
    contar_revisados, redactar_informe,
)
from revision_cualitativa_b17 import validar_revision


def base() -> list[dict]:
    return construir_base(leer_json(ORIGEN_B15))


def corpus_falso_20(tmp_path: Path) -> list[dict]:
    """SOLO para tests: 17 respuestas simuladas, nunca las sube como evidencia."""
    registros = base()
    ejecutar_consultas(
        registros,
        tmp_path / "falso_test.json",
        lambda pregunta: "Respuesta SIMULADA en pruebas offline: " + pregunta,
        17,
    )
    return registros


def test_catalogo_contiene_17_consultas_nuevas():
    assert len(PREGUNTAS_NUEVAS) == 17
    assert len({pregunta for pregunta, _ in PREGUNTAS_NUEVAS}) == 17


def test_base_proviene_de_tres_respuestas_reales_versionadas():
    registros = base()
    assert [r["caso"] for r in registros] == [1, 2, 3]
    assert all(r["respuesta"] and r["f1"] > 0 for r in registros)


def test_catalogo_20_casos():
    assert set(catalogo_completo(base())) == set(range(1, 21))


def test_generacion_por_lotes_guarda_cada_caso(tmp_path):
    destino = tmp_path / "corpus_test.json"
    registros = base()
    llamadas = []
    def falsa(pregunta):
        llamadas.append(pregunta)
        return "SIMULACION DE TEST: " + pregunta

    ejecutar_consultas(registros, destino, falsa, 2)
    assert len(registros) == 5
    assert len(llamadas) == 2
    assert len(leer_json(destino)) == 5


def test_reanudar_solo_pide_los_restantes(tmp_path):
    destino = tmp_path / "corpus_test.json"
    registros = base()
    ejecutar_consultas(registros, destino, lambda q: "SIMULADO " + q, 2)
    guardados = validar_guardados(leer_json(destino), base())
    llamadas = []
    def falsa(pregunta):
        llamadas.append(pregunta)
        return "SIMULADO " + pregunta
    ejecutar_consultas(guardados, destino, falsa, 17)
    assert len(guardados) == 20
    assert len(llamadas) == 15


def test_generacion_completa_no_llama_api(tmp_path):
    corpus = corpus_falso_20(tmp_path)
    def nunca(_):
        raise AssertionError("No debería volver a consultar")
    ejecutar_consultas(corpus, tmp_path / "corpus_test.json", nunca, 17)
    assert len(corpus) == 20


def test_fallo_de_api_conserva_respuestas_previas(tmp_path):
    destino = tmp_path / "corpus_test.json"
    registros = base()
    llamadas = [0]
    def falla_despues_de_una(pregunta):
        llamadas[0] += 1
        if llamadas[0] == 2:
            raise TimeoutError("Simulación de cuota")
        return "SIMULACIÓN " + pregunta
    with pytest.raises(TimeoutError):
        ejecutar_consultas(registros, destino, falla_despues_de_una, 4)
    assert len(leer_json(destino)) == 4


def test_rechaza_texto_vacio(tmp_path):
    registros = base()
    with pytest.raises(ValueError, match="texto válido"):
        ejecutar_consultas(registros, tmp_path / "nada.json", lambda _: "", 1)
    assert len(registros) == 3


def test_rechaza_modificar_respuesta_original():
    registros = base()
    registros[0]["respuesta"] = "Reemplazo no verificable"
    with pytest.raises(ValueError, match="originales"):
        validar_guardados(registros, base())


def test_rechaza_metricas_manipuladas():
    registros = base()
    registros[0]["f1"] = 1.0
    with pytest.raises(ValueError, match="métricas"):
        validar_guardados(registros, base())


def test_requiere_20_casos_antes_de_revisar():
    with pytest.raises(ValueError, match="20 casos"):
        construir_muestra_core(base())


def test_20_casos_seleccionan_diez_extremos_unicos(tmp_path):
    muestra = construir_muestra_core(corpus_falso_20(tmp_path))
    assert len(muestra) == 10
    assert len({r["caso"] for r in muestra}) == 10
    assert all(r["correccion_factual"] is None for r in muestra)


def test_plantilla_ya_guardada_no_sobrescribe_notas(tmp_path):
    muestra = construir_muestra_core(corpus_falso_20(tmp_path))
    ruta = tmp_path / "revision_prueba.json"
    inicial = leer_o_preparar(ruta, muestra)
    inicial[0].update({
        "correccion_factual": "si", "completitud": "si",
        "contradiccion": "no", "justificacion": "Juicio humano simulado",
        "fecha_revision": "2026-10-29",
    })
    ruta.write_text(
        json.dumps(inicial, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    recargado = leer_o_preparar(ruta, muestra)
    assert recargado[0]["justificacion"] == "Juicio humano simulado"
    assert contar_revisados(recargado) == 1
    assert validar_revision(recargado[0])


def test_informe_rechaza_casos_no_revisados(tmp_path):
    muestra = construir_muestra_core(corpus_falso_20(tmp_path))
    with pytest.raises(ValueError, match="10 juicios"):
        redactar_informe(muestra)


def test_informe_transcribe_juicios_no_los_inventa(tmp_path):
    muestra = construir_muestra_core(corpus_falso_20(tmp_path))
    for registro in muestra:
        registro.update({
            "correccion_factual": "parcialmente",
            "completitud": "si",
            "contradiccion": "no",
            "justificacion": f"Nota SIMULADA para prueba caso {registro['caso']}",
            "fecha_revision": "2026-10-29",
        })
    reporte = redactar_informe(muestra)
    assert "10 casos únicos" in reporte
    assert "Nota SIMULADA para prueba" in reporte
    assert reporte.count("**Justificación humana:**") == 10
