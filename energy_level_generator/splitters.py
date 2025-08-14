# splitters.py

from abc import ABC, abstractmethod
from typing import List
from energy_level_generator.models import Level
from energy_level_generator.physics import zeeman_split, sideband_split   # your existing function, now returns List[Level]

class Splitter(ABC):
    """Abstract base class for any splitting kernel."""
    name: str

    @abstractmethod
    def split(self, lvl: Level) -> List[Level]:
        """
        Given one Level, return its sub‐levels according to this splitter.
        Return an empty list if no splitting applies.
        """
        pass


class ZeemanSplitter(Splitter):
    """Zeeman splitting: calls physics.zeeman_split and wires up parent/child links."""
    name = "zeeman"

    def __init__(self, B: float):
        """
        Parameters
        ----------
        B : float
            Magnetic field strength in Tesla.
        """
        self.B = B

    def split(self, lvl: Level) -> List[Level]:
        # Only split if this level is flagged for Zeeman and B>0
        if not lvl.zeeman or self.B <= 0:
            return []

        # Delegate to your physics module
        # Expecting zeeman_split to now return List[Level]
        children = zeeman_split(lvl, self.B)

        # Wire up the tree info on each child
        for child in children:
            child.sublevel   = lvl.sublevel + 1
            child.parent     = lvl
            child.split_type = self.name
            # prevent further Zeeman on these sub‐levels
            child.zeeman     = False

        # Attach back to the parent
        lvl.children = children
        return children


# energy_level_generator/splitters.py
from dataclasses import replace
from fractions import Fraction
from typing import List, Optional
from energy_level_generator.models import Level

class SidebandSplitter:
    def __init__(self, gap: float = 100.0, label_suffixes=("red sideband","blue sideband")):
        self.gap = gap
        self.label_suffixes = label_suffixes  # [lower, higher]

    @staticmethod
    def _match_mj(child: Level, mj_str: str) -> bool:
        # mj_str like "-5/2"; child.label contains "m_j=±p/q"
        try:
            return f"m_j={mj_str}" in (child.label or "")
        except Exception:
            return False

    def split(self, base: Level, zeeman_children: Optional[List[Level]] = None) -> List[Level]:
        """
        Create sideband children. If base.sideband has {"m_j": ["-5/2", ..."]},
        attach sidebands to those *Zeeman* children. Otherwise, attach to base.
        """
        if not base.sideband:
            return []

        targets: List[Level] = []
        mj_list = []
        if isinstance(base.sideband, dict) and "m_j" in base.sideband:
            mj_list = list(base.sideband["m_j"])  # list of strings like "-5/2"

        if zeeman_children and mj_list:
            # attach to the matching Zeeman child(ren)
            for mj in mj_list:
                match = next((c for c in zeeman_children if self._match_mj(c, mj)), None)
                if match:
                    targets.append(match)
        if not targets:
            # fallback: no match provided → treat base as the parent
            targets = [base]

        kids: List[Level] = []
        for parent in targets:
            # energies around the chosen parent
            e_low  = parent.energy - self.gap
            e_high = parent.energy + self.gap
            labels = [self.label_suffixes[0], self.label_suffixes[1]]  # red, blue

            # sublevel index one deeper than the parent (e.g., Zeeman has 1 → sideband 2)
            sublevel_idx = (parent.sublevel or 0) + 1

            for e, suffix in zip((e_low, e_high), labels):
                lbl = f"{parent.label}, {suffix}"
                child = Level(
                    label    = lbl,
                    energy   = e,
                    zeeman   = False,
                    sideband = None,
                    sublevel = sublevel_idx,
                    parent   = parent,
                    split_type = "sideband",
                    children = [],
                    meta = dict(parent.meta),  # inherit meta (e.g., m_j)
                )
                # keep a tree if you use it
                parent.children.append(child)
                kids.append(child)

        # if you also want the base to know about its new grandchildren,
        # you can append to base.children too (optional for layout)
        return kids
