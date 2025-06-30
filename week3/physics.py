# physics.py

import re
import numpy as np
from typing import List
from scipy.constants import physical_constants, h, c

from .models import Level

μB = physical_constants["Bohr magneton"][0]
hc = h * c

def lande_g_factor(L: float, S: float, J: float) -> float:
    return 1.5 + (S*(S+1) - L*(L+1)) / (2 * J * (J+1))

def zeeman_split(parent: Level, B: float) -> List[Level]:
    # 1) guard: no splitting if not requested
    if not parent.zeeman or B <= 0:
        return []                  # ← always a list

    # 2) parse term symbol
    term = parent.label.split()[1]
    m = re.match(r"(\d+)([SPDF])(\d)/(\d)", term)
    if not m:
        return []                  # ← still a list

    mult, Lsym, num, den = m.groups()
    J = int(num)/int(den)
    S = (int(mult)-1)/2
    L = {"S":0,"P":1,"D":2,"F":3}[Lsym]

    gJ   = lande_g_factor(L, S, J)
    conv = (gJ * μB * B) / hc * 1e2

    out: List[Level] = []
    for mJ in np.arange(-J, J+1, 1):
        ΔE = conv * mJ
        child = Level(
            label      = f"{parent.label}, m={mJ:+.1f}",
            energy     = parent.energy + ΔE,
            zeeman     = False,
            sublevel   = parent.sublevel + 1,
            parent     = parent,
            split_type = "zeeman"
        )
        out.append(child)

    parent.children = out
    return out
