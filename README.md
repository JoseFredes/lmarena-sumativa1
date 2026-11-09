# ¿Contenido o formato? Preferencias humanas en LMArena

Sumativa 1 · Fases 1 y 2 · MCDI500 Programación para la Ciencia de Datos · Magíster en Inteligencia Artificial, UNAB
Entrega: **domingo 8 de noviembre de 2026, 23:59** · Vale 40 % de la nota · Trabajo grupal

**Integrantes:** Jose Fredes, Alejandro Poirer, Valentina Carvajal, Angelo Morales
**Docente:** Omar Salinas

---

## De qué trata

Hoy se decide qué modelo de lenguaje es "mejor" mirando votos de personas que comparan dos respuestas anónimas (el caso más conocido es LMArena). Eso supone que el voto refleja calidad, pero también podría reflejar estilo: una respuesta más larga y con más listas, encabezados y negritas puede *parecer* mejor sin serlo. Si pasa eso, un ranking puede premiar el formato y no la capacidad real, lo que es un problema de evaluación y de seguridad de los modelos.

Queremos mirar eso con datos reales de 2025.

## Datos

[`lmarena-ai/arena-human-preference-140k`](https://huggingface.co/datasets/lmarena-ai/arena-human-preference-140k): unos 135 mil votos humanos (abril–julio de 2025), 53 modelos, con el ganador de cada batalla, la posición dentro de la sesión, el idioma, etiquetas de categoría y conteos de tokens, listas, encabezados y negritas de cada respuesta.
Los prompts son CC-BY-4.0, pero las respuestas de los modelos dependen de cada proveedor, así que **no subimos textos de respuestas al repo**.
Descartamos `Anthropic/persuasion` (nuestra idea inicial) porque es de 2024 y solo tiene modelos de una familia.

## Preguntas

- **P1 · Estilo vs. calidad:** ¿gana más seguido la respuesta más larga y con más formato?

Son preguntas para la Fase 3. Solo vamos a hablar de **asociación**, no de causas.

## Qué hacemos en esta entrega (Fases 1 y 2)

| Fase | Qué hacemos | Qué dejamos para después |
|---|---|---|
| **F1** | Definir problema, objetivos, alcance y supuestos; dejar el entorno reproducible y un código base mínimo | Todo análisis |
| **F2** | Descargar el dataset, explorarlo, limpiarlo, transformarlo (tipos, columnas anidadas, variables derivadas, escalamiento) y validarlo con pruebas | Comparar ganadores con perdedores, tasas de victoria, tests, modelos |

Entregables: informe PDF, este repo (carpetas `F1/` y `F2/`, README, dependencias, historial de commits), notebook `F1_Definición.ipynb` (en el repo `F1_Definicion.ipynb`, sin tilde), notebooks de F2 y evidencias de ejecución y pruebas.

## Cómo nos repartimos el trabajo

*Propuesta inicial; la ajustamos entre todos.*

| Tarea | Quién |
|---|---|
| Repo, entorno, `requirements.txt`, estructura | Jose |
| Descarga del dato y exploración (`F2_01`) | Jose |
| Validación y pruebas (`F2_03`) | Jose |
| Notebook F1 (problema, objetivos, alcance) | Ale |
| Limpieza y transformación (`F2_02`) | Ale |
| Informe PDF (portada, índice, formato) | Todos |
| Mapa conceptual y su vinculación con el proyecto | Valentina, Angelo |
| Bibliografía APA 7 (mínimo 5 fuentes) | Valentina, Jose |
| Revisión cruzada antes de entregar | Todos |

## Cómo trabajamos

- Una rama por tema (`f1/definition`, `f2/exploration`, `f2/cleaning`, …) y se integra a `main` por merge o PR.
- Commits chicos, en inglés, con el formato `type(scope): what was done`. Ejemplo: `feat(f2): parse conversation metadata`.
- Cada persona hace sus propios commits con su usuario, y no hacemos squash: el historial es parte de la evidencia.
- Cualquier decisión que no sea obvia (por ejemplo, qué hacer con los empates) se anota en el notebook correspondiente.

## Calendario

| Fecha | Qué queremos tener |
|---|---|
| Lun 2 – mar 3 nov | Dataset y preguntas acordados, repo y entorno listos |
| Mié 4 nov | Dataset descargado y explorado |
| Jue 5 nov | Limpieza y transformación |
| Vie 6 nov | Validación y notebook F1 |
| Sáb 7 nov | Todo ejecutándose de punta a punta, informe armado |
| Dom 8 nov | Revisión final y entrega antes de las 23:59 (la sube una sola persona en Canvas) |

## Supuestos y avisos del dataset

Revisamos el dataset con el `validar_dataset.py` del curso, sobre una muestra aplanada (1 de los 7 archivos, 19.377 filas). Cumple todos los requisitos obligatorios (filas, columnas, roles analíticos, variable numérica y categórica). Lo que no cumple o no podemos asegurar, lo declaramos acá:

- **Sin valores faltantes.** La muestra tiene 0 % de nulos. Lo "sucio" de este dataset está en otro lado: 126 idiomas, empates (`tie`, `both_bad`), votos agrupados en sesiones y etiquetas puestas por un sistema automático.
- **Tamaño.** El dato original pesa ~1,6 GB, más que los 100 MB sugeridos. No se sube al repo (`data/raw/` está ignorado); se descarga con `make data`. El dataset procesado no incluye texto, así que debería pesar mucho menos.
- **Datos personales.** Los prompts son texto libre de personas reales y no podemos asegurar que no contengan datos identificables. Solo usamos su largo y no publicamos ningún texto.
- **Licencia.** Los prompts son CC-BY-4.0; las respuestas de los modelos dependen de cada proveedor.
- **Ventana temporal.** Los datos cubren abril–julio de 2025 (unos 3 meses), así que no hacemos análisis de tendencias de largo plazo.
- **Alcance de las conclusiones.** Es un estudio observacional: hablamos de asociaciones, no de causas.

## Avance

- [x] Repo, entorno, `requirements.txt` y estructura (Jose)
- [x] Descarga con SHA-256 y exploración inicial: `F2/F2_01_acquisition_exploration.ipynb` (Jose)
- [x] Notebook F1: `F1/F1_Definicion.ipynb` (Alejandro)
- [x] Limpieza y transformación: `F2/F2_02_cleaning_transformation.ipynb` y `src/arena/preprocessing.py` (Alejandro)
- [x] Validación (`validation.py`, 55 pruebas con `pytest`) y notebook `F2/F2_03_validation.ipynb` sobre dato original y procesado (Jose)
- [x] Evidencias de `make all` desde un clon limpio y verificación en múltiples equipos, en `docs/evidence/`
- [x] Informe técnico integrado, mapa conceptual actualizado y bibliografía APA 7 (Valentina, Angelo, Alejandro, Jose)

## Decisiones cerradas y pendientes para Fase 3

- [x] Trabajar con el dataset completo (135.634 filas; cargando 11 de 14 columnas ocupa ~115 MB en memoria)
- [x] Confirmar con el docente que el dataset no esté repetido en otro equipo
- [x] Mapa conceptual de la actividad formativa integrado con el avance de F1 y F2
- [x] Confirmar y aplanar la estructura real de las columnas anidadas (`conv_metadata` → 26 columnas; `category_tag` → 12 columnas)
- [ ] En Fase 3: evaluar el tratamiento analítico de `tie` y `both_bad` (se creó `winner_binary` en F2 conservando todas las filas) y el control por idioma/modelo

## Licencia

El código y la documentación de este repo están bajo licencia MIT (ver `LICENSE`). Los datos de LMArena tienen su propia licencia, indicada arriba.

## Cómo correrlo

Necesitas Python 3.12 (sirve cualquier 3.11 o superior; ajusta `PYTHON=` en el `Makefile`) y `make`.

```bash
git clone https://github.com/JoseFredes/lmarena-sumativa1.git
cd lmarena-sumativa1
make all
```

`make all` crea `.venv` e instala `requirements.txt` (versiones fijas), descarga los 7 archivos del dataset (~1,6 GB) y los verifica contra `data/raw/CHECKSUMS.txt`, corre las pruebas, ejecuta los notebooks y guarda las evidencias en `docs/evidence/`. Se probó desde un clon limpio: termina sin errores en unos 3 minutos.

También se puede ir por partes:

| Comando | Qué hace |
|---|---|
| `make install` | crea el entorno virtual e instala las dependencias |
| `make data` | descarga lo que falte y verifica las huellas SHA-256 |
| `make test` | corre `pytest` (sin red) y guarda la salida en `docs/evidence/pytest.txt` |
| `make run` | ejecuta los notebooks de `F1/` y `F2/` y guarda el log en `docs/evidence/nbconvert.txt` |
| `make evidence` | guarda versión de Python, commit y `pip freeze` en `docs/evidence/entorno.txt` |
| `make validate-dataset` | valida el dato con el script del curso y escribe `docs/validacion_dataset.md` |
| `make metadata` | genera `docs/metadatos_fase1.json` y `docs/metadatos_proyecto.csv` |

Nota: el log de `nbconvert` incluye un aviso de Jupyter (`Kernel is running over TCP without encryption`). Es un mensaje informativo de la comunicación local con el kernel y no una advertencia del código; no aparece en las salidas de los notebooks.

### Notebooks

Pasos comunes, desde la raíz:

1. Crear el entorno e instalar dependencias: "make install"
2. Activar el entorno:
- macOS / Linux: "source .venv/bin/activate"
- Windows (Git Bash): "source .venv/bin/activate"
3. Abrir Jupyter desde la raíz, para que funcionen las rutas realtivas: "python -m jupyter lab"
4. Elegir como kernel el Python de ".venv" (Jupyter: Kernel > Change Kernel ; VS Code: Select Kernel)
5. Ejecutar Notebook de arriba a abajo


| Notebook | Qué hace | Estado |
|---|---|---|
| `F1/F1_Definicion.ipynb` (es el "F1_Definición.ipynb" solicitado, sin tilde por portabilidad) | definición del problema, entorno y condiciones iniciales | listo |
| `F2/F2_01_acquisition_exploration.ipynb` | descarga, estructura, variables, tiempo, sesiones y muestreo | listo |
| `F2/F2_02_cleaning_transformation.ipynb` | limpieza, aplanamiento, conversión de tipos y variables derivadas | listo |
| `F2/F2_03_validation.ipynb` | validación y pruebas (casos normales, límite y excepciones sobre dato original y procesado) | listo |

## Estructura del repo

```
README.md          esta descripción
LICENSE            MIT
Makefile           install, test, data, run, all
requirements.txt   dependencias con versión fija
pytest.ini         configuración de pytest
src/arena/         paquete: env, io (descarga y SHA-256), profile (inspección), preprocessing, plots, sampling, validation
tests/             pruebas con datos sintéticos, sin red
F1/                notebook de la Fase 1 y mapa conceptual
F2/                notebooks de la Fase 2 (01 exploración, 02 limpieza, 03 validación)
data/raw/          dato descargado (no se versiona; se verifica con CHECKSUMS.txt)
data/processed/    dato procesado (arena_clean.parquet, generado por F2_02)
docs/evidence/     test and execution outputs (pytest, nbconvert, entorno)
```

## Declaración de uso de herramientas de apoyo (IA)

- **Claude (Anthropic):** utilizado como asistente de apoyo y aprendizaje autodidacta para profundizar en los contenidos técnicos del curso y realizar el seguimiento estructurado de tareas e hitos del proyecto.
- **Gemini (Google):** utilizado como apoyo editorial para revisar y mejorar la redacción, cohesión y comunicación escrita del informe técnico y la documentación, manteniendo todas las decisiones metodológicas, el código y la verificación de resultados a cargo de los integrantes del equipo.
