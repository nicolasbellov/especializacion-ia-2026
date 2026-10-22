
# Especialización en Desarrollo con IA Generativa — 2026

## Miniaplicación Gate 1 — Módulo 1

Proyecto académico desarrollado para la Especialización en Desarrollo con IA Generativa de Skillnest, Accenture y CChIA.

### 1. Objetivo

Implementar una miniaplicación Python que consuma un modelo de inteligencia artificial generativa mediante una API REST.

La aplicación permite:

- Construir solicitudes HTTP para Gemini.
- Autenticarse mediante una API key almacenada fuera del repositorio.
- Enviar preguntas y recibir respuestas del modelo.
- Incorporar instrucciones de sistema y esquemas JSON.
- Extraer y validar respuestas estructuradas.
- Gestionar errores HTTP, conexión, tiempo de espera y JSON.
- Ejecutar pruebas automatizadas.

### 2. Tecnologías

- Python 3.12.8 (versión utilizada durante el desarrollo).
- Google Gemini API.
- requests.
- python-dotenv.
- Git y GitHub.
- unittest.

Modelo utilizado y validado:
`gemini-3.5-flash-lite`

El modelo puede cambiarse mediante la variable `GEMINI_MODEL`.

### 3. Estructura del proyecto

- `src/consumir_gemini.py`: cliente REST principal.
- `src/comparar_modelos_u14.py`: comparación de modelos.
- `src/reanudar_comparacion_u14.py`: recuperación de mediciones.
- `prompts/`: banco de prompts y validaciones U1.5.
- `tests/`: pruebas automatizadas y ejercicios.
- `docs/`: arquitectura, evidencias y mediciones.
- `requirements.txt`: dependencias fijadas.
- `.env.example`: ejemplo de configuración.
- `.gitignore`: exclusiones de seguridad.
- `modulos/`: organización del programa académico.

### 4. Instalación

Clonar el repositorio:

```powershell
git clone https://github.com/nicolasbellov/especializacion-ia-2026.git
cd especializacion-ia-2026
```

Crear el entorno virtual:

```powershell
py -3.12 -m venv venv
```

Si no está disponible el lanzador de Python 3.12, utilizar una instalación compatible de Python 3.10 o superior.

Instalar dependencias:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Comprobar su consistencia:

```powershell
.\venv\Scripts\python.exe -m pip check
```

No es obligatorio activar el entorno virtual en PowerShell. Los comandos utilizan directamente su intérprete Python.

### 5. Configuración

Crear el archivo local:

```powershell
Copy-Item .env.example .env
```

Editar `.env` e incorporar una credencial real:

```dotenv
GEMINI_API_KEY=tu_clave_real
GEMINI_MODEL=gemini-3.5-flash-lite
```

La credencial debe obtenerse mediante el proveedor de la API.

**Seguridad:** nunca subir `.env` ni compartir claves reales. El archivo se encuentra excluido mediante `.gitignore`.

### 6. Ejecución principal

Desde la raíz del proyecto:

```powershell
.\venv\Scripts\python.exe -m src.consumir_gemini
```

Si la conexión funciona, la aplicación muestra un texto generado por Gemini.

Ejemplo de una ejecución validada durante el desarrollo:

```text
Resultado: ¡Conexión establecida y funcionando perfectamente!
```

Para comprobar el código de salida en PowerShell:

```powershell
$LASTEXITCODE
```

El valor esperado es `0` cuando finaliza correctamente.

Ante errores controlados, el programa muestra un mensaje y termina con código `1`.

### 7. Pruebas automatizadas

Ejecutar:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

Resultado verificado en el entorno de desarrollo:

```text
Ran 19 tests

OK
```

Las pruebas cubren extracción de respuestas, errores de conexión, autenticación simulada, timeouts, estructura de peticiones y validación JSON.

Estas pruebas utilizan simulaciones para verificar el cliente sin necesitar llamadas reales al proveedor.

### 8. Respuestas JSON estructuradas

El cliente permite configurar instrucciones de sistema y un esquema de respuesta mediante:

```python
armar_peticion(
    pregunta,
    system_instruction,
    response_schema
)
```

Posteriormente, la salida puede procesarse con:

```python
parsear_respuesta_json(texto, response_schema)
```

Ejemplo de respuesta validada durante U1.5:

```json
{
  "intencion": "crear",
  "confianza": 0.99
}
```

La validación básica verifica claves obligatorias, tipos de datos y restricciones definidas en el esquema.

### 9. Manejo de errores

La aplicación contempla:

- Preguntas vacías o inválidas.
- Errores de autenticación HTTP 401/403.
- Solicitudes rechazadas HTTP 400.
- Límites de cuota HTTP 429.
- Respuestas HTTP no exitosas, incluido 503.
- Fallos de conexión y timeout.
- Respuestas sin JSON válido.
- Estructuras de respuesta inesperadas.

Los errores se comunican mediante excepciones y mensajes controlados.

### 10. Comparación de modelos — U1.4

Los scripts de U1.4 permiten registrar latencia, consumo de tokens, respuestas y costos estimados.

Las mediciones se almacenan en:

`docs/mediciones_modelos_u14.csv`

Las tarifas utilizadas son referencias del ejercicio y deben comprobarse nuevamente antes de utilizarlas para estimaciones actuales.

Estos scripts son complementarios y no forman parte de la ejecución principal del Gate 1.

**Nota:** ejecutarlos genera nuevas solicitudes reales a la API y podría consumir cuota o generar cargos.

### 11. Documentación de arquitectura

El directorio `docs/` contiene las decisiones de arquitectura, los diagramas y las evidencias técnicas generadas durante el Módulo 1.

La documentación se conserva para evolucionar la aplicación durante los módulos siguientes.

### 12. Estado del proyecto

- Cliente REST implementado.
- Manejo básico de errores implementado.
- Pruebas automatizadas: 19/19 aprobadas.
- Conexión real con Gemini verificada.
- Respuesta JSON estructurada verificada.
- Ensayo de instalación limpia: completado satisfactoriamente desde GitHub, con 19/19 pruebas aprobadas. Evidencia en docs/registro_ensayo_gate1.md.
- Gate 1: pendiente de evaluación formal.

## Evolución del programa

- Módulo 1: fundamentos técnicos y consumo de API.
- Módulo 2: orquestación, agentes y RAG.
- Módulo 3: integración, despliegue y validación end-to-end.

El repositorio constituye una base incremental para los siguientes módulos de la especialización.

## Evidencia del Gate 1

Se realizó un ensayo de instalación limpia
clonando el repositorio directamente desde GitHub.

Resultados:
- 19/19 pruebas automatizadas aprobadas.
- Instalación de dependencias sin conflictos.
- Consumo exitoso de la API Gemini.
- Código de salida 0.
- Exclusión de credenciales locales verificada.

Consultar el [registro completo del ensayo](docs/registro_ensayo_gate1.md).
