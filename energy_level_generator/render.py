# energy_level_generator/render.py
from __future__ import annotations
import json
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Optional
from pathlib import Path

from matplotlib.pyplot import title
from .splitters import ZeemanSplitter, SidebandSplitter
from .models import Level
from .plotter import plot_energy_levels
from .style import StyleConfig, default_style
from .layout import LayoutConfig, default_layout

# ---- Helpers to rebuild non-JSON types --------------------------------------
def _build_energy_group_key(spec: Optional[dict]) -> Callable:
    """
    Recreate a callable from a small JSON spec.
    Supported forms:
      {"kind": "floor_div", "divisor": 10000}
    """
    if not isinstance(spec, dict):
        # default: floor by 10 (matches your class default comment),
        # but you'll likely override via your JSON.
        return lambda lvl: int(lvl.energy // 10)

    kind = spec.get("kind", "floor_div")
    if kind == "floor_div":
        divisor = spec.get("divisor", 10000)
        if not isinstance(divisor, (int, float)) or divisor == 0:
            raise ValueError("energy_group_key.floor_div requires a non-zero numeric 'divisor'.")
        return (lambda div: (lambda lvl: int(lvl.energy // div)))(divisor)

    raise ValueError(f"Unsupported energy_group_key.kind: {kind!r}")


def _normalize_cmap_sublevels(obj) -> Optional[Mapping[int, str]]:
    if obj is None:
        return None
    if not isinstance(obj, dict):
        raise TypeError("cmap_sublevels must be a mapping of int->str (as JSON object).")
    out = {}
    for k, v in obj.items():
        try:
            ik = int(k)
        except Exception as e:
            raise TypeError(f"cmap_sublevels keys must be integers (got {k!r}).") from e
        if not isinstance(v, str):
            raise TypeError(f"cmap_sublevels[{ik}] must be a color string.")
        out[ik] = v
    return out


def _to_set(seq) -> Set[str]:
    if seq is None:
        return set()
    if isinstance(seq, set):
        return seq
    if not isinstance(seq, (list, tuple)):
        raise TypeError("hide_split_types must be a list of strings.")
    return set(map(str, seq))


# ---- Main loader ------------------------------------------------------------
def json_breaker(src: Union[str, Path, dict]) -> Tuple[LayoutConfig, StyleConfig]:
    """
    Load JSON (path, str path, or dict), split into Layout and Style configs,
    rebuild non-JSON types, and return (layout_cfg, style_cfg).
    """
    if isinstance(src, (str, Path)):
        with open(src, "r", encoding="utf-8") as f:
            config = json.load(f)
    elif isinstance(src, dict):
        config = src
    else:
        raise TypeError("src must be a dict or a path-like string/Path to a JSON file.")

    layout_in = dict(config.get("layout", {}))
    style_in = dict(config.get("style", {}))

    # ---- Layout
    if "column_letters" not in layout_in or "column_positions" not in layout_in:
        raise ValueError("layout.column_letters and layout.column_positions are required.")

    # Build energy_group_key callable then remove raw spec before dataclass init
    egk_spec = layout_in.pop("energy_group_key", None)
    energy_group_key = _build_energy_group_key(egk_spec)

    layout_cfg = LayoutConfig(
        column_letters=layout_in.pop("column_letters"),
        column_positions=layout_in.pop("column_positions"),
        energy_group_key=energy_group_key,
        **layout_in,  # remaining optional fields
    )

    # ---- Style
    # Convert JSON forms to Python forms
    if "hide_split_types" in style_in:
        style_in["hide_split_types"] = _to_set(style_in["hide_split_types"])
    if "cmap_sublevels" in style_in:
        style_in["cmap_sublevels"] = _normalize_cmap_sublevels(style_in["cmap_sublevels"])

    style_cfg = StyleConfig(**style_in)

    return layout_cfg, style_cfg




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

def load_and_split(
        path: Path,
        *,
        b_tesla: float = 0.01,
        sideband_gap: float = 10.0,
        attach_sidebands_to_zeeman: bool = True
    ) -> dict:
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
            split_levels.extend(sb.split(lvl, zeeman_children=zkids) if attach_sidebands_to_zeeman else sb.split(lvl))
    data["levels"] = split_levels
    return data

def generate_energy_levels(energy_json_path, style_json_path):

    data = load_and_split(energy_json_path)
    data["title"] = data.get("title") or title

    layout_cfg, style_cfg = json_breaker(style_json_path)

    plot_energy_levels(data, layout_cfg, style_cfg, show_axis=False)