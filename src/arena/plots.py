"""Small matplotlib helpers so notebooks only call a function and show the figure."""
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure


def plot_bars(freq: pd.DataFrame, title: str, xlabel: str = "") -> Figure:
    """Horizontal bar chart of a ``frequency_table`` (largest on top)."""
    fig, ax = plt.subplots(figsize=(7, 0.4 * len(freq) + 1.5))
    ax.barh(freq.index.astype(str)[::-1], freq["count"][::-1])
    ax.set_title(title)
    ax.set_xlabel(xlabel or "count")
    fig.tight_layout()
    plt.close(fig)
    return fig


def plot_hist(s: pd.Series, title: str, bins: int = 50, log_x: bool = False) -> Figure:
    """Histogram of a numeric series, optionally on a log10(1 + x) scale for skewed data."""
    values = s.dropna()
    xlabel = s.name or "value"
    if log_x:
        values = (values + 1).apply("log10")
        xlabel = f"log10(1 + {xlabel})"
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.hist(values, bins=bins)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("rows")
    fig.tight_layout()
    plt.close(fig)
    return fig


def plot_daily_counts(timestamps: pd.Series, title: str) -> Figure:
    """Line chart of how many rows fall on each calendar day."""
    daily = timestamps.dt.floor("D").value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(daily.index, daily.values)
    ax.set_title(title)
    ax.set_ylabel("rows per day")
    fig.autofmt_xdate()
    fig.tight_layout()
    plt.close(fig)
    return fig


def plot_escalamiento(tabla: pd.DataFrame, columna: str, title: str, xlabel: str = "n") -> Figure:
    """Líneas en escala log-log de ``columna`` contra ``n``, una por implementación."""
    fig, ax = plt.subplots(figsize=(7, 4))
    for nombre, g in tabla.groupby("implementacion", sort=False):
        ax.plot(g["n"], g[columna], marker="o", label=nombre)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(columna)
    ax.legend()
    fig.tight_layout()
    plt.close(fig)
    return fig


def plot_tasa_por_tramos(tablas: dict, title: str, xlabel: str, ylabel: str, fuente: str) -> Figure:
    """Tasa de victoria con intervalo de confianza, una línea por tabla de `tasa_por_tramos`.

    `tablas` mapea la etiqueta de la leyenda a la tabla. La línea punteada marca 50 %, donde
    ninguno de los dos lados gana más seguido. `fuente` se escribe al pie.
    """
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    for etiqueta, t in tablas.items():
        err = [t["tasa"] - t["ic_bajo"], t["ic_alto"] - t["tasa"]]
        ax.errorbar(t["centro"], t["tasa"] * 100, yerr=[e * 100 for e in err], marker="o", capsize=3, label=etiqueta)
    ax.axhline(50, color="grey", linestyle="--", linewidth=1)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(title=None, fontsize=8)
    ax.grid(alpha=0.3)
    fig.text(0.01, 0.005, fuente, fontsize=7, color="dimgrey", ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    plt.close(fig)
    return fig


def plot_coeficientes(tabla: pd.DataFrame, title: str, xlabel: str, fuente: str, etiquetas: dict | None = None) -> Figure:
    """Gráfico de bosque: un punto con intervalo por fila de `coeficientes_por_subconjunto`.

    Las filas se agrupan por variable (color) y se ordenan por subconjunto; la línea en 0
    marca "sin asociación". `etiquetas` cambia el nombre de las variables en la leyenda.
    """
    etiquetas = etiquetas or {}
    sub = list(dict.fromkeys(tabla.index.get_level_values(0)))
    vars_ = list(dict.fromkeys(tabla.index.get_level_values(1)))
    fig, ax = plt.subplots(figsize=(7.5, 0.6 * len(sub) + 2.2))
    ancho = 0.35
    for j, v in enumerate(vars_):
        pos = [i + (j - (len(vars_) - 1) / 2) * ancho for i in range(len(sub))]
        t = tabla.xs(v, level=1).loc[sub]
        ax.errorbar(t["coef"], pos, xerr=[t["coef"] - t["ic_bajo"], t["ic_alto"] - t["coef"]], fmt="o", capsize=3, label=etiquetas.get(v, v))
    ax.axvline(0, color="grey", linestyle="--", linewidth=1)
    ax.set_yticks(range(len(sub)))
    ax.set_yticklabels(sub)
    ax.invert_yaxis()
    ax.set_title(title, fontsize=11)
    ax.set_xlabel(xlabel)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(axis="x", alpha=0.3)
    fig.text(0.01, 0.005, fuente, fontsize=7, color="dimgrey", ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    plt.close(fig)
    return fig
