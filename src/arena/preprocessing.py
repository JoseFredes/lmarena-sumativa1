"""F2_02 · Cleaning and transformation of the LMArena dataset.

Pipeline: load_raw → flatten → convert types → derive variables → save.
Everything runs on the full dataset (135 634 rows); no sampling.
"""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from arena.io import PROJECT_ROOT
from arena.profile import load_raw

logger = logging.getLogger(__name__)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_NAME = "arena_clean.parquet"

# ── helpers ────────────────────────────────────────────────────────────

# These come from nested dicts inside conv_metadata.
# We rename the `**` / `__` bold keys to something valid.
_BOLD_RENAME = {"**": "asterisk", "__": "underscore"}


def _flatten_conv_metadata(series: pd.Series) -> pd.DataFrame:
    """Flatten the ``conv_metadata`` dicts into one column per leaf value.

    Produces clean column names like ``header_a_h2``, ``list_b_unordered``,
    ``bold_a_asterisk`` (instead of ``bold_count_a_**``).
    """
    rows: list[dict] = []
    for d in series:
        flat: dict[str, int] = {}
        for key, val in d.items():
            if isinstance(val, dict):
                for sub, v in val.items():
                    # e.g. header_count_a + h2 → header_a_h2
                    #      bold_count_a   + ** → bold_a_asterisk
                    prefix = key.replace("_count", "")      # header_count_a → header_a
                    suffix = _BOLD_RENAME.get(sub, sub)
                    flat[f"{prefix}_{suffix}"] = v
                continue
            flat[key] = val
        rows.append(flat)
    return pd.DataFrame(rows)


def _flatten_category_tag(series: pd.Series) -> pd.DataFrame:
    """Flatten ``category_tag`` dicts.

    The two sub-dicts (creative_writing_v0.1, criteria_v0.1, if_v0.1, math_v0.1)
    become columns like ``cat_creative_writing``, ``cat_criteria_complexity``, etc.
    """
    rows: list[dict] = []
    for d in series:
        flat: dict = {}
        for group_key, group_val in d.items():
            # group_key like "criteria_v0.1"
            prefix = group_key.rsplit("_v", 1)[0]           # criteria_v0.1 → criteria
            if isinstance(group_val, dict):
                for sub, v in group_val.items():
                    if sub == prefix:                        # e.g. creative_writing.creative_writing
                        flat[f"cat_{prefix}"] = v
                    else:
                        flat[f"cat_{prefix}_{sub}"] = v
            else:
                flat[f"cat_{group_key}"] = group_val
        rows.append(flat)
    return pd.DataFrame(rows)


# ── main pipeline ──────────────────────────────────────────────────────

def flatten(df: pd.DataFrame) -> pd.DataFrame:
    """Replace ``conv_metadata`` and ``category_tag`` with their flat columns."""
    meta = _flatten_conv_metadata(df["conv_metadata"])
    cat = _flatten_category_tag(df["category_tag"])
    flat = pd.concat(
        [df.drop(columns=["conv_metadata", "category_tag"]).reset_index(drop=True), meta, cat],
        axis=1,
    )
    return flat


def convert_types(df: pd.DataFrame) -> pd.DataFrame:
    """Cast columns to their analysis types."""
    df = df.copy()

    # Categoricals (low cardinality)
    for col in ("winner", "language"):
        df[col] = df[col].astype("category")

    # Boolean that arrives as numpy bool → keep
    # is_code is already bool; just ensure it
    df["is_code"] = df["is_code"].astype(bool)

    # timestamp is already datetime64[ns]

    # Integer columns that are int32 from parquet → int16 where range allows
    if "evaluation_order" in df.columns:
        df["evaluation_order"] = df["evaluation_order"].astype("int16")

    return df


def derive_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Create the derived columns needed for P1 (format vs. content).

    New columns
    -----------
    format_a, format_b : int
        Sum of all formatting marks (headers h1–h6 + lists + bolds) per side.
    tokens_log_a, tokens_log_b : float
        log₁₀(1 + tokens) for each side.
    longer_response : str {"a", "b", "equal"}
        Which side wrote more tokens.
    more_formatted : str {"a", "b", "equal"}
        Which side used more formatting marks.
    winner_binary : str {"a", "b", "other"}
        Simplifies winner for quick crosstabs (tie/both_bad → "other").
    """
    df = df.copy()

    # ── Format score: headers + lists + bolds per side ──
    header_cols_a = [c for c in df.columns if c.startswith("header_a_")]
    list_cols_a = [c for c in df.columns if c.startswith("list_a_")]
    bold_cols_a = [c for c in df.columns if c.startswith("bold_a_")]
    df["format_a"] = df[header_cols_a + list_cols_a + bold_cols_a].sum(axis=1).astype(int)

    header_cols_b = [c for c in df.columns if c.startswith("header_b_")]
    list_cols_b = [c for c in df.columns if c.startswith("list_b_")]
    bold_cols_b = [c for c in df.columns if c.startswith("bold_b_")]
    df["format_b"] = df[header_cols_b + list_cols_b + bold_cols_b].sum(axis=1).astype(int)

    # ── Log-transformed tokens ──
    df["tokens_log_a"] = np.log1p(df["sum_assistant_a_tokens"]).astype("float32")
    df["tokens_log_b"] = np.log1p(df["sum_assistant_b_tokens"]).astype("float32")

    # ── Comparison flags ──
    df["longer_response"] = np.where(
        df["sum_assistant_a_tokens"] > df["sum_assistant_b_tokens"], "a",
        np.where(df["sum_assistant_a_tokens"] < df["sum_assistant_b_tokens"], "b", "equal"),
    )
    df["more_formatted"] = np.where(
        df["format_a"] > df["format_b"], "a",
        np.where(df["format_a"] < df["format_b"], "b", "equal"),
    )

    # ── Simplified winner ──
    df["winner_binary"] = df["winner"].map(
        {"model_a": "a", "model_b": "b", "tie": "other", "both_bad": "other"}
    )

    return df


def clean_dataset(raw_dir=None) -> pd.DataFrame:
    """Full pipeline: load → flatten → types → derive.

    Parameters
    ----------
    raw_dir : Path, optional
        Forwarded to ``load_raw``.

    Returns
    -------
    pd.DataFrame
        Ready for analysis, with ~47 columns and 135 634 rows.
    """
    kwargs = {"raw_dir": raw_dir} if raw_dir else {}
    logger.info("Loading raw data…")
    df = load_raw(**kwargs)
    n_raw = len(df)
    logger.info("Loaded %d rows.", n_raw)

    logger.info("Flattening nested columns…")
    df = flatten(df)

    logger.info("Converting types…")
    df = convert_types(df)

    logger.info("Deriving variables…")
    df = derive_variables(df)

    assert len(df) == n_raw, f"Row count changed: {n_raw} → {len(df)}"
    logger.info("Done: %d rows × %d columns.", *df.shape)
    return df


def save_clean(df: pd.DataFrame, directory: Path = PROCESSED_DIR, name: str = OUTPUT_NAME) -> Path:
    """Write the clean DataFrame to parquet."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    df.to_parquet(path, index=False)
    logger.info("Saved %s (%.1f MB).", path, path.stat().st_size / 1e6)
    return path
