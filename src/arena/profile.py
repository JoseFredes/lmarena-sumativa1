"""Structural inspection of the raw dataset: schema, row counts and per-column summary."""
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from arena.io import RAW_DIR

# Conversation columns hold full model answers (license: not redistributed) and are heavy.
TEXT_COLUMNS = ["conversation_a", "conversation_b", "full_conversation"]


def parquet_files(raw_dir: Path = RAW_DIR) -> list[Path]:
    """Return the downloaded parquet files in a stable order."""
    files = sorted(Path(raw_dir).rglob("*.parquet"))
    if not files:
        raise FileNotFoundError(f"no parquet files under {raw_dir}; run download_dataset first")
    return files


def raw_schema(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Column names and Arrow types read from file metadata, without loading any data."""
    schema = pq.ParquetFile(parquet_files(raw_dir)[0]).schema_arrow
    return pd.DataFrame({"column": schema.names, "arrow_type": [str(t)[:60] for t in schema.types]})


def count_rows(raw_dir: Path = RAW_DIR) -> dict[str, int]:
    """Rows per file (from metadata) plus the total, without loading any data."""
    counts = {f.name: pq.ParquetFile(f).metadata.num_rows for f in parquet_files(raw_dir)}
    counts["total"] = sum(counts.values())
    return counts


def load_raw(raw_dir: Path = RAW_DIR, exclude: list[str] | None = None) -> pd.DataFrame:
    """Load all parquet files into one DataFrame, skipping the columns in ``exclude``.

    By default the heavy conversation text columns are skipped.
    """
    exclude = TEXT_COLUMNS if exclude is None else exclude
    files = parquet_files(raw_dir)
    names = pq.ParquetFile(files[0]).schema_arrow.names
    columns = [c for c in names if c not in exclude]
    return pd.concat([pd.read_parquet(f, columns=columns) for f in files], ignore_index=True)


def structure_summary(df: pd.DataFrame) -> pd.DataFrame:
    """One row per column: dtype, null count and percentage, distinct values.

    Nested columns (dicts) are not hashable, so their distinct count is left empty.
    """
    rows = []
    for col in df.columns:
        s = df[col]
        try:
            n_unique = s.nunique()
        except TypeError:
            n_unique = pd.NA
        rows.append(
            {
                "column": col,
                "dtype": str(s.dtype),
                "nulls": int(s.isna().sum()),
                "null_pct": round(float(s.isna().mean() * 100), 2),
                "n_unique": n_unique,
            }
        )
    return pd.DataFrame(rows)


def frequency_table(s: pd.Series, top: int | None = None) -> pd.DataFrame:
    """Counts and percentages of each value in ``s``, most frequent first (NA included)."""
    counts = s.value_counts(dropna=False)
    if top is not None:
        counts = counts.head(top)
    return pd.DataFrame({"count": counts, "pct": (counts / len(s) * 100).round(2)})


def nested_paths(value: dict, prefix: str = "") -> dict[str, str]:
    """Map every leaf of a nested dict to its Python type name, using dotted paths."""
    paths = {}
    for key, item in value.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(item, dict):
            paths.update(nested_paths(item, path))
        else:
            paths[path] = type(item).__name__
    return paths


def nested_to_frame(s: pd.Series) -> pd.DataFrame:
    """Expand a column of dicts into flat columns (inspection only; cleaning does the real flatten)."""
    return pd.json_normalize(s.tolist(), sep="_")


def flat_view(df: pd.DataFrame) -> pd.DataFrame:
    """Return ``df`` with ``conv_metadata`` and ``category_tag`` expanded into flat columns.

    Inspection/validation view only: the cleaning step owns the real flattening.
    """
    nested = [c for c in ("conv_metadata", "category_tag") if c in df.columns]
    parts = [df.drop(columns=nested).reset_index(drop=True)]
    parts += [nested_to_frame(df[c]) for c in nested]
    return pd.concat(parts, axis=1)


def export_flat_csv(out_path: Path, raw_dir: Path = RAW_DIR) -> Path:
    """Write the flat view of the raw data (no conversation text) as CSV, e.g. for validar_dataset.py."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    flat_view(load_raw(raw_dir)).to_csv(out_path, index=False)
    return out_path
