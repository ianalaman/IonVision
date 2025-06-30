# style.py

from dataclasses import dataclass
from typing import Mapping

@dataclass
class StyleConfig:
    base_bar_color:      str            = "k"
    zeeman_bar_color:    str            = "grey"
    sublevel_tick_color: str            = "red"
    line_width:          float          = 0.5
    tick_size:           float          = 0.3
    cmap_sublevels:      Mapping[int,str] = None  # e.g. {1:"C0", 2:"C1", ...}
