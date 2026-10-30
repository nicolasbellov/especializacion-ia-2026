# U2.2 · Bloque 17 Core — Guía de ejecución y entrega

**Fuente:** enunciado oficial Skillnest «Interpreta tus resultados y documenta sus límites [Actividad core]» y captura de la pantalla de entrega, facilitados el 29/10/2026.  
**Estado inicial verificable:** **3/20 respuestas reales**, **0/10 revisiones humanas**, documento preliminar en [limites_metrica.md](limites_metrica.md). No es una entrega final.

## Requisitos de la actividad oficial

1. **20 respuestas realmente generadas por `consultar_modelo`**, con precisión, cobertura y F1 calculados por `calcular_metricas` y guardados.
2. **Al menos 10 valoraciones humanas**, seleccionando casos con F1 menor y mayor; rúbrica de factual (sí/no/parcialmente), completitud (sí/no/parcialmente), contradicción (sí/no), cada una con una justificación.
3. **Documento de límites basado en los hallazgos de esas revisiones**, con qué mide, modos de falla con ejemplos propios, tamaño/criterio de muestra y recomendación específica.
4. **Publicar los archivos en Git y remitir un enlace** en la pantalla Skillnest. No confundir enlace entregado con evaluación aprobada.

## Preparación en PowerShell

Desde `C:\Users\nbello\dev\especializacion-ia-2026`:

```powershell
git pull --ff-only origin main

# 1. Verificar pruebas offline del proyecto y del nuevo flujo Core
.\venv\Scripts\python.exe -m pytest -q .\test_pipeline_texto.py .\test_metricas_texto.py .\test_limitaciones_metricas_b16.py .\test_evaluar_salidas_b16.py .\test_revision_cualitativa_b17.py .\test_core_b17.py

# 2. Vista previa SIN llamar a la API
.\venv\Scripts\python.exe .\core_b17_generar.py --plan
```

Se esperan **55 pruebas en total** (40 previas + 15 nuevas), todavía **no verificadas en Windows** para este cambio. Las pruebas nuevas emplean textos simulados exclusivamente para controlar errores de programa: **no son evidencia de 20 respuestas reales**.

## Generar el corpus real

```powershell
# 3. Generar SOLO las 17 consultas faltantes con tu cliente real
.\venv\Scripts\python.exe .\core_b17_generar.py --generar --max-nuevas 17
```

**Atención:** esta orden sí hace llamadas externas a Gemini, puede consumir cuota o generar cargos. Utiliza la `GEMINI_API_KEY` local ya configurada en `.env`; no copiar, imprimir ni publicar la clave. Se mantienen intactas las **tres** salidas reales de B15. Se generan **17 consultas nuevas** de fundamentos técnicos, con sus propias referencias, y se guardan las respuestas a medida que llegan en `resultados_core_b17.json`.

Si hay errores de red, cuota o límite, los registros exitosos ya guardados no se pierden. Repetir **la misma orden** cuando la API vuelva a estar disponible; solo consultará los casos pendientes. La evidencia del curso no puede completarse con respuestas inventadas ni mocks de pruebas.

**Confirmar en consola:** `Resultado: 20/20 respuestas REALES.`

## Aplicar las diez revisiones HUMANAS

```powershell
# 4. Seleccionar cinco F1 bajos y cinco altos, sin repetidos
.\venv\Scripts\python.exe .\core_b17_revisar.py --preparar

# 5. Leer y calificar personalmente las diez parejas referencia/respuesta
.\venv\Scripts\python.exe .\core_b17_revisar.py --revisar

# 6. Comprobar que las diez valoraciones incluyen justificación
.\venv\Scripts\python.exe .\core_b17_revisar.py --validar

# 7. Generar informe a partir de las diez valoraciones, SIN inventar juicios
.\venv\Scripts\python.exe .\core_b17_revisar.py --informe
```

Cada caso muestra consulta, referencia y **respuesta real**. La persona revisora responde los tres criterios y escribe un motivo concreto. El sistema guarda cada caso inmediatamente en `revision_manual_core_b17.json`. Si se interrumpe, basta con ejecutar nuevamente `--revisar`: continuará donde quedó. El informe `docs/revision_manual_core_b17.md` **transcribe** dichas valoraciones.

La rúbrica solo compara el texto con la referencia; si surge una cuestión factual externa, verificarla con una fuente apropiada antes de asegurar que es verdadera.

## Documentar los límites propios y publicar evidencia

Leer `docs/revision_manual_core_b17.md` y actualizar [limites_metrica.md](limites_metrica.md) para que, además de los ejemplos educativos ya conocidos, presente:

- Ejemplos observados en el **corpus real de 20**, referenciando cada caso concreto revisado y su justificación.
- **Muestra: 10 revisados / 20 generados**, fecha(s), **5 F1 inferiores + 5 superiores**, una vez confirmado por la ejecución.
- Recomendación fundada en los hallazgos, no copiada de Skillnest.
- Distinción entre limitaciones léxicas generales y errores realmente identificados en las respuestas propias.

**Ficheros de evidencia esperados cuando se termine:**
- `resultados_core_b17.json` — 20 consultas, referencias, respuestas reales y métricas.
- `revision_manual_core_b17.json` — 10 valoraciones y justificaciones humanas.
- `docs/revision_manual_core_b17.md` — informe trazable de las diez revisiones.
- `docs/limites_metrica.md` — límites actualizados con los hallazgos propios.

Para publicar a través del flujo ya usado en este proyecto, **compartir estos archivos de resultados en el chat** después de generarlos; se pueden integrar al repositorio mediante una rama, PR y fusión, y después sincronizar `main` en Windows. No subir credenciales ni información confidencial; el repositorio es público.

## Comprobación final y entrega en Skillnest

No marcar como cerrada la unidad ni pulsar **«Enviar entrega»** hasta validar los cuatro archivos y confirmar que representan 20 respuestas reales y 10 juicios humanos. En la pantalla observada se permite **«Enlace (Drive, etc.)»**: usar el enlace GitHub verificado de la entrega **una vez publicada**. Guardar comprobante de envío y resultado institucional por separado.

**Siguiente unidad tras cerrar Core:** U2.3, Bloque 18 (LangChain: templates parametrizables).
