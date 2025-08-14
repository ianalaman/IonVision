# plotter.py


import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import math
from typing import List, Dict
import re


from energy_level_generator.models import Level
from energy_level_generator.layout import compute_x_map, compute_y_map, LayoutConfig, infer_column
from energy_level_generator.style  import StyleConfig
from energy_level_generator.format import format_term_symbol, format_ion_label

from collections import defaultdict

def _format_sublevel_text(lvl):
    """
    Return a short label for a sublevel:
      - If sideband: show "red sideband"/"blue sideband" (ignore parent m_j/m_f).
      - Else prefer meta['m_f'] or meta['m_j'] if present.
      - Else parse "m_f=..." or "m_j=..." or "m=..." from the label.
      - Else return "".
    """
    # 1) Sideband names first
    if getattr(lvl, "split_type", None) == "sideband":
        parts = (lvl.label or "").split(",", 1)
        return parts[1].strip() if len(parts) > 1 else "sideband"

    # 2) Otherwise, show m_f/m_j if available in meta
    meta = getattr(lvl, "meta", {}) or {}
    for nm in ("m_f", "m_j", "m"):
        if nm in meta and meta[nm] is not None:
            return f"{nm}={meta[nm]}"

    # 3) Fallback: parse from label
    m = re.search(r"\b(m_f|m_j|m)\s*=\s*([+-]?\d+(?:/\d+)?)", getattr(lvl, "label", "") or "")
    if m:
        return f"{m.group(1)}={m.group(2)}"

    return ""



def draw_levels(
    ax: plt.Axes,
    levels: List[Level],
    x_map: Dict[str, float],
    y_map: Dict[str, float],
    cfg: LayoutConfig,
    style: StyleConfig
) -> None:
    pad = 0.02
    bar_half = cfg.bar_half

    # 1) Identify all parent labels
    parent_labels = {
        lvl.parent.label
        for lvl in levels
        if lvl.sublevel > 0 and lvl.parent
    }

    # 2) Draw base bars, sublevel ticks, and term‐symbol text
    for lvl in levels:
        x = x_map[lvl.label]
        y = y_map[lvl.label]

        if lvl.sublevel == 0:
            # draw the main energy bar
            if lvl.label in parent_labels:
                color, ls, lw = (
                    style.parent_bar_color,
                    style.parent_bar_linestyle,
                    style.parent_bar_line_width
                )
            else:
                color, ls, lw = (
                    style.base_bar_color,
                    style.base_bar_linestyle,
                    style.line_width
                )
            ax.hlines(y, x - bar_half, x + bar_half,
                      color=color, lw=lw, linestyle=ls)

            # term symbol: left for col 0, right otherwise
            col = infer_column(lvl, cfg)
            if col == 0:
                x_txt = x - bar_half - style.level_label_x_offset
                ha_txt = 'right'
            else:
                x_txt = x + bar_half + style.level_label_x_offset
                ha_txt = 'left'
            
            # inside the lvl.sublevel == 0 block, just before ax.text(...)
            is_parent = (lvl.label in parent_labels)
            if is_parent:
                fam = 'Cambria'
                sz  = style.level_label_fontsize
            else:
                fam = 'Cambria'
                sz  = style.level_label_fontsize

            ax.text(
                x_txt,
                y + style.level_label_y_offset,
                format_term_symbol(lvl),
                va='center', ha=ha_txt,
                fontfamily=fam,
                fontsize=sz,
            )

            # ax.text(
            #     x_txt,
            #     y + style.level_label_y_offset,
            #     format_term_symbol(lvl),
            #     va='center', ha=ha_txt,
            #     fontfamily='Cambria',
            #     fontsize=style.level_label_fontsize,
            # )

        else:
            # sublevel tick styling
            if getattr(lvl, "split_type", None) == "sideband":
                # choose colors for sidebands
                name = (lvl.label or "").lower()
                sb_color = (
                    getattr(style, "sideband_blue_color", "blue") if "blue sideband" in name
                    else getattr(style, "sideband_red_color", "red") if "red sideband" in name
                    else getattr(style, "sublevel_tick_color", "k")
                )
                ls = getattr(style, "sublevel_tick_linestyle", "-")
                lw = getattr(style, "sublevel_tick_line_width", 1.5)
                length = getattr(style, "sideband_tick_length", getattr(style, "sublevel_tick_length", 1.0))
                tick_color = sb_color
            else:
                if lvl.parent and lvl.parent.label in parent_labels:
                    tick_color, ls, lw, length = (
                        style.parent_sublevel_tick_color,
                        style.parent_sublevel_tick_linestyle,
                        style.parent_sublevel_tick_line_width,
                        style.parent_sublevel_tick_length
                    )
                else:
                    tick_color, ls, lw, length = (
                        style.sublevel_tick_color,
                        style.sublevel_tick_linestyle,
                        style.sublevel_tick_line_width,
                        style.sublevel_tick_length
                    )

            tick_half = bar_half * length
            ax.hlines(y, x - tick_half, x + tick_half,
                    color=tick_color, lw=lw, linestyle=ls)


   # 3) Stack sublevel “m” labels at each parent
    from collections import defaultdict
    subs_by_parent: Dict[str, List[Level]] = defaultdict(list)
    for lvl in levels:
        if lvl.sublevel > 0 and lvl.parent:
            subs_by_parent[lvl.parent.label].append(lvl)

    hide_types = set(getattr(style, "hide_split_types", ()))
    show_header = getattr(style, "show_qnum_header", True)
    pad_factor  = float(getattr(style, "qnum_header_pad_factor", 0.35))
    value_only  = bool(getattr(style, "zeeman_label_value_only", True))

    for parent_lbl, subs in subs_by_parent.items():
        x0 = x_map[parent_lbl]

        # side: left for column 0, otherwise right (match your existing logic)
        parent = next((L for L in levels if L.label == parent_lbl), None)
        col = infer_column(parent, cfg) if parent else 1
        if col == 0:
            x_txt = x0 - bar_half - style.sublevel_label_x_offset
            ha_txt = 'right'
        else:
            x_txt = x0 + bar_half + style.sublevel_label_x_offset
            ha_txt = 'left'

        def _outward(x, ha, delta):
        # positive delta moves the text farther away from the bar
            return x - delta if ha == 'right' else x + delta

        # ------- header position -------
        x_txt_hdr = _outward(x_txt, ha_txt, float(getattr(style, "qnum_header_x_shift", 0.0)))


        # split by type
        others    = [s for s in subs if getattr(s, "split_type", None) != "sideband"]
        sidebands = [s for s in subs if getattr(s, "split_type", None) == "sideband"]

        # -------- optional header ("m_j") drawn once per parent --------
        if show_header and others:
            # infer which q-number to print from the first non-sideband label
            # expects something like "m_j=+1/2" or "m_f=..." from _format_sublevel_text
            import re as _re
            header_name = None
            for s in others:
                t = _format_sublevel_text(s) or ""
                m = _re.match(r"^\s*(m_j|m_f|m)\s*=", t)
                if m:
                    header_name = m.group(1)
                    break
            if header_name:
                y_top = max(y_map[s.label] for s in others)
                y_hdr = y_top + pad_factor * cfg.sublevel_uniform_spacing
                ax.text(
                    x_txt_hdr, y_hdr, header_name,
                    fontfamily='Cambria', fontsize=style.sublevel_label_fontsize,
                    va='bottom', ha=ha_txt
                )

        # -------- draw each sublevel label (skip hidden types) --------

        # ------- value positions -------
        x_txt_val = _outward(x_txt, ha_txt, float(getattr(style, "qnum_value_x_shift", 0.0)))
        for lvl in subs:
            if getattr(lvl, "split_type", None) in hide_types:
                continue

            y_txt = y_map[lvl.label] + style.sublevel_label_y_offset
            txt = _format_sublevel_text(lvl)
            if not txt:
                continue

            # For Zeeman/hyperfine values: strip "m_j=" / "m_f=" → show value only
            if value_only and getattr(lvl, "split_type", None) != "sideband":
                if "=" in txt:
                    txt = txt.split("=", 1)[1].strip()

            ax.text(
                x_txt_val, y_txt, txt,
                fontfamily='Cambria',
                va='center', ha=ha_txt,
                fontsize=style.sublevel_label_fontsize
            )




import math
from collections import defaultdict
from typing import List, Dict

def draw_transitions(
    ax: plt.Axes,
    transitions: List[dict],
    x_map: Dict[str, float],
    y_map: Dict[str, float],
    style: StyleConfig
) -> None:
    """
    Draw transitions between nodes:
      • reversible=True  → plain line
      • reversible=False → line + single '>' marker at midpoint
    """

    # 1) Group identical from→to pairs so we can offset them
    pairs = defaultdict(list)
    for i, t in enumerate(transitions):
        pairs[(t['from'], t['to'])].append(i)

    # 2) Compute centered slot indices
    slots = {}
    for idxs in pairs.values():
        n = len(idxs)
        for rank, i in enumerate(idxs):
            slots[i] = (rank - (n-1)/2, n)

    # 3) Draw each
    for i, t in enumerate(transitions):
        x1, y1 = x_map[t['from']], y_map[t['from']]
        x2, y2 = x_map[t['to']],   y_map[t['to']]

        # unit direction and normal
        dx, dy = x2-x1, y2-y1
        L = math.hypot(dx, dy)
        if L == 0:
            continue  # avoid division by zero
        ux, uy = dx/L, dy/L
        nx, ny = -uy, ux

        # offset so lines don’t overlap
        slot_index, _ = slots[i]
        delta = style.transition_offset
        ox, oy = nx*(slot_index*delta), ny*(slot_index*delta)
        x1, y1, x2, y2 = x1+ox, y1+oy, x2+ox, y2+oy

        # styling
        ls    = '-' if t.get('style','solid')=='solid' else ':'
        color = t.get('color','k')
        label = t.get('label','')
        reversible = t.get('reversible', True)

        # draw the base line
        line, = ax.plot(
            [x1, x2], [y1, y2],
            linestyle=ls,
            color=color,
            lw=style.transition_line_width,
            solid_capstyle="butt",
            label=label
        )

        if not reversible:
            # add an arrow at the midpoint via annotate()
            mx, my = (x1 + x2)/2, (y1 + y2)/2
            # small half-length along the direction vector
            arrow_len = getattr(style, 'transition_arrow_length', delta*2) / 2
            tail = (mx - ux*arrow_len, my - uy*arrow_len)
            tip  = (mx + ux*arrow_len, my + uy*arrow_len)

            ax.annotate(
                '', 
                xy=tip, xytext=tail,
                arrowprops=dict(
                    arrowstyle=style.transition_arrowstyle,
                    mutation_scale=style.transition_mutation_scale,
                    color=color,
                    linewidth=style.transition_arrow_line_width,
                )
            )

        # optional text label
        if t.get('show_label', False):
            mx, my = (x1 + x2)/2, (y1 + y2)/2
            px, py = -uy, ux
            ax.text(
                mx + px * style.transition_label_shift,
                my + py * style.transition_label_shift,
                label,
                va='center', ha='center',
                fontsize=style.transition_label_fontsize,
                fontfamily='Cambria',
                color=color
            )


def plot_energy_levels(
    data: dict,
    layout_cfg: LayoutConfig,
    style_cfg: StyleConfig,
    figsize=(8,5),
    show_axis=True,
    title_pad=20,
    ylabel_pad=15,
    left_margin=0.2
) -> None:
    """
    High-level entry-point: compute layout, draw levels and transitions,
    and apply axis styling.
    """
    levels      = data['levels']
    transitions = data.get('transitions', [])

    # compute x/y maps
    y_map = compute_y_map(levels, layout_cfg)
    x_map = compute_x_map(levels, layout_cfg)

    fig, ax = plt.subplots(figsize=figsize)

    # pass style_cfg into both drawing functions
    draw_levels(ax, levels, x_map, y_map, layout_cfg, style_cfg)
    draw_transitions(ax, transitions, x_map, y_map, style_cfg)
    # draw legend of all transition‐labels
    ax.legend(loc=style_cfg.legend_loc,
              fontsize=style_cfg.legend_fontsize,
              frameon=False)
    
    ion_label = format_ion_label(data.get('ion',''))
    title_text = data.get('title', '')
    ax.set_title(f"{ion_label} {title_text}", pad=title_pad, fontsize=18)
    ax.set_ylabel(f"Energy ({data.get('unit','cm$^{-1}$')})", labelpad=ylabel_pad)
    ax.set_xticks([])

    if show_axis:
        for side in ['top','right','bottom']:
            ax.spines[side].set_visible(False)
        ax.spines['left'].set_visible(True)
        ax.yaxis.set_visible(True)
    else:
        ax.axis('off')

    spacing = layout_cfg.spacing
    yvals, xvals = list(y_map.values()), list(x_map.values())
    ax.set_ylim(min(yvals)-100*spacing, max(yvals)+spacing)
    ax.set_xlim(min(xvals)-spacing/2, max(xvals)+spacing/2)
    fig.subplots_adjust(left=left_margin, bottom=0.15)
    fig.tight_layout()
    plt.show()
