# physics.py

import re
import numpy as np
from typing import List
from scipy.constants import physical_constants, h, c

from energy_level_generator.models import Level
from fractions import Fraction

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
        # Represent mJ as a fraction string with explicit sign
        mJ_frac = Fraction(mJ).limit_denominator()
        # str(mJ_frac) → '1/2' or '-1/2'; add leading '+' if positive
        s = str(mJ_frac)
        if not s.startswith('-'):
            s = '+' + s
        child = Level(
            label      = f"{parent.label}, m_j={s}",
            energy     = parent.energy + conv * mJ,
            zeeman     = False,
            sublevel   = parent.sublevel + 1,
            parent     = parent,
            split_type = "zeeman"
        )
        out.append(child)

    parent.children = out
    return out

def sideband_split(parent: Level, gap: float) -> List[Level]:
    """
    Creates two levels spaced by `gap` above and below the parent level.
    
    Parameters:
        parent (Level): The reference energy level.
        gap (float): Energy offset from the parent in cm^-1 (or whatever units parent.energy uses).
    
    Returns:
        List[Level]: Two new Level objects (upper and lower).
    """
    if gap <= 0:
        return []

    out: List[Level] = []

    # Upper level
    out.append(Level(
        label      = f"{parent.label}, blue sideband",
        energy     = parent.energy + gap,
        sideband   = None,
        sublevel   = parent.sublevel + 1,
        parent     = parent,
        split_type = "sideband"
    ))

    # Lower level
    out.append(Level(
        label      = f"{parent.label}, red sideband",
        energy     = parent.energy - gap,
        sideband   = None,
        sublevel   = parent.sublevel + 1,
        parent     = parent,
        split_type = "sideband"
    ))

    parent.children = out
    return out
