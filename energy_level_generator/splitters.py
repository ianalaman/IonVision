"""Splitting kernels for energy level trees: Zeeman, sideband, hyperfine.

Provides splitter classes that generate physically motivated sub-structures
under a Level. These are intended to be composed by a higher-level builder.
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, List, Optional, Tuple
import re

from energy_level_generator.models import Level
from energy_level_generator.physics import zeeman_split


class Splitter:  # pylint: disable=too-few-public-methods
    """Abstract base interface for all splitting kernels."""

    name: str

    def split(self, lvl: Level) -> List[Level]:
        """Split a level into children. Must be implemented by subclasses."""
        raise NotImplementedError


class ZeemanSplitter(Splitter):  # pylint: disable=too-few-public-methods
    """Zeeman splitter using physics.zeeman_split.

    Args:
        b_tesla: Magnetic field strength in Tesla.
    """

    name = "zeeman"

    def __init__(self, b_tesla: float) -> None:
        self.b_tesla = float(b_tesla)

    def split(self, lvl: Level) -> List[Level]:
        """Generate Zeeman children for a Level if enabled and B > 0."""
        if not getattr(lvl, "zeeman", False) or self.b_tesla <= 0:
            return []
        children = zeeman_split(lvl, self.b_tesla)
        for child in children:
            child.sublevel = (lvl.sublevel or 0) + 1
            child.parent = lvl
            child.split_type = self.name
            child.zeeman = False  # disable recursive Zeeman
        lvl.children = children
        return children


class SidebandSplitter(Splitter):  # pylint: disable=too-few-public-methods
    """Generate red/blue motional sidebands around selected levels.

    Args:
        gap: Energy gap for sidebands (same units as energy).
        label_suffixes: Tuple of suffix labels for (lower, higher).
    """

    name = "sideband"

    def __init__(
        self,
        gap: float = 100.0,
        label_suffixes: Tuple[str, str] = ("red sideband", "blue sideband"),
    ) -> None:
        self.gap = float(gap)
        self.label_suffixes = label_suffixes

    @staticmethod
    def _match_mj(child: Level, mj_str: str) -> bool:
        """True if child.label contains m_j={mj_str}."""
        return f"m_j={mj_str}" in (child.label or "")

    def split(
        self, base: Level, zeeman_children: Optional[List[Level]] = None
    ) -> List[Level]:
        """Attach sidebands to base or specified Zeeman children."""
        if not getattr(base, "sideband", None):
            return []

        sideband_cfg = base.sideband if isinstance(base.sideband, dict) else {}
        mj_list = list(sideband_cfg.get("m_j", [])) if isinstance(sideband_cfg, dict) else []

        targets: List[Level] = []
        if zeeman_children and mj_list:
            for mj in mj_list:
                match = next((c for c in zeeman_children if self._match_mj(c, mj)), None)
                if match:
                    targets.append(match)
        if not targets:
            targets = [base]

        kids: List[Level] = []
        for parent in targets:
            sub_idx = (parent.sublevel or 0) + 1
            for offset, suffix in zip((-self.gap, self.gap), self.label_suffixes):
                child = Level(
                    label=f"{parent.label}, {suffix}",
                    energy=parent.energy + offset,
                    zeeman=False,
                    sideband=None,
                    sublevel=sub_idx,
                    parent=parent,
                    split_type=self.name,
                    children=[],
                    meta=dict(parent.meta or {}),
                )
                parent.children.append(child)
                kids.append(child)
        return kids


# Hyperfine splitting helpers/constants
_MHZ_TO_CM1 = 1.0e6 * 3.335_640_951_981_52e-11  # MHz to cm^-1
_J_RE = re.compile(r"\b(\d+)([SPDFGHI])([1-9]/2|\d)\b", re.I)


def _parse_j_from_label(label: Optional[str]) -> Optional[float]:
    """Extract J from the second token of label (e.g. '2S1/2')."""
    if not label:
        return None
    toks = label.split()
    if len(toks) < 2:
        return None
    match = _J_RE.search(toks[1])
    if not match:
        return None
    try:
        return float(Fraction(match.group(3)))
    except (ValueError, ZeroDivisionError):
        return None


def _allowed_f_values(i_nuc: float, j_val: float) -> List[float]:
    """Compute allowed F values from |I−J| to I+J."""
    f_min, f_max = abs(i_nuc - j_val), i_nuc + j_val
    return [f_min + i for i in range(int(round((f_max - f_min) + 1)))]


def _cm1_from_mhz(x_mhz: Optional[float]) -> float:
    """Convert MHz to cm^-1."""
    return 0.0 if x_mhz in (None, 0) else float(x_mhz) * _MHZ_TO_CM1


class HyperfineSplitter(Splitter):  # pylint: disable=too-few-public-methods
    """Generate hyperfine F and optional m_F sublevels.

    Args:
        i_nuc: Nuclear spin I.
        a_mhz: A constant (MHz). Overrides defaults if provided.
        b_mhz: B constant (MHz). Overrides defaults if provided.
        make_mf: If True, generate m_F sublevels.
        magnifier: Visual scale multiplier for energy offsets.
        f_colors: Optional mapping of F (string) to colors.
    """

    name = "hyperfine"

    def __init__(
        self,
        i_nuc: float,
        a_mhz: Optional[float] = None,
        b_mhz: Optional[float] = None,
        make_mf: bool = True,
        magnifier: float = 1.0,
        f_colors: Optional[Dict[str, str]] = None,
    ) -> None:
        self.i_nuc = float(i_nuc)
        self.a_mhz = a_mhz
        self.b_mhz = b_mhz
        self.make_mf = bool(make_mf)
        self.magnifier = float(magnifier)
        self.f_colors = f_colors or {}

    def _fetch_a_b_if_needed(
        self,
        _element: Optional[str],
        _isotope: Optional[int],
        _term: Optional[str],
    ) -> Tuple[float, float]:
        """Return (A_MHz, B_MHz); 0 if not provided."""
        return float(self.a_mhz or 0.0), float(self.b_mhz or 0.0)

    @staticmethod
    def _delta_cm1(
        f_val: float, j_val: float, a_cm1: float, b_cm1: float, i_nuc: float
    ) -> float:
        """Hyperfine zero-field energy offset for given F."""
        k = f_val * (f_val + 1) - i_nuc * (i_nuc + 1) - j_val * (j_val + 1)
        energy = 0.5 * a_cm1 * k
        if b_cm1 != 0.0 and (j_val > 0.5) and (i_nuc > 0.5):
            denom = (2 * i_nuc * (2 * i_nuc - 1)) * (2 * j_val * (2 * j_val - 1))
            if denom != 0.0:
                num = 0.75 * k * (k + 1) - i_nuc * (i_nuc + 1) * j_val * (j_val + 1)
                energy += b_cm1 * (num / denom)
        return energy

    def split(self, base: Level) -> List[Level]:
        """Generate hyperfine children (F and optional m_F) for a base level."""
        if getattr(base, "sublevel", 0) != 0:
            return []

        meta = base.meta or {}
        element = meta.get("element")
        isotope = meta.get("isotope")
        term = meta.get("term") or (base.label.split()[1] if base.label and len(base.label.split()) >= 2 else None)

        j_val_opt = meta.get("J")
        j_val = float(Fraction(str(j_val_opt))) if j_val_opt is not None else _parse_j_from_label(base.label)
        if j_val is None:
            return []

        a_mhz, b_mhz = self._fetch_a_b_if_needed(element, isotope, term)
        a_cm1 = _cm1_from_mhz(a_mhz)
        b_cm1 = _cm1_from_mhz(b_mhz)

        kids: List[Level] = []
        for f_val in _allowed_f_values(self.i_nuc, j_val):
            delta_e = self._delta_cm1(f_val, j_val, a_cm1, b_cm1, self.i_nuc)
            energy_f = base.energy + delta_e * self.magnifier
            f_label = f"{base.label}, F={f_val:g}"
            f_level = type(base)(
                label=f_label,
                energy=energy_f,
                zeeman=False,
                sideband=None,
                sublevel=1,
                parent=base,
                split_type=self.name,
                children=[],
                meta={**meta,
                      "I": self.i_nuc,
                      "J": j_val,
                      "F": f_val,
                      "A_MHz": a_mhz,
                      "B_MHz": b_mhz,
                      "magnifier": self.magnifier,
                      "term": term,
                      "element": element,
                      "isotope": isotope,
                      "color": self.f_colors.get(str(int(f_val)))},
            )
            base.children.append(f_level)
            kids.append(f_level)

            if self.make_mf:
                m2_min, m2_max = int(round(-2 * f_val)), int(round(2 * f_val))
                for m2 in range(m2_min, m2_max + 1, 2):
                    m_f = m2 / 2.0
                    mf_label = f"{f_label}, m_f={m_f:g}"
                    mf_level = type(base)(
                        label=mf_label,
                        energy=energy_f,
                        zeeman=False,
                        sideband=None,
                        sublevel=2,
                        parent=f_level,
                        split_type="hyperfine_mF",
                        children=[],
                        meta={**f_level.meta, "m_f": m_f},
                    )
                    f_level.children.append(mf_level)
                    kids.append(mf_level)
        return kids
