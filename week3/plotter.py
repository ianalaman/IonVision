# plotter.py


import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import math
from typing import List, Dict

from models import Level
from layout import compute_x_map, compute_y_map, LayoutConfig, infer_column
from style  import StyleConfig
from format import format_term_symbol, format_ion_label

from collections import defaultdict


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
            # just draw the little sublevel tick
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

    # 3) Stack sublevel “m=” labels at each parent
    from collections import defaultdict
    subs_by_parent: Dict[str, List[Level]] = defaultdict(list)
    for lvl in levels:
        if lvl.sublevel > 0 and lvl.parent:
            subs_by_parent[lvl.parent.label].append(lvl)

    for parent_lbl, subs in subs_by_parent.items():
        x0 = x_map[parent_lbl]
        for lvl in subs:
            # flip to left for column 0 parents
            col = infer_column(lvl.parent, cfg)
            if col == 0:
                x_txt = x0 - bar_half - style.sublevel_label_x_offset
                ha_txt = 'right'
            else:
                x_txt = x0 + bar_half + style.sublevel_label_x_offset
                ha_txt = 'left'

            y_txt = y_map[lvl.label] + style.sublevel_label_y_offset
            ax.text(
                x_txt,
                y_txt,
                lvl.label.split("m=")[1],
                fontfamily='Cambria',
                va='center', ha=ha_txt,
                fontsize=style.sublevel_label_fontsize
            )

def draw_transitions(
    ax: plt.Axes,
    transitions: List[dict],
    x_map: Dict[str, float],
    y_map: Dict[str, float],
    style: StyleConfig
) -> None:
    """
    Draw arrows/lines for each transition dict with keys:
      'from', 'to', optional 'label','color','style','reversible'
    Uses the passed `style` for arrow‐ and label‐ styling.
    """

    # build index‐lists for each from→to pair
    pairs = defaultdict(list)
    for i, t in enumerate(transitions):
        pairs[(t['from'], t['to'])].append(i)

    # for each index, store its “slot” and the total count
    slots = {}
    for key, idxs in pairs.items():
        n = len(idxs)
        for rank, i in enumerate(idxs):
            # rank runs 0..n-1; center them around 0
            slots[i] = (rank - (n-1)/2, n)

            
    for t in transitions:
        x1, y1 = x_map[t['from']], y_map[t['from']]
        x2, y2 = x_map[t['to']],   y_map[t['to']]
        # get the unit normal to the transition vector
        dx, dy = x2-x1, y2-y1
        L = math.hypot(dx, dy)
        ux, uy = dx/L, dy/L
        nx, ny = -uy, ux

        # find our slot offset and spacing (you can tweak delta to taste)
        slot_index, total = slots[i]
        delta = style.transition_offset  # e.g. 0.02 in data‐units
        ox, oy = nx*(slot_index*delta), ny*(slot_index*delta)

        # apply the shift
        x1, y1 = x1 + ox, y1 + oy
        x2, y2 = x2 + ox, y2 + oy
        ls = '-' if t.get('style','solid')=='solid' else ':'
        color = t.get('color','k')

        if t.get('reversible', False):
            ax.plot(
                [x1, x2], [y1, y2],
                linestyle=ls,
                color=color,
                lw=style.transition_line_width,
                label=t.get('label','')
            )
        else:
            arrow = FancyArrowPatch(
                (x1, y1), (x2, y2),
                arrowstyle=style.transition_arrowstyle,
                mutation_scale=style.transition_mutation_scale,
                color=color,
                lw=style.transition_arrow_line_width,
                label=t.get('label',''),
                linestyle=ls
            )
            ax.add_patch(arrow)

        # place transition label
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        ux, uy = dx/L, dy/L
        px, py = -uy, ux

        ax.text(
            mx + px * style.transition_label_shift,
            my + py * style.transition_label_shift,
            t.get('label',''),
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
    x_map = compute_x_map(levels, layout_cfg, style_cfg)

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
