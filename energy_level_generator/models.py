# models.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Level:
    label:    str
    energy:   float
    zeeman:   bool = False              # “eligible for Zeeman split?”
    sublevel: int  = 0                  # generation/depth
    parent:   Optional[Level] = None    # pointer back
    split_type: Optional[str] = None    # e.g. "zeeman", "hyperfine"
    children:  List[Level]   = field(default_factory=list)
