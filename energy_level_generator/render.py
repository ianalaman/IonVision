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

PKG_DIR = Path(__file__).resolve().parent

# --- helpers for remapping transitions ---
def _simplify_label(s: str) -> str:
    """Normalize a label for matching: collapse spaces, drop leading token."""
    s = re.sub(r"\s+", " ", s or "").strip()
    return re.sub(r"^[A-Za-z0-9]+?\s+", "", s)

def _build_aliases(levels: list[Level]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for L in levels:
        if not L.label:
            continue
        exact = L.label
        norm = re.sub(r"\s+", " ", exact).strip()
        simple = _simplify_label(exact)
        aliases[exact] = exact
        aliases[norm] = exact
        aliases[simple] = exact
    return aliases

def _remap_transitions(transitions: list[dict], aliases: dict[str, str]) -> list[dict]:
    out = []
    for t in transitions:
        t = dict(t)
        for k in ("from", "to"):
            lbl = t.get(k, "")
            for cand in (lbl, re.sub(r"\s+", " ", lbl).strip(), _simplify_label(lbl)):
                if cand in aliases:
                    t[k] = aliases[cand]
                    break
        out.append(t)
    return out

def _normalize_levels(levels: list[dict]) -> list[Level]:
    """Convert JSON dicts to Level objects; fix parent to SimpleNamespace if needed."""
    out: list[Level] = []
    for d in levels:
        d = dict(d)
        p = d.get("parent")
        if isinstance(p, dict):
            d["parent"] = SimpleNamespace(label=p.get("label"))
        elif isinstance(p, str):
            d["parent"] = SimpleNamespace(label=p)
        elif p is None or isinstance(p, SimpleNamespace):
            pass
        else:
            d["parent"] = None
        out.append(Level(**d))
    return out

# --- main function ---
def plot_from_json(
    levels_json_path: str | Path,
    style_json_path: Optional[str | Path] = None,
    save_path: Optional[str | Path] = None,
    show_axis: bool = True,
    figsize: tuple[int, int] = (8, 5)
):
    # Load levels JSON
    with open(levels_json_path, "r") as f:
        levels_data = json.load(f)

     # --- Load the raw levels JSON ---
    raw_path = Path(levels_json_path)
    raw = json.loads(raw_path.read_text(encoding="utf-8"))

    levels = _normalize_levels(levels_data.get("levels", []))
    aliases = _build_aliases(levels)
    transitions = _remap_transitions(levels_data.get("transitions", []), aliases)
    raw = json.loads(raw_path.read_text(encoding="utf-8"))

    data = {
        "levels": levels,
        "transitions": raw.get("transitions", []),
        "ion": levels_data.get("ion", ""),
        "unit": levels_data.get("unit", "cm$^{-1}$"),
        "title": levels_data.get("title", "")
    }

    # Load style/layout JSON if provided
    style_dict = {}
    if style_json_path:
        with open(style_json_path, "r") as f:
            style_dict = json.load(f)

    # Defaults + overrides
    layout_cfg = LayoutConfig(**{**default_layout().__dict__, **style_dict.get("layout", {})})
    style_cfg = StyleConfig(**{**default_style().__dict__, **style_dict.get("style", {})})

    # Plot
    fig = plot_energy_levels(
        data=data,
        layout_cfg=layout_cfg,
        style_cfg=style_cfg,
        figsize=figsize,
        show_axis=show_axis,
        return_fig=True
    )

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig
