# ===== pulseplot/plot.py =====
import matplotlib.pyplot as plt
from .core import Sequence
from .config import DEFAULT_CHANNEL_ORDER, DEFAULT_COLORS


def plot_matplotlib(
    seq: Sequence,
    channel_order=None,
    colors=None,
    xlim=None,
    ax=None
):
    """
    Draw a static pulse sequence with Matplotlib.
    """
    if channel_order is None:
        channel_order = DEFAULT_CHANNEL_ORDER
    if colors is None:
        colors = DEFAULT_COLORS

    by_ch = seq.by_channel()
    # assign y positions
    ypos = {ch: i for i, ch in enumerate(channel_order)}

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 2 + len(channel_order)))
    else:
        fig = ax.figure

    # plot each channel
    for ch, pulses in by_ch.items():
        y = ypos.get(ch, len(ypos))
        intervals = [(p.t0, p.dt) for p in pulses]
        facecols = [p.color or colors.get(ch, '#888888') for p in pulses]
        ax.broken_barh(intervals, (y - 0.4, 0.4), facecolors=facecols)
        for p in pulses:
            if p.label:
                ax.text(p.t0 + p.dt/2, y + 0.5, p.label,
                        ha='center', va='bottom', fontsize=8)

    ax.set_yticks(list(ypos.values()), list(ypos.keys()))
    if xlim is None:
        # auto from data
        max_t = max((p.t0 + p.dt) for p in seq.pulses)
        ax.set_xlim(0, max_t * 1.05)
    else:
        ax.set_xlim(*xlim)

    # Draw a horizontal time axis with an arrow and label 't'
    ylim = ax.get_ylim()
    xlim = ax.get_xlim()
    y_axis = ylim[0] - 0.5
    ax.annotate(
        't', 
        xy=(xlim[1], y_axis), 
        xytext=(xlim[0], y_axis),
        arrowprops=dict(arrowstyle='->', lw=1.5, color='black')
    )
    ax.get_xaxis().set_visible(True)
    return fig, ax

# Placeholder for interactive backend
# def plot_interactive(seq: Sequence, ...):
#     pass
