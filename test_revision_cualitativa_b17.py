"""Pruebas offline B17 L1: selección, rúbrica y protección de juicios."""

import json
from pathlib import Path

import pytest

from revision_cualitativa_b17 import (
    guardar_plantilla_si_no_existe,
    preparar_revision,
    seleccionar_muestra,
    validar_revision,
)


def crear_casos(n: int) -> list[dict]:
    return [
        {
            "caso": i + 1, "consulta": f"Consulta {i + 1}",
            "referencia": f"Referencia {i + 1}",
            "respuesta": f"Respuesta {i + 1}",
            "f1": i / max(1, n),
        }
        for i in range(n)
    ]


def test_tres_casos_no_se_duplican():
    muestra = seleccionar_muestra(crear_casos(3))
    assert [r["caso"] for r in muestra] == [1, 2, 3]


def test_docek_casos_toma_cinco_de_cada_extremo():
    muestra = seleccionar_muestra(crear_casos(12))
    assert [r["caso"] for r in muestra] == [1, 2, 3, 4, 5, 8, 9, 10, 11, 12]


def test_menos_de_diez_se_toman_todos_sin_repetir():
    muestra = seleccionar_muestra(crear_casos(7))
    assert len(muestra) == 7
    assert len({r["caso"] for r in muestra}) == 7


def test_muestra_vacia():
    assert seleccionar_muestra([]) == []


def test_por_extremo_no_valido():
    with pytest.raises(ValueError, match="positivo"):
        seleccionar_muestra(crear_casos(2), 0)


def test_rechaza_ids_duplicados():
    casos = crear_casos(2)
    casos[1]["caso"] = casos[0]["caso"]
    with pytest.raises(ValueError, match="duplicados"):
        seleccionar_muestra(casos)


def test_plantilla_no_inventa_evaluaciones():
    original = crear_casos(3)
    registros = preparar_revision(original)
    assert [r["caso"] for r in registros] == [1, 2, 3]
    assert all(
        r["correccion_factual"] is None
        and r["completitud"] is None
        and r["contradiccion"] is None
        and r["justificacion"] == ""
        for r in registros
    )
    assert all(validar_revision(r) for r in registros)
    assert "correccion_factual" not in original[0]


def test_validacion_respetando_la_rubrica_del_curso():
    registro = preparar_revision(crear_casos(1))[0]
    registro.update({
        "correccion_factual": "si",
        "completitud": "parcialmente",
        "contradiccion": "no",
        "justificacion": "Falta un detalle de la referencia.",
    })
    assert validar_revision(registro)
    registro["contradiccion"] = "parcialmente"
    assert not validar_revision(registro)


def test_juicios_incompletos_o_no_justificados():
    registro = preparar_revision(crear_casos(1))[0]
    registro["completitud"] = "si"
    assert not validar_revision(registro)
    registro.update({
        "correccion_factual": "si",
        "contradiccion": "no",
    })
    assert not validar_revision(registro)


def test_guardar_no_sobrescribe_revision_humana(tmp_path: Path):
    ruta = tmp_path / "revision_cualitativa_b17.json"
    registros = preparar_revision(crear_casos(1))
    assert guardar_plantilla_si_no_existe(ruta, registros)
    original = ruta.read_text(encoding="utf-8")
    with pytest.raises(FileExistsError):
        guardar_plantilla_si_no_existe(ruta, [])
    assert ruta.read_text(encoding="utf-8") == original
    assert json.loads(original) == registros


def test_casos_reales_de_gemini_disponibles_y_sin_duplicados():
    ruta = Path(__file__).with_name("resultados_metricas.json")
    resultados = json.loads(ruta.read_text(encoding="utf-8"))
    muestra = preparar_revision(resultados)
    assert [r["caso"] for r in muestra] == [3, 2, 1]
    assert [r["f1"] for r in muestra] == pytest.approx(
        [6 / 31, 1 / 3, 4 / 9]
    )
