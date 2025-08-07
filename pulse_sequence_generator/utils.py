'''Helper functions to draw parts of a pulse sequence plot.'''  
import matplotlib.pyplot as plt
from typing import List
from core import Sequence
from config import BASELINE_HEIGHT, SEPARATOR_STYLE, TIME_AXIS_PROPS


def draw_pulses(
    ax: plt.Axes,
    seq: Sequence,
    channel_order: List[str],
    colors: dict,
    *,
    baseline_height: float = BASELINE_HEIGHT
) -> None:
    """
    Draw filled bars for each pulse on each channel.
    """
    by_ch = seq.by_channel()
    ypos = {ch: i for i, ch in enumerate(channel_order)}
    for ch, pulses in by_ch.items():
        y = ypos.get(ch, len(ypos))
        intervals = [(p.t0, p.dt) for p in pulses]
        facecols = [p.color or colors.get(ch, '#888') for p in pulses]
        ax.broken_barh(
            intervals,
            (y - baseline_height, baseline_height),
            facecolors=facecols
        )
        for p in pulses:
            if p.label:
                ax.text(
                    p.t0 + p.dt / 2,
                    (y - 0.30 * baseline_height),
                    p.label,
                    ha='center',
                    va='bottom',
                    fontsize=12,
                    family='Cambria',
                    color='white'
                )


def draw_baselines(
    ax: plt.Axes,
    seq: Sequence,
    channel_order: List[str]
) -> None:
    """
    Draw baselines connecting pulse on/off transitions.
    """
    boundaries = seq.time_boundaries()
    for idx, ch in enumerate(channel_order):
        intervals = [
            (p.t0, p.t0 + p.dt) for p in seq.by_channel().get(ch, [])
        ]
        xs, ys = [], []
        t_cursor = 0
        y0 = idx
        y1 = idx - BASELINE_HEIGHT
        for start, end in intervals:
            xs += [t_cursor, start]; ys += [y0, y0]   # OFF to next start
            xs += [start, start]; ys += [y0, y1]    # rise
            xs += [start, end]; ys += [y1, y1]      # ON plateau
            xs += [end, end]; ys += [y1, y0]        # fall
            t_cursor = end
        xs += [t_cursor, boundaries[-1]]; ys += [y0, y0]  # final OFF
        ax.plot(
            xs,
            ys,
            color='black',
            linewidth=1.5,
            solid_capstyle='butt',
            zorder=5
        )


def draw_separators(
    ax: plt.Axes,
    seq: Sequence,
    labels: List[str],
    *,
    separator_style: dict = SEPARATOR_STYLE
) -> None:
    """
    Draw dashed vertical lines at boundaries and annotate intervals.
    """
    boundaries = seq.time_boundaries()
    ylim = ax.get_ylim()

    # vertical separator lines
    for t in boundaries[1:-1]:
        ax.axvline(
            t,
            **separator_style,
            clip_on=False,
            ymin=-0.12,
            ymax=1.0
        )
        ax.plot(
            [t, t],
            [ylim[0] - 0.3, ylim[0]],
            transform=ax.get_xaxis_transform(),
            **separator_style
        )

    # double-headed arrows and labels
    for start, end, text in zip(boundaries[:-1], boundaries[1:], labels):
        ax.annotate(
            '',
            xy=(start, ylim[1]),
            xytext=(end,   ylim[1]),
            arrowprops=dict(arrowstyle='<->', lw=1),
            zorder=6
        )
        ax.text(
            (start + end) / 2,
            ylim[1] + 0.4,
            text,
            ha='center',
            va='bottom',
            zorder=6
        )


def draw_time_axis(
    ax: plt.Axes,
    *,
    time_axis_props: dict = TIME_AXIS_PROPS
) -> None:
    """
    Draw horizontal time axis with arrow and 't' label.
    """
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    y_axis = ylim[0] - 0.5
    ax.annotate(
        't',
        xy=(xlim[1], y_axis),
        xytext=(xlim[0], y_axis),
        arrowprops=time_axis_props
    )
    ax.get_xaxis().set_visible(True)
