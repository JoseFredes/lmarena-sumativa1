"""Dataset validation: a structured report of checks; critical failures raise on ``assert_ok``."""
from dataclasses import dataclass

import pandas as pd

ALLOWED_WINNERS = ("model_a", "model_b", "tie", "both_bad")
REQUIRED_COLUMNS = (
    "id", "model_a", "model_b", "winner", "evaluation_session_id",
    "evaluation_order", "language", "is_code", "timestamp",
)
TOKEN_COLUMNS = (
    "sum_assistant_a_tokens", "sum_assistant_b_tokens", "sum_user_tokens",
    "context_a_tokens", "context_b_tokens",
)
ORDER_RANGE = (1, 28)  # observed in the raw data (dataset card: 1-28)
DATE_RANGE = ("2025-04-17", "2025-07-24")  # observed in the raw data


@dataclass(frozen=True)
class Check:
    """One validation result. A non-critical failure is a warning and never raises."""

    name: str
    ok: bool
    detail: str
    critical: bool = True


@dataclass
class ValidationReport:
    """Collection of checks with helpers to inspect and enforce them."""

    checks: list[Check]

    @property
    def failures(self) -> list[Check]:
        """Critical checks that failed."""
        return [c for c in self.checks if not c.ok and c.critical]

    @property
    def warnings(self) -> list[Check]:
        """Non-critical checks that failed."""
        return [c for c in self.checks if not c.ok and not c.critical]

    def to_frame(self) -> pd.DataFrame:
        """Report as a table: status, check name and detail."""
        def status(c: Check) -> str:
            return "OK" if c.ok else ("FAIL" if c.critical else "WARN")

        return pd.DataFrame(
            [{"status": status(c), "check": c.name, "detail": c.detail} for c in self.checks]
        )

    def assert_ok(self) -> None:
        """Raise ``ValueError`` listing every critical failure; warnings do not raise."""
        if self.failures:
            lines = "; ".join(f"{c.name}: {c.detail}" for c in self.failures)
            raise ValueError(f"{len(self.failures)} critical validation check(s) failed: {lines}")


def validate_dataset(
    df: pd.DataFrame,
    expected_rows: int | None = None,
    expected_dtypes: dict[str, str] | None = None,
    order_range: tuple[int, int] = ORDER_RANGE,
    date_range: tuple[str, str] = DATE_RANGE,
) -> ValidationReport:
    """Run every check on ``df`` and return the report (nothing is raised here).

    ``expected_rows`` checks row conservation against the raw data; ``expected_dtypes`` maps
    column names to dtype names. Checks that need a missing column are skipped, since the
    missing column is already reported as a critical failure.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df must be a pandas DataFrame, got {type(df).__name__}")

    checks: list[Check] = []
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    checks.append(Check("required columns", not missing, f"missing: {missing}" if missing else "all present"))
    has = lambda *cols: all(c in df.columns for c in cols)  # noqa: E731

    key_cols = [c for c in REQUIRED_COLUMNS if c in df.columns]
    na = df[key_cols].isna().sum()
    na = na[na > 0]
    checks.append(Check("no NA in key columns", na.empty, "none" if na.empty else na.to_dict().__str__()))

    if has("id"):
        dup = int(df["id"].duplicated().sum())
        checks.append(Check("unique id", dup == 0, "none duplicated" if dup == 0 else f"{dup} duplicated"))

    if has("winner"):
        bad = df.loc[~df["winner"].astype(str).isin(ALLOWED_WINNERS), "winner"].unique().tolist()
        checks.append(Check("winner in allowed set", not bad, "all valid" if not bad else f"invalid: {bad}"))

    if has("evaluation_order"):
        order = pd.to_numeric(df["evaluation_order"], errors="coerce")
        lo, hi = order_range
        n_bad = int((order.isna() | (order < lo) | (order > hi) | (order % 1 != 0)).sum())
        checks.append(Check(f"evaluation_order integer in [{lo}, {hi}]", n_bad == 0, f"{n_bad} out of range"))

    if has("timestamp"):
        if pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            start, end = (pd.Timestamp(d) for d in date_range)
            n_bad = int(((df["timestamp"] < start) | (df["timestamp"] >= end + pd.Timedelta(days=1))).sum())
            checks.append(Check(f"timestamp within {date_range[0]}..{date_range[1]}", n_bad == 0, f"{n_bad} outside"))
        else:
            checks.append(Check("timestamp is datetime", False, f"dtype is {df['timestamp'].dtype}"))

    for col in (c for c in TOKEN_COLUMNS if c in df.columns):
        n_neg = int((df[col] < 0).sum())
        checks.append(Check(f"{col} >= 0", n_neg == 0, f"{n_neg} negative"))

    if expected_dtypes:
        wrong = {c: str(df[c].dtype) for c, t in expected_dtypes.items() if c in df.columns and str(df[c].dtype) != t}
        absent = [c for c in expected_dtypes if c not in df.columns]
        ok = not wrong and not absent
        checks.append(Check("target dtypes", ok, "all match" if ok else f"wrong: {wrong}, absent: {absent}"))

    if expected_rows is not None:
        checks.append(Check("row count conserved", len(df) == expected_rows, f"{len(df)} rows, expected {expected_rows}"))

    if has("model_a", "model_b"):
        same = int((df["model_a"] == df["model_b"]).sum())
        checks.append(Check("model_a differs from model_b", same == 0, f"{same} rows with the same model", critical=False))

    return ValidationReport(checks)
