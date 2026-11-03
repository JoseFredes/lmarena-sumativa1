import arena


def test_package_imports():
    assert arena.__version__


def test_synthetic_fixture(synthetic_df):
    assert len(synthetic_df) == 3
    assert synthetic_df["winner"].isin(["model_a", "model_b", "tie", "both_bad"]).all()
