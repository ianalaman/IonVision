# style.py
"""
Styling configuration for energy-level diagrams.
"""

from dataclasses import dataclass, field
from typing import Mapping, Optional, Set

@dataclass
class StyleConfig:
    """Collection of style knobs used by the plotter."""

    # ── Base-level bars ───────────────────────────────────────────────────────
    base_bar_color: str = "k"
    """Color for base level bars."""

    base_bar_linestyle: str = "solid"
    """Linestyle for base level bars."""

    zeeman_bar_color: str = "black"
    """Color for bars drawn on Zeeman parents (if used)."""

    # ── Parent-level overrides ────────────────────────────────────────────────
    parent_bar_color: str = "#7B7B7B"
    """Color for parent bars that have sublevels."""

    parent_bar_linestyle: str = "dotted"
    """Linestyle for parent bars."""

    parent_bar_line_width: float = 1.0
    """Line width for parent bars."""

    # ── Sublevel ticks ────────────────────────────────────────────────────────
    sublevel_tick_color: str = "red"
    """Tick color for sublevels."""

    sublevel_tick_linestyle: str = "solid"
    """Tick linestyle for sublevels."""

    sublevel_tick_line_width: float = 1.0
    """Tick line width for sublevels."""

    sublevel_tick_length: float = 0.3
    """Tick half-length as a fraction of `bar_half`."""

    # ── Parent-sublevel tick overrides ────────────────────────────────────────
    parent_sublevel_tick_color: str = "black"
    """Tick color for sublevels of a parent with children."""

    parent_sublevel_tick_linestyle: str = "solid"
    """Tick linestyle for sublevels of a parent with children."""

    parent_sublevel_tick_line_width: float = 1.0
    """Tick line width for sublevels of a parent with children."""

    parent_sublevel_tick_length: float = 0.30
    """Tick half-length for sublevels of a parent with children."""

    # ── Level text ────────────────────────────────────────────────────────────
    level_label_x_offset: float = 0.4
    """Extra x-offset from bar end (data units)."""

    level_label_y_offset: float = 0.0
    """Vertical offset for level labels (data units)."""

    level_label_fontsize: float = 15.0
    """Font size for level labels."""

    # ── Sublevel text ─────────────────────────────────────────────────────────
    sublevel_label_x_offset: float = 0.15
    """Extra x-offset for sublevel labels."""

    sublevel_label_y_offset: float = 5.0
    """Vertical offset for each sublevel label (data units)."""

    sublevel_label_y_spacing: float = 900.0
    """Extra vertical gap between stacked sublevel labels."""

    sublevel_label_fontsize: float = 9.0
    """Font size for sublevel labels."""

    # ── Transitions ───────────────────────────────────────────────────────────
    transition_line_width: float = 1.0
    """Line width for transition segments."""

    transition_arrow_line_width: float = 1.0
    """Line width for transition arrows."""

    transition_arrowstyle: str = "-|>"
    """Matplotlib arrowstyle for one-way transitions."""

    transition_mutation_scale: float = 10.0
    """Arrow head size (Matplotlib mutation scale)."""

    transition_offset: float = 0.025
    """Normal offset for stacked parallel transitions."""

    # ── Transition labels ─────────────────────────────────────────────────────
    transition_label_shift: float = 0.35
    """Perpendicular distance from the transition line for labels."""

    transition_label_fontsize: float = 15.0
    """Font size for transition labels."""

    # ── Global / legend ───────────────────────────────────────────────────────
    line_width: float = 0.5
    """Fallback line width."""

    tick_size: float = 0.3
    """Fallback tick size."""

    cmap_sublevels: Optional[Mapping[int, str]] = None
    """Optional mapping `m → color` to color-code sublevels."""

    legend_fontsize: float = 10.0
    """Legend font size."""

    legend_loc: str = "lower right"
    """Legend location string."""

    hide_split_types: Set[str] = field(default_factory=set)
    """Split types to hide in labels/ticks (e.g., `{'sideband'}`)."""

    F_legend: bool = True
    """Whether to include an F-legend when hyperfine is present."""

    # Header / value shifts (data units, applied by _outward)
    qnum_header_x_shift: float = 0.0
    qnum_value_x_shift: float = 0.0

    # Quantum-number label toggles
    show_qnum_header: bool = True
    zeeman_label_value_only: bool = True

    # Fonts/colors for sublevel values
    sublevel_value_fontfamily: str = "DejaVu Sans Mono"

    # Optional sideband overrides
    sideband_blue_color: str = "blue"
    sideband_red_color: str = "red"
    sideband_tick_length: float = 0.6  # fraction of bar_half
# ↑ END OF CLASS --------------------------------------------------------------


def default_style() -> StyleConfig:
    """Return a StyleConfig with sensible project defaults."""
    s = StyleConfig()
    # your custom defaults
    s.hide_split_types = {"sideband"}
    s.show_qnum_header = True
    s.zeeman_label_value_only = True
    s.qnum_header_x_shift = 0.045
    s.qnum_value_x_shift = 0.00
    s.sublevel_value_fontfamily = "DejaVu Sans Mono"
    return s
