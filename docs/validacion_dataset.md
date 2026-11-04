# Validación del dataset — MCDI500

**Archivo:** `arena_flat.csv` · 135634 filas × 47 columnas

## Perfil de variables

| variable | dtype | rol | unicos | pct_nulos |
| --- | --- | --- | --- | --- |
| id | str | identificador | 135634 | 0.0 |
| model_a | str | alta cardinalidad | 53 | 0.0 |
| model_b | str | alta cardinalidad | 53 | 0.0 |
| winner | str | nominal | 4 | 0.0 |
| evaluation_session_id | str | alta cardinalidad | 115372 | 0.0 |
| evaluation_order | int64 | discreta | 28 | 0.0 |
| language | str | alta cardinalidad | 126 | 0.0 |
| is_code | bool | binaria | 2 | 0.0 |
| timestamp | str | fecha | 135634 | 0.0 |
| sum_assistant_a_tokens | int64 | continua | 7100 | 0.0 |
| context_a_tokens | int64 | continua | 7649 | 0.0 |
| sum_assistant_b_tokens | int64 | continua | 7084 | 0.0 |
| context_b_tokens | int64 | continua | 7682 | 0.0 |
| sum_user_tokens | int64 | discreta | 3331 | 0.0 |
| turns | int64 | discreta | 35 | 0.0 |
| header_count_a_h1 | int64 | discreta | 44 | 0.0 |
| header_count_a_h2 | int64 | discreta | 64 | 0.0 |
| header_count_a_h3 | int64 | discreta | 101 | 0.0 |
| header_count_a_h4 | int64 | discreta | 67 | 0.0 |
| header_count_a_h5 | int64 | discreta | 18 | 0.0 |
| header_count_a_h6 | int64 | discreta | 5 | 0.0 |
| list_count_a_ordered | int64 | discreta | 184 | 0.0 |
| list_count_a_unordered | int64 | discreta | 362 | 0.0 |
| bold_count_a_** | int64 | discreta | 430 | 0.0 |
| bold_count_a___ | int64 | discreta | 31 | 0.0 |
| header_count_b_h1 | int64 | discreta | 49 | 0.0 |
| header_count_b_h2 | int64 | discreta | 65 | 0.0 |
| header_count_b_h3 | int64 | discreta | 103 | 0.0 |
| header_count_b_h4 | int64 | discreta | 70 | 0.0 |
| header_count_b_h5 | int64 | discreta | 20 | 0.0 |
| header_count_b_h6 | int64 | discreta | 3 | 0.0 |
| list_count_b_ordered | int64 | discreta | 183 | 0.0 |
| list_count_b_unordered | int64 | discreta | 365 | 0.0 |
| bold_count_b_** | int64 | discreta | 431 | 0.0 |
| bold_count_b___ | int64 | discreta | 31 | 0.0 |
| creative_writing_v0.1_creative_writing | bool | binaria | 2 | 0.0 |
| creative_writing_v0.1_score | str | nominal | 14 | 0.0 |
| criteria_v0.1_complexity | bool | binaria | 2 | 0.0 |
| criteria_v0.1_creativity | bool | binaria | 2 | 0.0 |
| criteria_v0.1_domain_knowledge | bool | binaria | 2 | 0.0 |
| criteria_v0.1_problem_solving | bool | binaria | 2 | 0.0 |
| criteria_v0.1_real_world | bool | binaria | 2 | 0.0 |
| criteria_v0.1_specificity | bool | binaria | 2 | 0.0 |
| criteria_v0.1_technical_accuracy | bool | binaria | 2 | 0.0 |
| if_v0.1_if | bool | binaria | 2 | 0.0 |
| if_v0.1_score | float64 | discreta | 6 | 0.0 |
| math_v0.1_math | bool | binaria | 2 | 0.0 |

## Requisitos del curso

| estado | requisito | detalle |
| --- | --- | --- |
| OK | Al menos 2000 filas | 135634 filas |
| OK | Al menos 12 columnas | 47 columnas |
| OK | Combina al menos 3 roles analíticos | discreta, binaria, alta cardinalidad, continua, nominal, fecha |
| OK | Al menos una variable numérica | 28 numéricas (continuas o discretas) |
| OK | Al menos una variable categórica | 13 categóricas (nominales, binarias u ordinales) |
| AVISO | Presencia de valores faltantes | máximo 0.0% en una variable |
| OK | Ninguna variable sobre 60% de faltantes | máximo 0.0% |
| OK | Incluye alguna variable de fecha | 1 detectadas |
| OK | Incluye texto o categórica de alta cardinalidad | 4 detectadas |
| OK | Archivo bajo 100 MB | 37.6 MB |
| OK | Sin filas duplicadas exactas | ninguna |

## Resultado

El conjunto **cumple** los requisitos mínimos.