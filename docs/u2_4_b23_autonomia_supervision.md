# U2.4 · Bloque 23 / Lección 1 — Límites de autonomía y supervisión humana

**Programa:** Especialización IA 2026 · Skillnest / Accenture / CChIA  
**Fecha de preparación:** 09/11/2026 (Chile)  
**Estado:** validación principal ejecutada en Windows: pruebas automáticas, rechazo humano y supervisión de Gemini ante timeout y rechazo correctos. **Pendiente observar aprobación manual con `s`**.

## Fuente principal: qué enseña Skillnest

La lección clasifica las operaciones por impacto: riesgo bajo (consulta), medio (escritura reversible) y alto (acciones irreversibles o de impacto económico). Para las de riesgo alto propone: aprobación humana previa, tiempo máximo de espera, **rechazo por defecto** ante falta de aprobación y registro de la decisión con herramienta, argumentos, resultado y momento.

El material usa input() y select.select(). **Aclara que select() sobre stdin no sirve en Windows**, por lo que ese detalle no se copia sin adaptación.

## Aplicación a Booking Core AI

**Código:** [supervision_b23_booking_core.py](../src/supervision_b23_booking_core.py)

- consultar_reserva_simulada: lectura de reservas ficticias.
- cancelar_reserva_simulada: operación considerada de riesgo alto por su equivalente real; solo puede cambiar el diccionario ficticio en memoria después de autorización independiente.
- ArgumentosCancelacion: esquema Pydantic con reserva_id (DEMO-###) y motivo; **no incluye un campo de aprobación que Gemini pueda manipular**.
- EntornoReservasDemo: contiene reservas DEMO-001 y DEMO-002, registro temporal de aprobaciones y prevención de reintentos automáticos.
- DecisionSupervisor: registra aprobado, rechazado, timeout, falta de canal y error de aprobador.
- esperar_aprobacion_con_timeout: espera una decisión humana por teclado; usa msvcrt en Windows y select en sistemas compatibles, siempre con rechazo por defecto.

**Alcance:** no hay conexión a Booking Core, Supabase, correo ni pagos. No existen reservas reales en este laboratorio.

**Diferencia respecto del curso:** sustituimos el reembolso del ejemplo por una cancelación de reserva ficticia y usamos msvcrt para la terminal de Windows. El material del curso menciona como alternativa para Windows un hilo con Event; aquí se eligió una solución sin hilo bloqueado, válida para el laboratorio de consola, no para un servicio productivo.

### Pruebas automáticas y aprobación humana

El modo de prueba usa aprobadores ficticios programados para aceptar o rechazar. **No constituyen decisiones humanas reales**. Solo comprueban que la herramienta nunca cambia el estado cuando falta una decisión externa válida.

Los modos --interactivo y --agente sí piden al operador que responda s/n y Enter, pero solo afectan reservas ficticias.

## Ejecución en PowerShell

~~~powershell
cd C:\Users\nbello\dev\especializacion-ia-2026
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
~~~

Revisar estado y sincronizar la rama local con la versión publicada en main; **ejecutar el merge únicamente si Git está limpio**:

~~~powershell
git status --short
git fetch origin
git merge --no-ff origin/main -m "merge: incorporar supervision humana B23"
~~~

No ejecutar reset --hard, stash pop ni push sobre la rama divergente sin revisión.

### A. Primera prueba: sin Gemini y sin interacción

~~~powershell
python -m src.supervision_b23_booking_core
~~~

Comprueba rechazo, ausencia de canal, timeout inmediato, aprobación de prueba, validación Pydantic, prevención de solicitudes repetidas y registro de auditoría.

**Salida final observada en Windows:**

~~~text
B23/L1: CONTROLES DE APROBACION SIMULADA VERIFICADOS.
~~~

### B. Aprobación humana por consola (sin Gemini)

~~~powershell
python -m src.supervision_b23_booking_core --interactivo --timeout 60
~~~

Primero ejecutar y responder **n**: la reserva DEMO-001 debe permanecer confirmada. Volver a ejecutar y responder **s**: debe quedar cancelada **solo dentro del proceso ficticio**. Sin respuesta en 60 segundos, se rechaza.

### C. Integración opcional con Gemini real

~~~powershell
python -m src.supervision_b23_booking_core --agente --timeout 60
~~~

Gemini recibe una petición de cancelación de DEMO-001, puede solicitar la herramienta, pero **la decisión es del operador en la consola**. Se comprueba la selección en intermediate_steps y la coherencia entre aprobación, bitácora y estado ficticio. Este modo consume API y requiere una terminal interactiva.

Salida esperada si Gemini solicita la herramienta y el registro queda coherente:

~~~text
B23/L1: SUPERVISION DEL AGENTE VERIFICADA.
~~~

## Riesgos residuales y producción

- Una consulta de datos reales puede implicar riesgos de acceso o privacidad, aunque sea de solo lectura.
- El supervisor y el cliente no se autentican en este laboratorio. Para producción, verificar identidad y permisos.
- La auditoría es volátil; un sistema real requiere persistencia, integridad, retención y controles de acceso.
- Un sistema real debe vincular la aprobación al conjunto exacto de argumentos, y usar idempotencia y transacciones frente a concurrencia.
- Nunca autorizar una acción por el texto o una variable que el propio LLM pueda rellenar.
- Sin canal o con timeout, la opción segura es **no ejecutar**.

## Checklist académico

- [x] Material del curso revisado: riesgos, consentimiento humano, timeout y registro.
- [x] Código de laboratorio publicado en GitHub.
- [x] Pruebas sin API preparadas.
- [x] Confirmación por consola y rechazo por defecto implementados.
- [x] Modo opcional de Gemini con trazas implementado.
- [x] Pruebas sin API verificadas en Windows (rechazo, timeout, ausencia de supervisor, aceptación ficticia, validación y auditoría).
- [x] Rechazo manual `n` verificado; reserva DEMO-001 permanece confirmada.
- [ ] Aprobación manual `s` verificada (sigue pendiente).
- [x] Modo Gemini probado: caso timeout y caso rechazo manual; ambos bloquearon la cancelación.
- [ ] Cierre de cobertura completa de la lección: falta probar la ruta humana `s`; el camino de aprobación con doble programado sí fue validado.
- [ ] Entrega o evaluación institucional (no confirmadas).

**Siguiente lección Skillnest:** Bloque 23 — «Qué revela la traza de decisión de un agente».

## Evidencia observada: 09/11/2026

El estudiante sincronizó la rama local con `origin/main` mediante merge exitoso, verificó estado Git limpio y ejecutó las pruebas siguientes en PowerShell:

### Prueba sin Gemini — pasada

```powershell
python -m src.supervision_b23_booking_core
```

```text
RECHAZO OK: no se cancela ni se repite la solicitud.
SIN CANAL/TIMEOUT OK: rechazo por defecto.
APROBACION FICTICIA OK: solo cambia el diccionario demo.
PYDANTIC OK: rechaza un identificador fuera de DEMO-###.
B23/L1: CONTROLES DE APROBACION SIMULADA VERIFICADOS.
```

El registro de la aprobación **programada de prueba** informó `aprobado=True`, `decision='aprobado'`, `origen='doble_prueba'`, `ejecutada=True`. **No fue una aprobación humana.**

### Rechazo interactivo — pasado

Con `--interactivo --timeout 60` el supervisor respondió **n**:

```text
Cancelacion SIMULADA de DEMO-001 NO ejecutada. Decision: rechazado.
ESTADO FINAL: confirmada
AUDITORIA: aprobado=False, decision='rechazado',
          origen='consola_demo', ejecutada=False
```

### Dos ejecuciones reales con Gemini — pasadas

En ambas ejecuciones el agente invocó `cancelar_reserva_simulada` con `reserva_id='DEMO-001'` y `motivo='cambio de planes'`. La traza `intermediate_steps` confirmó la herramienta utilizada y sus argumentos.

1. **Sin decisión dentro de 60 segundos:** `decision='timeout'`, `aprobado=False`, `ejecutada=False`, reserva **confirmada**; terminal: `B23/L1: SUPERVISION DEL AGENTE VERIFICADA.`
2. **Supervisor responde n:** `decision='rechazado'`, `aprobado=False`, `ejecutada=False`, reserva **confirmada**; misma salida de validación.

Se comprobó que la propuesta de Gemini no altera el estado sin aprobación externa. Los valores se guardaron en memoria y se registraron con instante UTC. Estos ensayos **no** cancelaron ninguna reserva real.

### Única comprobación pendiente

Falta ejecutar la ruta de **aprobación humana positiva**, idealmente sin consumir llamadas a Gemini:

```powershell
python -m src.supervision_b23_booking_core --interactivo --timeout 60
```

Responder **s** y Enter dentro del plazo. El estado **esperado**, todavía no observado, es `ESTADO FINAL: cancelada` y `aprobado=True`, `ejecutada=True`, `origen='consola_demo'`. Esta cancelación solo afecta el diccionario ficticio del proceso Python.

**Estado de la lección:** controles de rechazo y de seguridad validados, con el camino aprobado cubierto únicamente por un doble de prueba. Pendiente la comprobación humana de aprobación para declarar cobertura práctica completa. **Ninguna calificación o entrega institucional ha sido confirmada.**
