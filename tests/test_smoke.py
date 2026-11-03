import arena


def test_paquete_importa():
    assert arena.__version__


def test_fixture_sintetica(df_sintetico):
    assert len(df_sintetico) == 3
    assert df_sintetico["winner"].isin(["model_a", "model_b", "tie", "both_bad"]).all()
