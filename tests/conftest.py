"""Fixtures compartidas. Los tests no usan red: trabajan con datos sintéticos."""
import pandas as pd
import pytest


@pytest.fixture
def df_sintetico() -> pd.DataFrame:
    """Tres votos de ejemplo con las columnas planas esperadas (esquema provisional)."""
    return pd.DataFrame(
        {
            "id": ["a1", "a2", "a3"],
            "model_a": ["modelo-x", "modelo-y", "modelo-x"],
            "model_b": ["modelo-y", "modelo-z", "modelo-z"],
            "winner": ["model_a", "tie", "model_b"],
            "evaluation_session_id": ["s1", "s1", "s2"],
            "evaluation_order": [1, 2, 1],
            "language": ["en", "es", "en"],
            "is_code": [False, False, True],
        }
    )
