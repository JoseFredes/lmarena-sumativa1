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
