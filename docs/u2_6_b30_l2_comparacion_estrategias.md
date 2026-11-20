# U2.6 · Bloque 30 / Lección 2 — Comparación de estrategias

**Fuente:** Skillnest / Accenture / CChIA, «Cómo comparar estrategias de personalización para tu caso» (B30/L2, requisito «Ver»), recibido el 20/11/2026.

## 1. Los cinco criterios oficiales

| Pregunta (clave Python) | Puntos si es True |
| --- | --- |
| `informacion_cambia_seguido` | RAG +3 |
| `problema_de_formato_o_tono` | PEFT +2, Fine-tuning completo +1 |
| `dataset_grande_y_de_calidad` | Fine-tuning completo +2, PEFT +1 |
| `presupuesto_limitado_o_iterar_rapido` | RAG +2, PEFT +1 |
| `necesita_multiples_variantes` | PEFT +2 |

El curso compara **RAG, fine-tuning completo y PEFT**. **Prompting y soft-prompting no participan en esta fórmula**, aunque pueden ser alternativas útiles.

**Bug enseñado por Skillnest:** `max(puntos, key=puntos.get)` devuelve una sola clave aunque haya empate; por conservar el orden de inserción, el primer método elige «Fine-tuning completo» sin justificación. La corrección usa `maximo = max(puntos.values())` y `[tecnica for tecnica, p in puntos.items() if p == maximo]` para devolver **todas** las técnicas empatadas. El script versionado implementa directamente la versión corregida.

## 2. Reproducción de los dos casos del curso

| Caso | RAG | Fine-tuning | PEFT | Ganadoras |
| --- | ---: | ---: | ---: | --- |
| Caso 2, clasificador con dataset grande | 0 | 3 | 3 | Fine-tuning completo y PEFT |
| Caso 1, bot con políticas cambiantes | 5 | 1 | 3 | RAG |

En el caso 2, invertir una respuesta a la vez produce las ganadoras:

| Pregunta invertida | Nuevas ganadoras |
| --- | --- |
| `informacion_cambia_seguido` a True | RAG, Fine-tuning completo, PEFT |
| `problema_de_formato_o_tono` a False | Fine-tuning completo |
| `dataset_grande_y_de_calidad` a False | PEFT |
| `presupuesto_limitado_o_iterar_rapido` a True | PEFT |
| `necesita_multiples_variantes` a True | PEFT |

**5/5 inversiones cambian las ganadoras:** el empate es frágil y la elección requiere criterio cualitativo.

## 3. Aplicación propia a Booking Core AI

Las respuestas de Booking Core son **supuestos propios**, no valores entregados por Skillnest ni resultados medidos.

**Sistema completo:** `True, True, False, True, False`. Políticas/documentación pueden cambiar, la salida JSON debe ser estable, solo existe un dataset didáctico de 20 ejemplos sintéticos (no «grande y de calidad»), queremos iterar rápido y no se han requerido múltiples adapters. **RAG 5, fine-tuning 1, PEFT 3 → RAG**. Importante: RAG se reserva para **documentos**; disponibilidad, reservas y cancelaciones transaccionales pertenecen al backend autorizado.

**Solo clasificador de intenciones:** `False, True, False, True, False`. Para clasificar intención/ruta no hace falta recuperar políticas cambiantes. **RAG 2, fine-tuning 1, PEFT 3 → PEFT** según la heurística del curso. **Decisión técnica adicional:** con 20 ejemplos sintéticos no se ha demostrado generalización; evaluar **primero prompting estructurado con JSON Schema** en casos de prueba separados, antes de considerar entrenamiento. Esta recomendación es propia, no una sexta regla de Skillnest.

## 4. Límites y validación

La puntuación es una **heurística académica**, no precisión real, presupuesto de proveedor, ni autorización para operaciones de agenda. Un sistema puede combinar RAG, prompting y herramientas transaccionales. No se llaman API ni se entrena modelo.

- Implementación: [comparar_estrategias.py](../comparar_estrategias.py), con pesos del curso, empates y análisis de sensibilidad.
- Pruebas: [tests/test_comparar_estrategias_b30.py](../tests/test_comparar_estrategias_b30.py), **19 casos** offline.
- CI: el script se ejecuta en el workflow académico y las pruebas se descubren con `unittest`.

### Reproducir en Windows

```powershell
git pull --ff-only origin main
.\.venv\Scripts\python.exe .\comparar_estrategias.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_comparar_estrategias_b30.py" -v
git status -sb
```

**Estado:** código publicado; **Windows pendiente hasta ver la salida del usuario**, sin asumir aprobación institucional.

**Próximo paso:** B30/L3 Core «Redacta tu decisión de personalización fundamentada»; analizar la consigna antes de redactar la entrega.
