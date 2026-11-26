"""Los cuatro no compensables de Skillnest, adaptados al servicio propio.

Chroma real persistido temporalmente, embeddings/LLM simulados explícitamente.
La corrida Gemini y la revisión humana manual se validan además en consola.
"""
import json
import uuid

import pytest

from gate2.servicio import RESPONDIDA
from gate2.supervision import crear_supervision, resolver
from servicio_rag import (CORPUS, EmbeddingsEnsayo, abrir_preparado,
                          ejecutar_consulta, generador_ensayo)

CORREO = "ana.perez@example.com"
PREGUNTA = "¿Qué requisitos hay para reprogramar una cita ficticia? Mi correo es " + CORREO


@pytest.fixture(scope="module")
def indice(tmp_path_factory):
    ruta = tmp_path_factory.mktemp("gate2_oficial") / "indice"
    store, info = abrir_preparado(ruta, CORPUS, EmbeddingsEnsayo())
    assert info["documentos"] == 5 and info["chunks"] == 10
    return store, info


def ejecutar_servicio(indice):
    store, info = indice
    return ejecutar_consulta(store, PREGUNTA, generador_ensayo,
                             simulado=True, estado_indice=info)


def test_1_pipeline_sin_excepciones(indice):
    resultado, auditoria = ejecutar_servicio(indice)
    assert resultado.estado == RESPONDIDA
    assert resultado.respuesta.strip()
    assert resultado.documentos_recuperados > 0
    assert {e["trace_id"] for e in auditoria} == {resultado.trace_id}


def test_2_respuesta_cita_fuente(indice):
    resultado, _ = ejecutar_servicio(indice)
    assert resultado.citas_utilizadas
    for n in resultado.citas_utilizadas:
        assert n in resultado.fuentes
        assert resultado.fuentes[n] in resultado.respuesta


def test_3_logs_sin_contenido_crudo(indice):
    # El logger B31 tiene propagate=False: se comprueba el StreamHandler
    # que produce los logs JSON reales, no un caplog que podría quedar vacío.
    resultado, auditoria = ejecutar_servicio(indice)
    assert len(auditoria) >= 5
    texto = json.dumps(auditoria, ensure_ascii=False)
    assert CORREO not in texto
    assert PREGUNTA not in texto
    assert resultado.respuesta not in texto
    assert any(e.get("evento") == "consumo_llm" for e in auditoria)


def test_4_supervision_pausa_y_reanuda():
    app, entrada = crear_supervision("DEMO-001")
    config = {"configurable": {"thread_id": "gate2-test-" + uuid.uuid4().hex}}
    pausado = app.invoke(entrada, config=config)
    assert "__interrupt__" in pausado
    assert pausado["estado_reserva"] == "confirmada"
    assert pausado["ejecutada"] is False
    final = resolver(app, config, True)
    assert "__interrupt__" not in final
    assert final["aprobado"] is True
    assert final["estado_reserva"] == "cancelada"
    assert final["ejecutada"] is True
    # Segunda solicitud independiente: rechazo conserva el estado.
    config2 = {"configurable": {"thread_id": "gate2-test-" + uuid.uuid4().hex}}
    assert "__interrupt__" in app.invoke(entrada, config=config2)
    rechazo = resolver(app, config2, False)
    assert rechazo["estado_reserva"] == "confirmada"
    assert rechazo["ejecutada"] is False
