# U2.3 — Bloque 18 — Evidencia de la actividad 20344

**Fecha de ejecución comunicada:** 2026-11-06 (Chile)  
**Actividad:** Construye tu chain de al menos tres pasos encadenados  
**Repositorio:** `nicolasbellov/especializacion-ia-2026`  
**Entorno local:** Windows, Python 3.12.8, `.venv`, pytest 9.2.0  
**Modelo utilizado:** `gemini-3.5-flash-lite`

## Objetivo

Implementar un caso original de orquestación LangChain con tres pasos encadenados
mediante `|`, `PromptTemplate`, `StrOutputParser` y adaptadores de salida.
Se utiliza una incidencia **ficticia** de consistencia de indicadores de
urgencias; no se accede a TrakCare ni a datos clínicos reales.

## Archivos

- `src/cadena_tres_pasos.py` — implementación del flujo de análisis, planificación de verificaciones y comunicación.
- `tests/test_cadena_tres_pasos.py` — dos pruebas con un modelo simulado.
- `requirements.txt` — dependencias declaradas del proyecto.

## Validaciones realizadas por el participante

Comando ejecutado:

```powershell
python -m pytest tests/test_cadena_tres_pasos.py -v
```

Resultado informado por la terminal:

```text
tests/test_cadena_tres_pasos.py::test_encadena_tres_pasos_y_entrega_texto PASSED
tests/test_cadena_tres_pasos.py::test_falta_variable_obligatoria_sin_llamar_al_modelo PASSED
2 passed in 0.92s
```

Se verificó, sin llamadas reales al proveedor durante pytest, que:

1. El modelo simulado se invoca tres veces.
2. La salida del paso anterior se encuentra en el prompt del siguiente.
3. Se obtiene una salida compatible con `str`.
4. La falta de la variable obligatoria se detecta antes de invocar el modelo.

Comando de ejecución real:

```powershell
python -m src.cadena_tres_pasos
```

La terminal informó:

```text
Actividad 20344 | Caso ficticio: consistencia de indicador de urgencias
Modelo: gemini-3.5-flash-lite | llamadas previstas: 3
INFORME FINAL:
# Informe Técnico para el Equipo de Implementación
[Objetivo y tres validaciones sugeridas]
Salida compatible con str: True
```

**Resultado:** ejecución completa exitosa, con informe en Markdown. No se
observaron excepciones en la ejecución compartida.

## Revisión de calidad del contenido

El informe del modelo propone comparar IDs de episodios, filtros, fechas,
zonas horarias y registros de actualización del cubo. Son pasos razonables
como hipótesis de investigación, pero requieren dos cautelas:

- La diferencia de conteos 42 frente a 36 no implica necesariamente seis
  IDs únicos faltantes: podrían existir duplicados o criterios distintos.
- No se debe asumir que el proceso de actualización corresponde a un
  ETL/script concreto sin inspeccionar la implementación del cubo.

El resultado **no acredita una causa raíz** ni representa evidencia
de investigación de un ambiente real.

## Estado de aceptación

- [x] Tres prompts con responsabilidades diferentes.
- [x] Salidas enlazadas mediante `|` y adaptadores.
- [x] Uso de `StrOutputParser`.
- [x] Pruebas automatizadas aprobadas (2/2).
- [x] Flujo end-to-end ejecutado con Gemini.
- [x] Dependencias y código publicados en GitHub.
- [ ] Confirmación de entrega y aprobación en Skillnest.

**Estado académico:** actividad validada técnicamente; entrega formal por confirmar.  
**Siguiente tema:** Bloque 19 — enrutamiento condicional según el tipo de entrada.
