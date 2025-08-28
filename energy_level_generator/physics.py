# physics.py
"""
Physics utilities for atomic energy-level calculations.

Example:
    lande\_g\_factor(L=1, S=1/2, J=3/2) -> 1.3333\n
    zeeman\_sublevels("2P3/2", B=1.0) -> \[(-3/2, ΔE), (-1/2, ΔE), (1/2, ΔE), (3/2, ΔE)]\n
    sideband\_splitting(E0=100.0, spacing=1.2) -> {"red": 98.8, "blue": 101.2}

"""


import re
import numpy as np
from typing import List
from scipy.constants import physical_constants, h, c
from energy_level_generator.models import Level
from fractions import Fraction

# Physical constants: used in Zeeman shift calculation
mu_B = physical_constants["Bohr magneton"][0]  # Bohr magneton (J/T)
hc = h * c  # Planck constant × speed of light (J·m)


def lande_g_factor(L: float, S: float, J: float) -> float:
    """Compute Landé g-factor g_J for LS coupling.

    g_J = 3/2 + [S(S+1) - L(L+1)] / [2 J (J+1)]

    Args:
        L: Orbital angular momentum quantum number.
        S: Spin quantum number.
        J: Total angular momentum quantum number (>0).

    Returns:
        Landé g-factor.

    Raises:
        ValueError: If J <= 0.
    """
    if J <= 0:
        raise ValueError("J must be positive for Landé g-factor.")
    return 1.5 + (S * (S + 1) - L * (L + 1)) / (2 * J * (J + 1))


def zeeman_split(parent: Level, B: float) -> List[Level]:
    """Generate Zeeman-split sublevels for a given magnetic field.

    Parses the term from the second token of parent.label (e.g. "2P3/2").
    Creates sublevels with equally spaced m_j values.

    Args:
        parent: Level to split; must have zeeman=True.
        B: Magnetic field strength in Tesla.

    Returns:
        List of new sublevels with m_j labels and shifted energies.
        Returns [] if disabled, invalid label, or B <= 0.
    """
    if not getattr(parent, "zeeman", False) or B <= 0:
        return []

    tokens = (parent.label or "").split()
    if len(tokens) < 2:
        return []

    term = tokens[1]
    # Expect format like "2P3/2": multiplicity, letter, J numerator/denominator
    m = re.match(r"^\s*(\d+)\s*([A-Za-z])\s*(\d+)\s*/\s*(\d+)\s*$", term)
    if not m:
        return []

    mult_s, Lsym, num_s, den_s = m.groups()
    mult, num, den = int(mult_s), int(num_s), int(den_s)

    # Map letter to L index (supports S,P,D,F,... up to N)
    Lsym = Lsym.upper()
    Lseries = "SPDFGHIKLMN"
    if Lsym not in Lseries:
        return []
    L = Lseries.index(Lsym)

    J = Fraction(num, den)
    if J <= 0:
        return []

    S = Fraction(mult - 1, 2)
    gJ = lande_g_factor(float(L), float(S), float(J))

    # Energy shift coefficient: convert from m^-1 to cm^-1
    conv = (gJ * mu_B * B) / hc * 1e-2

    # m_j values: -J, -J+1, ..., +J
    mJ_values = [(-J + i) for i in range(int(2 * J) + 1)]

    children: List[Level] = []
    for mJ in mJ_values:
        # Format m_j with explicit sign
        s = str(mJ)
        if not s.startswith("-"):
            s = "+" + s
        children.append(
            Level(
                label=f"{parent.label}, m_j={s}",
                energy=parent.energy + conv * float(mJ),
                zeeman=False,
                sublevel=(parent.sublevel or 0) + 1,
                parent=parent,
                split_type="zeeman",
            )
        )

    parent.children = children
    return children


def sideband_split(parent: Level, gap: float) -> List[Level]:
    """Generate blue/red motional sidebands around a parent level.

    Args:
        parent: Reference level.
        gap: Energy offset (same units as parent.energy). Must be > 0.

    Returns:
        Two sideband levels (blue above, red below). Returns [] if gap <= 0.
    """
    if gap <= 0:
        return []

    out: List[Level] = [
        Level(
            label=f"{parent.label}, blue sideband",
            energy=parent.energy + gap,
            sideband=None,
            sublevel=(parent.sublevel or 0) + 1,
            parent=parent,
            split_type="sideband",
        ),
        Level(
            label=f"{parent.label}, red sideband",
            energy=parent.energy - gap,
            sideband=None,
            sublevel=(parent.sublevel or 0) + 1,
            parent=parent,
            split_type="sideband",
        ),
    ]
    parent.children = out
    return out
