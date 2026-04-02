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

# ===== core.py =====
from dataclasses    import dataclass, field
from typing        import List, Dict, Tuple, Optional
import matplotlib.pyplot as plt  # for type hints

import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional
# assume plot_matplotlib lives in plot.py


@dataclass
class Pulse:
    """A single rectangular pulse on a named hardware channel."""
    channel: str
    t0:      float
    dt:      float
    color:   str
    label:   Optional[str] = None

    @staticmethod
    def from_dict(d: Dict) -> "Pulse":
        """Build a Pulse from a dict with keys: channel, t0, dt, [color], [label]."""
        return Pulse(
            channel = d["channel"],
            t0      = d["t0"],
            dt      = d["dt"],
            color   = d.get("color", "#888"),
            label   = d.get("label", "")
        )


@dataclass
class Sequence:
    """A collection of pulses with helpers for grouping, timing, and plotting."""
    pulses: List[Pulse] = field(default_factory=list)

    @staticmethod
    def from_dict(d: Dict) -> "Sequence":
        """Build a Sequence from a dict: {'pulses': [...], ...}. Preserves raw JSON."""
        seq = Sequence()
        for pd in d.get("pulses", []):
            seq.pulses.append(Pulse.from_dict(pd))
        seq._json_data = d  # store raw JSON for time_boundaries etc.
        return seq

    @staticmethod
    def from_json_file(path: str) -> "Sequence":
        """Load a Sequence from a JSON file on disk."""
        with open(path) as f:
            data = json.load(f)
        return Sequence.from_dict(data)
    
    def add(self, pulse: Pulse) -> None:
        """Append a pulse to the sequence."""
        self.pulses.append(pulse)

    def by_channel(self) -> Dict[str, List[Pulse]]:
        """Group pulses by channel name, preserving insertion order."""
        d: Dict[str, List[Pulse]] = {}
        for p in self.pulses:
            d.setdefault(p.channel, []).append(p)
        return d

    def channel_order(self) -> List[str]:
        """
        Return channels in the order they first appear.
        """
        # Since by_channel() preserves insertion order (Python 3.7+),
        # this is just the dict’s keys.
        return list(self.by_channel().keys())

    def time_boundaries(self) -> List[float]:
        """
        Return sorted unique time boundaries.

        Uses 'time_boundaries' from the original JSON if present; otherwise
        derives boundaries from pulse start/end times (including 0.0).
        """
        if hasattr(self, "_json_data"):
            boundaries = self._json_data.get("time_boundaries", None)
            if boundaries is not None:
                return sorted(set(boundaries))
        # fallback: compute from pulses
        edges = {0.0}
        for p in self.pulses:
            edges.add(p.t0)
            edges.add(p.t0 + p.dt)
        return sorted(edges)

    def plot(
        self,
        channel_order: Optional[List[str]]    = None,
        colors:        Optional[Dict[str,str]] = None,
        xlim:          Optional[Tuple[float,float]] = None,
        labels:        Optional[List[str]]     = None,
        ax:            Optional[plt.Axes]      = None,
        hide_xticks:   bool = True,
        title:         Optional[str]           = None
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Render the sequence as a channel timeline (Matplotlib).

        Defaults:
        - channel_order: order of first appearance
        - xlim: (0, max(time_boundaries()))
        - labels/colors: passed through to plotter if provided

        Returns (fig, ax). Y-axis is inverted so the first channel is on top.
        """
        from pulse_sequence_generator.plot import plot_matplotlib  
        # 1) defaults
        channel_order = channel_order or self.channel_order()
        bounds        = self.time_boundaries()
        xlim          = xlim or (0, bounds[-1])

        # 2) delegate to your plot routine
        fig, ax = plot_matplotlib(
            self,
            channel_order=channel_order,
            colors=colors,
            xlim=xlim,
            labels=labels,
            ax=ax
        )
        ax.invert_yaxis()
        if title is not None:
            ax.set_title(title)
        if hide_xticks:
             ax.set_xticks([])

        return fig, ax
