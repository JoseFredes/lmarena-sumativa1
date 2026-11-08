# Informe técnico · Avance del proyecto, Fases 1 y 2

> **Borrador de trabajo.** Sigue el orden y la numeración de la guía de desarrollo de la Sumativa 1 (apartados 4.1 a 4.15) para que el índice del informe final coincida con lo que pide la rúbrica.
<!-- REVISIÓN FINAL ANTES DE LA ENTREGA:
Cuando el informe esté aproximadamente al 90% de avance, actualizar y verificar la información de todas las secciones.
Revisar especialmente cifras, resultados, estado de los notebooks, contribuciones, commits, Pull Requests, bibliografía y evidencias del repositorio.
Confirmar que las capturas correspondan a la versión definitiva del proyecto.
-->
> Estado de cada apartado: ✅ redactado · 🟡 redactado con datos pendientes · ⬜ por redactar.
> Marcas: `[PENDIENTE]` depende de trabajo aún no hecho; `TODO(humano)` lo debe completar el grupo; `[VERIFICAR]` es un dato que hay que confirmar antes de entregar.
> Este texto es un punto de partida: cada integrante debe leerlo, corregirlo y dejarlo en su propia voz, porque el informe debe ser de elaboración propia.

---

## 1. Portada e índice · 🟡

| Campo | Contenido |
|---|---|
| Curso y código | MCDI500 · Programación para la Ciencia de Datos (sección MCDI500.202683.1529.EL.ON) `[VERIFICAR]` |
| Programa | Magíster en Ciencia de Datos e Inteligencia Artificial · Universidad Andrés Bello |
| Título del proyecto | ¿Contenido o formato? Preferencias humanas en LMArena |
| Subtítulo | Avance del proyecto, Fases 1 y 2 |
| Integrantes | Alejandro Poirier Gomez, Angelo Morales Serrano, Jose Fredes Acevedo y Valentina Carvajal Jacob |
| Grupo | 6 |
| Docente responsable | Dr. Omar Salinas Silva |
| Fecha | 8 de noviembre de 2026 |
| Repositorio | https://github.com/JoseFredes/lmarena-sumativa1 |

**Índice:** automático, generado desde los estilos de título (Título 1, 2 y 3) y actualizado justo antes de exportar. Los apartados son los de este documento, en el mismo orden.

**Observaciones sobre la plantilla institucional** (`f1_s01_evaluacion_entregable.docx`), a resolver antes de entregar:
- Dice "MCDIA500" y "AVANCE DEL PROYECTO FASE 1"; la entrega cubre las Fases 1 y 2 y el curso se llama MCDI500.
- La plantilla original solo contempla "Nombre integrante/s", "Curso" y "Fecha". En esta portada se agregaron el título del proyecto, docente, grupo y enlace al repositorio. Revisar si faltan otros datos institucionales solicitados.
- La lista de "Apartados" no incluye codificación funcional, preprocesamiento, validación técnica ni los notebooks de la Fase 2.
- No trae índice automático ni estilos de título: hay que agregarlos.
- Nombre del archivo: la instrucción pide `f1_s01_evaluacion_entregable_grupox` y a la vez "no superar los 20 caracteres", lo que es incompatible (el nombre base ya tiene 35). Consultar al docente.

---

## 2. Introducción y contextualización · ✅

Los modelos de lenguaje de gran tamaño se comparan cada vez más mediante evaluaciones basadas en preferencia humana: una persona formula una pregunta, recibe dos respuestas anónimas de modelos distintos y vota por la que prefiere. La plataforma más conocida de este tipo es Chatbot Arena, hoy LMArena, descrita por Chiang et al. (2024) como una plataforma abierta que recoge comparaciones por pares de forma masiva. Sus resultados se utilizan para ordenar modelos y, en la práctica, para decidir cuáles se adoptan.

Ese uso supone que el voto refleja la calidad de la respuesta. Sin embargo, también podría reflejar su estilo: una respuesta más larga o con más listas, encabezados y negritas puede parecer mejor sin serlo. La literatura ya documenta sesgos de este tipo. Dubois et al. (2024) muestran que los evaluadores automáticos favorecen respuestas más largas y proponen corregirlo, y Wu y Aji (2025) encuentran que anotadores colectivos, expertos y modelos pueden calificar mejor respuestas con errores factuales que respuestas cortas o con errores gramaticales. Si un sesgo de forma afecta los rankings, estos miden mal la capacidad real de los modelos, lo que constituye un problema de evaluación y, por extensión, de seguridad: se podrían desplegar o promover modelos por su apariencia y no por su fiabilidad.

Este proyecto estudia esa situación con el conjunto de datos público `lmarena-ai/arena-human-preference-140k` (LMArena, 2025), que reúne 135.634 votos humanos emitidos entre el 17 de abril y el 24 de julio de 2025, con 53 modelos y 126 idiomas. Las preguntas que orientan el proyecto son dos: si el lado ganador tiende a ser el de respuesta más larga y con más formato (estilo frente a calidad), y si la posición en que se presenta el modelo o el orden del voto dentro de la sesión se asocia al resultado (sesgo de posición y de sesión).

El **objetivo general** del proyecto es construir y validar un conjunto de datos reproducible que permita analizar si las características de estilo y de presentación se asocian a la preferencia humana en LMArena. El alcance de este informe se limita a las Fases 1 y 2: definir el problema, dejar el entorno reproducible y preparar el dato. El análisis se reserva para las fases siguientes.

La problemática requiere un enfoque basado en programación y análisis de datos por tres razones: el volumen (más de 135 mil filas en 7 archivos de 1,6 GB en total), la estructura (columnas anidadas que deben aplanarse) y la heterogeneidad (idiomas, longitudes muy asimétricas y votos agrupados en sesiones). Nada de esto puede revisarse a mano ni de forma reproducible sin código.

Las fases del proyecto se articulan así: la **Fase 1** define el problema y configura el entorno; la **Fase 2** obtiene, explora, limpia, transforma y valida el dato; la **Fase 3** analiza las asociaciones planteadas con incertidumbre; y la **Fase 4** integra los resultados, concluye y discute sus implicancias para la evaluación de modelos.

---

## 3. Definición de la problemática y objetivos · ✅

### 3.1 Problemática
Las evaluaciones por preferencia humana se usan como medida de calidad de los modelos de lenguaje, pero su resultado puede depender de factores ajenos al contenido: la longitud de la respuesta, su formato (listas, encabezados, negritas), la posición en que se muestra (lado A o B) y el momento de la sesión en que se vota. Se desconoce cuánto pesa cada factor en datos recientes y cómo varía entre tipos de prompt e idiomas.

### 3.2 Preguntas del análisis
- **Pregunta central.** ¿En qué medida las preferencias humanas registradas en LMArena se asocian a características de estilo y de presentación de la respuesta, y no solo a su contenido?
- **P1 · Estilo frente a calidad.** ¿El lado ganador tiende a ser el de respuesta más larga y con más formato? ¿Cambia según categoría de prompt, idioma o modelo?

Estas preguntas se responden en las Fases 3 y 4.

### 3.3 Objetivo general
Construir y validar un conjunto de datos reproducible que permita analizar si las características de estilo y de presentación se asocian a la preferencia humana en LMArena.

### 3.4 Objetivos específicos
1. **OE1.** Configurar un entorno reproducible y un repositorio versionado, verificable mediante `make install` y la ejecución de las pruebas automáticas.
2. **OE2.** Obtener los 7 archivos del dataset con verificación de integridad (SHA-256) y documentar su estructura real: columnas, tipos, nulos y cardinalidades.
3. **OE3.** Limpiar y transformar el dato: aplanar las columnas anidadas, tipificar, tratar casos atípicos y duplicados, derivar variables de estilo y de posición, y escalar las que lo requieran, justificando cada decisión con una medición.
4. **OE4.** Validar el conjunto resultante con chequeos automáticos y pruebas unitarias que cubran casos normales, límite y excepciones.
5. **OE5.** Dejar documentadas las limitaciones y el dataset procesado como entrada directa de la Fase 3.

### 3.5 Alcance
**Se aborda:** definición del problema; entorno y repositorio; obtención, exploración univariada, limpieza, transformación y validación del dato; muestreo para pruebas.
**No se aborda en este informe:** comparaciones entre ganadores y perdedores, tasas de victoria por modelo, pruebas de hipótesis, intervalos de confianza, modelos predictivos y análisis de tendencias temporales. Quedan proyectados para las Fases 3 y 4.

### 3.6 Restricciones
Condiciones impuestas por el dato o por el contexto, distintas de las decisiones de alcance:
- **Ventana temporal:** los datos cubren cerca de 3 meses (17 de abril a 24 de julio de 2025) y la recolección es despareja: abril es parcial y hay días con 330 votos y otros con 2.865.
- **Estructura de sesiones:** el 79,9 % de los votos es el primero de su sesión y solo el 11,4 % de las sesiones tiene más de un voto, lo que limita el análisis del efecto del orden.
- **Definiciones faltantes:** la ficha del dataset no define la diferencia entre `tie` y `both_bad` ni documenta el método de las etiquetas de categoría, que son automáticas.
- **Tamaño:** el dato original pesa 1,6 GB, por sobre los 100 MB sugeridos; no se versiona y se descarga con verificación de integridad.
- **Licencia:** los prompts son CC-BY-4.0; las respuestas de los modelos dependen de cada proveedor, por lo que no se redistribuyen.
- **Datos personales:** los prompts son texto libre de personas reales y no es posible asegurar que carezcan de datos identificables. Solo se utiliza su longitud y no se publica ningún texto.
- **Herramientas del curso:** en las Fases 1 y 2 se usan NumPy, pandas, matplotlib y pyarrow; scikit-learn y SciPy se reservan para la Fase 3.

### 3.7 Supuestos
- La ficha de Hugging Face describe correctamente las columnas; las diferencias detectadas con el dato real se documentan (por ejemplo, `conv_metadata` trae 26 valores y no un conteo único por variable).
- Los conteos de `conv_metadata` (tokens, encabezados, listas, negritas) miden con fidelidad el estilo de cada respuesta.
- Un voto `model_a` o `model_b` expresa una preferencia real del votante.
- Las filas de una misma sesión no son independientes; cualquier análisis posterior debe considerarlo.
- El estudio es observacional: se hablará de asociaciones y no de causas.
- El dataset no tiene valores faltantes en las 11 columnas cargadas (se verifica en la Fase 2); su “suciedad” se encuentra en los ceros, los valores extremos, los idiomas no determinados (`und`), los empates y 10 filas en que ambos lados son el mismo modelo.

### 3.8 Articulación con las fases
| Fase | Pregunta que responde | Producto |
|---|---|---|
| F1 | ¿Qué problema, con qué alcance y con qué límites? | Notebook `F1_Definicion`, entorno, repositorio |
| F2 | ¿Se dispone de un dato limpio, tipificado y validado? | Notebooks `F2_01` a `F2_03`, dataset procesado |
| F3 | ¿Qué asociaciones hay entre estilo, posición y resultado? | Análisis bivariado con incertidumbre |
| F4 | ¿Qué se concluye y qué implica para evaluar modelos? | Informe final |

---

## 4. Aplicación de herramientas científicas · 🟡

**Entorno.** Python 3.12.13 en un entorno virtual (`.venv`). Librerías principales (versiones fijas en `requirements.txt`): NumPy 2.5.4, pandas 3.1.0, pyarrow 26.0.0, matplotlib 3.11.2, huggingface_hub 2.4.0, pytest 9.2.0, nbconvert 7.17.2, ipykernel 7.4.0, ipywidgets 8.1.9. Control de versiones con Git y GitHub.

**Qué hace cada herramienta en el proyecto.**
| Herramienta | Uso | Dónde |
|---|---|---|
| pandas | carga, tipificación, resúmenes y tablas de frecuencia | `src/arena/profile.py` |
| pyarrow | lectura de los archivos parquet por columnas | `src/arena/profile.py` |
| NumPy | operaciones numéricas bajo pandas | `src/arena/` |
| matplotlib | gráficos de barras, histogramas y serie diaria | `src/arena/plots.py` |
| huggingface_hub | descarga de los archivos del dataset | `src/arena/io.py` |
| hashlib (estándar) | huella SHA-256 de cada archivo | `src/arena/io.py` |
| pytest | pruebas automáticas sin red | `tests/` |
| Jupyter / nbconvert | notebooks ejecutables y verificación de ejecución | `F1/`, `F2/` |
| Git / GitHub | versionado y trazabilidad | repositorio |

**Módulos.** `env` (registro del entorno), `io` (descarga y huellas), `profile` (inspección estructural, tablas de frecuencia, columnas anidadas), `plots` (gráficos), `sampling` (muestreo por filas y por sesiones). Los notebooks solo llaman a estas funciones.

`[PENDIENTE]` Agregar `preprocessing` y `validation` cuando estén listos (F2_02 y F2_03), y fragmentos de código comentados que muestren la integración entre ellos.

---

## 5. Reproducibilidad técnica · 🟡

- **Ambiente virtual:** `make install` crea `.venv` con Python 3.12 e instala `requirements.txt` (versiones fijas con `==`) y el paquete del proyecto en modo editable (`pip install -e .`).
- **Verificación de la instalación:** `pip check` informa que no hay dependencias rotas.
- **Pruebas:** `make test` ejecuta 51 pruebas automáticas que no usan la red.
- **Rutas y semilla:** todas las rutas son relativas a la raíz del proyecto (calculada desde el propio código) y la semilla aleatoria está fijada en 42.
- **Integridad del dato:** `data/raw/CHECKSUMS.txt` guarda la huella SHA-256 de los 7 archivos y `verify_checksums()` las recalcula.

- **Evidencia de ejecución de punta a punta:** `make all` se ejecutó desde un clon limpio y terminó sin errores en unos 3 minutos (entorno nuevo, descarga y verificación de los 7 archivos, 51 pruebas y notebooks ejecutados). Las salidas están en `docs/evidence/` (`entorno.txt`, `pytest.txt`, `nbconvert.txt`). El log de `nbconvert` contiene un aviso informativo de Jupyter sobre la comunicación local con el kernel; no es una advertencia del código y no aparece en los notebooks.
`[PENDIENTE]` Prueba en un segundo equipo (la del clon limpio se hizo en el mismo computador): un integrante que no armó el entorno clona el repositorio, ejecuta `make install` y corre los notebooks desde cero.
- **Registro del entorno en los notebooks:** la celda de entorno lista cada dependencia con su versión fijada frente a la instalada, la semilla, la rama y el commit de la ejecución. Los metadatos quedan además en `docs/metadatos_fase1.json` y `docs/metadatos_proyecto.csv`.

---

## 6. Control de versiones · ✅

- **Repositorio:** https://github.com/JoseFredes/lmarena-sumativa1 (público, licencia MIT).
- **Convención:** commits en inglés con el formato `type(scope): message` (`feat`, `fix`, `docs`, `data`, `build`, `test`, `refactor`); ramas `f1/<tema>`, `f2/<tema>` y `docs/<tema>`; integración a `main` mediante pull request.
- **Historial:** la rama `main` registra commits realizados por las cuentas de GitHub de los cuatro integrantes del grupo.

**Contribuciones identificadas:**

- `JoseFredes`: contribuciones relacionadas con la configuración del entorno, reproducibilidad, validación y documentación del proyecto.
- `poirierunited`: desarrollo de la definición del problema y del proceso de limpieza y transformación de los datos.
- `vcjacob`: aportes a la documentación del informe y a la trazabilidad del mapa conceptual.
- `angelo-morales-serrano`: incorporación de instrucciones para ejecutar los notebooks desde README.

**Pull Requests incorporados a main:**

- **PR #4 – F2/cleaning:** incorpora el notebook y el proceso de limpieza y transformación de los datos, desarrollado por `poirierunited`.
- **PR #5 – Instrucciones del README:** incorpora las indicaciones para ejecutar los notebooks, desarrollado por `angelo-morales-serrano`.

La evidencia del historial de commits, los Pull Requests y las ramas se presenta en el Anexo E.

## 7. Documentación del proceso · 🟡

**Flujo de trabajo, de la carga a los resultados.**
1. `download_dataset()` descarga los 7 archivos parquet a `data/raw/` y `write_checksums()` registra su huella.
2. `load_raw()` carga 11 de las 14 columnas (135.634 filas, 115 MB en memoria); las tres columnas de conversaciones se excluyen por peso y licencia.
3. `structure_summary()` y `frequency_table()` describen cada variable; `nested_paths()` revela la estructura de las columnas anidadas.
4. `[PENDIENTE]` Limpieza y transformación (`preprocessing`), que produce el dataset procesado en `data/processed/`.
5. `validate_dataset()` comprueba el dato (`F2_03`); `[PENDIENTE]` aplicarlo al dataset procesado.

**Decisiones técnicas.** El registro completo, con motivo, impacto y commit, está en `docs/decisiones.md` y se resume en la sección 11 del informe final. Principales decisiones hasta ahora: cambio de dataset, foco en dos preguntas, uso del dataset completo, exclusión de las columnas de conversaciones, muestreo por sesión para pruebas, y validación con el script del curso sobre una versión aplanada del dato.

**Coherencia.** Cada cifra del informe proviene de una salida ejecutada en los notebooks o de `docs/validacion_dataset.md`; si se corrige una, se corrige en los tres lugares.

---


## 8. Repositorio GitHub · 🟡

El repositorio está organizado en carpetas según las fases y el tipo de trabajo realizado. Cuenta con `F1/` y `F2/` para los notebooks, `F3/` y `F4/` para las fases proyectadas, `src/arena/` para el código, `tests/` para las pruebas, `data/` para los datos y `docs/` y `report/` para la documentación.

El archivo `README.md` contiene la descripción del proyecto, las preguntas de investigación, el reparto de tareas, el calendario, los supuestos del dataset y las instrucciones para trabajar con el repositorio.

También se incorporaron instrucciones para ejecutar los notebooks. Se explica cómo instalar las dependencias, activar el entorno virtual, abrir Jupyter y seleccionar el kernel correspondiente. Además, se incluyen comandos para ejecutar las distintas etapas del proyecto mediante el `Makefile`.

Las contribuciones individuales se encuentran respaldadas mediante el historial de commits y los Pull Requests incorporados a `main`. Las capturas correspondientes se presentan en la sección 6 y en el Anexo E.

[PENDIENTE] Revisar y actualizar la tabla de avance del README antes de la entrega. Actualmente `F2_02` sigue figurando como pendiente, aunque el notebook ya fue incorporado a `main` mediante el PR #4. También se debe revisar la diferencia entre el estado del notebook F1 indicado en la tabla y el que aparece en la lista de avance.

---

## 9. Codificación funcional · ⬜
`[PENDIENTE]` Se redacta al cerrar F2_02 y F2_03. Mostrar: funciones con parámetros claros y tipos, un propósito por función, uso de bucles para recorrer columnas (en lugar de repetir bloques), `copy()` antes de transformar, y flujo de datos verificable.

## 10. Preprocesamiento y transformación del dataset · ⬜
`[PENDIENTE]` Depende de F2_02. La guía exige: diagnóstico previo (dimensiones, tipos, nulos, duplicados, atípicos), comparación de alternativas antes de decidir, transformaciones según el rol de cada variable, validación integral, y justificación en tres planos (pertinencia, impacto medido y coherencia con los objetivos).
Diagnóstico ya disponible (F2_01): 0 nulos en 11 columnas; 10 filas con `model_a == model_b`; 61 y 58 respuestas con 0 tokens; tokens muy asimétricos (mediana 748, máximo 137.128); 8,7 % de votos con idioma `und`.

## 11. Validación técnica y verificación del código · 🟡
- **Dataset:** `docs/validacion_dataset.md`, generado con `validar_dataset.py` del curso sobre la versión aplanada del dato (135.634 filas × 47 columnas). Resultado: cumple todos los requisitos obligatorios y tiene un aviso (sin valores faltantes). El criterio de tamaño (37,6 MB) se evaluó sobre el CSV aplanado; el dato original pesa 1,6 GB.
- **Código:** 51 pruebas con pytest, sin red, que cubren casos normales (datos válidos), límite (`evaluation_order` en 1 y 28, 0 tokens, archivo vacío, sesión de un voto) y excepciones (columna faltante, ganador inválido, tokens negativos, id repetido, entrada que no es DataFrame, archivo de huellas inexistente, huella que no coincide, tamaños de muestra inválidos). Salida guardada en `docs/evidence/pytest.txt`.
- **Validador del dataset:** `validate_dataset` devuelve un `ValidationReport` con chequeos críticos (lanzan `ValueError` con `assert_ok()`) y advertencias. Sobre el dato original: 0 fallos críticos y 1 advertencia (10 filas con el mismo modelo en ambos lados). El notebook `F2_03` provoca errores a propósito para mostrar que se detectan.
`[PENDIENTE]` Pruebas del módulo `preprocessing` y validación del dataset procesado (dependen de F2_02).

## 12. Notebook F1_Definicion.ipynb · 🟡

El notebook F1 ya está incorporado al repositorio. En él se explica el problema que se quiere estudiar, la pregunta de investigación, los objetivos y el alcance del proyecto.

También se incluye información sobre el entorno de trabajo, la semilla utilizada y las carpetas donde se guardan los datos. Además, se muestra cómo se relaciona el proyecto con el mapa conceptual.

El notebook cuenta con dos celdas de código que ya tienen resultados guardados. Sin embargo, todavía es necesario volver a ejecutarlo para comprobar que funcione correctamente desde el inicio.

[PENDIENTE] Reiniciar y ejecutar todas las celdas del notebook para comprobar que no se produzcan errores.

[PENDIENTE] Revisar algunos resultados que quedaron guardados, ya que muestran información del computador donde se ejecutó originalmente.

## 13. Notebooks ejecutables de la Fase 2 · 🟡

- **F2_01 – Obtención y exploración:** este notebook ya tiene resultados guardados. En él se descargan los siete archivos del dataset y se revisa cómo están organizados los datos, los tipos de variables, los votos, los idiomas, las fechas y las sesiones.

- **F2_02 – Limpieza y transformación:** ya está incorporado al repositorio mediante el PR #4 y también cuenta con resultados registrados. En este notebook se ordenan las columnas, se ajustan algunos tipos de datos y se crean nuevas variables para el análisis. Al finalizar, se mantienen las 135.634 filas y se obtiene un archivo procesado con 54 columnas. Las revisiones realizadas no muestran errores críticos, aunque queda una advertencia relacionada con 10 registros en que ambos lados corresponden al mismo modelo.

- **F2_03 – Validación:** contiene las revisiones del dataset original y pruebas para comprobar que se detecten errores en los datos. En los resultados guardados se muestran 51 pruebas aprobadas. Todavía falta completar la revisión del dataset después de aplicar la limpieza y transformación.

[PENDIENTE] Completar la validación del dataset procesado y revisar la ejecución de los notebooks desde la versión final del repositorio.

## 14. Vinculación del mapa conceptual con el avance · 🟡

A continuación, se muestra cómo se relacionan los elementos del mapa conceptual con los avances que tiene ya el repositorio y lo que todavía falta completar.

| Elemento del mapa | Tipo | Estado (implementado / proyectado) | Evidencia |
|---|---|---|---|
| Python, pandas, Jupyter, Git y GitHub | Herramientas | Implementado. Se cuenta con el entorno de trabajo, las librerías necesarias y los notebooks para desarrollar el proyecto. | `requirements.txt`, carpeta `src/arena/`, notebooks F1 y F2|
| Descarga, exploración, limpieza y validación de los datos | Procesos | La descarga y exploración ya están realizadas. También se completó la limpieza y transformación de los datos. La validación del dataset procesado todavía está pendiente. El análisis se realizará en F3. | Notebooks `F2_01`, `F2_02` y `F2_03`, carpeta `src/arena/` |
| Instalación de dependencias, descarga de datos y ejecución de pruebas y notebooks | Flujo reproducible | Ya se cuenta con comandos para instalar las dependencias, descargar los datos y ejecutar las pruebas y notebooks. También se guardaron los resultados de estas ejecuciones. Falta comprobar el proceso en otro computador. | `Makefile`, `requirements.txt`, `docs/evidence/` |
| Elección del dataset y criterios para trabajar con los datos | Decisiones técnicas | Ya se definió qué dataset utilizar y qué información se necesita para el proyecto. También se dejó registrado por qué no se guardan los textos de las respuestas. Todavía quedan algunos aspectos por revisar, como el tratamiento de los empates. | `docs/decisiones.md`, `README.md` |
| Carpetas para separar los datos, notebooks, código, pruebas y documentos | Organización del repositorio | Implementado. El repositorio cuenta con carpetas separadas según la fase y el tipo de contenido, lo que permite mantener ordenados los archivos del proyecto. | `F1/`, `F2/`, `F3/`, `F4/`, `data/`, `src/`, `tests/`, `docs/`, `report/` |
| Notebooks separados según el trabajo de cada fase | Estructura del notebook | Los notebooks de F1 y F2 ya están incorporados al repositorio. F2_01 contiene la exploración de los datos, F2_02 la limpieza y transformación, y F2_03 la validación. Todavía falta completar la validación de los datos procesados. | `F1/F1_Definicion.ipynb`, notebooks de `F2/`, PR #4 |

Los avances muestran que ya se cuenta con el entorno, la estructura del repositorio y los notebooks necesarios para trabajar con los datos. También se completó la limpieza y transformación del dataset. Sin embargo, todavía falta terminar su validación. Una vez completada esta etapa, se podrá continuar con el análisis de los datos en F3.

## 15. Bibliografía · 🟡

Mínimo exigido: 5 fuentes en APA 7, con al menos 2 del material docente, 2 de documentación técnica oficial y 1 académica reciente, todas citadas en el texto. **Verificar autores, años y enlaces de cada una antes de entregar.**

**Académicas (últimos 5 años), citadas en la introducción**
- Chiang, W.-L., Zheng, L., Sheng, Y., Angelopoulos, A. N., Li, T., Li, D., Zhu, B., Zhang, H., Jordan, M., Gonzalez, J. E., & Stoica, I. (2024). Chatbot Arena: An open platform for evaluating LLMs by human preference. En *Proceedings of the 41st International Conference on Machine Learning* (Vol. 235, pp. 8359–8388). PMLR. https://proceedings.mlr.press/v235/chiang24b.html `[VERIFICAR orden de autores]`
- Dubois, Y., Galambosi, B., Liang, P., & Hashimoto, T. B. (2024). *Length-controlled AlpacaEval: A simple way to debias automatic evaluators*. arXiv. https://arxiv.org/abs/2404.04475
- Wu, M., & Aji, A. F. (2025). Style over substance: Evaluation biases for large language models. En *Proceedings of the 31st International Conference on Computational Linguistics* (pp. 297–312). Association for Computational Linguistics. https://aclanthology.org/2025.coling-main.21

**Datos**
- LMArena. (2025). *arena-human-preference-140k* [Conjunto de datos]. Hugging Face. https://huggingface.co/datasets/lmarena-ai/arena-human-preference-140k

**Material docente** `[VERIFICAR autor, año y título exactos]`
- Salinas Silva, O. (2026). *Guía de desarrollo — Evaluación Sumativa 1 (Fases 1 y 2)* [Documento de apoyo]. MCDI500, Universidad Andrés Bello.
- Salinas Silva, O. (2026). *MCDI500 · Material didáctico de la Semana 1* [Repositorio]. GitHub. https://github.com/magistercienciadatos/Material_Didactico_Semana1
- Sugeridas por la guía (verificar datos): Chacon y Straub (2014), *Pro Git*; McKinney (2022), *Python for data analysis*; Wilson et al. (2017), *Good enough practices in scientific computing*, PLOS Computational Biology.

**Documentación técnica oficial** `[VERIFICAR versión, año y URL]`
- The pandas development team. *pandas documentation* (v3.1). https://pandas.pydata.org/docs/
- NumPy Developers. *NumPy documentation* (v2.5). https://numpy.org/doc/
- Python Software Foundation. *venv — Creation of virtual environments*. https://docs.python.org/3/library/venv.html
- Project Jupyter. *nbconvert documentation*. https://nbconvert.readthedocs.io/

---


## Anexos

- A. Informe de validación del dataset (`docs/validacion_dataset.md`).
- B. Evaluación de criterios del dataset (`docs/evaluacion_criterios_dataset.csv`).
- C. Salida de `pytest` y de `nbconvert` (`docs/evidence/`).
- D. Bitácora de decisiones (`docs/decisiones.md`).

### E. Evidencia del control de versiones

Las siguientes capturas respaldan las contribuciones identificadas en la sección 6 y muestran los cambios incorporados al repositorio y las ramas utilizadas durante el desarrollo del informe.

**E.1. Historial de commits por integrante**

*Contribuciones de Valentina Carvajal Jacob (`vcjacob`).*

![Commits de vcjacob](../docs/evidence/commits_vcjacob.png)

*Contribuciones de JoseFredes.*

![Commits de JoseFredes](../docs/evidence/commits_josefredes.png)

*Contribuciones de Alejandro Poirier (`poirierunited`).*

![Commits de poirierunited](../docs/evidence/commits_poirierunited.png)

*Contribuciones de Angelo Morales (`angelo-morales-serrano`).*

![Commits de angelo](../docs/evidence/commits_angelo.png)

**E.2. Pull Requests incorporados a la rama main**

*PR #4 – Limpieza y transformación de datos.*

![Pull Request 4](../docs/evidence/pr-4-cleaning.png)

*PR #5 – Instrucciones para ejecutar los notebooks.*

![Pull Request 5](../docs/evidence/pr-5-readme.png)

