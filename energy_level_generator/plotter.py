# plotter.py
"""
Energy level plotting utilities.

Functions:
 draw_levels: Draws level bars, sublevel ticks, and quantum number labels.
 draw_transitions: Draws transitions with optional arrows and labels.
 plot_energy_levels: High-level wrapper to plot levels and transitions with styling.
"""

from __future__ import annotations
import math
import re
from collections import defaultdict
from typing import Dict, List
import matplotlib.pyplot as plt  # type: ignore

from energy_level_generator.models import Level
from energy_level_generator.layout import compute_x_map, compute_y_map, LayoutConfig, infer_column
from energy_level_generator.style import StyleConfig
from energy_level_generator.format import format_term_symbol, format_ion_label


def _format_sublevel_text(lvl: Level) -> str:
    """Return a short text label for a sublevel with proper subscripts."""
    if getattr(lvl, "split_type", None) == "sideband":
        parts = (lvl.label or "").split(",", 1)
        return parts[1].strip() if len(parts) > 1 else "sideband"

    meta = getattr(lvl, "meta", {}) or {}
    for nm in ("m_f", "m_j", "m"):
        if nm in meta and meta[nm] is not None:
            if nm in ("m_j", "m_f"):
                return f"$m_{{{nm[-1]}}}={meta[nm]}$"  # LaTeX-style subscript
            return f"${nm}={meta[nm]}$"

    mobj = re.search(r"\b(m_f|m_j|m)\s*=\s*([+-]?\d+(?:/\d+)?)", getattr(lvl, "label", "") or "")
    if mobj:
        nm, val = mobj.group(1), mobj.group(2)
        if nm in ("m_j", "m_f"):
            return f"$m_{{{nm[-1]}}}={val}$"
        return f"${nm}={val}$"
    return ""

def draw_levels(
    ax: plt.Axes,
    levels: List[Level],
    x_map: Dict[str, float],
    y_map: Dict[str, float],
    cfg: LayoutConfig,
    style: StyleConfig,
) -> None:
    """Draw energy levels and their labels on an axis.

    Draws:
    - Base level horizontal bars with term symbols.
    - Sublevel ticks and optional m_j/m_f/m labels.
    """
    bar_half = cfg.bar_half
    parent_labels = {lvl.parent.label for lvl in levels if lvl.sublevel > 0 and lvl.parent}

    # --- base bars, term symbols, and sublevel ticks ---
    for lvl in levels:
        x = x_map[lvl.label]
        y = y_map[lvl.label]

        if lvl.sublevel == 0:
            if lvl.label in parent_labels:
                color, ls, lw = style.parent_bar_color, style.parent_bar_linestyle, style.parent_bar_line_width
            else:
                color, ls, lw = style.base_bar_color, style.base_bar_linestyle, style.line_width
            ax.hlines(y, x - bar_half, x + bar_half, color=color, lw=lw, linestyle=ls)

            col = infer_column(lvl, cfg)
            if col == 0:
                x_txt, ha_txt = x - bar_half - style.level_label_x_offset, "right"
            else:
                x_txt, ha_txt = x + bar_half + style.level_label_x_offset, "left"
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
            if getattr(lvl, "split_type", None) == "sideband":
                name = (lvl.label or "").lower()
                tick_color = (
                    getattr(style, "sideband_blue_color", "blue")
                    if "blue sideband" in name
                    else getattr(style, "sideband_red_color", "red")
                    if "red sideband" in name
                    else getattr(style, "sublevel_tick_color", "k")
                )
                ls = getattr(style, "sublevel_tick_linestyle", "-")
                lw = getattr(style, "sublevel_tick_line_width", 1.5)
                length = getattr(style, "sideband_tick_length", getattr(style, "sublevel_tick_length", 1.0))
            else:
                c_override = (lvl.meta or {}).get("color")
                if lvl.parent and lvl.parent.label in parent_labels:
                    tick_color, ls, lw, length = (
                        c_override or style.parent_sublevel_tick_color,
                        style.parent_sublevel_tick_linestyle,
                        style.parent_sublevel_tick_line_width,
                        style.parent_sublevel_tick_length,
                    )
                else:
                    tick_color, ls, lw, length = (
                        c_override or style.sublevel_tick_color,
                        style.sublevel_tick_linestyle,
                        style.sublevel_tick_line_width,
                        style.sublevel_tick_length,
                    )
            tick_half = bar_half * length
            ax.hlines(y, x - tick_half, x + tick_half, color=tick_color, lw=lw, linestyle=ls)

    # --- prep for labels ---
    subs_by_parent: Dict[str, List[Level]] = defaultdict(list)
    for lvl in levels:
        if lvl.sublevel > 0 and lvl.parent:
            subs_by_parent[lvl.parent.label].append(lvl)

    hide_types = set(getattr(style, "hide_split_types", ()))
    show_header = getattr(style, "show_qnum_header", True)
    pad_factor = float(getattr(style, "qnum_header_pad_factor", 0.35))
    value_only = bool(getattr(style, "zeeman_label_value_only", True))

    def _outward(xval: float, ha: str, delta: float) -> float:
        return xval - delta if ha == "right" else xval + delta

    # --- per parent: header + values ---
    for parent_lbl, subs in subs_by_parent.items():
        x0 = x_map[parent_lbl]
        parent = next((lvl for lvl in levels if lvl.label == parent_lbl), None)
        col = infer_column(parent, cfg) if parent else 1

        if col == 0:
            x_txt, ha_txt = x0 - bar_half - style.sublevel_label_x_offset, "right"
        else:
            x_txt, ha_txt = x0 + bar_half + style.sublevel_label_x_offset, "left"

        # numeric column x-position
        x_txt_val = _outward(
            x_txt, 
            ha_txt, 
            float(getattr(style, "qnum_value_x_shift", 0.0))  # shift for numbers
        )

        # header x-position (separate configurable shift)
        x_txt_hdr = _outward(
            x_txt, 
            ha_txt, 
            float(getattr(style, "qnum_header_x_shift", 0.0))  # shift for header
        )


        # header (m_j, m_f, m) — flush-aligned with numbers
        others = [s for s in subs if getattr(s, "split_type", None) != "sideband"]
        if show_header and others:
            header_name = None
            for s in others:
                meta = getattr(s, "meta", {}) or {}
                for nm in ("m_j", "m_f", "m"):
                    if nm in meta and meta[nm] is not None:
                        header_name = nm
                        break
                if header_name:
                    break
                raw = getattr(s, "label", "") or ""
                mobj = re.search(r"\b(m_j|m_f|m)\s*=", raw)
                if mobj:
                    header_name = mobj.group(1)
                    break
                t = _format_sublevel_text(s) or ""
                mobj = re.search(r"m_\{([jf])\}", t)
                if mobj:
                    header_name = f"m_{mobj.group(1)}"
                    break
                if re.search(r"\bm\b", t):
                    header_name = "m"
                    break

            if header_name:
                y_top = max(y_map[s.label] for s in others)
                y_hdr = y_top + pad_factor * cfg.sublevel_uniform_spacing
                header_display = f"$m_{{{header_name[-1]}}}$" if header_name in ("m_j", "m_f") else "$m$"
                ax.text(
                    x_txt_hdr,
                    y_hdr,
                    header_display,
                    fontfamily="Cambria",
                    fontsize=style.sublevel_label_fontsize,
                    va="bottom",
                    ha=ha_txt,  # same alignment as numbers
                )

        # value labels
        for s in subs:
            if getattr(s, "split_type", None) in hide_types:
                continue
            y_txt = y_map[s.label] + style.sublevel_label_y_offset
            txt = _format_sublevel_text(s)
            if not txt:
                continue

            if value_only and getattr(s, "split_type", None) != "sideband":
                # unwrap $...$, drop "m_j=" part, and avoid dangling $
                is_math = txt.startswith("$") and txt.endswith("$")
                inner = txt[1:-1] if is_math else txt
                if "=" in inner:
                    inner = inner.split("=", 1)[1].strip()
                txt = f"${inner}$" if is_math else inner

            ax.text(
                x_txt_val,
                y_txt,
                txt,
                fontfamily="Cambria",
                va="center",
                ha=ha_txt,
                fontsize=style.sublevel_label_fontsize,
            )


def draw_transitions(
    ax: plt.Axes,
    transitions: List[dict],
    x_map: Dict[str, float],
    y_map: Dict[str, float],
    style: StyleConfig,
) -> None:
    """Draw transitions as lines with optional arrow and label.

    If reversible=True: simple line.
    If reversible=False: add arrow at midpoint.
    Supports multiple transitions between same levels with offset.
    """
    pairs = defaultdict(list)
    for i, tdef in enumerate(transitions):
        pairs[(tdef["from"], tdef["to"])].append(i)

    # Determine offset slots for overlapping transitions
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

        # Base transition line
        ax.plot([x1, x2], [y1, y2], linestyle=ls, color=color, lw=style.transition_line_width,
                solid_capstyle="butt", label=label)

        if not reversible:
            # Arrow marker at midpoint
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            arrow_len = getattr(style, "transition_arrow_length", delta * 2) / 2
            tail = (mx - ux * arrow_len, my - uy * arrow_len)
            tip = (mx + ux * arrow_len, my + uy * arrow_len)
            ax.annotate("", xy=tip, xytext=tail,
                        arrowprops={"arrowstyle": style.transition_arrowstyle,
                                    "mutation_scale": style.transition_mutation_scale,
                                    "color": color,
                                    "linewidth": style.transition_arrow_line_width})

        if tdef.get("show_label", False):
            # Draw transition label offset perpendicular to the line
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            px, py = -uy, ux
            ax.text(mx + px * style.transition_label_shift,
                    my + py * style.transition_label_shift,
                    label, va="center", ha="center",
                    fontsize=style.transition_label_fontsize,
                    fontfamily="Cambria", color=color)


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
    """High-level plot routine for energy levels and transitions.

    Computes layout, draws levels and transitions, and styles the axes.
    """
    levels = data["levels"]
    transitions = data.get("transitions", [])

    y_map = compute_y_map(levels, layout_cfg)
    x_map = compute_x_map(levels, layout_cfg)

    fig, ax = plt.subplots(figsize=figsize)  # type: ignore

    draw_levels(ax, levels, x_map, y_map, layout_cfg, style_cfg)
    draw_transitions(ax, transitions, x_map, y_map, style_cfg)

    ax.legend(loc=style_cfg.legend_loc, fontsize=style_cfg.legend_fontsize, frameon=False)

    ion_label = format_ion_label(data.get("ion", ""))
    title_text = data.get("title", "")
    ax.set_title(f"{ion_label} {title_text}", pad=title_pad, fontsize=18)
    ax.set_ylabel(f"Energy ({data.get('unit', 'cm$^{-1}$')})", labelpad=ylabel_pad)
    ax.set_xticks([])

    # Configure axis visibility
    if show_axis:
        for side in ["top", "right", "bottom"]:
            ax.spines[side].set_visible(False)
        ax.spines["left"].set_visible(True)
        ax.yaxis.set_visible(True)
    else:
        ax.axis("off")

    spacing = layout_cfg.spacing
    yvals, xvals = list(y_map.values()), list(x_map.values())
    ax.set_ylim(min(yvals) - 100 * spacing, max(yvals) + spacing)
    ax.set_xlim(min(xvals) - spacing / 2, max(xvals) + spacing / 2)

    fig.subplots_adjust(left=left_margin, bottom=0.15)
    fig.tight_layout()
    plt.show()
