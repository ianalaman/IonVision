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

"""Default configuration for pulse-sequence plotting."""

from typing import Dict, List

DEFAULT_CHANNEL_ORDER: List[str] = ["MW", "EOM", "PMT", "AOM"]
"""Order in which channels are drawn (top→bottom)."""

DEFAULT_COLORS: Dict[str, str] = {
    "MW":  "#B0B0B0",
    "EOM": "#A0D468",
    "PMT": "#4C4C4C",
    "AOM": "#4A89DC",
}
"""Default fill colors for each channel."""

RC_PARAMS: Dict[str, int | float | str] = {
    "font.size":       16,
    "axes.titlesize":  18,
    "axes.labelsize":  16,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
}
"""Global Matplotlib rcParams applied to pulse plots."""

BASELINE_HEIGHT: float = 0.4
"""Relative height of each pulse bar."""

SEPARATOR_STYLE: Dict[str, object] = {"linestyle": "--", "linewidth": 0.8, "color": "grey"}
"""Style for dashed separators between time sections."""

TIME_AXIS_PROPS: Dict[str, object] = {"arrowstyle": "->", "lw": 1.5, "color": "black"}
"""Style for the time-axis arrow."""

FONT_SIZE: int = 12
"""Font size for pulse labels."""

FONT_FAMILY: str = "Cambria"
"""Font family for pulse labels."""

FONT_COLOR: str = "white"
"""Text color for pulse labels."""

HORIZONTAL_SHIFT: float = 0.0
"""x-offset applied to label position (in time units)."""

VERTICAL_SHIFT: float = 0.0
"""y-offset applied to label position (axes units)."""

__all__ = [
    "DEFAULT_CHANNEL_ORDER",
    "DEFAULT_COLORS",
    "RC_PARAMS",
    "BASELINE_HEIGHT",
    "SEPARATOR_STYLE",
    "TIME_AXIS_PROPS",
    "FONT_SIZE",
    "FONT_FAMILY",
    "FONT_COLOR",
    "HORIZONTAL_SHIFT",
    "VERTICAL_SHIFT",
]
