import pandas as pd
import pytest

from arena.profile import count_rows, load_raw, parquet_files, raw_schema, structure_summary


@pytest.fixture
def raw_dir(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    for i in range(2):
        pd.DataFrame(
            {
                "id": [f"{i}-{j}" for j in range(3)],
                "winner": ["model_a", "tie", None],
                "conversation_a": ["x", "y", "z"],
                "conv_metadata": [{"tokens": j} for j in range(3)],
            }
        ).to_parquet(d / f"train-{i}.parquet")
    return tmp_path


def test_parquet_files_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="download_dataset"):
        parquet_files(tmp_path)


def test_count_rows(raw_dir):
    assert count_rows(raw_dir) == {"train-0.parquet": 3, "train-1.parquet": 3, "total": 6}


def test_raw_schema_lists_all_columns(raw_dir):
    assert list(raw_schema(raw_dir)["column"]) == ["id", "winner", "conversation_a", "conv_metadata"]


def test_load_raw_skips_text_columns(raw_dir):
    df = load_raw(raw_dir)
    assert len(df) == 6
    assert "conversation_a" not in df.columns


def test_structure_summary_nulls_and_nested(raw_dir):
    summary = structure_summary(load_raw(raw_dir)).set_index("column")
    assert summary.loc["winner", "nulls"] == 2
    assert summary.loc["id", "n_unique"] == 6
    assert pd.isna(summary.loc["conv_metadata", "n_unique"])
