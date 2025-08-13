# splitters.py

from abc import ABC, abstractmethod
from typing import List
from energy_level_generator.models import Level
from energy_level_generator.physics import zeeman_split   # your existing function, now returns List[Level]

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
