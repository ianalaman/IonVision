# models.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class Level:
    label:    str
    energy:   float
    zeeman:   bool = False
    sublevel: int  = 0
    parent:   Optional["Level"] = None
    split_type: Optional[str] = None
    children:  List["Level"]   = field(default_factory=list)
    # NEW: free bag for rendering/extra quantum numbers (color, fixed offsets, mF, etc.)
    meta: Dict[str, Any] = field(default_factory=dict)
