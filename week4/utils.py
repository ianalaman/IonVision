# ===== pulseplot/utils.py =====
"""
Helper functions to draw parts of a pulse sequence plot.
"""
from typing import List, Tuple
import matplotlib.pyplot as plt
from .core import Sequence
from .config import BASELINE_HEIGHT, SEPARATOR_STYLE, TIME_AXIS_PROPS

def draw_pulses(ax: plt.Axes, seq: Sequence, channel_order: List[str], colors: dict) -> None:
    """
    Draw the filled bars for each pulse on each channel.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes on which to draw.
    seq : Sequence
        Pulse sequence to render.
    channel_order : list of str
        Display order of channels (top-to-bottom).
    colors : dict
        Mapping channel->default color.
    """
    by_ch = seq.by_channel()
    ypos = {ch: i for i, ch in enumerate(channel_order)}
    for ch, pulses in by_ch.items():
        y = ypos.get(ch, len(ypos))
        intervals = [(p.t0, p.dt) for p in pulses]
        facecols = [p.color or colors.get(ch, '#888') for p in pulses]
        ax.broken_barh(intervals, (y - BASELINE_HEIGHT/2, BASELINE_HEIGHT),
                       facecolors=facecols)
        for p in pulses:
            if p.label:
                ax.text(p.t0 + p.dt/2, y + BASELINE_HEIGHT,
                        p.label, ha='center', va='bottom', fontsize=8)


def draw_baselines(ax: plt.Axes, seq: Sequence, channel_order: List[str]) -> None:
    """
    Draw the bumpy baselines behind the pulse bars, connecting on/off edges.
    """
    boundaries = seq.time_boundaries()
    for idx, ch in enumerate(channel_order):
        intervals = [(p.t0, p.t0 + p.dt) for p in seq.by_channel().get(ch, [])]
        xs, ys = [], []
        t_cursor = 0
        y0 = idx
        y1 = idx - BASELINE_HEIGHT
        for start, end in intervals:
            # OFF to next start
            xs += [t_cursor, start]
            ys += [y0, y0]
            # rise
            xs += [start, start]
            ys += [y0, y1]
            # ON plateau
            xs += [start, end]
            ys += [y1, y1]
            # fall
            xs += [end, end]
            ys += [y1, y0]
            t_cursor = end
        # final OFF to end
        xs += [t_cursor, boundaries[-1]]
        ys += [y0, y0]
        ax.plot(xs, ys, color='black', linewidth=2.5,
                solid_capstyle='butt', zorder=5)


def draw_separators(ax: plt.Axes, seq: Sequence, labels: List[str]) -> None:
    """
    Draw dashed vertical lines at each time boundary and annotate regions.
    """
    boundaries = seq.time_boundaries()
    ylim = ax.get_ylim()
    y_top = ylim[1] + 0.2
    # separators
    for t in boundaries[1:-1]:
        ax.axvline(t, **SEPARATOR_STYLE, clip_on=False,
                   ymin=-0.12, ymax=1.0)
        # extend below axis
        ax.plot([t, t], [ylim[0] - 0.3, ylim[0]],
                transform=ax.get_xaxis_transform(), **SEPARATOR_STYLE)
    # arrows and labels
    for start, end, text in zip(boundaries[:-1], boundaries[1:], labels):
        ax.annotate('', xy=(start, ylim[1]), xytext=(end, ylim[1]),
                    arrowprops=dict(arrowstyle='<->', lw=1), zorder=6)
        ax.text((start + end) / 2, ylim[1] + 0.1,
                text, ha='center', va='bottom', zorder=6)


def draw_time_axis(ax: plt.Axes) -> None:
    """
    Draw a horizontal time axis with an arrow and label 't'.
    """
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    y_axis = ylim[0] - 0.5
    ax.annotate('t', xy=(xlim[1], y_axis), xytext=(xlim[0], y_axis),
                arrowprops=TIME_AXIS_PROPS)
    ax.get_xaxis().set_visible(True)
