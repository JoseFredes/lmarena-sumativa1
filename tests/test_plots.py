import numpy as np
import pandas as pd

from arena.plots import plot_coeficientes, plot_tasa_por_tramos


def _tabla():
    return pd.DataFrame(
        {"centro": [-1.0, 0.0, 1.0], "tasa": [0.3, 0.5, 0.7], "ic_bajo": [0.28, 0.48, 0.68], "ic_alto": [0.32, 0.52, 0.72]}
    )


def test_plot_tasa_por_tramos_tiene_titulo_ejes_leyenda_y_fuente():
    fig = plot_tasa_por_tramos({"todos": _tabla(), "otro": _tabla()}, "Título", "x", "y", "Fuente: prueba")
    ax = fig.axes[0]
    assert ax.get_title() == "Título"
    assert ax.get_xlabel() == "x" and ax.get_ylabel() == "y"
    assert [t.get_text() for t in ax.get_legend().get_texts()] == ["todos", "otro"]
    assert any(t.get_text() == "Fuente: prueba" for t in fig.texts)


def test_plot_coeficientes_dibuja_una_fila_por_subconjunto():
    idx = pd.MultiIndex.from_product([["todos", "inglés"], ["longitud", "formato"]], names=["subconjunto", "variable"])
    t = pd.DataFrame({"coef": [0.5, 0.04, 0.6, 0.0], "ic_bajo": [0.4, 0.0, 0.5, -0.05], "ic_alto": [0.6, 0.08, 0.7, 0.05]}, index=idx)
    fig = plot_coeficientes(t, "Título", "log-odds", "Fuente: prueba")
    ax = fig.axes[0]
    assert [x.get_text() for x in ax.get_yticklabels()] == ["todos", "inglés"]
    assert [x.get_text() for x in ax.get_legend().get_texts()] == ["longitud", "formato"]
    assert ax.get_title() == "Título"
