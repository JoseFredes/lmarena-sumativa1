# Diccionario de variables

Variables de `data/processed/arena_clean.parquet` (135.634 filas × 54 columnas) generado por `F2/F2_02_cleaning_transformation.ipynb` con las funciones de `src/arena/preprocessing.py`.

Convención: las variables con `_a` y `_b` corresponden a la respuesta del modelo A y modelo B respectivamente.

## 1. Campos iniciales (9)

| Variable | Tipo | Descripción |
|---|---|---|
| `id` | str | Identificador único de cada votación |
| `model_a` | str | Modelo que generó la respuesta A |
| `model_b` | str | Modelo que generó la respuesta B |
| `winner` | category | Resultado del voto: `model_a`, `model_b`, `tie` (empate) o `both_bad` (ambas malas) |
| `evaluation_session_id` | str | Identificador de la sesión de votación |
| `evaluation_order` | int16 | Posición del voto dentro de su sesión |
| `language` | category | Idioma del prompt (código ISO; `und` = no determinado) |
| `is_code` | bool | Indica si la conversación trata sobre programación |
| `timestamp` | datetime64 | Fecha y hora del voto |

## 2. Métricas aplanadas de `conv_metadata`(26)

Se muestran para la respuesta del modelo A(`_a`), son las mismas 12 variables para la respuesta del modelo B(`_b`).

| Variable | Tipo | Descripción |
|---|---|---|
| `sum_assistant_a_tokens` | int64 | Largo de la respuesta A, en tokens |
| `header_a_h1` … `header_a_h6` | int64 | Cantidad de encabezados Markdown de nivel 1 a 6 en la respuesta A |
| `list_a_ordered` | int64 | Cantidad de elementos en listas numeradas |
| `list_a_unordered` | int64 | Cantidad de elementos en listas con viñetas |
| `bold_a_asterisk` | int64 | Cantidad de textos en negrita escritos con `**texto**` |
| `bold_a_underscore` | int64 | Cantidad de textos en negrita escritos con `__texto__` |
| `context_a_tokens` | int64 | Tokens de la pregunta más el contexto de la conversación para la respuesta A |

nota: `header_a_h1` … `header_a_h6` son 6 variables distintas

Variables comunes a ambas respuestas:

| Variable | Tipo | Descripción |
|---|---|---|
| `sum_user_tokens` | int64 | Largo del prompt de la persona, en tokens |
| `turns` | int64 | Cantidad de turnos de la conversación |

## 3. Etiqueta `category_tag`(12)

| Variable | Tipo | Descripción |
|---|---|---|
| `cat_creative_writing` | bool | El prompt pide escritura creativa |
| `cat_creative_writing_score` | str | Puntaje asociado a la etiqueta de escritura creativa |
| `cat_criteria_complexity` | bool | El prompt es complejo |
| `cat_criteria_creativity` | bool | El prompt requiere creatividad |
| `cat_criteria_domain_knowledge` | bool | El prompt requiere conocimiento especializado |
| `cat_criteria_problem_solving` | bool | El prompt requiere resolver un problema |
| `cat_criteria_real_world` | bool | El prompt se refiere a una situación del mundo real |
| `cat_criteria_specificity` | bool | El prompt es específico |
| `cat_criteria_technical_accuracy` | bool | El prompt exige precisión técnica |
| `cat_if` | bool | El prompt evalúa seguimiento de instrucciones (*instruction following*) |
| `cat_if_score` | float64 | Puntaje de seguimiento de instrucciones, de 0 a 5 valores enteros |
| `cat_math` | bool | El prompt es de matemáticas |

Las etiquetas fueron asignadas por un sistema automático de LMArena, no por personas.

## 4. Variables derivadas (7)

| Variable | Tipo | Descripción |
|---|---|---|
| `format_a`, `format_b` | int64 | Total de marcado Markdown de cada respuesta (encabezados + listas + negritas) |
| `tokens_log_a`, `tokens_log_b` | float32 | `log(1 + tokens)` del largo de cada respuesta; reduce la asimetría y admite valores cero |
| `longer_response` | str | Respuesta más larga: `a`, `b` o `equal` |
| `more_formatted` | str | Respuesta con más formato: `a`, `b` o `equal` |
| `winner_binary` | str | Ganador simplificado: `a`, `b` u `other` (empates y `both_bad`) |