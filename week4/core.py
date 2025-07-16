# ===== pulseplot/core.py =====
"""
Core data models for pulse sequences.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

@dataclass
class Pulse:
    """
    Represents a single pulse on a given channel.

    Attributes
    ----------
    channel : str
        Name of the channel (e.g., 'MW', 'AOM').
    t0 : float
        Start time of the pulse.
    dt : float
        Duration of the pulse.
    color : str
        Matplotlib or HTML color code for rendering.
    label : str, optional
        Optional label for the pulse (default: '').
    """
    channel: str
    t0: float
    dt: float
    color: str
    label: str = ""

@dataclass
class Sequence:
    """
    A sequence of pulses across potentially multiple channels.

    Methods
    -------
    by_channel()
        Group pulses by their channel name.
    channels()
        List all channel names present in the sequence.
    time_boundaries()
        Compute the sorted unique time boundaries (pulse edges).
    plot(**kwargs)
        Convenient wrapper around `plot_matplotlib`.
    """
    pulses: List[Pulse] = field(default_factory=list)

    def add(self, pulse: Pulse) -> None:
        """Add a new Pulse to the sequence."""
        self.pulses.append(pulse)

    def by_channel(self) -> Dict[str, List[Pulse]]:
        """
        Return a dict mapping channel names to lists of pulses on that channel.
        """
        d: Dict[str, List[Pulse]] = {}
        for p in self.pulses:
            d.setdefault(p.channel, []).append(p)
        return d

    def channels(self) -> List[str]:
        """
        Return a sorted list of channel names present in this sequence.
        """
        return sorted(self.by_channel().keys())

    def time_boundaries(self) -> List[float]:
        """
        Compute the unique sorted list of times where any pulse starts or ends.
        """
        edges = {0.0}
        for p in self.pulses:
            edges.add(p.t0)
            edges.add(p.t0 + p.dt)
        return sorted(edges)

    def plot(self, **kwargs) -> Tuple:
        """
        Wrapper to draw this sequence with Matplotlib.

        Parameters
        ----------
        **kwargs
            Passed directly to `plot_matplotlib`, e.g. channel_order, colors, xlim, ax.

        Returns
        -------
        fig, ax : Matplotlib Figure and Axes objects.
        """
        return plot_matplotlib(self, **kwargs)
