# plotter.py

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import math
from typing import List, Dict

from .models import Level
from .layout import compute_x_map, compute_y_map, LayoutConfig
from .style  import StyleConfig
from .format  import format_term_symbol, format_ion_label


def draw_levels(
    ax: plt.Axes,
    levels: List[Level],
    x_map: Dict[str, float],
    y_map: Dict[str, float],
    cfg: LayoutConfig,
    style: StyleConfig
) -> None:
    """
    Draw energy‐level bars and sublevel ticks on `ax`.

    - Base bars (sublevel==0) use cfg.bar_half and style.base_bar_color.
    - Sublevel ticks (sublevel>0) use style.sublevel_tick_color.
    - Labels only for sublevel==0.
    """
    pad      = 0.02
    tick_half = cfg.bar_half * style.tick_size

    for lvl in levels:
        x = x_map[lvl.label]
        y = y_map[lvl.label]
        lw = style.line_width

        # choose color by split_type
        color = (style.zeeman_bar_color
                 if lvl.split_type == "zeeman"
                 else style.base_bar_color)

        # draw bar or tick
        if lvl.sublevel == 0:
            print("Drawing base-bar for", lvl.label, "at", x, y)
            ax.hlines(y, x - cfg.bar_half, x + cfg.bar_half,
                      color=color, lw=lw)
            ax.text(x + cfg.bar_half + pad, y,
                    format_term_symbol(lvl),
                    va='center', ha='left', fontsize=9)
        else:
            ax.hlines(y, x - tick_half, x + tick_half,
                      color=style.sublevel_tick_color, lw=lw)
            m_txt = lvl.label.split("m=")[1]   # e.g. "+1.5"
            ax.text(x + tick_half + pad,
                y,
                m_txt,
                va='center', ha='left', fontsize=6)


def draw_transitions(
    ax: plt.Axes,
    transitions: List[dict],
    x_map: Dict[str, float],
    y_map: Dict[str, float]
) -> None:
    """
    Draw arrows/lines for each transition dict with keys:
      'from', 'to', optional 'label','color','style','reversible'
    """
    for t in transitions:
        x1, y1 = x_map[t['from']], y_map[t['from']]
        x2, y2 = x_map[t['to']],   y_map[t['to']]
        ls = '-' if t.get('style','solid')=='solid' else ':'
        color = t.get('color','k')

        if t.get('reversible', False):
            ax.plot([x1,x2], [y1,y2], linestyle=ls, color=color, lw=2)
        else:
            arrow = FancyArrowPatch((x1,y1), (x2,y2),
                                     arrowstyle='->',
                                     mutation_scale=10,
                                     color=color, lw=2, linestyle=ls)
            ax.add_patch(arrow)

        # place label offset from the line
        mx, my = (x1 + x2)/2, (y1 + y2)/2
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        ux, uy = dx/L, dy/L
        px, py = -uy, ux
        shift = 0.035
        ax.text(mx + px*shift, my + py*shift,
                t.get('label',''),
                va='center', ha='center', fontsize=8)


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

    `data` must contain:
      - 'ion' (str)
      - 'unit' (str)
      - 'levels' (List[Level])
      - 'transitions' (List[dict])
    """
    levels      = data['levels']
    transitions = data.get('transitions', [])

    
    y_map = compute_y_map(levels, layout_cfg)
    x_map = compute_x_map(levels, layout_cfg, style_cfg)

    fig, ax = plt.subplots(figsize=figsize)
    draw_levels(ax, levels, x_map, y_map, layout_cfg, style_cfg)
    draw_transitions(ax, transitions, x_map, y_map)

    ion_label = format_ion_label(data.get('ion',''))
    ax.set_title(f"{ion_label} Energy Levels", pad=title_pad)
    ax.set_ylabel(f"Energy ({data.get('unit','cm$^{-1}$')})",
                  labelpad=ylabel_pad)
    ax.set_xticks([])

    if show_axis:
        for side in ['top','right','bottom']:
            ax.spines[side].set_visible(False)
        ax.spines['left'].set_visible(True)
        ax.yaxis.set_visible(True)
    else:
        ax.axis('off')

    # set limits
    spacing = layout_cfg.spacing
    yvals = list(y_map.values())
    xvals = list(x_map.values())
    ax.set_ylim(min(yvals)-spacing, max(yvals)+spacing)
    ax.set_xlim(min(xvals)-spacing/2, max(xvals)+spacing/2)
    fig.subplots_adjust(left=left_margin, bottom=0.15)
    fig.tight_layout()
    ax.set_ylim(-500, 13400)

    plt.show()
