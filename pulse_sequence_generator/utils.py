# ---------------------------------------------------------------------
# Copyright 2026 UK Research and Innovation, Science and Technology Facilities Council
#
# [Authors: Daisy Smith, Ian Irwan Ambak]
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ---------------------------------------------------------------------

import matplotlib.pyplot as plt
from typing import List

from pulse_sequence_generator.core import Sequence
from pulse_sequence_generator.config import (
    BASELINE_HEIGHT,
    SEPARATOR_STYLE,
    TIME_AXIS_PROPS,
    FONT_SIZE,
    FONT_FAMILY,
    FONT_COLOR,
    HORIZONTAL_SHIFT,
    VERTICAL_SHIFT,
)


def draw_pulses(
    ax: plt.Axes,
    seq: Sequence,
    channel_order: List[str],
    colors: dict,
    *,
    baseline_height: float = BASELINE_HEIGHT,
    font_size: float = FONT_SIZE,
    font_family: str = FONT_FAMILY,
    font_color: str = FONT_COLOR,
    horizontal_shift: float = HORIZONTAL_SHIFT,
    vertical_shift: float = VERTICAL_SHIFT,
) -> None:
    """
    Draw filled bars for each pulse on each channel, with labels pulled
    from config for font size, family, color, and shift.
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
                    (p.t0 + p.dt / 2) + horizontal_shift,
                    (y - 0.5 * baseline_height) + vertical_shift,
                    p.label,
                    ha='center',
                    va='center',
                    fontsize=font_size,
                    family=font_family,
                    color=font_color
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
