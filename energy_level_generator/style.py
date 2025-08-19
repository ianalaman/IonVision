# style.py
"""
Styling configuration for energy level diagrams.
"""

from dataclasses import dataclass
from typing import Mapping

@dataclass
class StyleConfig:
    # ─── Base‐level bar styling ────────────────────────────────────────────────
    base_bar_color:        str             = "k"
    base_bar_linestyle:    str             = "solid"
    zeeman_bar_color:      str             = "black"

    # ─── Parent‐level bar overrides ────────────────────────────────────────────
    parent_bar_color:      str             = "#7B7B7B"
    parent_bar_linestyle:  str             = "dotted"
    parent_bar_line_width: float           = 1.0

    # ─── Sub‐level tick styling ───────────────────────────────────────────────
    sublevel_tick_color:        str       = "red"
    sublevel_tick_linestyle:    str       = "solid"
    sublevel_tick_line_width:   float     = 1.0
    sublevel_tick_length:       float     = 0.3     # fraction of bar_half

    # ─── Parent‐sublevel tick overrides ───────────────────────────────────────
    parent_sublevel_tick_color:        str   = "black"
    parent_sublevel_tick_linestyle:    str   = "solid"
    parent_sublevel_tick_line_width:   float = 1.0
    parent_sublevel_tick_length:       float = 0.30

    # ─── Energy‐level text styling ────────────────────────────────────────────
    level_label_x_offset:    float     = 0.4    # in data‐units (added to bar_half)
    level_label_y_offset:    float     = 0.0
    level_label_fontsize:    float     = 15.0

    # ─── Sub‐level “m=” text styling ──────────────────────────────────────────
    sublevel_label_x_offset: float     = 0.15
    # base y offset for the first sublevel label (from parent y)
    sublevel_label_y_offset: float     = 5.0
    sublevel_label_y_spacing: float    = 900  # NEW: vertical gap between stacked sublevel labels
    sublevel_label_fontsize: float     = 9.0
    # base y offset for the first sublevel label (from parent y)
    sublevel_label_y_offset: float     = 0

    # ─── Transition line & arrow styling ─────────────────────────────────────
    transition_line_width:        float = 1.0    # for reversible lines
    # make the arrow “shaft” thicker
    transition_arrow_line_width:  float = 1.0
    # pick a fancier arrow head, or keep "-" for a simple triangular head
    transition_arrowstyle:        str   = "-|>"  # "->" for a simple arrow head, "-|" for a bar head
    # scale the arrow head—bigger numbers → bigger heads
    transition_mutation_scale:    float = 10.0
    transition_offset:              float = 0.025   # offset for arrows from line

    # ─── Transition‐label styling ─────────────────────────────────────────────
    transition_label_shift:      float  = 0.35  # perp‐distance from line
    transition_label_fontsize:   float  = 15.0

    # ─── Global fallback ──────────────────────────────────────────────────────
    line_width:            float           = 0.5
    tick_size:             float           = 0.3
    cmap_sublevels:        Mapping[int,str]= None
    legend_fontsize:      float           = 10.0
    legend_loc:           str             = "lower right"

    hide_split_types = {"sideband"}   # hides only sideband labels

    hide_split_types: set = set()          # e.g. {"sideband"} or {"hyperfine_mF"}
    F_legend: bool = True                  # show legend entries per F color if present
