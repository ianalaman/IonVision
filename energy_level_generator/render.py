# energy_level_generator/render.py
from __future__ import annotations
import json
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Optional
from pathlib import Path
from .models import Level
from .plotter import plot_energy_levels
from .style import StyleConfig, default_style
from .layout import LayoutConfig, default_layout


def _sanitize(obj: Any) -> Any:
    """Return a JSON-safe version (Levels→label)."""
    if isinstance(obj, Level):
        return obj.label
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_sanitize(v) for v in obj]
    try:
        json.dumps(obj); return obj
    except TypeError:
        return repr(obj)

def _level_to_shallow_dict(lvl: Level) -> dict:
    """Flatten Level for debug printing."""
    return {
        "label": lvl.label,
        "energy": lvl.energy,
        "zeeman": lvl.zeeman,
        "sideband": _sanitize(lvl.sideband),
        "sublevel": lvl.sublevel,
        "parent": lvl.parent.label if isinstance(lvl.parent, Level) else lvl.parent,
        "split_type": lvl.split_type,
        "children": [c.label if isinstance(c, Level) else c for c in (lvl.children or [])],
        "meta": _sanitize(lvl.meta),
    }

def dump_levels(levels: Iterable[Level], sort: bool=True, n:int=10) -> None:
    """Quick peek at first `n` flattened levels (sorted by energy, label)."""
    items = list(levels)
    if sort:
        items.sort(key=lambda l: (getattr(l, "energy", 0.0), getattr(l, "label", "")))
    for row in [_level_to_shallow_dict(x) for x in items[:n]]:
        print(row)
def load_and_split(path: Path, *, b_tesla: float, sideband_gap: float, attach_to_zeeman: bool) -> dict:
    """Return a `data` dict ready for `plot_energy_levels`."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    levels = [Level(**entry) for entry in raw["levels"]]
    data = {
        "ion": raw.get("ion", ""),
        "unit": raw.get("unit", "cm⁻¹"),
        "levels": levels,
        "transitions": raw.get("transitions", []),
        "title": raw.get("title", ""),
    }

    zs = ZeemanSplitter(b_tesla=b_tesla)
    sb = SidebandSplitter(gap=sideband_gap)

    base_levels = list(data["levels"])
    split_levels: List[Level] = []
    for lvl in base_levels:
        split_levels.append(lvl)
        zkids = zs.split(lvl) if b_tesla > 0 else []
        split_levels.extend(zkids)
        if sideband_gap > 0:
            split_levels.extend(sb.split(lvl, zeeman_children=zkids) if attach_to_zeeman else sb.split(lvl))
    data["levels"] = split_levels
    return data


def default_layout() -> LayoutConfig:
    return LayoutConfig(
        column_letters=["S1/2", "P1/2", "P3/2", "D3/2", "D5/2"],
        column_positions=[0, 0, 1, 2, 2],
        spacing=1.0,
        bar_half=0.30,
        x_jitter=0.25,
        y_jitter=100.0,
        energy_group_key=lambda lvl: int(lvl.energy // 10000),
        energy_group_y_scale=30.0,
        sublevel_uniform_spacing=1000.0,
        sublevel_uniform_centered=True,
    )

def default_style() -> StyleConfig:
    s = StyleConfig()
    s.hide_split_types = {"sideband"}  # Hides sideband labels
    s.show_qnum_header = True
    s.qnum_header_pad_factor = 0.30
    s.zeeman_label_value_only = True
    s.qnum_header_x_shift = 0.045
    s.qnum_value_x_shift = 0.00
    s.sublevel_value_fontfamily = "DejaVu Sans Mono"
    # s.hide_split_types = {"sideband"}  # uncomment to hide sideband ticks/labels
    return s

for title, path in SCENES.items():
    # show the explanation markdown first
    display(Markdown(f"### {title}\n\n{EXPLAINS.get(title, '')}"))

    data = load_and_split(
        path,
        b_tesla=b_tesla,
        sideband_gap=sideband_gap,
        attach_to_zeeman=attach_sidebands_to_zeeman,
    )
    data["title"] = data.get("title") or title
    plot_energy_levels(data, default_layout(), default_style(), show_axis=False)