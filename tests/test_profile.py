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


def test_frequency_table_counts_and_pct():
    from arena.profile import frequency_table

    table = frequency_table(pd.Series(["a", "a", "b", None]))
    assert table.loc["a", "count"] == 2
    assert table.loc["a", "pct"] == 50.0
    assert len(frequency_table(pd.Series(list("aabbc")), top=2)) == 2


def test_nested_paths_and_frame():
    from arena.profile import nested_paths, nested_to_frame

    value = {"a": 1, "b": {"c": True, "d": "x"}}
    assert nested_paths(value) == {"a": "int", "b.c": "bool", "b.d": "str"}
    flat = nested_to_frame(pd.Series([value]))
    assert list(flat.columns) == ["a", "b_c", "b_d"]


def test_flat_view_expands_nested_columns(raw_dir):
    from arena.profile import flat_view

    flat = flat_view(load_raw(raw_dir))
    assert "conv_metadata" not in flat.columns
    assert "tokens" in flat.columns
    assert len(flat) == 6


def test_export_flat_csv_roundtrip(raw_dir, tmp_path):
    from arena.profile import export_flat_csv

    out = export_flat_csv(tmp_path / "interim" / "flat.csv", raw_dir)
    assert len(pd.read_csv(out)) == 6
