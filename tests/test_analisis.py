import numpy as np
import pandas as pd
import pytest

from arena.analisis import (
    estandarizar,
    gana_el_mayor,
    intervalo_wilson,
    modelos_p1,
    regresion_logistica,
    tasa_empates_por_diferencia,
    tasa_por_tramos,
    votos_decisivos,
)


@pytest.fixture
def limpio():
    """Seis votos: A gana 3, B gana 2 y uno sin ganador."""
    return pd.DataFrame(
        {
            "winner_binary": ["a", "a", "b", "b", "a", "other"],
            "tokens_log_a": np.float32([6.0, 5.0, 4.0, 7.0, 5.0, 5.0]),
            "tokens_log_b": np.float32([5.0, 4.0, 6.0, 5.0, 5.0, 5.0]),
            "format_a": [3, 0, 0, 10, 2, 1],
            "format_b": [0, 0, 4, 0, 2, 1],
            "longer_response": ["a", "a", "b", "a", "equal", "equal"],
            "more_formatted": ["a", "equal", "b", "a", "equal", "equal"],
        }
    )


# ── votos_decisivos ──────────────────────────────────────────────────────

def test_votos_decisivos_quita_los_sin_ganador_y_arma_las_diferencias(limpio):
    d = votos_decisivos(limpio)
    assert len(d) == 5
    assert d["y"].tolist() == [1, 1, 0, 0, 1]
    assert d["dif_tokens_log"].iloc[0] == pytest.approx(1.0)
    assert d["dif_formato_log"].iloc[0] == pytest.approx(np.log1p(3))


def test_votos_decisivos_no_modifica_la_entrada(limpio):
    columnas = list(limpio.columns)
    votos_decisivos(limpio)
    assert list(limpio.columns) == columnas


def test_votos_decisivos_pide_las_columnas_del_dataset_limpio():
    with pytest.raises(KeyError, match="faltan columnas"):
        votos_decisivos(pd.DataFrame({"winner_binary": ["a"]}))


def test_votos_decisivos_sin_votos_con_ganador_devuelve_tabla_vacia():
    df = pd.DataFrame({"winner_binary": ["other"], "tokens_log_a": [1.0], "tokens_log_b": [1.0],
                       "format_a": [0], "format_b": [0]})
    assert len(votos_decisivos(df)) == 0


# ── intervalo de Wilson ─────────────────────────────────────────────────

def test_wilson_valor_conocido():
    bajo, alto = intervalo_wilson(50, 100)
    assert bajo == pytest.approx(0.4038, abs=1e-3)
    assert alto == pytest.approx(0.5962, abs=1e-3)


def test_wilson_acepta_arreglos_y_n_cero_da_nan():
    bajo, alto = intervalo_wilson(np.array([50, 0]), np.array([100, 0]))
    assert bajo[0] == pytest.approx(0.4038, abs=1e-3)
    assert np.isnan(bajo[1]) and np.isnan(alto[1])


def test_wilson_en_el_borde_no_se_sale_de_cero_y_uno():
    bajo, alto = intervalo_wilson(0, 20)
    assert bajo == pytest.approx(0.0, abs=1e-12) and 0 < alto < 1
    bajo, alto = intervalo_wilson(20, 20)
    assert alto == pytest.approx(1.0, abs=1e-12) and 0 < bajo < 1


# ── gana_el_mayor y tramos ──────────────────────────────────────────────

def test_gana_el_mayor_excluye_los_equal(limpio):
    d = votos_decisivos(limpio)
    r = gana_el_mayor(d, "longer_response")
    # votos con más largo y ganador: a/a, a/a, b/b, a/b -> 3 de 4
    assert (r["n"], r["victorias"]) == (4, 3)
    assert r["tasa"] == pytest.approx(0.75)
    assert r["ic_bajo"] < 0.75 < r["ic_alto"]


def test_gana_el_mayor_columna_inexistente(limpio):
    with pytest.raises(KeyError):
        gana_el_mayor(votos_decisivos(limpio), "no_existe")


def test_gana_el_mayor_sin_casos_da_nan():
    d = pd.DataFrame({"winner_binary": ["a"], "longer_response": ["equal"]})
    assert np.isnan(gana_el_mayor(d, "longer_response")["tasa"])


def test_tasa_por_tramos_cuantiles_y_cortes():
    rng = np.random.default_rng(0)
    x = rng.normal(size=2000)
    d = pd.DataFrame({"x": x, "y": (rng.random(2000) < 1 / (1 + np.exp(-2 * x))).astype(int)})
    t = tasa_por_tramos(d, "x", 5)
    assert len(t) == 5 and t["n"].sum() == 2000
    assert t["tasa"].is_monotonic_increasing          # a mayor x, más victorias
    assert ((t["ic_bajo"] <= t["tasa"]) & (t["tasa"] <= t["ic_alto"])).all()
    assert len(tasa_por_tramos(d, "x", [-10, 0, 10])) == 2


def test_tasa_empates_por_diferencia():
    df = pd.DataFrame(
        {
            "tokens_log_a": [5.0, 5.0, 5.0, 8.0],
            "tokens_log_b": [5.0, 5.05, 7.0, 5.0],
            "winner_binary": ["other", "other", "a", "b"],
        }
    )
    t = tasa_empates_por_diferencia(df, tramos=(0, 0.1, 5))
    assert t["n"].tolist() == [2, 2]
    assert t["tasa"].tolist() == [1.0, 0.0]


# ── regresión logística ─────────────────────────────────────────────────

def test_regresion_recupera_los_coeficientes_simulados():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(30000, 2))
    verdad = np.array([-0.3, 1.2, -0.5])
    y = (rng.random(30000) < 1 / (1 + np.exp(-(verdad[0] + X @ verdad[1:])))).astype(int)
    t = regresion_logistica(X, y, ["a", "b"])
    assert t["coef"].to_numpy() == pytest.approx(verdad, abs=0.06)
    assert list(t.index) == ["intercepto", "a", "b"]
    assert t.loc["a", "odds"] == pytest.approx(np.exp(t.loc["a", "coef"]))
    assert t.loc["a", "p"] < 0.001


def test_regresion_p_valor_de_z_196_es_cercano_a_005():
    # Se arma una tabla con datos al azar; solo se revisa la aproximación de la normal.
    from arena.analisis import _erf
    z = 1.959964
    assert 2 * (1 - 0.5 * (1 + _erf(z / np.sqrt(2)))) == pytest.approx(0.05, abs=1e-4)


def test_regresion_acepta_x_de_una_dimension():
    rng = np.random.default_rng(2)
    x = rng.normal(size=5000)
    y = (rng.random(5000) < 1 / (1 + np.exp(-x))).astype(int)
    assert list(regresion_logistica(x, y).index) == ["intercepto", "x1"]


@pytest.mark.parametrize(
    "X, y, mensaje",
    [
        (np.ones((4, 1)), [0, 1, 0], "distinto número"),
        (np.array([[1.0], [np.nan], [2.0], [3.0]]), [0, 1, 0, 1], "faltantes"),
        (np.array([[1.0], [2.0], [3.0], [4.0]]), [0, 1, 2, 1], "0 y 1"),
        (np.ones((6, 1)), [0, 1, 0, 1, 0, 1], "singular"),
    ],
)
def test_regresion_rechaza_entradas_invalidas(X, y, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        regresion_logistica(X, y)


def test_regresion_con_nombres_de_mas_falla():
    with pytest.raises(ValueError, match="nombres"):
        regresion_logistica(np.arange(10.0)[:, None] % 3, [0, 1] * 5, ["a", "b"])


def test_regresion_con_separacion_perfecta_no_converge():
    x = np.array([-2.0, -1.0, 1.0, 2.0])
    with pytest.raises(ValueError):
        regresion_logistica(x, [0, 0, 1, 1])


# ── estandarizar y modelos ──────────────────────────────────────────────

def test_estandarizar_da_media_cero_y_desviacion_uno():
    z = estandarizar(pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [10.0, 20.0, 40.0]}), ["a", "b"])
    assert z.mean().abs().max() < 1e-12
    assert z.std(ddof=0).tolist() == pytest.approx([1.0, 1.0])


def test_estandarizar_columna_constante_falla():
    with pytest.raises(ValueError, match="constante"):
        estandarizar(pd.DataFrame({"a": [2.0, 2.0, 2.0]}), ["a"])


def test_modelos_p1_devuelve_los_tres_modelos():
    rng = np.random.default_rng(3)
    n = 6000
    dl = rng.normal(size=n)
    df = pd.DataFrame({"dif_tokens_log": dl, "dif_formato_log": 0.7 * dl + 0.7 * rng.normal(size=n)})
    df["y"] = (rng.random(n) < 1 / (1 + np.exp(-1.0 * dl))).astype(int)
    t = modelos_p1(df)
    assert set(t.index.get_level_values("modelo")) == {"solo longitud", "solo formato", "longitud y formato"}
    # El formato solo parece asociado, pero al controlar por longitud se apaga.
    assert t.loc[("solo formato", "dif_formato_log"), "coef"] > 0.3
    assert abs(t.loc[("longitud y formato", "dif_formato_log"), "coef"]) < 0.1


def test_coeficientes_por_subconjunto_y_error_si_es_muy_chico():
    from arena.analisis import coeficientes_por_subconjunto
    rng = np.random.default_rng(4)
    n = 4000
    dl = rng.normal(size=n)
    d = pd.DataFrame({"dif_tokens_log": dl, "dif_formato_log": 0.5 * dl + rng.normal(size=n)})
    d["y"] = (rng.random(n) < 1 / (1 + np.exp(-dl))).astype(int)
    t = coeficientes_por_subconjunto(d, {"todos": np.ones(n, bool), "mitad": np.arange(n) < n // 2})
    assert set(t.index.get_level_values("subconjunto")) == {"todos", "mitad"}
    assert t.loc[("todos", "dif_tokens_log"), "coef"] > 0.5
    with pytest.raises(ValueError, match="solo 10 votos"):
        coeficientes_por_subconjunto(d, {"chico": np.arange(n) < 10})


def _votos_con_modelos(n=20000, seed=5):
    """Tres modelos con fuerza distinta; el largo suma 0.8 log-odds por unidad."""
    rng = np.random.default_rng(seed)
    nombres = np.array(["m1", "m2", "m3"])
    fuerza = {"m1": 0.0, "m2": 0.8, "m3": -0.5}
    a = rng.choice(nombres, n)
    b = np.array([rng.choice([x for x in nombres if x != ai]) for ai in a])
    dl = rng.normal(size=n) + np.array([fuerza[x] for x in a]) * 0.3   # los modelos fuertes escriben más largo
    dl = dl - np.array([fuerza[x] for x in b]) * 0.3
    logit = np.array([fuerza[x] for x in a]) - np.array([fuerza[x] for x in b]) + 0.8 * dl
    return pd.DataFrame({"model_a": a, "model_b": b, "dif_tokens_log": dl,
                         "dif_formato_log": rng.normal(size=n),
                         "y": (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(int)})


def test_efecto_con_modelos_ajusta_sin_y_con_control():
    from arena.analisis import efecto_con_modelos
    t = efecto_con_modelos(_votos_con_modelos())
    assert set(t.index.get_level_values("ajuste")) == {"sin control de modelo", "con control de modelo"}
    sin = t.loc[("sin control de modelo", "dif_tokens_log"), "coef"]
    con = t.loc[("con control de modelo", "dif_tokens_log"), "coef"]
    assert sin > con > 0       # parte del efecto aparente era fuerza del modelo
    assert t["n_modelos"].iloc[0] == 3


def test_efecto_con_modelos_deja_fuera_los_modelos_con_pocos_votos():
    from arena.analisis import efecto_con_modelos
    d = _votos_con_modelos(4000)
    extra = d.iloc[:5].copy()
    extra["model_a"] = "raro"
    t = efecto_con_modelos(pd.concat([d, extra], ignore_index=True), minimo=100)
    assert t["n_modelos"].iloc[0] == 3 and t["n"].iloc[0] == 4000 - (d.iloc[:5]["model_b"].eq("raro").sum())


def test_efecto_con_modelos_errores():
    from arena.analisis import efecto_con_modelos
    with pytest.raises(KeyError):
        efecto_con_modelos(pd.DataFrame({"y": [1]}))
    d = _votos_con_modelos(300)
    with pytest.raises(ValueError, match="al menos dos modelos"):
        efecto_con_modelos(d, minimo=10_000)
