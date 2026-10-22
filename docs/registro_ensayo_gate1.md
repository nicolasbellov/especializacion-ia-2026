
# Gate 1 — Registro de ensayo de instalación limpia

## 1. Identificación

- Programa: Especialización en Desarrollo con IA Generativa 2026.
- Instituciones: Skillnest, Accenture y CChIA.
- Módulo: 1 — Fundamentos técnicos.
- Bloque: 11 — Entrega y verificación.
- Fecha del ensayo: 21/10/2026.
- Sistema operativo: Windows / PowerShell.
- Python: 3.12.8.
- Repositorio: https://github.com/nicolasbellov/especializacion-ia-2026
- Rama evaluada: main.
- Commit evaluado: 4243baf6891a6efa24980685fe5f53f01312cd67.

## 2. Objetivo

Verificar que la miniaplicación pueda clonarse desde
GitHub, instalarse y ejecutarse en un entorno virtual
nuevo, utilizando únicamente las dependencias
declaradas y las instrucciones documentadas.

## 3. Procedimiento ejecutado

### 3.1. Clonación remota

Se clonó el repositorio directamente desde GitHub
en una carpeta independiente:

    git clone https://github.com/nicolasbellov/especializacion-ia-2026.git prueba-gate1-remoto

Resultado: clonación exitosa.

El commit recuperado coincidió con el commit
publicado en la rama main.

### 3.2. Reconstrucción del entorno

Se creó un entorno virtual nuevo utilizando
Python 3.12.

Se instalaron las dependencias exclusivamente
desde requirements.txt.

Resultado de pip check:

    No broken requirements found.

No fue necesario reutilizar el entorno virtual
del proyecto original.

### 3.3. Configuración de credenciales

Se creó el archivo .env utilizando .env.example.

La API key se incorporó manualmente en el archivo
local, sin agregarla al repositorio.

Modelo configurado:

    gemini-3.5-flash-lite

### 3.4. Pruebas automatizadas

Comando ejecutado:

    .\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v

Resultado:

    Ran 19 tests in 0.055s

    OK

Las 19 pruebas se ejecutaron satisfactoriamente.

### 3.5. Ejecución de la miniaplicación

Comando:

    .\venv\Scripts\python.exe -m src.consumir_gemini

Respuesta obtenida:

    Resultado: ¡Conexión establecida y funcionando correctamente!

Código de salida del proceso:

    0

Se confirmó el consumo funcional de la API Gemini.

### 3.6. Verificación de seguridad

Se ejecutaron las comprobaciones:

    git status --short
    git check-ignore -v .env
    git ls-files -- .env

Resultados:

- Repositorio sin cambios pendientes.
- .env excluido por la regla 7 de .gitignore.
- .env no incluido entre los archivos versionados.
- No fue necesario incorporar credenciales al código.

Estas verificaciones son controles básicos de
seguridad y no reemplazan una auditoría exhaustiva.

## 4. Hallazgos y correcciones

### 4.1. Activación del entorno virtual

Hallazgo:
PowerShell bloqueó Activate.ps1 debido a su
política de ejecución de scripts.

Solución:
Se utilizó directamente el intérprete Python
del entorno virtual.

No fue necesario modificar la política de seguridad.

### 4.2. Disponibilidad del modelo Gemini

Hallazgo:
gemini-3.8-flash devolvió HTTP 503 durante
las pruebas previas.

Solución:
Se configuró gemini-3.5-flash-lite, obteniendo
respuestas satisfactorias.

La configuración quedó documentada en .env.example.

### 4.3. Documentación y punto de entrada

Se actualizó README.md con instrucciones
de instalación, configuración, ejecución y pruebas.

Se modificó el punto de entrada del cliente
para finalizar con código de salida distinto de cero
cuando ocurre un error controlado.

Estas correcciones fueron realizadas antes
del ensayo final.

## 5. Resultado consolidado

- Clonación desde GitHub: APROBADA.
- Instalación de dependencias: APROBADA.
- Consistencia de dependencias: APROBADA.
- Pruebas automatizadas: 19/19 APROBADAS.
- Consumo funcional de Gemini: APROBADO.
- Ejecución sin errores: APROBADA.
- Exclusión local de credenciales: CONFIRMADA.
- Reproducibilidad en entorno virtual nuevo: VALIDADA.

## 6. Limitaciones

El ensayo se realizó en una carpeta independiente
del mismo computador utilizado para desarrollar.

Aunque se creó un entorno virtual nuevo y se
clonó desde GitHub, el ensayo comparte el sistema
operativo, la instalación base de Python y
posibles recursos globales del equipo original.

Por lo tanto, el resultado demuestra
reproducibilidad local, pero no garantiza por sí
solo compatibilidad con cualquier otro computador.

## 7. Conclusión

El ensayo de instalación limpia desde GitHub
finalizó satisfactoriamente.

La miniaplicación pudo reconstruirse y ejecutarse
sin utilizar el entorno virtual original.

Se verificaron las dependencias, las pruebas
automatizadas, la conexión real con Gemini
y las exclusiones básicas de seguridad.

El proyecto presenta evidencia técnica favorable
para los criterios no compensables del Gate 1.

La aprobación formal y la calificación final
corresponden al equipo evaluador de Skillnest.
