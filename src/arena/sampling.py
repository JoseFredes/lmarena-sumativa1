"""Sampling helpers. Rows are not independent: votes of one session belong together."""
import pandas as pd

SESSION_COL = "evaluation_session_id"


def sample_rows(df: pd.DataFrame, n: int, seed: int = 42) -> pd.DataFrame:
    """Simple random sample of ``n`` rows (may split sessions apart)."""
    if not 0 < n <= len(df):
        raise ValueError(f"n must be between 1 and {len(df)}, got {n}")
    return df.sample(n=n, random_state=seed)


def sample_sessions(df: pd.DataFrame, n_sessions: int, seed: int = 42) -> pd.DataFrame:
    """Cluster sample: pick ``n_sessions`` sessions at random and keep all their rows."""
    sessions = df[SESSION_COL].drop_duplicates()
    if not 0 < n_sessions <= len(sessions):
        raise ValueError(f"n_sessions must be between 1 and {len(sessions)}, got {n_sessions}")
    chosen = sessions.sample(n=n_sessions, random_state=seed)
    return df[df[SESSION_COL].isin(chosen)]


def complete_session_share(sample: pd.DataFrame, full: pd.DataFrame) -> float:
    """Among multi-vote sessions that appear in ``sample``, share that are fully present.

    Returns NaN if the sample contains no multi-vote session of ``full``.
    """
    full_sizes = full.groupby(SESSION_COL).size()
    multi = full_sizes[full_sizes > 1]
    kept = sample.groupby(SESSION_COL).size().reindex(multi.index).dropna()
    if kept.empty:
        return float("nan")
    return float((kept == multi.reindex(kept.index)).mean())
