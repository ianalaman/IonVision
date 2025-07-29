# ===== week4/core.py =====
from dataclasses    import dataclass, field
from typing        import List, Dict, Tuple, Optional
import matplotlib.pyplot as plt  # for type hints

import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional
# assume plot_matplotlib lives in week4/plot.py



@dataclass
class Pulse:
    channel: str
    t0:      float
    dt:      float
    color:   str
    label:   Optional[str] = None

    @staticmethod
    def from_dict(d: Dict) -> "Pulse":
        return Pulse(
            channel = d["channel"],
            t0      = d["t0"],
            dt      = d["dt"],
            color   = d.get("color", "#888"),
            label   = d.get("label", "")
        )


@dataclass
class Sequence:
    pulses: List[Pulse] = field(default_factory=list)

    @staticmethod
    def from_dict(d: Dict) -> "Sequence":
        seq = Sequence()
        for pd in d.get("pulses", []):
            seq.pulses.append(Pulse.from_dict(pd))
        return seq

    @staticmethod
    def from_json_file(path: str) -> "Sequence":
        with open(path) as f:
            data = json.load(f)
        return Sequence.from_dict(data)
    
    def add(self, pulse: Pulse) -> None:
        self.pulses.append(pulse)

    def by_channel(self) -> Dict[str, List[Pulse]]:
        d: Dict[str, List[Pulse]] = {}
        for p in self.pulses:
            d.setdefault(p.channel, []).append(p)
        return d

    def channel_order(self) -> List[str]:
        """
        Return the channels in the order they first appear in self.pulses.
        """
        # Since by_channel() preserves insertion order (Python 3.7+),
        # this is just the dict’s keys.
        return list(self.by_channel().keys())

    def time_boundaries(self) -> List[float]:
        """
        Return the sorted list of all pulse start- and end-times,
        plus zero as the global start.
        """
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
        Plot this Sequence using plot_matplotlib, filling in any
        missing arguments from the data in self.
        """
        from .plot import plot_matplotlib  
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

