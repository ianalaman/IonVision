"""
layout.py — deterministic x/y layout for energy-level diagrams.

Assigns **x** (horizontal) and **y** (vertical) coordinates to `Level` objects for
plotting. Placement is column-based (S, P, D, F, …) with optional energy
grouping on **y** and structured offsets for sub-levels.

Concepts
--------
- **Columns**: Chosen from spectroscopic term symbols via `infer_column`.
- **Base levels** (`sublevel == 0`): 
  - Horizontal: fanned within the column (bar width `2*cfg.bar_half`).
  - Vertical: fanned inside energy groups (`cfg.energy_group_key`) using
    `cfg.y_jitter * cfg.energy_group_y_scale` to reduce overplotting.
- **Sublevels** (`sublevel > 0`):
  - Horizontal: jittered about the parent (±`cfg.x_jitter`).
  - Vertical: uniformly spaced by `cfg.sublevel_uniform_spacing`, centered if
    `cfg.sublevel_uniform_centered`. Order set by parsed m quantum number.

Assumptions
-----------
- `Level.label` has ≥2 whitespace-separated tokens; the **second** token is the
  term (e.g. `"2P3/2"`). Sublevels must also contain `m=<rational>` somewhere
  (e.g. `"... m=+3/2"`), or provide it in `Level.meta`.
- `cfg.column_letters` must include the exact lookup keys used by
  `infer_column` (e.g. `"S1/2"`, `"P3/2"`, not just `"S"`, `"P"`).
- All **y** values use the same units as `Level.energy`.

"""


import re
from dataclasses import dataclass
from typing import List, Dict
import numpy as np
from energy_level_generator.style import StyleConfig
from energy_level_generator.models import Level
from typing import Callable
from fractions import Fraction
from collections.abc import Hashable
from collections import defaultdict

style = StyleConfig()
# ---------- quantum number parsing helpers (m_j, m_f, fallback m) ----------
_QNUM_RES = {
    "m_j": re.compile(r"\bm_j\s*=\s*([+-]?\d+(?:/\d+)?)"),
    "m_f": re.compile(r"\bm_f\s*=\s*([+-]?\d+(?:/\d+)?)"),
    "m":   re.compile(r"\bm\s*=\s*([+-]?\d+(?:/\d+)?)"),
}

def _qnum_value(level, names=("m_j", "m_f", "m")):
    """Extract quantum number value from level metadata or label.

    Args:
        level (Level): The level object containing metadata and label.
        names (tuple, optional): Ordered names to check in metadata and label.
            Defaults to ("m_j", "m_f", "m").

    Returns:
        tuple[str|None, float|None]: A tuple of (name, value) if found, else (None, None).
    """
    meta = getattr(level, "meta", {}) or {}
    # Prefer structured metadata (set it in your splitters)
    for nm in names:
        if nm in meta and meta[nm] is not None:
            v = meta[nm]
            if isinstance(v, (int, float)): 
                return nm, float(v)
            try:
                return nm, float(Fraction(str(v)))
            except Exception:
                pass
    # Fallback: parse from label (handles "+3/2", "-1/2", etc.)
    label = getattr(level, "label", "") or ""
    for nm in names:
        rx = _QNUM_RES.get(nm)
        if not rx:
            continue
        m = rx.search(label)
        if m:
            try:
                return nm, float(Fraction(m.group(1)))
            except Exception:
                pass
    return None, None

def _qnum_sort_key(level, names=("m_j", "m_f", "m")):
    """Sort key for levels by quantum number.

    Args:
        level (Level): Level object.
        names (tuple, optional): Quantum number names to check. Defaults to ("m_j","m_f","m").

    Returns:
        tuple: (bool, float) where bool indicates if value is missing and float is value or 0.
    """
    _, val = _qnum_value(level, names)
    return (val is None, 0.0 if val is None else val)


@dataclass
class LayoutConfig:
    """Configuration for horizontal and vertical placement of energy levels.

    Attributes:
        column_letters (List[str]): 
            Ordered list of term keys used to assign columns.
            Each key should match the substring **after** the principal 
            quantum number in the term token.
            Example: ["S1/2", "P1/2", "P3/2", "D3/2", "D5/2", ...].

        column_positions (List[int]): 
            Integer column ID for each entry in `column_letters`.
            Must match the length of `column_letters`.
            These are multiplied by `spacing` to determine column center x-coordinates.

        spacing (float): 
            Horizontal distance between neighboring integer columns (x units).

        bar_half (float): 
            Half-width of each energy bar; total bar width is `2 * bar_half`.
            Used when fanning multiple base levels at the same energy group.

        x_jitter (float): 
            Maximum horizontal offset (±) for sublevels around the parent center.

        y_jitter (float): 
            Base vertical jitter scale (same units as `Level.energy`).
            Combined with `energy_group_y_scale` to spread base levels within a group.

        energy_group_key (Callable[[Level], int]): 
            Function mapping a `Level` to a hashable key for vertical energy grouping.
            Default groups by `floor(level.energy / 10)`.

        energy_group_y_scale (float): 
            Multiplier for `y_jitter` when fanning base levels within the same energy group.

        sublevel_uniform_spacing (float): 
            Vertical distance between adjacent sublevels (same units as energy)
            when using uniform spacing in `compute_y_map`.

        sublevel_uniform_centered (bool): 
            If True, sublevels are centered around the parent;
            otherwise they extend in +y direction starting from the parent.

        sideband_vertical_offset (float): 
            Vertical offset for sidebands around their Zeeman parent.
    """
    column_letters: List[str]
    column_positions: List[int]
    spacing: float = 0.5
    bar_half: float = 0.1
    x_jitter: float = 0.2
    y_jitter: float = 20000.0
    energy_group_key: Callable[[Level], int] = lambda lvl: int(lvl.energy // 10)
    energy_group_y_scale: float = 3000000.0
    sublevel_uniform_spacing: float = 1000.0
    sublevel_uniform_centered: bool = True
    sideband_vertical_offset: float = 350.0



def infer_column(level: Level, cfg: LayoutConfig) -> int:
    """Infer integer column index for a level.

    Args:
        level (Level): Level whose column is to be determined.
        cfg (LayoutConfig): Layout configuration.

    Returns:
        int: Column index or 0 if not found.
    """
    term   = level.label.split()[1]   # e.g. "2P3/2"
    letter = term[1:]                  # → "P3/2" (or "P1/2")
    try:
        idx = cfg.column_letters.index(letter)
        return cfg.column_positions[idx]
    except ValueError:
        return 0


def compute_base_x_map(
    levels: List[Level],
    cfg: LayoutConfig
) -> Dict[str, float]:
    """Compute x positions for base levels (sublevel==0).

    Args:
        levels (List[Level]): Level objects.
        cfg (LayoutConfig): Layout configuration.

    Returns:
        Dict[str, float]: Mapping from level label to x-coordinate.
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

    # Grouping function (defaults to floor(energy/10000) if missing)
    group_key = getattr(cfg, "energy_group_key", lambda lvl: int(lvl.energy // 10000))

    for col, bases in cols.items():
        col_center = col * cfg.spacing
        energy_groups: Dict[int, List[Level]] = defaultdict(list)
        for lvl in bases:
            key = group_key(lvl)
            energy_groups[key].append(lvl)

        # Process groups in energy order for reproducibility
        for energy in sorted(energy_groups):
            group = energy_groups[energy]
            n = len(group)

            if n == 1:
                # Single base level → centered on the column
                base_map[group[0].label] = col_center
            else:
                # Multiple base levels → fan to the right from the center
                offsets = [i * bar_width for i in range(n)]
                # Sort by label for deterministic ordering
                for lvl, off in zip(sorted(group, key=lambda l: l.label), offsets):
                    base_map[lvl.label] = col_center + off

    return base_map


def compute_sublevel_x_map(
    levels: List[Level],
    base_map: Dict[str, float],
    cfg: LayoutConfig
) -> Dict[str, float]:
    """Compute x positions for sublevels (sublevel>0).

    Args:
        levels (List[Level]): All levels.
        base_map (Dict[str,float]): Mapping of base level labels to x.
        cfg (LayoutConfig): Layout configuration.

    Returns:
        Dict[str, float]: Mapping from sublevel label to x-coordinate.
    """
    from collections import defaultdict

    # parent_label → [sublevels...]
    subs_by_parent: Dict[str, List[Level]] = defaultdict(list)
    for lvl in levels:
        if lvl.sublevel > 0 and lvl.parent:
            subs_by_parent[lvl.parent.label].append(lvl)

    sub_map: Dict[str, float] = {}
    for parent_lbl, subs in subs_by_parent.items():
      base_x = base_map.get(parent_lbl, 0.0)

      sidebands = [s for s in subs if getattr(s, "split_type", None) == "sideband"]
      others    = [s for s in subs if getattr(s, "split_type", None) != "sideband"]

      if others:
          others_sorted = sorted(others, key=_qnum_sort_key)
          offsets = np.linspace(-cfg.x_jitter, cfg.x_jitter, len(others_sorted))
          for lvl, off in zip(others_sorted, offsets):
              sub_map[lvl.label] = base_x + off

      # pin sidebands to immediate parent x
      parent_x = sub_map.get(parent_lbl, base_x)
      for sb in sidebands:
          sub_map[sb.label] = parent_x


    return sub_map


def compute_x_map(
    levels: List[Level],
    cfg:   LayoutConfig
) -> Dict[str, float]:
    """Compute x positions for all levels (base and sublevels).

    Args:
        levels (List[Level]): All levels.
        cfg (LayoutConfig): Layout configuration.

    Returns:
        Dict[str, float]: Mapping from level label to x-coordinate.
    """
    base_map = compute_base_x_map(levels, cfg)
    sub_map = compute_sublevel_x_map(levels, base_map, cfg)
    return {**base_map, **sub_map}


def compute_y_map(
    levels: List[Level],
    cfg: LayoutConfig
) -> Dict[str, float]:
    """Compute y positions for all levels with vertical fanning and uniform sublevel spacing.

    Args:
        levels (List[Level]): All levels.
        cfg (LayoutConfig): Layout configuration.

    Returns:
        Dict[str, float]: Mapping from level label to y-coordinate.
    """
    from collections import defaultdict

    y_map: Dict[str, float] = {}

    # ---------- Stage 1: base-level vertical fanning by energy group ----------
    total_base_jitter = cfg.y_jitter * cfg.energy_group_y_scale

    # Column → [base levels]
    cols: Dict[int, List[Level]] = defaultdict(list)
    for lvl in levels:
        if lvl.sublevel == 0:
            cols[infer_column(lvl, cfg)].append(lvl)

    for bases in cols.values():
        # Group base levels inside the column by energy group key
        by_group: Dict[Hashable, List[Level]] = defaultdict(list)  # type: ignore[name-defined]
        for lvl in bases:
            by_group[cfg.energy_group_key(lvl)].append(lvl)

        # Fan each group symmetrically around its nominal energy
        for key in sorted(by_group):
            group = by_group[key]
            ordered = sorted(group, key=lambda L: L.energy)
            n = len(ordered)

            # Symmetric offsets across the jitter span (or 0 if singleton)
            offsets = (
                np.linspace(-total_base_jitter, total_base_jitter, n)
                if n > 1 else [0.0]
            )

            # Apply offsets relative to the *true* energy of each level
            for lvl, off in zip(ordered, offsets):
                y_map[lvl.label] = lvl.energy + off

    # ---------- Stage 2: uniform sublevel spacing around parent ----------
    subs_by_parent: Dict[str, List[Level]] = defaultdict(list)
    for lvl in levels:
        if lvl.sublevel > 0 and lvl.parent:
            subs_by_parent[lvl.parent.label].append(lvl)

    for parent_lbl, subs in subs_by_parent.items():
      parent_y = y_map.get(parent_lbl)
      if parent_y is None:
          continue

      # partition: zeeman/hyperfine-like vs sidebands
      sidebands = [s for s in subs if getattr(s, "split_type", None) == "sideband"]
      others    = [s for s in subs if getattr(s, "split_type", None) != "sideband"]

      # 1) place non-sideband sublevels with uniform spacing (by m)
      if others:
          # NEW: sort by 'F' if present, else by _qnum_sort_key
          def _sort_key(l):
              F = (l.meta or {}).get("F")
              return (0, float(F)) if F is not None else (1, ) + _qnum_sort_key(l)
          sorted_others = sorted(others, key=_sort_key)
          n = len(sorted_others)
          step = cfg.sublevel_uniform_spacing
          start = -step * (n - 1) / 2 if cfg.sublevel_uniform_centered else 0.0
          for i, lvl in enumerate(sorted_others):
              y_map[lvl.label] = parent_y + start + i * step

      # 2) place sidebands tightly around the parent (blue above, red below)
      if sidebands:
          off = getattr(cfg, "sideband_vertical_offset", 100.0)
          for s in sidebands:
              name = (s.label or "").lower()
              if "blue sideband" in name:
                  y_map[s.label] = parent_y + off
              elif "red sideband" in name:
                  y_map[s.label] = parent_y - off
              else:
                  # fallback: keep them close but below
                  y_map[s.label] = parent_y - off


    return y_map


def compute_sublevel_y_map(
    levels: List[Level],
    base_y_map: Dict[str, float],
    cfg: LayoutConfig
) -> Dict[str, float]:
    """Compute y positions for sublevels preserving true energy splitting.

    Args:
        levels (List[Level]): All levels.
        base_y_map (Dict[str,float]): Mapping of base level label to y.
        cfg (LayoutConfig): Layout configuration with sublevel_y_scale defined.

    Returns:
        Dict[str, float]: Mapping from sublevel label to y-coordinate.
    """
    from collections import defaultdict

    # Group sub-levels by parent label
    subs_by_parent: Dict[str, List[Level]] = defaultdict(list)
    for lvl in levels:
        if lvl.sublevel > 0 and lvl.parent:
            subs_by_parent[lvl.parent.label].append(lvl)

    sub_y: Dict[str, float] = {}
    # Total symmetric jitter for sublevels (requires cfg.sublevel_y_scale)
    total_jitter = cfg.y_jitter * cfg.sublevel_y_scale  # type: ignore[attr-defined]

    for parent_lbl, subs in subs_by_parent.items():
        parent_y = base_y_map.get(parent_lbl)
        if parent_y is None:
            continue

       # Sort by available m_* (m_j/m_f/m). Negative values first naturally.
        subs_sorted = sorted(subs, key=_qnum_sort_key)

        n = len(subs_sorted)

        # Symmetric jitter offsets (or 0 for single sublevel)
        offs = (np.linspace(-total_jitter, total_jitter, n)
                if n > 1 else [0.0])

        # Retrieve the parent's *true* energy once for ΔE
        parent_energy = next(
            (l.energy for l in levels if l.label == parent_lbl),
            None
        )

        for lvl, extra in zip(subs_sorted, offs):
            # True energy shift relative to parent (ΔE)
            delta = lvl.energy - (parent_energy or lvl.energy)
            sub_y[lvl.label] = parent_y + delta + extra

    return sub_y
