# U1.5 · Banco de prompts de agenda (Skillnest)

## Integración con el repositorio existente

Los archivos de este paquete están listos para copiarse **en la raíz** de `nicolasbellov/especializacion-ia-2026`, respetando su estructura.

- `src/consumir_gemini.py` — **actualiza el archivo existente**. Conserva `armar_peticion()` con retorno `(url, headers, body)`, las demás funciones y compatibilidad con llamadas anteriores. Se añade `system_instruction`, `response_schema` y el parser JSON genérico.
- `prompts/banco.py` — tres prompts ficticios de agenda.
- `prompts/test_consistencia.py` — tres llamadas reales por prompt; genera `prompts/registro_resultados.json`.
- `tests/test_prompts_u15.py` — pruebas unitarias **locales**, sin conexión a Gemini.

No se incluyen credenciales ni un `registro_resultados.json` inventado.

## En Windows (PowerShell), desde la raíz del repositorio

```powershell
.\.venv\Scripts\Activate.ps1
python -m unittest discover -s tests -v
python -m prompts.test_consistencia
```

> Si el entorno virtual se llama `venv` (sin punto), usa `.\venv\Scripts\Activate.ps1`.

Comprueba que `.env` contiene `GEMINI_API_KEY=...` (nunca compartas ni commitees la clave). El script usa `gemini-3.8-flash` como el repositorio, pero puedes definir `GEMINI_MODEL=gemini-3.6-flash` en `.env` para reproducir el modelo de Skillnest. Ambos identificadores existen en la documentación oficial; la disponibilidad de tu cuenta debe comprobarse al ejecutar.

## Qué significa el resultado

- `exitos_estructura`: JSON válido, objeto y claves/tipos/enums requeridos correctos.
- `exitos_contenido`: además coincide con los valores conocidos de la entrada ficticia.
- `fallos`: detalle por intento, incluyendo problemas HTTP, validación y discrepancias de contenido.

La salida NO significa que exista una cita real. Ningún prompt consulta disponibilidad ni escribe en la agenda.

## Entrega una vez ejecutadas las pruebas reales

Verifica que `prompts/registro_resultados.json` existe, inspecciónalo y después:

```bash
git status
git add src/consumir_gemini.py prompts/banco.py prompts/test_consistencia.py prompts/registro_resultados.json tests/test_prompts_u15.py
git commit -m "agrega banco de prompts de agenda y validacion de consistencia"
git push
```

No incluir `.env`. Si las respuestas son inconsistentes, corregir instrucciones, repetir pruebas y documentar el cambio antes del commit.
