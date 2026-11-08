import numpy as np
import pandas as pd
import pytest

from arena.preprocessing import convert_types, derive_variables, flatten, save_clean


@pytest.fixture
def nested_df() -> pd.DataFrame:
    """Synthetic raw DataFrame with nested conv_metadata and category_tag."""
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
            "conv_metadata": [
                {
                    "sum_assistant_a_tokens": 200,
                    "sum_assistant_b_tokens": 100,
                    "header_count_a": {"h1": 1, "h2": 2},
                    "header_count_b": {"h1": 0, "h2": 0},
                    "list_count_a": {"ordered": 1, "unordered": 3},
                    "list_count_b": {"ordered": 0, "unordered": 1},
                    "bold_count_a": {"**": 4, "__": 0},
                    "bold_count_b": {"**": 1, "__": 0},
                },
                {
                    "sum_assistant_a_tokens": 50,
                    "sum_assistant_b_tokens": 50,
                    "header_count_a": {"h1": 0, "h2": 0},
                    "header_count_b": {"h1": 0, "h2": 0},
                    "list_count_a": {"ordered": 0, "unordered": 0},
                    "list_count_b": {"ordered": 0, "unordered": 0},
                    "bold_count_a": {"**": 0, "__": 0},
                    "bold_count_b": {"**": 0, "__": 0},
                },
                {
                    "sum_assistant_a_tokens": 0,
                    "sum_assistant_b_tokens": 300,
                    "header_count_a": {"h1": 0, "h2": 0},
                    "header_count_b": {"h1": 2, "h2": 1},
                    "list_count_a": {"ordered": 0, "unordered": 0},
                    "list_count_b": {"ordered": 2, "unordered": 0},
                    "bold_count_a": {"**": 0, "__": 0},
                    "bold_count_b": {"**": 3, "__": 1},
                },
            ],
            "category_tag": [
                {
                    "creative_writing_v0.1": {"creative_writing": False, "score": 0.1},
                    "criteria_v0.1": {"complexity": True, "specificity": False},
                },
                {
                    "creative_writing_v0.1": {"creative_writing": True, "score": 0.9},
                    "criteria_v0.1": {"complexity": False, "specificity": True},
                },
                {
                    "creative_writing_v0.1": {"creative_writing": False, "score": 0.0},
                    "criteria_v0.1": {"complexity": True, "specificity": True},
                },
            ],
        }
    )


def test_flatten_expands_nested_dicts_and_renames_bold_keys(nested_df):
    flat = flatten(nested_df)
    assert len(flat) == len(nested_df)
    assert "conv_metadata" not in flat.columns
    assert "category_tag" not in flat.columns
    assert "bold_a_asterisk" in flat.columns
    assert "bold_b_underscore" in flat.columns
    assert "header_a_h2" in flat.columns
    assert "cat_creative_writing" in flat.columns
    assert "cat_criteria_complexity" in flat.columns


def test_convert_types_casts_without_mutating_input(nested_df):
    flat = flatten(nested_df)
    converted = convert_types(flat)
    assert flat["winner"].dtype != "category"  # input untouched
    assert converted["winner"].dtype == "category"
    assert converted["language"].dtype == "category"
    assert converted["evaluation_order"].dtype == "int16"
    assert converted["is_code"].dtype == bool


def test_derive_variables_computes_format_logs_and_flags(nested_df):
    df = derive_variables(convert_types(flatten(nested_df)))
    # Row 0: A has 1+2 headers + 1+3 lists + 4+0 bolds = 11; B has 0+1+1 = 2
    assert list(df["format_a"]) == [11, 0, 0]
    assert list(df["format_b"]) == [2, 0, 9]
    assert list(df["longer_response"]) == ["a", "equal", "b"]
    assert list(df["more_formatted"]) == ["a", "equal", "b"]
    assert list(df["winner_binary"]) == ["a", "other", "other"]
    # Zero tokens on row 2 side A must produce log1p(0) == 0.0
    assert df.loc[2, "tokens_log_a"] == pytest.approx(0.0)
    assert df.loc[0, "tokens_log_a"] == pytest.approx(np.log1p(200), rel=1e-5)


def test_save_clean_writes_readable_parquet(nested_df, tmp_path):
    df = derive_variables(convert_types(flatten(nested_df)))
    out_path = save_clean(df, directory=tmp_path, name="test_clean.parquet")
    assert out_path.exists()
    reloaded = pd.read_parquet(out_path)
    assert reloaded.shape == df.shape
    assert list(reloaded["id"]) == ["a1", "a2", "a3"]
