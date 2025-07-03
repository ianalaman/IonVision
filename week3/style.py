# style.py

from dataclasses import dataclass
from typing import Mapping

@dataclass
class StyleConfig:
    # ─── Base‐level bar styling ────────────────────────────────────────────────
    base_bar_color:        str             = "k"
    base_bar_linestyle:    str             = "solid"
    zeeman_bar_color:      str             = "black"

    # ─── Parent‐level bar overrides ────────────────────────────────────────────
    parent_bar_color:      str             = "#929292"
    parent_bar_linestyle:  str             = "dotted"
    parent_bar_line_width: float           = 1.0

    # ─── Sub‐level tick styling ───────────────────────────────────────────────
    sublevel_tick_color:        str       = "red"
    sublevel_tick_linestyle:    str       = "solid"
    sublevel_tick_line_width:   float     = 1.0
    sublevel_tick_length:       float     = 0.3     # fraction of bar_half

    # ─── Parent‐sublevel tick overrides ───────────────────────────────────────
    parent_sublevel_tick_color:        str   = "purple"
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
    transition_line_width:        float = 2.0    # for reversible lines
    transition_arrow_line_width:  float = 3.0
    transition_arrowstyle:        str   = "-"
    transition_mutation_scale:    float = 10.0

    # ─── Transition‐label styling ─────────────────────────────────────────────
    transition_label_shift:      float  = 0.25  # perp‐distance from line
    transition_label_fontsize:   float  = 15.0

    # ─── Global fallback ──────────────────────────────────────────────────────
    line_width:            float           = 0.5
    tick_size:             float           = 0.3
    cmap_sublevels:        Mapping[int,str]= None
