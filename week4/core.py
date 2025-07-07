# ===== pulseplot/core.py =====
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Pulse:
    channel: str       # e.g. 'MW', 'EOM', ...
    t0: float          # start time
    dt: float          # duration
    color: str         # Matplotlib/HTML color
    label: str = ''    # optional label for hover/legend

@dataclass
class Sequence:
    pulses: List[Pulse] = field(default_factory=list)

    def add(self, pulse: Pulse):
        self.pulses.append(pulse)

    def by_channel(self) -> Dict[str, List[Pulse]]:
        d: Dict[str, List[Pulse]] = {}
        for p in self.pulses:
            d.setdefault(p.channel, []).append(p)
        return d