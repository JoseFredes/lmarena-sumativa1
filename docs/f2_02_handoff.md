# Nota para Alejandro: limpieza y transformación (F2_02)

Punto de partida: `from arena.profile import load_raw` carga el dato sin las columnas de texto. Los hallazgos de la
sección 9 de `F2/F2_01_acquisition_exploration.ipynb` dicen qué hay que resolver.

## Qué hay que hacer

1. Aplanar `conv_metadata` (26 valores) y `category_tag` (12 valores). Decidir si se suman los encabezados por nivel, las listas ordenadas y no ordenadas, y las dos clases de negrita. Hoy existe `nested_to_frame()` solo para inspeccionar; el aplanado de verdad va en `src/arena/preprocessing.py`.
2. Tipos: `model_a`, `model_b`, `language` a `category`; `winner` a categórica; `is_code` a bool; `timestamp` a fecha.
3. Texto del prompt: sacar el largo (palabras y caracteres) desde `conversation_a` y descartar el texto. No se publica ningún texto de respuestas.
4. Duplicados y casos raros: 10 filas con `model_a == model_b`, 61 y 58 respuestas con 0 tokens.
5. Variables derivadas: `ganador_lado`/`hay_ganador`, `gana_a`, diferencias A − B de tokens, encabezados, listas y negritas.
6. Escalamiento: z-score y/o logaritmo de los tokens. Conservar siempre la columna sin escalar.

## Lo que pide la guía del profesor (apartado 4.10)

- **Primero medir, después decidir.** Cada decisión muestra la tabla o la cifra que la respalda.
- **Comparar alternativas** antes de decidir (por ejemplo, tokens crudos vs. logaritmo, o qué hacer con los ceros), y medir el impacto.
- Escalar o transformar según el **rol de la variable**, no "porque corresponde".
- Una ordinal no se deja en orden alfabético.
- Trabajar sobre una copia (`df.copy()`); cada paso es una función pura en `src/`.
- Dejar `assert` o pruebas en cada paso y **conservar las salidas** del notebook.
- Como el dataset no tiene nulos, el manejo de NA se justifica con el diagnóstico (0 nulos) y con lo que sí es "sucio": ceros, extremos, `und`, empates.

## Cómo trabajar

- Rama `f2/cleaning` y pull request hacia `main`. Commits en inglés con `type(scope): message`.
- Notebook: `F2/F2_02_cleaning_transformation.ipynb`, con el esquema de F2_01 (qué, por qué, qué esperamos, código, interpretación).
- Al final, guardar el resultado en `data/processed/` (sin columnas de texto) y avisar a Jose para empezar `F2_03`.
