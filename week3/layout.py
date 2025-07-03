# layout.py

from dataclasses import dataclass
from typing import List, Dict
import numpy as np
from week3.style     import StyleConfig
from .models import Level
from collections import defaultdict
from typing import Callable
from .models import Level
from fractions import Fraction


@dataclass
class LayoutConfig:
    """
    Configuration for horizontal & vertical placement of energy levels.

    Attributes:
      column_letters:   list of spectroscopic letters, e.g. ['S','P','D','F']
      column_positions: integer column index for each letter (same length)
      spacing:          horizontal base‐offset for each column (may be < bar width)
      bar_half:         half-width of each energy-bar along x
      x_jitter:         max horizontal offset for sub-levels around parent
      y_jitter:         vertical jitter magnitude for stacking base levels
    """
    column_letters:   List[str]
    column_positions: List[int]
    spacing:          float = 0.5
    bar_half:         float = 0.1
    x_jitter:         float = 0.2
    y_jitter:         float = 20000.0
    energy_group_key: Callable[[Level], int] = lambda lvl: int(lvl.energy // 10)
    energy_group_y_scale: float = 3000000
    # sublevel_y_scale:     float = 1.0 
    # sub_vis_min: float = 5   # minimum “visual” offset for a sub‐level
    # sub_vis_max: float = 1000   # maximum “visual” offset for a sub‐level
    sublevel_uniform_spacing: float = 1000.0   # distance between adjacent sublevels
    sublevel_uniform_centered: bool = True   # whether to center around parent


def infer_column(level: Level, cfg: LayoutConfig) -> int:
    """
    Map a Level to its integer column index.

    Extracts the second char of the term (e.g. '2P3/2'→'P'),
    finds its index in cfg.column_letters and returns
    cfg.column_positions[idx], or 0 if missing.
    """
    term   = level.label.split()[1]
    letter = term[1]
    try:
        idx = cfg.column_letters.index(letter)
        return cfg.column_positions[idx]
    except ValueError:
        return 0

def compute_base_x_map(
    levels: List[Level],
    cfg: LayoutConfig
) -> Dict[str, float]:
    """
    Compute x-positions for *base* levels (sublevel == 0).

    For each spectroscopic column (S, P, D, F...):
      - Group base levels by unique energy (energy groups) within each column.
      - For each energy group, spread all levels in the group out symmetrically
        around the column center (not just the first at center).
      - Bar centers at: x = col*spacing + (i - (n-1)/2) * 2*bar_half

    All levels in an energy group are spread out, centered at the column center.
    The grouping key function is provided by cfg.energy_group_key.
    """

    # Group base levels by column index
    cols: Dict[int, List[Level]] = {}
    for lvl in levels:
        if lvl.sublevel != 0:
            continue
        col = infer_column(lvl, cfg)
        cols.setdefault(col, []).append(lvl)

    base_map: Dict[str, float] = {}
    bar_width = 2 * cfg.bar_half

    # Use the grouping key function from config, or default to int(lvl.energy // 10000)
    group_key = getattr(cfg, "energy_group_key", lambda lvl: int(lvl.energy // 10000))

    for col, bases in cols.items():
        col_center = col * cfg.spacing
        energy_groups: Dict[int, List[Level]] = defaultdict(list)
        for lvl in bases:
            key = group_key(lvl)
            energy_groups[key].append(lvl)

        # Sort groups by energy
        for energy in sorted(energy_groups):
            group = energy_groups[energy]
            n = len(group)
            # Spread all levels in the group out, centered at col_center
            if n == 1:
                base_map[group[0].label] = col_center
            else:
                # fan to the right only
                offsets = [i * bar_width for i in range(n)]
                for lvl, off in zip(sorted(group, key=lambda l: l.label), offsets):
                    base_map[lvl.label] = col_center + off

    return base_map

def compute_sublevel_x_map(
    levels: List[Level],
    base_map: Dict[str, float],
    cfg: LayoutConfig,
    style: StyleConfig
) -> Dict[str, float]:
    """
    Compute x-positions for sublevels (sublevel > 0).

    For each parent:
      - Collect its sublevels.
      - Extract the numeric m from each label (e.g. ", m=+1.5").
      - Sort by that m-value so negatives on left.
      - Spread within [-x_jitter, +x_jitter] around parent center.
    """
    from collections import defaultdict

    subs_by_parent: Dict[str, List[Level]] = defaultdict(list)
    for lvl in levels:
        if lvl.sublevel > 0 and lvl.parent:
            subs_by_parent[lvl.parent.label].append(lvl)

    sub_map: Dict[str, float] = {}
    for parent_lbl, subs in subs_by_parent.items():
        base_x = base_map.get(parent_lbl, 0.0)
        n = len(subs)
        if n == 0:
            continue

        # sort by numeric m
        subs_sorted = sorted(subs, key=lambda L: float(Fraction(L.label.split("m=")[1])))

        # use cfg.x_jitter instead of safe jitter
        offsets = np.linspace(-cfg.x_jitter, cfg.x_jitter, n)

        for lvl, off in zip(subs_sorted, offsets):
            sub_map[lvl.label] = base_x + off

    return sub_map



def compute_x_map(
    levels: List[Level],
    cfg:   LayoutConfig,
    style: StyleConfig
) -> Dict[str, float]:
    """
    Merge base and sublevel x-maps into one dict: label → x coordinate.
    """
    base_map = compute_base_x_map(levels, cfg)
    sub_map = compute_sublevel_x_map(levels, base_map, cfg, style)
    return {**base_map, **sub_map}


def compute_y_map(
    levels: List[Level],
    cfg: LayoutConfig
) -> Dict[str, float]:
    from collections import defaultdict
    import numpy as np

    y_map: Dict[str, float] = {}

    # 1) Base-level vertical fan (per column → energy_group_key)
    total_base_jitter = cfg.y_jitter * cfg.energy_group_y_scale
    cols: Dict[int, List[Level]] = defaultdict(list)
    for lvl in levels:
        if lvl.sublevel == 0:
            cols[infer_column(lvl, cfg)].append(lvl)

    for bases in cols.values():
        # bucket by energy_group_key
        by_group: Dict[Hashable, List[Level]] = defaultdict(list)
        for lvl in bases:
            by_group[cfg.energy_group_key(lvl)].append(lvl)

        # fan each bucket over ±total_base_jitter
        for key in sorted(by_group):
            group = by_group[key]
            ordered = sorted(group, key=lambda L: L.energy)
            n = len(ordered)
            offsets = (
                np.linspace(-total_base_jitter, total_base_jitter, n)
                if n > 1 else [0.0]
            )
            for lvl, off in zip(ordered, offsets):
                y_map[lvl.label] = lvl.energy + off

    # 2) Sublevel splitting with uniform vertical spacing
    subs_by_parent: Dict[str, List[Level]] = defaultdict(list)
    for lvl in levels:
        if lvl.sublevel > 0 and lvl.parent:
            subs_by_parent[lvl.parent.label].append(lvl)

    for parent_lbl, subs in subs_by_parent.items():
        parent_y = y_map.get(parent_lbl)
        if parent_y is None:
            continue

        sorted_subs = sorted(
            subs,
            key=lambda L: float((Fraction(L.label.split("m=")[1])))
        )
        n = len(sorted_subs)
        step = cfg.sublevel_uniform_spacing

        if cfg.sublevel_uniform_centered:
            start = -step * (n - 1) / 2
        else:
            start = 0.0

        for i, lvl in enumerate(sorted_subs):
            y_map[lvl.label] = parent_y + start + i * step
    return y_map


def compute_sublevel_y_map(
    levels: List[Level],
    base_y_map: Dict[str, float],
    cfg: LayoutConfig
) -> Dict[str, float]:
    from collections import defaultdict

    # bucket sub-levels by parent label
    subs_by_parent: Dict[str, List[Level]] = defaultdict(list)
    for lvl in levels:
        if lvl.sublevel > 0 and lvl.parent:
            subs_by_parent[lvl.parent.label].append(lvl)

    sub_y: Dict[str, float] = {}
    # total jitter to apply
    total_jitter = cfg.y_jitter * cfg.sublevel_y_scale

    for parent_lbl, subs in subs_by_parent.items():
        parent_y = base_y_map.get(parent_lbl)
        if parent_y is None:
            continue

        # sort by m quantum number (so negative m on bottom)
        subs_sorted = sorted(
            subs,
            key=lambda L: float(Fraction(L.label.split("m=")[1]))
        )
        n = len(subs_sorted)
        # symmetric offsets
        offs = (np.linspace(-total_jitter, total_jitter, n)
                if n > 1 else [0.0])

        # also preserve the actual ΔE shift
        parent_energy = next(
            (l.energy for l in levels if l.label == parent_lbl),
            None
        )

        for lvl, extra in zip(subs_sorted, offs):
            # true energy shift
            delta = lvl.energy - (parent_energy or lvl.energy)
            sub_y[lvl.label] = parent_y + delta + extra

    return sub_y


