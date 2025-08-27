# ===== pulseplot/plot.py =====
"""
Matplotlib-based static plotting of pulse sequences.
"""
import matplotlib.pyplot as plt
from typing import Optional, List, Tuple, Dict
from pulse_sequence_generator.config import DEFAULT_CHANNEL_ORDER, DEFAULT_COLORS
from pulse_sequence_generator.utils import draw_pulses, draw_baselines, draw_separators, draw_time_axis
import matplotlib as mpl
from pulse_sequence_generator.config import RC_PARAMS

# apply once, globally
mpl.rcParams.update(RC_PARAMS)


def plot_matplotlib(
    seq: "Sequence",
    channel_order: Optional[List[str]] = None,
    colors: Optional[Dict[str, str]] = None,
    xlim: Optional[Tuple[float, float]] = None,
    ax: Optional[plt.Axes] = None,
    labels: Optional[List[str]] = None,
) -> Tuple[plt.Figure, plt.Axes]:
    """Draw a static pulse sequence with Matplotlib.

    Args:
        seq: Pulse sequence to plot.
        channel_order: Channel order (top → bottom). Defaults to config.
        colors: Mapping ``channel -> color``. Defaults to config.
        xlim: X-axis limits; default is full data extent.
        ax: Existing axes to draw onto. If ``None``, a new figure/axes is created.
        labels: Text labels for each region between separators.

    Returns:
        tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]: Figure and axes.

    ??? example "Quick example"
        ```python
        fig, ax = plot_matplotlib(seq)  # uses defaults from config
        ```
    """
    from pulse_sequence_generator.core import Sequence
    if channel_order is None:
        channel_order = DEFAULT_CHANNEL_ORDER
    if colors is None:
        colors = DEFAULT_COLORS
    if ax is None:
        fig, ax = plt.subplots(figsize=( 2*len(channel_order), len(channel_order)))
    else:
        fig = ax.figure

    # Draw components
    draw_pulses(ax, seq, channel_order, colors)
    draw_baselines(ax, seq, channel_order)
    if labels:
        draw_separators(ax, seq, labels)
    draw_time_axis(ax)

    # Set y-ticks
    ax.set_yticks(list(range(len(channel_order))), channel_order)

    # Set x-limits
    if xlim:
        ax.set_xlim(*xlim)
    else:
        # auto-range based on data
        max_t = max((p.t0 + p.dt) for p in seq.pulses)
        ax.set_xlim(0, max_t * 1.05)

    return fig, ax