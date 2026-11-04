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
