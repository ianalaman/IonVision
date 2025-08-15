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
# --- add near the top of splitters.py ---
from dataclasses import replace
from fractions import Fraction
from typing import List, Optional
from energy_level_generator.models import Level

# MHz → cm^-1  (1 cm^-1 ≈ 29.9792458 GHz)
_MHZ_TO_CM1 = 1.0e6 / 2.99792458e10

def _parse_J_from_label(label: str) -> Optional[float]:
    """
    label like '5s  2S1/2' → J = 1/2
    Works even if you append ', F=...' later because we only read token[1].
    """
    try:
        term = (label or "").split()[1]           # '2S1/2' or '2D5/2'
    except IndexError:
        return None
    # find trailing fractional number after spectroscopic letter
    import re
    m = re.search(r'[SPDFGIH]\s*(\d+(?:/\d+)?)$', term)
    if not m:
        return None
    return float(Fraction(m.group(1)))

class HyperfineSplitter:
    """
    Make hyperfine F-levels from a base J-level, and optionally m_F sublevels.

    Energies use the Breit-Rabi (weak-field, zero B) hyperfine shift:
      K = F(F+1) - I(I+1) - J(J+1)
      E_HFS = (A/2) * K + B * [ 3/4 K(K+1) - I(I+1)J(J+1) ] / [ 2I(2I-1) 2J(2J-1) ]

    A, B given in MHz; output ΔE added in cm^-1 to the parent energy.
    If B is None or the denominator vanishes (I<1 or J<1), the B term is skipped.
    """

    def __init__(self, I: float, A_MHz: float, B_MHz: Optional[float] = None, make_mF: bool = True):
        self.I = float(I)
        self.A = float(A_MHz)
        self.B = None if B_MHz is None else float(B_MHz)
        self.make_mF = bool(make_mF)

    def _delta_cm1(self, F: float, J: float) -> float:
        I = self.I
        K = F*(F+1) - I*(I+1) - J*(J+1)
        A_term = 0.5 * self.A * K
        B_term = 0.0
        if self.B not in (None, 0.0):
            denom = (2*I*(2*I-1)) * (2*J*(2*J-1))
            if denom != 0.0:
                B_term = self.B * ( (0.75*K*(K+1) - I*(I+1)*J*(J+1)) / denom )
        return (A_term + B_term) * _MHZ_TO_CM1

    def _F_values(self, J: float) -> List[float]:
        I = self.I
        Fmin, Fmax = abs(I - J), I + J
        # step by 1, but allow half-integers
        n = int(round((Fmax - Fmin) + 1))
        return [Fmin + i for i in range(n)]

    def split(self, base: Level) -> List[Level]:
        # Only split base J-levels (sublevel==0). If you want to allow splitting an
        # already-split level, drop this check.
        if getattr(base, "sublevel", 0) != 0:
            return []

        # prefer J from metadata if present
        J = None
        if base.meta and "J" in base.meta:
            try:
                J = float(Fraction(str(base.meta["J"])))
            except Exception:
                J = None
        if J is None:
            J = _parse_J_from_label(base.label)
        if J is None:
            return []  # can't determine J → no split

        kids: List[Level] = []
        for F in self._F_values(J):
            dE = self._delta_cm1(F, J)
            F_lbl = f"{base.label}, F={F:g}"
            F_level = Level(
                label      = F_lbl,
                energy     = base.energy + dE,
                zeeman     = False,
                sideband   = None,
                sublevel   = 1,                 # one deeper than base
                parent     = base,
                split_type = "hyperfine",
                children   = [],
                meta       = {**getattr(base, "meta", {}), "I": self.I, "J": J, "F": F},
            )
            base.children.append(F_level)
            kids.append(F_level)

            if self.make_mF:
                mF_vals = [m for m in range(-int(round(2*F)), int(round(2*F))+1, 2)]
                # convert integer steps in 2m to half-integers
                for m2 in mF_vals:
                    m = m2 / 2.0
                    m_lbl = f"{F_lbl}, m_f={m:g}"
                    m_level = Level(
                        label      = m_lbl,
                        energy     = F_level.energy,   # zero-field: all m_F degenerate
                        zeeman     = False,
                        sideband   = None,
                        sublevel   = 2,
                        parent     = F_level,
                        split_type = "hyperfine_mF",
                        children   = [],
                        meta       = {**F_level.meta, "m_f": m},
                    )
                    F_level.children.append(m_level)
                    kids.append(m_level)
        return kids
