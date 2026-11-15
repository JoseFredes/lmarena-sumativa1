"""Shared fixtures. Tests never use the network: they run on synthetic data."""
import pandas as pd
import pytest


@pytest.fixture
def synthetic_df() -> pd.DataFrame:
    """Three sample votes with the expected flat columns (provisional schema)."""
    return pd.DataFrame(
        {
            "id": ["a1", "a2", "a3"],
            "model_a": ["model-x", "model-y", "model-x"],
            "model_b": ["model-y", "model-z", "model-z"],
            "winner": ["model_a", "tie", "model_b"],
            "evaluation_session_id": ["s1", "s1", "s2"],
            "evaluation_order": [1, 2, 1],
            "language": ["en", "es", "en"],
            "is_code": [False, False, True],
            "timestamp": pd.to_datetime(["2025-04-17 00:20", "2025-06-01 12:00", "2025-07-24 23:59"]),
            "sum_assistant_a_tokens": [0, 120, 4000],
            "sum_assistant_b_tokens": [35, 0, 800],
        }
    )


@pytest.fixture
def raw_anidado() -> pd.DataFrame:
    """Tres votos con las columnas anidadas de LMArena (formato crudo, como load_raw)."""

    def meta(a, b, h2_a=0, h2_b=0, lista_a=0, negrita_a=0):
        return {
            "sum_assistant_a_tokens": a,
            "sum_assistant_b_tokens": b,
            "sum_user_tokens": 10,
            "header_count_a": {"h1": 0, "h2": h2_a},
            "header_count_b": {"h1": 0, "h2": h2_b},
            "list_count_a": {"ordered": 0, "unordered": lista_a},
            "list_count_b": {"ordered": 0, "unordered": 0},
            "bold_count_a": {"**": negrita_a, "__": 0},
            "bold_count_b": {"**": 0, "__": 0},
        }

    def etiqueta(creativa, puntaje):
        return {
            "creative_writing_v0.1": {"creative_writing": creativa, "score": puntaje},
            "criteria_v0.1": {"complexity": True, "specificity": False},
            "if_v0.1": {"if": False, "score": 2},
            "math_v0.1": {"math": False},
        }

    return pd.DataFrame(
        {
            "id": ["a1", "a2", "a3"],
            "model_a": ["m1", "m2", "m1"],
            "model_b": ["m2", "m3", "m3"],
            "winner": ["model_a", "tie", "both_bad"],
            "evaluation_session_id": ["s1", "s1", "s2"],
            "evaluation_order": pd.Series([1, 2, 1], dtype="int32"),
            "language": ["en", "es", "en"],
            "is_code": [False, True, False],
            "timestamp": pd.to_datetime(["2025-05-01", "2025-06-01", "2025-07-01"]),
            "conv_metadata": [meta(200, 100, h2_a=2, lista_a=3, negrita_a=4), meta(50, 50), meta(0, 300, h2_b=1)],
            "category_tag": [etiqueta(True, "yes"), etiqueta(False, "no"), etiqueta(False, "no")],
        }
    )
