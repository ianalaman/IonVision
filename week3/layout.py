# layout.py

from dataclasses import dataclass
from typing import List, Dict
import numpy as np

from .models import Level

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

    Within each column group:
      1. Sort bases by energy ascending.
      2. Place them left→right, each bar of width 2*bar_half,
         starting with its left edge at (col*spacing).
      3. Bar centers therefore at:
           x = col*spacing + bar_half + i*(2*bar_half)
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

    for col, bases in cols.items():
        start_x = col * cfg.spacing
        # sort by energy so bars stack sensibly left→right
        ordered = sorted(bases, key=lambda L: L.energy)
        for i, lvl in enumerate(ordered):
            # left edge = start_x + i*bar_width
            # center = left_edge + bar_half
            center = start_x + cfg.bar_half + i * bar_width
            base_map[lvl.label] = center

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
        subs_sorted = sorted(subs, key=lambda L: float(L.label.split("m=")[1]))

        # compute a “safe” jitter so that the outer ticks
        # sit exactly at the bar’s edges (±bar_half)
        tick_half   = cfg.bar_half * style.tick_size
        safe_jitter = cfg.bar_half - tick_half
        offsets     = np.linspace(-safe_jitter, safe_jitter, n)

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
    """
    Compute vertical positions for each level.

    - Base levels that share a parent (by label) are jittered within ±y_jitter.
    - Sublevels ride on their parent's bar, shifted by ΔE = (E_sub − E_parent).

    Returns a dict mapping level.label → y‐coordinate.
    """
    from collections import defaultdict

    # Group by parent_label (string), not by Level object
    groups: Dict[str, List[Level]] = defaultdict(list)
    for lvl in levels:
        parent_label = lvl.parent.label if lvl.parent else lvl.label
        groups[parent_label].append(lvl)

    y_map: Dict[str, float] = {}
    for parent_label, siblings in groups.items():
        # find the parent energy for ΔE calculations
        parent_energy = next(
            (l.energy for l in siblings if l.label == parent_label),
            None
        )

        # 1) stack base‐levels (sublevel==0)
        bases = [s for s in siblings if s.sublevel == 0]
        if bases:
            ordered = sorted(bases, key=lambda b: b.energy)
            n = len(ordered)
            offs = (np.linspace(-cfg.y_jitter, cfg.y_jitter, n)
                    if n > 1 else [0])
            for lvl, off in zip(ordered, offs):
                y_map[lvl.label] = lvl.energy + off

        # 2) place sub‐levels relative to the parent’s y
        for s in siblings:
            if s.sublevel > 0 and parent_energy is not None:
                delta = s.energy - parent_energy
                y_map[s.label] = y_map[parent_label] + delta

    return y_map

