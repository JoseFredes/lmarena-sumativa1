# Bitácora de decisiones técnicas

Una línea por decisión, con su motivo, su impacto medido y el commit donde quedó.

| ID | Fecha | Decisión | Motivo | Impacto / cifra | Commit |
|---|---|---|---|---|---|
| D-001 | 2026-11-02 | Descartar `Anthropic/persuasion` y usar `lmarena-ai/arena-human-preference-140k` | El primero es de 2024, con modelos de una sola familia (Claude); no permite escalar. LMArena es de abr–jul 2025, 53 modelos | Se reescribe esquema, preprocesamiento y validación. 135.634 filas frente a ~3.940 | `2e1ab81` |
| D-002 | 2026-11-02 | Foco en una pregunta: P1 (estilo vs. calidad) | P1 usa casi directo `conv_metadata` | P2, P4 y P5 quedan como trabajo futuro | `2e1ab81` |
| D-003 | 2026-11-02 | Plantear los resultados como asociaciones, no como causas | Longitud y formato se confunden con calidad, modelo y tipo de prompt | Se declara en restricciones y supuestos | `be6a217` |
| D-004 | 2026-11-04 | Usar el dataset completo, sin muestrear para el análisis | Cargando 11 de 14 columnas ocupa 115 MB y carga en menos de 1 s | Se evita justificar una muestra; el muestreo queda para pruebas rápidas | `ae2f4f0` |
| D-005 | 2026-11-04 | Excluir las columnas de conversaciones al cargar | Pesan mucho y las respuestas de los modelos no se redistribuyen (licencia) | De 14 a 11 columnas; del texto solo se extraerá el largo del prompt | `ae2f4f0` |
| D-006 | 2026-11-04 | Python 3.12 en el entorno | El Python por defecto del equipo era 3.15; se eligió una versión estable con las librerías fijadas | `requirements.txt` con `==`; 25 pruebas en verde | `6716c57` |
| D-007 | 2026-11-04 | Reutilizar archivos ya descargados sin llamar al Hub | Evitar advertencias de la red en la ejecución y hacer la descarga idempotente | Cero advertencias en el notebook | `0800dce` |
| D-008 | 2026-11-04 | Muestreo por sesiones (no por filas) para pruebas rápidas | Con 10 % de filas, solo el 3,9 % de las sesiones con más de un voto quedan completas; por sesiones, el 100 % | Se declara que las filas no son independientes | `3ac488e` |
| D-009 | 2026-11-04 | Validar el dataset con `validar_dataset.py` del curso sobre una versión aplanada | El script solo lee CSV/Excel y el original es parquet anidado | 135.634 × 47; cumple los obligatorios, 1 aviso (0 % de nulos); CSV de 37,6 MB frente a 1,6 GB originales | `e7dd744` |
| D-010 | 2026-11-04 | Commits, código, carpetas y ramas en inglés | Convención del grupo | README actualizado | `dc90064` |
| D-011 | 2026-11-04 | Trabajar con ramas y pull request desde la redacción del informe | La guía pide ramas e integración mediante PR | PR #1 mergeado; este trabajo en `feat/env-validation-evidence` | `4d7b6bd` |
| D-012 | 2026-11-04 | Chequeos críticos que lanzan `ValueError` y advertencias que no | El caso `model_a == model_b` (10 filas) es raro pero no invalida el dato | 0 fallos críticos y 1 advertencia sobre el dato original | `2078783` |
| D-013 | 2026-11-04 | `make data` usa `CHECKSUMS.txt` versionado como referencia y no lo reescribe | Detectar descargas corruptas o distintas entre integrantes | 7 de 7 archivos coinciden en un clon limpio | `828d3ec` |
| D-014 | 2026-11-04 | No usar transporte IPC para silenciar el aviso del kernel en `nbconvert` | Falló en un clon con ruta larga y no existe en Windows | El log conserva un aviso informativo de Jupyter; se documenta en el README | `cb42166` |
| D-015 | 2026-11-07 | Aplanar `conv_metadata` y `category_tag` renombrando claves Markdown (`**` → `asterisk`, `__` → `underscore`) y derivar 7 variables (`format_a/b`, `tokens_log_a/b`, `longer_response`, `more_formatted`, `winner_binary`) sin eliminar filas en F2 | Conservar las 135.634 filas íntegras para evitar sesgos de selección prematuros y corregir la fuerte asimetría de tokens mediante `log1p` | De 11 a 54 columnas en `data/processed/arena_clean.parquet`; 0 fallos críticos en `F2_03` | `b1d826b`, `3c41aa4` |

## Pendientes de decisión para Fase 3

| ID | Tema | Estado |
|---|---|---|
| P-01 | Tratamiento de `tie` y `both_bad` (la ficha no los define; 27,5 % de los votos) | En F2 se creó `winner_binary` (`a`, `b`, `other`) conservando las 135.634 filas; en F3 se comparará con y sin empates |
| P-02 | Filtro o estratificación por idioma (126 idiomas; 52,5 % inglés; 8,7 % `und`) | Se conserva completo en F2 (`language` como `category`); en F3 se evaluará estratificar |
| P-03 | 10 filas con `model_a == model_b` | Se reportan como `WARN` en `validate_dataset` y se conservan en F2 para decidir su exclusión en los modelos de F3 |
| P-04 | 61 y 58 respuestas con 0 tokens | `log1p(0) = 0.0` las maneja sin indeterminación en F2; su sensibilidad se evaluará en F3 |
| P-05 | Transformación de tokens (crudo vs. logaritmo) | Resuelto en F2_02 (`D-015`): se conserva el conteo crudo y se agrega `tokens_log_a/b = log(1 + tokens)` |
| P-06 | Confirmar con el docente que el dataset no esté repetido en otro equipo | Confirmado |
