# models.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Level:
    """
    Represents an energy level with optional Zeeman splitting and hierarchical relationships.

    Attributes:
        label (str): Identifier or name for the energy level.
        energy (float): Energy value of the level.
        zeeman (bool, optional): Indicates if Zeeman splitting applies. Defaults to False.
        sublevel (int, optional): Sublevel index or quantum number. Defaults to 0.
        parent (Optional[Level], optional): Reference to the parent Level, if any.
        split_type (Optional[str], optional): Type of splitting (e.g., Zeeman, hyperfine).
        children (List[Level], optional): List of child Level instances. Defaults to empty list.
        meta (Dict[str, Any], optional): Additional metadata for rendering or extra quantum numbers (e.g., color, fixed offsets, mF). Defaults to empty dict.
    """

    label:    str
    energy:   float
    zeeman:   bool = False
    sublevel: int  = 0
    parent:   Optional[Level] = None
    split_type: Optional[str] = None
    children:  List[Level]   = field(default_factory=list)
    # NEW: free bag for rendering/extra quantum numbers (color, fixed offsets, mF, etc.)
    meta: Dict[str, Any] = field(default_factory=dict)
