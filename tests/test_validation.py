import pandas as pd
import pytest

from arena.validation import ValidationReport, validate_dataset


def test_clean_data_passes_every_check(synthetic_df):
    report = validate_dataset(synthetic_df, expected_rows=3)
    assert not report.failures and not report.warnings
    report.assert_ok()  # must not raise


def test_limit_values_are_accepted(synthetic_df):
    df = synthetic_df.copy()
    df["evaluation_order"] = [1, 28, 1]  # both ends of the allowed range
    df["winner"] = ["both_bad", "tie", "model_a"]
    assert not validate_dataset(df).failures


def test_zero_tokens_are_valid(synthetic_df):
    assert (synthetic_df["sum_assistant_a_tokens"] == 0).any()
    assert not validate_dataset(synthetic_df).failures


@pytest.mark.parametrize(
    "column, value, check_name",
    [
        ("winner", "draw", "winner in allowed set"),
        ("evaluation_order", 29, "evaluation_order integer in [1, 28]"),
        ("evaluation_order", 0, "evaluation_order integer in [1, 28]"),
        ("sum_assistant_a_tokens", -5, "sum_assistant_a_tokens >= 0"),
        ("id", "a1", "unique id"),
        ("language", None, "no NA in key columns"),
    ],
)
def test_bad_values_are_critical_failures(synthetic_df, column, value, check_name):
    df = synthetic_df.copy()
    df.loc[1, column] = value
    report = validate_dataset(df)
    assert check_name in [c.name for c in report.failures]
    with pytest.raises(ValueError, match=check_name.split(" ")[0]):
        report.assert_ok()


def test_missing_column_is_reported_clearly(synthetic_df):
    report = validate_dataset(synthetic_df.drop(columns=["winner"]))
    assert "winner" in report.failures[0].detail
    with pytest.raises(ValueError, match="required columns"):
        report.assert_ok()


def test_timestamp_out_of_range(synthetic_df):
    df = synthetic_df.copy()
    df.loc[0, "timestamp"] = pd.Timestamp("2024-01-01")
    assert "timestamp within 2025-04-17..2025-07-24" in [c.name for c in validate_dataset(df).failures]


def test_non_datetime_timestamp_fails(synthetic_df):
    df = synthetic_df.copy()
    df["timestamp"] = df["timestamp"].astype(str)
    assert "timestamp is datetime" in [c.name for c in validate_dataset(df).failures]


def test_same_model_on_both_sides_is_only_a_warning(synthetic_df):
    df = synthetic_df.copy()
    df.loc[0, "model_b"] = df.loc[0, "model_a"]
    report = validate_dataset(df)
    assert [c.name for c in report.warnings] == ["model_a differs from model_b"]
    report.assert_ok()  # warnings never raise


def test_row_conservation_and_dtypes(synthetic_df):
    assert validate_dataset(synthetic_df, expected_rows=10).failures[0].name == "row count conserved"
    wrong = validate_dataset(synthetic_df, expected_dtypes={"is_code": "category"})
    assert "target dtypes" in [c.name for c in wrong.failures]


def test_non_dataframe_input_raises_type_error():
    with pytest.raises(TypeError, match="DataFrame"):
        validate_dataset([1, 2, 3])


def test_report_to_frame_status(synthetic_df):
    df = synthetic_df.copy()
    df.loc[0, "model_b"] = df.loc[0, "model_a"]
    frame = ValidationReport(validate_dataset(df).checks).to_frame()
    assert set(frame["status"]) == {"OK", "WARN"}
