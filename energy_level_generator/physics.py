# physics.py
"""
Physics utilities for atomic and molecular energy-level manipulations.

This module provides helper functions to:
  * Compute the Landé g-factor for LS-coupled states.
  * Generate Zeeman-split sublevels of a parent `Level` at a given magnetic field.
  * Generate motional sideband levels above and below a parent `Level`.

Conventions:
    * `Level.label` should have its second token as the spectroscopic term,
      e.g., "2P3/2" (multiplicity, term letter, and J in fraction form).
    * Energies are assumed consistent across your pipeline (e.g., in cm^-1).
      `zeeman_split` converts μ_B B / (h c) into the same units.
    * Zeeman sublevels are labeled with explicit signed m_j values (e.g., +3/2).
    * Sidebands are labeled as "blue sideband" (above) and "red sideband" (below).

Examples:
    >>> lande_g_factor(L=1, S=0.5, J=1.5)
    1.3333333333333333

    >>> children = zeeman_split(parent, B=1.0)  # Tesla
    >>> [c.label for c in children]
    ['<parent>, m_j=-3/2', '<parent>, m_j=-1/2', '<parent>, m_j=+1/2', '<parent>, m_j=+3/2']

    >>> sidebands = sideband_split(parent, gap=0.5)
    >>> [s.label for s in sidebands]
    ['<parent>, blue sideband', '<parent>, red sideband']
"""

import re
import numpy as np
from typing import List
from scipy.constants import physical_constants, h, c

from energy_level_generator.models import Level
from fractions import Fraction

μB = physical_constants["Bohr magneton"][0]
hc = h * c

def lande_g_factor(L: float, S: float, J: float) -> float:
    """Compute the Landé g-factor in LS coupling.

    Uses:
        g_J = 3/2 + [S(S+1) − L(L+1)] / [2 J (J+1)]

    Args:
        L (float): Orbital angular momentum quantum number.
        S (float): Spin quantum number.
        J (float): Total angular momentum quantum number (must be > 0).

    Returns:
        float: Landé g-factor g_J.

    Raises:
        ValueError: If `J <= 0`.
    """
    if J <= 0:
        raise ValueError("J must be positive for Landé g-factor.")
    return 1.5 + (S * (S + 1.0) - L * (L + 1.0)) / (2.0 * J * (J + 1.0))


def zeeman_split(parent: Level, B: float) -> List[Level]:
    """Generate Zeeman sublevels for a parent level at magnetic field `B`.

    The parent label must contain a spectroscopic term as its second token,
    e.g. "... 2P3/2 ...". Sublevels are created for all m_J in {-J, -J+1, …, J}
    with energies:
        E_m = E_parent + (g_J μ_B B / (h c)) * m_J
    returned in cm^{-1} if `parent.energy` is in cm^{-1}.

    Args:
        parent (Level): Parent level to split. Requires `parent.zeeman` truthy.
        B (float): Magnetic field strength in Tesla. No splitting if `B <= 0`.

    Returns:
        List[Level]: Newly created Zeeman sublevels, or an empty list if disabled,
            unparsable term, or `B <= 0`.

    Notes:
        * Sets `split_type="zeeman"`, increments `sublevel`, and sets `parent`.
        * Populates `parent.children` with the returned list.
        * m_J labels use explicit signs with rational formatting (e.g., +3/2).
    """
    if not getattr(parent, "zeeman", False) or B <= 0:
        return []

    tokens = (parent.label or "").split()
    if len(tokens) < 2:
        return []

    term = tokens[1]
    m = re.match(r"^\s*(\d+)\s*([A-Za-z])\s*(\d)\s*/\s*(\d)\s*$", term)
    if not m:
        return []

    mult_s, Lsym, num_s, den_s = m.groups()
    mult, num, den = int(mult_s), int(num_s), int(den_s)

    Lmap = {"S": 0, "P": 1, "D": 2, "F": 3}
    Lsym = Lsym.upper()
    if Lsym not in Lmap:
        return []

    J = Fraction(num, den)
    if J <= 0:
        return []

    S = Fraction(mult - 1, 2)
    L = Lmap[Lsym]
    gJ = lande_g_factor(L=float(L), S=float(S), J=float(J))

    # (gJ μB B)/(h c) has units of 1/m; convert to 1/cm by multiplying by 1e-2
    conv = (gJ * μB * B) / hc * 1e-2

    children: List[Level] = []
    for k in range(-num, num + 1):
        mJ = Fraction(k, den)
        s = str(mJ)
        if not s.startswith("-"):
            s = "+" + s
        child = Level(
            label=f"{parent.label}, m_j={s}",
            energy=parent.energy + conv * float(mJ),
            zeeman=False,
            sublevel=(parent.sublevel or 0) + 1,
            parent=parent,
            split_type="zeeman",
        )
        children.append(child)

    parent.children = children
    return children


def sideband_split(parent: Level, gap: float) -> List[Level]:
    """Create blue/red sidebands separated by `gap` around a parent level.

    Args:
        parent (Level): Reference level.
        gap (float): Energy offset relative to the parent (same units as
            `parent.energy`). Must be positive.

    Returns:
        List[Level]: Two new levels (blue above, red below). Empty list if `gap <= 0`.

    Notes:
        * Labels: "<parent.label>, blue sideband" and "... red sideband".
        * Sets `split_type="sideband"`, increments `sublevel`, sets `parent`.
        * Populates `parent.children` with the returned list.
    """
    if gap <= 0:
        return []

    out: List[Level] = []

    out.append(
        Level(
            label=f"{parent.label}, blue sideband",
            energy=parent.energy + gap,
            sideband=None,
            sublevel=(parent.sublevel or 0) + 1,
            parent=parent,
            split_type="sideband",
        )
    )

    out.append(
        Level(
            label=f"{parent.label}, red sideband",
            energy=parent.energy - gap,
            sideband=None,
            sublevel=(parent.sublevel or 0) + 1,
            parent=parent,
            split_type="sideband",
        )
    )

    parent.children = out
    return out
