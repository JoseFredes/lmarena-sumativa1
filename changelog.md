# Registro de cambios

Historial resumido del proyecto, en el orden en que ocurrió. Cada fila remite a commits verificables en GitHub (`git log` completo en el repositorio). Los números de PR (#20, #21…) son los pull requests de donde salió el cambio.

## 1. Observaciones y acciones de mejora

La retroalimentación de la Sumativa 1 está resumida a partir de lo que quedó registrado en los PR #17 y #18; las revisiones internas son hallazgos del propio equipo al armar F3 y F4.

| Origen | Observación | Acción de mejora | Commit | Impacto técnico |
|---|---|---|---|---|
| Retroalimentación de la Sumativa 1 | Las referencias del informe a pruebas, entorno y generación local del dato procesado eran imprecisas. | Se corrigieron con la ejecución real y se refrescaron las evidencias (PR #17 y #18). | [`f5e6888`](https://github.com/JoseFredes/lmarena-sumativa1/commit/f5e6888), [`70c5a80`](https://github.com/JoseFredes/lmarena-sumativa1/commit/70c5a80) | Documentación: el informe remite a archivos que existen y dicen lo mismo. |
| Retroalimentación de la Sumativa 1 | El mapa conceptual no detallaba la relación entre sus elementos, su estado y sus evidencias. | Se detalló la relación entre sus elementos, su estado y sus evidencias, y se incorporó el mapa revisado (PNG) con su archivo editable (Excalidraw). | [`3432b65`](https://github.com/JoseFredes/lmarena-sumativa1/commit/3432b65) | Documentación: trazabilidad entre el mapa, el informe y el repositorio. |
| Retroalimentación de la Sumativa 1 | F3 estaba descrita de forma general. | Se precisó como núcleo algorítmico: diseño orientado a objetos, equivalencia de resultados y eficiencia. | [`70c5a80`](https://github.com/JoseFredes/lmarena-sumativa1/commit/70c5a80), [`3432b65`](https://github.com/JoseFredes/lmarena-sumativa1/commit/3432b65) | Documentación: F3 pasó a tener un alcance verificable. |
| Revisión interna de F3 | El README y el informe decían 0 % de nulos y tras aplanar `category_tag` quedan 17. | Se explicó el origen (dato original, 0,0125 %) y qué hace F3 con ellos (D-016). | [`e2f9d8b`](https://github.com/JoseFredes/lmarena-sumativa1/commit/e2f9d8b) | Documentación: las cifras coinciden con los datos. |
| Revisión interna de F3 | Los porcentajes de `tie` y `both_bad` del informe no coincidían con los datos. | Se corrigieron a 15,9 % y 11,6 %. | [`5d28e91`](https://github.com/JoseFredes/lmarena-sumativa1/commit/5d28e91) | Documentación: el 27,5 % total ya era correcto. |
| Revisión interna de F3 | El docstring de `derive_variables` decía log₁₀ y el código usa `np.log1p`. | Se corrigió el docstring. | [`e2f9d8b`](https://github.com/JoseFredes/lmarena-sumativa1/commit/e2f9d8b) | Documentación: evita un error al interpretar `tokens_log_*`. |
| Revisión interna de F3 | `ConversorCategoria` daba un aviso de pandas que pronto sería un error. | Se pasan a nulo los valores no vistos antes de convertir. | [`3bc4959`](https://github.com/JoseFredes/lmarena-sumativa1/commit/3bc4959) | Robustez: el código no depende de una conducta que va a cambiar. |
| Revisión interna de F3 | El aplanador usa la comprensión de listas, y `json_normalize` + `reindex` da lo mismo en 1,3 s contra 2,3 s. | Queda como decisión pendiente del equipo y documentada en el informe. | [`e9980cf`](https://github.com/JoseFredes/lmarena-sumativa1/commit/e9980cf) | Rendimiento: ahorro de cerca de 1 s sobre el dataset completo. |
| Revisión interna de F3 | Las evidencias guardadas (`pytest.txt`) decían 58 pruebas y hoy son 120 (150 con F4). | Se regeneraron con `make test` y `make evidence`. | [`aa33d54`](https://github.com/JoseFredes/lmarena-sumativa1/commit/aa33d54) | Documentación: el informe y las evidencias muestran lo mismo. |
| Revisión interna de F4 | El análisis simple no controlaba por el modelo de cada lado, y el objetivo del proyecto lo pide. | Se agregó un Bradley-Terry con control de estilo (`efecto_con_modelos`). | [`662181b`](https://github.com/JoseFredes/lmarena-sumativa1/commit/662181b) | Calidad analítica: el coeficiente del largo baja de 0,55 a 0,45 y el del formato sube de 0,04 a 0,11. |

## 2. Registro de cambios

| Fecha | Fase | Descripción | Commit | Justificación técnica |
|---|---|---|---|---|
| 2026-11-02 | F1 | Entorno, `requirements.txt` con versiones fijas, `Makefile` y estructura del repo | [`6716c57`](https://github.com/JoseFredes/lmarena-sumativa1/commit/6716c57) | Que cualquier integrante pueda reproducir el entorno con `make install`. |
| 2026-11-04 | F2 | Descarga del dataset con huellas SHA-256 | [`2c892ff`](https://github.com/JoseFredes/lmarena-sumativa1/commit/2c892ff), [`828d3ec`](https://github.com/JoseFredes/lmarena-sumativa1/commit/828d3ec) | Detectar descargas corruptas o distintas entre integrantes (D-013). |
| 2026-11-04 | F2 | Cuaderno de exploración con interpretaciones y hallazgos | [`f7811d8`](https://github.com/JoseFredes/lmarena-sumativa1/commit/f7811d8) | Medir antes de decidir: cada decisión de limpieza se apoya en una cifra. |
| 2026-11-04 | F2 | Muestreo por sesiones, no por filas | [`3ac488e`](https://github.com/JoseFredes/lmarena-sumativa1/commit/3ac488e) | Con 10 % de las filas solo el 3,9 % de las sesiones con más de un voto quedan completas; por sesiones, el 100 % (D-008). |
| 2026-11-04 | F2 | `validate_dataset` con informe de chequeos y pruebas | [`2078783`](https://github.com/JoseFredes/lmarena-sumativa1/commit/2078783) | Separar fallas críticas de advertencias (D-012) y dejar la validación repetible. |
| 2026-11-04 | F2 | Se revierte el transporte IPC de los kernels | [`cb42166`](https://github.com/JoseFredes/lmarena-sumativa1/commit/cb42166) | Fallaba en Windows y en rutas largas; se prefirió un aviso informativo de Jupyter (D-014). |
| 2026-11-06 | F1 | Problema, pregunta, objetivos y alcance de F1; el alcance se reduce a P1 | [`78d7cca`](https://github.com/JoseFredes/lmarena-sumativa1/commit/78d7cca), [`9c531c4`](https://github.com/JoseFredes/lmarena-sumativa1/commit/9c531c4) | Un solo foco (P1) hace el trabajo abarcable y evaluable (D-002). |
| 2026-11-07 | F2 | Funciones de limpieza: aplanar, convertir tipos y derivar variables | [`b1d826b`](https://github.com/JoseFredes/lmarena-sumativa1/commit/b1d826b), [`3c41aa4`](https://github.com/JoseFredes/lmarena-sumativa1/commit/3c41aa4) | Pipeline puro y sin pérdida de filas; `log1p` para los 61 y 58 casos de 0 tokens (D-015). |
| 2026-11-08 | F2 | Pruebas unitarias de limpieza y validación del dato procesado | [`88c931b`](https://github.com/JoseFredes/lmarena-sumativa1/commit/88c931b), [`9a5e44b`](https://github.com/JoseFredes/lmarena-sumativa1/commit/9a5e44b) | Cada paso queda con un `assert` y evidencia, como pide la guía. |
| 2026-11-08 | F2 | Rutas de checksums en formato POSIX en Windows (cierra #7) | [`b647539`](https://github.com/JoseFredes/lmarena-sumativa1/commit/b647539) | La verificación fallaba en Windows; se probó `make all` en varios equipos. |
| 2026-11-09 | F2 | `numeric_summary` y `formatting_summary` y ajuste de textos de F2_01/F2_02 | [`0091f1a`](https://github.com/JoseFredes/lmarena-sumativa1/commit/0091f1a), [`e0fe3b7`](https://github.com/JoseFredes/lmarena-sumativa1/commit/e0fe3b7), [`934dbce`](https://github.com/JoseFredes/lmarena-sumativa1/commit/934dbce) | Describir mejor la asimetría de tokens y mostrar la vista final del dataset. |
| 2026-11-10 | F2 | Diccionario de variables del dataset procesado | [`f89411d`](https://github.com/JoseFredes/lmarena-sumativa1/commit/f89411d) | Dejar documentadas las 54 columnas para fases posteriores. |
| 2026-11-11 | F2 | Distribución de tokens y calidad del dato (F2_04) | [`f6a03dd`](https://github.com/JoseFredes/lmarena-sumativa1/commit/f6a03dd) | Revisar ceros, empates, idioma `und` y mismo modelo en ambos lados. |
| 2026-11-13 | F2 | Se refrescan la ejecución y las evidencias de F2 | [`f5e6888`](https://github.com/JoseFredes/lmarena-sumativa1/commit/f5e6888), [`70c5a80`](https://github.com/JoseFredes/lmarena-sumativa1/commit/70c5a80), [`7cc938f`](https://github.com/JoseFredes/lmarena-sumativa1/commit/7cc938f) | Corregir las referencias del informe a pruebas, entorno y generación local del dato (retroalimentación de la Sumativa 1). |
| 2026-11-13 | F3 | Módulo de carga (`carga.py`) y pipeline de F2 en clases (`transformadores.py`) | [`651f7b2`](https://github.com/JoseFredes/lmarena-sumativa1/commit/651f7b2), [`0596cb3`](https://github.com/JoseFredes/lmarena-sumativa1/commit/0596cb3) | Pasar de funciones sueltas a `Transformador` + `Pipeline` con parámetros aprendidos en `ajustar()`. |
| 2026-11-14 | F3 | Se elimina `cat_creative_writing_score` y `cat_if_score` pasa a `Int8` (D-016) | [`1c5edc9`](https://github.com/JoseFredes/lmarena-sumativa1/commit/1c5edc9), [`3fe6f11`](https://github.com/JoseFredes/lmarena-sumativa1/commit/3fe6f11) | La columna repetía a `cat_creative_writing`; `cat_if_score` solo tiene enteros de 0 a 5. |
| 2026-11-14 | F3 | Módulo de medición con `timeit` y tabla de comparación | [`71a6de3`](https://github.com/JoseFredes/lmarena-sumativa1/commit/71a6de3) | Mediciones reproducibles: mínimo de 3 repeticiones y pico de `tracemalloc` aparte. |
| 2026-11-15 | F3 | 62 pruebas nuevas y prueba de equivalencia `pasos_f2()` = `clean_dataset()` (PR #20) | [`b1f14cf`](https://github.com/JoseFredes/lmarena-sumativa1/commit/b1f14cf) | Comprobar que reorganizar el código no cambió el resultado. |
| 2026-11-15 | F3 | Implementaciones alternativas y notebook de eficiencia (PR #21) | [`02bd5d2`](https://github.com/JoseFredes/lmarena-sumativa1/commit/02bd5d2), [`e9980cf`](https://github.com/JoseFredes/lmarena-sumativa1/commit/e9980cf) | Elegir con evidencia: `json_normalize` + `reindex` es 1,8 veces más rápido que la comprensión; la suma vectorizada, 48 veces más que el bucle. |
| 2026-11-15 | F3 | Notebook de POO y recursión; `tracemalloc.stop()` en `finally`; el derivador usa los parámetros aprendidos (PR #22) | [`a1271e8`](https://github.com/JoseFredes/lmarena-sumativa1/commit/a1271e8), [`1666412`](https://github.com/JoseFredes/lmarena-sumativa1/commit/1666412), [`fe59a28`](https://github.com/JoseFredes/lmarena-sumativa1/commit/fe59a28) | Que un error al medir no deje encendido el rastreo, y que lo aprendido en `ajustar()` se use de verdad. |
| 2026-11-16 | F3 | `ConversorCategoria` sin el aviso de pandas (PR #25) | [`3bc4959`](https://github.com/JoseFredes/lmarena-sumativa1/commit/3bc4959) | El aviso decía que con valores nuevos pronto sería un error; ahora se pasan a nulo antes de convertir. |
| 2026-11-16 | F3 | Textos de nulos y de `log1p` alineados; `make run` ejecuta F3; porcentajes de empates corregidos (PR #24) | [`e2f9d8b`](https://github.com/JoseFredes/lmarena-sumativa1/commit/e2f9d8b), [`5d28e91`](https://github.com/JoseFredes/lmarena-sumativa1/commit/5d28e91) | El README decía 0 % de nulos y quedaban 17 (0,0125 %); el informe decía 16,5 % y 11,0 % de empates y los datos dan 15,9 % y 11,6 %. |
| 2026-11-16 | F3 | Informe técnico de la Fase 3 y su PDF (PR #26) | [`8272c88`](https://github.com/JoseFredes/lmarena-sumativa1/commit/8272c88) | Entregable de la Sumativa 2 con las cifras de los dos notebooks. |
| 2026-11-16 | F3 | README con F3 y evidencias de pruebas actualizadas (PR #28) | [`aa33d54`](https://github.com/JoseFredes/lmarena-sumativa1/commit/aa33d54), [`b66abc4`](https://github.com/JoseFredes/lmarena-sumativa1/commit/b66abc4) | `pytest.txt` seguía en 58 pruebas y hoy son 120; se justifica por escrito por qué no se escala. |
| 2026-11-18 | F4 | Funciones de análisis de P1 y dos gráficos nuevos (PR #30) | [`662181b`](https://github.com/JoseFredes/lmarena-sumativa1/commit/662181b) | Regresión logística escrita con NumPy y validada con datos simulados de coeficientes conocidos. |
| 2026-11-18 | F4 | Notebook integrador `F4_01` con tres figuras (PR #30) | [`690c783`](https://github.com/JoseFredes/lmarena-sumativa1/commit/690c783) | Parte de `pasos_f3()` y no de un archivo guardado, así el análisis se repite desde el dato crudo. |

## 3. Impacto de las mejoras

| Dimensión | Qué cambió |
|---|---|
| Modularidad | De 3 funciones de limpieza (`flatten`, `convert_types`, `derive_variables`) a una jerarquía de 8 clases (`Transformador` y 7 hijas) y un `Pipeline`. El análisis de F4 vive en `arena.analisis`, no en el notebook. |
| Rendimiento | Se midió con `timeit` y `tracemalloc`. Suma vectorizada: 48 veces más rápida que el bucle. Aplanado: `json_normalize` + `reindex` es 1,8 veces más rápido que la comprensión (aún no aplicado al pipeline). |
| Pruebas | De 25 pruebas el 4 de noviembre (D-006) a 58 al cierre de F2, 120 al cierre de F3 y 150 con F4, todas sin red y con datos simulados. |
| Documentación | 16 decisiones registradas (`docs/decisiones.md`), un README por fase, dos informes (F1/F2 y F3) y notebooks con texto antes de cada bloque de código. |

## 4. Contribuciones por integrante

El detalle está en `git log --author` y en `gh pr list`. En resumen:

| Integrante | Aportes principales |
|---|---|
| José Fredes | Entorno, descarga y verificación, exploración, validación y pruebas (F2); pruebas, eficiencia y análisis de P1 (F3 y F4); consistencia de la documentación. |
| Alejandro Poirier | Definición del problema (F1), funciones de limpieza y notebook de limpieza (F2), notebook de POO y recursión (F3). |
| Angelo Morales | Instrucciones por notebook, diccionario de variables, módulos de carga, clases y medición de F3 (decisión D-016). |
| Valentina Carvajal | Muestra y validaciones del notebook F1, distribución de tokens (F2_04), informe de F1/F2, mapa conceptual y evidencias de control de versiones. |
