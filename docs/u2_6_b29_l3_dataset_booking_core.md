# U2.6 · Bloque 29 / L3 — Dataset propio para personalización PEFT

**Actividad:** «Ejecuta el laboratorio guiado de personalización» ([Skillnest id 20469](https://learning-pro.skillnest.com/mod/page/view.php?id=20469)).  
**Fecha:** 20/11/2026. **Proyecto:** Booking Core AI (agenda de barbería, caso académico sintético).

## 1. Problema de comportamiento consistente (no de conocimiento)

Se requiere que un clasificador produzca siempre el **mismo contrato JSON**, a partir de mensajes libres dirigidos a un asistente de reservas:

```json
{"intencion": "reprogramar_reserva", "ruta": "operacion_supervisada"}
```

El problema elegido es la **clasificación y el enrutamiento consistentes**, no aprender horarios, precios o reglas vigentes. Estos últimos pertenecen al backend de agenda o a RAG documental. Por lo tanto, este dataset es un ejemplo didáctico de **personalización del comportamiento con PEFT** y no supone que PEFT sea obligatorio en producción; se debe comparar primero con prompting estructurado.

### Contrato de salida

| Intención | Ruta esperada | Significado |
| --- | --- | --- |
| `consultar_disponibilidad` | `consulta_agenda` | Requiere consultar disponibilidad en backend autorizado |
| `crear_reserva` | `operacion_supervisada` | Solicitud transaccional, requiere validación/autorización |
| `reprogramar_reserva` | `operacion_supervisada` | Solicitud de cambio de reserva existente |
| `cancelar_reserva` | `operacion_supervisada` | Solicitud de anulación |
| `consultar_politica` | `rag_documental` | Pregunta informativa, responder usando fuentes disponibles |

**Alcance:** `ruta` es solo una etiqueta, no ejecuta herramientas, no verifica identidad, no confirma citas y no afirma políticas reales. El texto del dataset y los servicios son ficticios. No se integran credenciales ni datos personales.

## 2. Dataset propio

- Archivo exigido por el curso: [`dataset_tuning.py`](../dataset_tuning.py).
- **20 pares entrada/salida** originales, escritos para Booking Core AI, con variaciones semánticas por categoría.
- **5 intenciones x 4 ejemplos**; razón entre la categoría mayor y menor **1,0x** por diseño (dato teórico de la definición del dataset, pendiente de ejecutar Windows).
- Salida de cada `types.TuningExample`: texto JSON generado con `json.dumps(ensure_ascii=False)`.
- Dos claves exactas: `intencion` y `ruta`. La validación adicional verifica dominios válidos y coherencia entre ambas.

## 3. Validación y pruebas

`chequear_balance(ejemplos_raw, "intencion")`: cuenta casos por etiqueta.  
`validar_dataset(examples)`: comprueba entradas vacías/duplicadas, salida no vacía, JSON válido, objeto JSON, claves exactas, intención reconocida y correspondencia intención/ruta.

Dos registros corruptos creados en memoria demuestran que el validador detecta fallas. No forman parte del dataset entregable.

Pruebas complementarias: [`tests/test_dataset_tuning_b29.py`](../tests/test_dataset_tuning_b29.py), 16 casos de contrato, balance y validación negativa.

### Ejecución Windows (sin activar entorno virtual ni consumir API)

Desde la raíz del repositorio:

```powershell
git pull --ff-only origin main
.\.venv\Scripts\python.exe .\dataset_tuning.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_dataset_tuning_b29.py" -v
git status -sb
```

**Criterios de éxito:** al menos 10 ejemplos; cinco categorías con cuatro casos cada una; `validar_dataset` sin problemas en el dataset original; validador detecta errores sembrados; unittest sin fallos; línea `DATASET PROPIO: VALIDACIONES APROBADAS`.

### Automatización

El workflow `.github/workflows/pruebas-offline.yml` ejecuta el script directamente y descubre las 16 pruebas por `unittest discover`. El job es offline y utiliza una credencial ficticia para sus tests; no realiza tuning.

## 4. Alcance curricular y límites

**Según la actividad Skillnest:** crear `dataset_tuning.py` con al menos 10 ejemplos propios, revisar balance, validar y comprobar que el validador detecta fallos; subirlo al repositorio. El envío real de `client.tunings.tune` es condicional («si tu cuenta tiene el tuning habilitado»).

**Extensiones del proyecto:** etiquetado de rutas para Booking Core AI, validación semántica de relación intención/ruta y pruebas automatizadas. No son requisitos textuales adicionales de Skillnest.

**No se afirma:** que el modelo haya aprendido, que la API admita el trabajo en la cuenta, que las clases generalicen con 20 casos, que el tuning tenga costo cero, ni que la actividad haya sido calificada por Skillnest. Para entrenamiento productivo se necesita mayor diversidad, partición de evaluación y criterios de seguridad.

**Continuidad:** comprobar la ejecución Windows, luego avanzar a U2.6 B30/L1 «Lo que cuesta personalizar», y evaluar RAG frente a PEFT según costo/datos/comportamiento.
