"""Default configuration for pulse-sequence plotting."""

from typing import Dict, List

DEFAULT_CHANNEL_ORDER: List[str] = ["MW", "EOM", "PMT", "AOM"]
"""Order in which channels are drawn (top→bottom)."""

DEFAULT_COLORS: Dict[str, str] = {
    "MW":  "#B0B0B0",
    "EOM": "#A0D468",
    "PMT": "#4C4C4C",
    "AOM": "#4A89DC",
}
"""Default fill colors for each channel."""

RC_PARAMS: Dict[str, int | float | str] = {
    "font.size":       16,
    "axes.titlesize":  18,
    "axes.labelsize":  16,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
}
"""Global Matplotlib rcParams applied to pulse plots."""

BASELINE_HEIGHT: float = 0.4
"""Relative height of each pulse bar."""

SEPARATOR_STYLE: Dict[str, object] = {"linestyle": "--", "linewidth": 0.8, "color": "grey"}
"""Style for dashed separators between time sections."""

TIME_AXIS_PROPS: Dict[str, object] = {"arrowstyle": "->", "lw": 1.5, "color": "black"}
"""Style for the time-axis arrow."""

FONT_SIZE: int = 12
"""Font size for pulse labels."""

FONT_FAMILY: str = "Cambria"
"""Font family for pulse labels."""

FONT_COLOR: str = "white"
"""Text color for pulse labels."""

HORIZONTAL_SHIFT: float = 0.0
"""x-offset applied to label position (in time units)."""

VERTICAL_SHIFT: float = 0.0
"""y-offset applied to label position (axes units)."""

__all__ = [
    "DEFAULT_CHANNEL_ORDER",
    "DEFAULT_COLORS",
    "RC_PARAMS",
    "BASELINE_HEIGHT",
    "SEPARATOR_STYLE",
    "TIME_AXIS_PROPS",
    "FONT_SIZE",
    "FONT_FAMILY",
    "FONT_COLOR",
    "HORIZONTAL_SHIFT",
    "VERTICAL_SHIFT",
]
