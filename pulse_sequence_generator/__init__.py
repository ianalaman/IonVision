# ===== pulseplot/__init__.py =====
"""
Pulseplot: A modular library for visualizing pulse sequences with Matplotlib (and future interactive backends).
"""

__version__ = "0.1.0"

from .core import Pulse, Sequence
from .plot import plot_matplotlib
from .config import DEFAULT_CHANNEL_ORDER, DEFAULT_COLORS
from .utils import (draw_pulses, draw_baselines, draw_separators, draw_time_axis)

__all__ = [
    "Pulse",
    "Sequence",
    "plot_matplotlib",
    "draw_pulses",
    "draw_baselines",
    "draw_separators",
    "draw_time_axis",
    "DEFAULT_CHANNEL_ORDER",
    "DEFAULT_COLORS",
]
