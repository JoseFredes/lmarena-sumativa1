# Bitácora de decisiones técnicas

Una línea por decisión, con su motivo, su impacto medido y el commit donde quedó.

| ID | Fecha | Decisión | Motivo | Impacto / cifra | Commit |
|---|---|---|---|---|---|
| D-001 | 2026-11-02 | Descartar `Anthropic/persuasion` y usar `lmarena-ai/arena-human-preference-140k` | El primero es de 2024, con modelos de una sola familia (Claude); no permite escalar. LMArena es de abr–jul 2025, 53 modelos | Se reescribe esquema, preprocesamiento y validación. 135.634 filas frente a ~3.940 | `2e1ab81` |
| D-002 | 2026-11-02 | Foco en dos preguntas: P1 (estilo vs. calidad) y P3 (posición y sesión) | P1 usa casi directo `conv_metadata`; P3 es calidad de dato y refuerza la validación | P2, P4 y P5 quedan como trabajo futuro | `2e1ab81` |
| D-003 | 2026-11-02 | Plantear los resultados como asociaciones, no como causas | Longitud y formato se confunden con calidad, modelo y tipo de prompt | Se declara en restricciones y supuestos | `be6a217` |
| D-004 | 2026-11-04 | Usar el dataset completo, sin muestrear para el análisis | Cargando 11 de 14 columnas ocupa 115 MB y carga en menos de 1 s | Se evita justificar una muestra; el muestreo queda para pruebas rápidas | `ae2f4f0` |
| D-005 | 2026-11-04 | Excluir las columnas de conversaciones al cargar | Pesan mucho y las respuestas de los modelos no se redistribuyen (licencia) | De 14 a 11 columnas; del texto solo se extraerá el largo del prompt | `ae2f4f0` |
| D-006 | 2026-11-04 | Python 3.12 en el entorno | El Python por defecto del equipo era 3.15; se eligió una versión estable con las librerías fijadas | `requirements.txt` con `==`; 25 pruebas en verde | `6716c57` |
| D-007 | 2026-11-04 | Reutilizar archivos ya descargados sin llamar al Hub | Evitar advertencias de la red en la ejecución y hacer la descarga idempotente | Cero advertencias en el notebook | `0800dce` |
| D-008 | 2026-11-04 | Muestreo por sesiones (no por filas) para pruebas rápidas | Con 10 % de filas, solo el 3,9 % de las sesiones con más de un voto quedan completas; por sesiones, el 100 % | Se declara que las filas no son independientes | `3ac488e` |
| D-009 | 2026-11-04 | Validar el dataset con `validar_dataset.py` del curso sobre una versión aplanada | El script solo lee CSV/Excel y el original es parquet anidado | 135.634 × 47; cumple los obligatorios, 1 aviso (0 % de nulos); CSV de 37,6 MB frente a 1,6 GB originales | rama `docs/report-draft` |
| D-010 | 2026-11-04 | Commits, código, carpetas y ramas en inglés | Convención del grupo | README actualizado | `dc90064` |
| D-011 | 2026-11-04 | Trabajar con ramas y pull request desde la redacción del informe | La guía pide ramas e integración mediante PR | Rama `docs/report-draft` | rama `docs/report-draft` |

## Pendientes de decisión

| ID | Tema | Estado |
|---|---|---|
| P-01 | Tratamiento de `tie` y `both_bad` (la ficha no los define; 27,5 % de los votos) | Se crean variables en F2; se decide en F3 |
| P-02 | Filtro por idioma (126 idiomas; 52,5 % inglés; 8,7 % `und`) | Se conserva todo en F2; se decide en F3 |
| P-03 | 10 filas con `model_a == model_b` | Decidir en F2_02 y verificar en F2_03 |
| P-04 | 61 y 58 respuestas con 0 tokens | Medir impacto y decidir en F2_02 |
| P-05 | Transformación de tokens (crudo vs. logaritmo vs. z-score) | Comparar alternativas en F2_02 |
| P-06 | Confirmar con el docente que el dataset no esté repetido en otro equipo | Pendiente |
