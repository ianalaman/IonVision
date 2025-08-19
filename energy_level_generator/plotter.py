# plotter.py
"""
Energy level plotting utilities:
- draw_levels: plot level bars, sublevel ticks, and quantum-number labels
- draw_transitions: plot transitions with optional direction arrows
- plot_energy_levels: high-level entry point
"""

from __future__ import annotations

# --- stdlib ---
import math
import re
from collections import defaultdict
from typing import Dict, List

# --- third-party ---
import matplotlib.pyplot as plt  # pylint: disable=import-error

# --- first-party ---
from energy_level_generator.models import Level
from energy_level_generator.layout import (
    compute_x_map,
    compute_y_map,
    LayoutConfig,
    infer_column,
)
from energy_level_generator.style import StyleConfig
from energy_level_generator.format import format_term_symbol, format_ion_label


def _format_sublevel_text(lvl: Level) -> str:
    """
    Produce a short sublevel label:
      - 'red sideband' / 'blue sideband' for sidebands
      - else prefer lvl.meta['m_f'|'m_j'|'m']
      - else parse "m_f=..", "m_j=..", or "m=.." from lvl.label
      - else ''
    """
    if getattr(lvl, "split_type", None) == "sideband":
        parts = (lvl.label or "").split(",", 1)
        return parts[1].strip() if len(parts) > 1 else "sideband"

    meta = getattr(lvl, "meta", {}) or {}
    for nm in ("m_f", "m_j", "m"):
        if nm in meta and meta[nm] is not None:
            return f"{nm}={meta[nm]}"

    mobj = re.search(
        r"\b(m_f|m_j|m)\s*=\s*([+-]?\d+(?:/\d+)?)", getattr(lvl, "label", "") or ""
    )
    if mobj:
        return f"{mobj.group(1)}={mobj.group(2)}"
    return ""


def draw_levels(  # pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements
    ax: plt.Axes,
    levels: List[Level],
    x_map: Dict[str, float],
    y_map: Dict[str, float],
    cfg: LayoutConfig,
    style: StyleConfig,
) -> None:
    """Draw base level bars, sublevel ticks, and term-symbol + m labels."""
    bar_half = cfg.bar_half

    # parents that have sublevels
    parent_labels = {
        lvl.parent.label for lvl in levels if lvl.sublevel > 0 and lvl.parent
    }

    # base bars and per-level text
    for lvl in levels:
        x = x_map[lvl.label]
        y = y_map[lvl.label]

        if lvl.sublevel == 0:
            if lvl.label in parent_labels:
                color, ls, lw = (
                    style.parent_bar_color,
                    style.parent_bar_linestyle,
                    style.parent_bar_line_width,
                )
            else:
                color, ls, lw = (
                    style.base_bar_color,
                    style.base_bar_linestyle,
                    style.line_width,
                )
            ax.hlines(y, x - bar_half, x + bar_half, color=color, lw=lw, linestyle=ls)

            # term symbol placement: left for col 0, else right
            col = infer_column(lvl, cfg)
            if col == 0:
                x_txt = x - bar_half - style.level_label_x_offset
                ha_txt = "right"
            else:
                x_txt = x + bar_half + style.level_label_x_offset
                ha_txt = "left"

            ax.text(
                x_txt,
                y + style.level_label_y_offset,
                format_term_symbol(lvl),
                va="center",
                ha=ha_txt,
                fontfamily="Cambria",
                fontsize=style.level_label_fontsize,
            )

        else:
            # sublevel tick styling
            if getattr(lvl, "split_type", None) == "sideband":
                name = (lvl.label or "").lower()
                tick_color = (
                    getattr(style, "sideband_blue_color", "blue")
                    if "blue sideband" in name
                    else (
                        getattr(style, "sideband_red_color", "red")
                        if "red sideband" in name
                        else getattr(style, "sublevel_tick_color", "k")
                    )
                )
                ls = getattr(style, "sublevel_tick_linestyle", "-")
                lw = getattr(style, "sublevel_tick_line_width", 1.5)
                length = getattr(
                    style,
                    "sideband_tick_length",
                    getattr(style, "sublevel_tick_length", 1.0),
                )
            else:
                c_override = (lvl.meta or {}).get("color")
                if lvl.parent and lvl.parent.label in parent_labels:
                    tick_color = c_override or style.parent_sublevel_tick_color
                    ls = style.parent_sublevel_tick_linestyle
                    lw = style.parent_sublevel_tick_line_width
                    length = style.parent_sublevel_tick_length
                else:
                    tick_color = c_override or style.sublevel_tick_color
                    ls = style.sublevel_tick_linestyle
                    lw = style.sublevel_tick_line_width
                    length = style.sublevel_tick_length

            tick_half = bar_half * length
            ax.hlines(
                y, x - tick_half, x + tick_half, color=tick_color, lw=lw, linestyle=ls
            )

    # group sublevels by parent
    subs_by_parent: Dict[str, List[Level]] = defaultdict(list)
    for lvl in levels:
        if lvl.sublevel > 0 and lvl.parent:
            subs_by_parent[lvl.parent.label].append(lvl)

    hide_types = set(getattr(style, "hide_split_types", ()))
    show_header = getattr(style, "show_qnum_header", True)
    pad_factor = float(getattr(style, "qnum_header_pad_factor", 0.35))
    value_only = bool(getattr(style, "zeeman_label_value_only", True))

    def _outward(xval: float, ha: str, delta: float) -> float:
        """Shift x further away from the bar depending on alignment."""
        return xval - delta if ha == "right" else xval + delta

    for parent_lbl, subs in subs_by_parent.items():
        x0 = x_map[parent_lbl]
        parent = next((lvl for lvl in levels if lvl.label == parent_lbl), None)
        col = infer_column(parent, cfg) if parent else 1

        if col == 0:
            x_txt = x0 - bar_half - style.sublevel_label_x_offset
            ha_txt = "right"
        else:
            x_txt = x0 + bar_half + style.sublevel_label_x_offset
            ha_txt = "left"

        x_txt_hdr = _outward(
            x_txt, ha_txt, float(getattr(style, "qnum_header_x_shift", 0.0))
        )

        # non-sideband entries for header inference
        others = [s for s in subs if getattr(s, "split_type", None) != "sideband"]

        # optional header like "m_j"
        if show_header and others:
            header_name = None
            for s in others:
                t = _format_sublevel_text(s) or ""
                mobj = re.match(r"^\s*(m_j|m_f|m)\s*=", t)
                if mobj:
                    header_name = mobj.group(1)
                    break
            if header_name:
                y_top = max(y_map[s.label] for s in others)
                y_hdr = y_top + pad_factor * cfg.sublevel_uniform_spacing
                ax.text(
                    x_txt_hdr,
                    y_hdr,
                    header_name,
                    fontfamily="Cambria",
                    fontsize=style.sublevel_label_fontsize,
                    va="bottom",
                    ha=ha_txt,
                )

        # value positions
        x_txt_val = _outward(
            x_txt, ha_txt, float(getattr(style, "qnum_value_x_shift", 0.0))
        )

        # draw values
        for s in subs:
            if getattr(s, "split_type", None) in hide_types:
                continue
            y_txt = y_map[s.label] + style.sublevel_label_y_offset
            txt = _format_sublevel_text(s)
            if not txt:
                continue
            if (
                value_only
                and getattr(s, "split_type", None) != "sideband"
                and "=" in txt
            ):
                txt = txt.split("=", 1)[1].strip()
            ax.text(
                x_txt_val,
                y_txt,
                txt,
                fontfamily="Cambria",
                va="center",
                ha=ha_txt,
                fontsize=style.sublevel_label_fontsize,
            )


def draw_transitions(  # pylint: disable=too-many-arguments,too-many-locals
    ax: plt.Axes,
    transitions: List[dict],
    x_map: Dict[str, float],
    y_map: Dict[str, float],
    style: StyleConfig,
) -> None:
    """
    Draw transitions:
      • reversible=True  → plain line
      • reversible=False → line + single arrow marker at midpoint
    """
    # group identical pairs for offsetting
    pairs = defaultdict(list)
    for i, tdef in enumerate(transitions):
        pairs[(tdef["from"], tdef["to"])].append(i)

    # centered slot indices
    slots: Dict[int, tuple[float, int]] = {}
    for idxs in pairs.values():
        n = len(idxs)
        for rank, i in enumerate(idxs):
            slots[i] = (rank - (n - 1) / 2, n)

    for i, tdef in enumerate(transitions):
        x1, y1 = x_map[tdef["from"]], y_map[tdef["from"]]
        x2, y2 = x_map[tdef["to"]], y_map[tdef["to"]]

        dx, dy = x2 - x1, y2 - y1
        seg_len = math.hypot(dx, dy)
        if seg_len == 0:
            continue
        ux, uy = dx / seg_len, dy / seg_len
        nx, ny = -uy, ux

        slot_index, _ = slots[i]
        delta = style.transition_offset
        ox, oy = nx * (slot_index * delta), ny * (slot_index * delta)
        x1, y1, x2, y2 = x1 + ox, y1 + oy, x2 + ox, y2 + oy

        ls = "-" if tdef.get("style", "solid") == "solid" else ":"
        color = tdef.get("color", "k")
        label = tdef.get("label", "")
        reversible = tdef.get("reversible", True)

        # base line
        ax.plot(
            [x1, x2],
            [y1, y2],
            linestyle=ls,
            color=color,
            lw=style.transition_line_width,
            solid_capstyle="butt",
            label=label,
        )

        if not reversible:
            # arrow at midpoint via annotate()
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            arrow_len = getattr(style, "transition_arrow_length", delta * 2) / 2
            tail = (mx - ux * arrow_len, my - uy * arrow_len)
            tip = (mx + ux * arrow_len, my + uy * arrow_len)
            ax.annotate(
                "",
                xy=tip,
                xytext=tail,
                arrowprops={
                    "arrowstyle": style.transition_arrowstyle,
                    "mutation_scale": style.transition_mutation_scale,
                    "color": color,
                    "linewidth": style.transition_arrow_line_width,
                },
            )

        if tdef.get("show_label", False):
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            px, py = -uy, ux
            ax.text(
                mx + px * style.transition_label_shift,
                my + py * style.transition_label_shift,
                label,
                va="center",
                ha="center",
                fontsize=style.transition_label_fontsize,
                fontfamily="Cambria",
                color=color,
            )


def plot_energy_levels(
    data: dict,
    layout_cfg: LayoutConfig,
    style_cfg: StyleConfig,
    figsize: tuple[int, int] = (8, 5),
    show_axis: bool = True,
    title_pad: int = 20,
    ylabel_pad: int = 15,
    left_margin: float = 0.2,
) -> None:
    """High-level: compute layout, draw levels/transitions, style axes."""
    levels = data["levels"]
    transitions = data.get("transitions", [])

    y_map = compute_y_map(levels, layout_cfg)
    x_map = compute_x_map(levels, layout_cfg)

    fig, ax = plt.subplots(figsize=figsize)  # type: ignore[call-arg]

    draw_levels(ax, levels, x_map, y_map, layout_cfg, style_cfg)
    draw_transitions(ax, transitions, x_map, y_map, style_cfg)

    ax.legend(
        loc=style_cfg.legend_loc, fontsize=style_cfg.legend_fontsize, frameon=False
    )

    ion_label = format_ion_label(data.get("ion", ""))
    title_text = data.get("title", "")
    ax.set_title(f"{ion_label} {title_text}", pad=title_pad, fontsize=18)
    ax.set_ylabel(f"Energy ({data.get('unit', 'cm$^{-1}$')})", labelpad=ylabel_pad)
    ax.set_xticks([])

    if show_axis:
        for side in ["top", "right", "bottom"]:
            ax.spines[side].set_visible(False)
        ax.spines["left"].set_visible(True)
        ax.yaxis.set_visible(True)
    else:
        ax.axis("off")

    spacing = layout_cfg.spacing
    yvals = list(y_map.values())
    xvals = list(x_map.values())
    ax.set_ylim(min(yvals) - 100 * spacing, max(yvals) + spacing)
    ax.set_xlim(min(xvals) - spacing / 2, max(xvals) + spacing / 2)

    fig.subplots_adjust(left=left_margin, bottom=0.15)
    fig.tight_layout()
    plt.show()
