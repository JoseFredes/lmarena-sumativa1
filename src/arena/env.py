"""Environment helpers: record which Python and library versions a notebook runs on."""
import sys

import numpy as np
import pandas as pd


def environment_info() -> dict[str, str]:
    """Return Python, numpy and pandas versions and the active interpreter path."""
    return {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "interpreter": sys.executable,
    }
