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
# models.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Union, List, Dict, Any


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
    sideband: Optional[ List[Dict[str, Any]]] = None
    sublevel: int  = 0
    parent:   Optional[Level] = None
    split_type: Optional[str] = None
    children:  List[Level]   = field(default_factory=list)
    # NEW: free bag for rendering/extra quantum numbers (color, fixed offsets, mF, etc.)
    meta: Dict[str, Any] = field(default_factory=dict)
