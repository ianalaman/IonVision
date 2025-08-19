"""Splitting kernels for energy level trees: Zeeman, sideband, hyperfine.

This module defines small, focused splitter classes that take a ``Level`` and add
physically motivated sub-structure under it. Classes are designed to be imported
and composed by a higher-level builder.

Pylint notes:
- These classes intentionally expose few public methods; we disable the
  ``too-few-public-methods`` warning per class to keep the API compact.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Optional, Tuple
import re

from energy_level_generator.models import Level
from energy_level_generator.physics import zeeman_split

# -----------------------------------------------------------------------------
# Base interface
# -----------------------------------------------------------------------------


class Splitter:  # pylint: disable=too-few-public-methods
    """Abstract protocol for a splitting kernel."""

    name: str

    def split(self, lvl: Level) -> List[Level]:  # pragma: no cover - interface only
        """Given one ``Level``, return the created children or ``[]``.

        Implementations typically also append the new children to ``lvl.children``
        and wire ``parent``/``sublevel``/``split_type`` fields.
        """
        raise NotImplementedError


# -----------------------------------------------------------------------------
# Zeeman
# -----------------------------------------------------------------------------


class ZeemanSplitter(Splitter):  # pylint: disable=too-few-public-methods
    """Zeeman splitting wrapper around ``physics.zeeman_split``.

    Parameters
    ----------
    b_tesla : float
        Magnetic field strength (Tesla).
    """

    name = "zeeman"

    def __init__(self, b_tesla: float) -> None:
        self.b_tesla = float(b_tesla)

    def split(self, lvl: Level) -> List[Level]:
        # Only split if this level is flagged for Zeeman and B>0
        if not getattr(lvl, "zeeman", False) or self.b_tesla <= 0:
            return []

        # Delegate to physics. Expecting ``List[Level]`` back.
        children = zeeman_split(lvl, self.b_tesla)

        # Wire tree info
        for child in children:
            child.sublevel = (lvl.sublevel or 0) + 1
            child.parent = lvl
            child.split_type = self.name
            # Prevent further Zeeman on sub-levels by default
            child.zeeman = False

        lvl.children = children
        return children


# -----------------------------------------------------------------------------
# Sidebands (e.g., motional sidebands around a parent line)
# -----------------------------------------------------------------------------


class SidebandSplitter(Splitter):  # pylint: disable=too-few-public-methods
    """Create red/blue sideband children around selected parent levels.

    If ``base.sideband`` is a mapping with key ``"m_j"`` listing target values
    (strings like ``"-5/2"``), the sidebands are attached to the matching Zeeman
    child(ren) whose label contains ``m_j=...``. Otherwise, sidebands are attached
    to ``base`` itself.
    """

    name = "sideband"

    def __init__(
        self,
        gap: float = 100.0,
        label_suffixes: Tuple[str, str] = ("red sideband", "blue sideband"),
    ) -> None:
        self.gap = float(gap)
        self.label_suffixes = label_suffixes  # [lower, higher]

    @staticmethod
    def _match_mj(child: Level, mj_str: str) -> bool:
        """Return True if ``child.label`` contains ``m_j={mj_str}``.

        Avoids exceptions by normalizing to an empty string when label is ``None``.
        """
        needle = f"m_j={mj_str}"
        hay = child.label or ""
        return needle in hay

    def split(
        self, base: Level, zeeman_children: Optional[List[Level]] = None
    ) -> List[Level]:
        # pylint: disable=too-many-locals
        """Create sideband children and append them under the chosen parents.

        Parameters
        ----------
        base : Level
            The candidate parent level.
        zeeman_children : Optional[List[Level]]
            If provided and ``base.sideband`` specifies particular ``m_j`` values,
            attach sidebands to those Zeeman children instead of ``base``.
        """
        if not getattr(base, "sideband", None):
            return []

        targets: List[Level] = []
        mj_list: List[str] = []

        sideband_cfg = base.sideband if isinstance(base.sideband, dict) else {}
        if isinstance(sideband_cfg, dict) and "m_j" in sideband_cfg:
            mj_list = list(sideband_cfg["m_j"])  # strings like "-5/2"

        if zeeman_children and mj_list:
            for mj in mj_list:
                match = next(
                    (c for c in zeeman_children if self._match_mj(c, mj)), None
                )
                if match:
                    targets.append(match)

        if not targets:
            targets = [base]

        kids: List[Level] = []
        offsets = (-self.gap, self.gap)
        suffixes = self.label_suffixes

        for parent in targets:
            sublevel_idx = (parent.sublevel or 0) + 1
            for offset, suffix in zip(offsets, suffixes):
                child = Level(
                    label=f"{parent.label}, {suffix}",
                    energy=parent.energy + offset,
                    zeeman=False,
                    sideband=None,
                    sublevel=sublevel_idx,
                    parent=parent,
                    split_type=self.name,
                    children=[],
                    meta=dict(parent.meta or {}),  # inherit meta (e.g., m_j)
                )
                parent.children.append(child)
                kids.append(child)

        return kids


# -----------------------------------------------------------------------------
# Hyperfine structure
# -----------------------------------------------------------------------------

_MHZ_TO_CM1 = 1.0e6 * 3.335_640_951_981_52e-11  # Hz->cm^-1, then MHz = 1e6 Hz
_J_RE = re.compile(r"\b(\d+)([SPDFGHI])([1-9]/2|\d)\b", re.I)  # "2S1/2", "2D3/2", ...


def _parse_j_from_label(label: Optional[str]) -> Optional[float]:
    """Extract J from something like '4s  2S1/2' (second token)."""
    if not label:
        return None
    toks = label.split()
    if len(toks) < 2:
        return None
    term = toks[1]  # e.g., '2S1/2'
    match = _J_RE.search(term)
    if not match:
        return None
    j_text = match.group(3)  # '1/2' or integer
    try:
        return float(Fraction(j_text))
    except (ValueError, ZeroDivisionError):
        return None


def _allowed_f_values(i_nuc: float, j_val: float) -> List[float]:
    """Return the list of F values from |I−J| to I+J in unit steps."""
    f_min, f_max = abs(i_nuc - j_val), i_nuc + j_val
    count = int(round((f_max - f_min) + 1))
    return [f_min + i for i in range(count)]


def _cm1_from_mhz(x_mhz: Optional[float]) -> float:
    """Convert MHz to cm^-1 (0.0 if ``None``)."""
    if x_mhz in (None, 0):
        return 0.0
    return float(x_mhz) * _MHZ_TO_CM1


class HyperfineSplitter(Splitter):  # pylint: disable=too-few-public-methods
    """Build hyperfine F and (optionally) m_F sublevels for a base J-level.

    Zero-field energy shift for a given F:

        K = F(F+1) − I(I+1) − J(J+1)\\
        E = (A/2)·K + B·[ 3/4·K(K+1) − I(I+1)J(J+1) ] / [ 2I(2I−1)·2J(2J−1) ]

    A and B are given in MHz and converted internally to cm^-1. At B=0, m_F
    sublevels are degenerate with their F parent level.

    Per-level options (typically via ``Level.meta``):
        - ``I`` (required to enable hyperfine),
        - ``A_MHz`` / ``B_MHz`` (overrides),
        - ``magnifier`` (visual scale, default 1),
        - ``make_mF`` (bool),
        - ``F_colors``: optional mapping of F (as string) to a CSS color.
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
    ) -> None:  # pylint: disable=too-many-arguments
        self.i_nuc = float(i_nuc)
        self.a_mhz = a_mhz
        self.b_mhz = b_mhz
        self.make_mf = bool(make_mf)
        self.magnifier = float(magnifier)
        self.f_colors = f_colors or {}

    # --- hook to fill A/B if not overridden (stub you can route to OITG later) ---
    def _fetch_a_b_if_needed(
        self,
        _element: Optional[str],
        _isotope: Optional[int],
        _term: Optional[str],
    ) -> Tuple[float, float]:
        """Return (A_MHz, B_MHz).

        If overrides are set on the instance, keep them. This stub returns (0, 0)
        if nothing is known; wire to a proper database as needed.
        """
        a_val = self.a_mhz if self.a_mhz is not None else 0.0
        b_val = self.b_mhz if self.b_mhz is not None else 0.0
        return float(a_val), float(b_val)

    @staticmethod
    def _delta_cm1(
        f_val: float, j_val: float, a_cm1: float, b_cm1: float, i_nuc: float
    ) -> float:
        """Hyperfine energy offset (cm^-1) for a given F at B=0."""
        k_val = f_val * (f_val + 1.0) - i_nuc * (i_nuc + 1.0) - j_val * (j_val + 1.0)
        energy = 0.5 * a_cm1 * k_val
        if b_cm1 != 0.0 and (j_val > 0.5) and (i_nuc > 0.5):
            denom = (2 * i_nuc * (2 * i_nuc - 1.0)) * (2 * j_val * (2 * j_val - 1.0))
            if denom != 0.0:
                num = 0.75 * k_val * (k_val + 1.0) - i_nuc * (i_nuc + 1.0) * j_val * (
                    j_val + 1.0
                )
                energy += b_cm1 * (num / denom)
        return energy

    def split(self, base: Level) -> List[Level]:  # pylint: disable=too-many-locals
        """Create hyperfine F (and optional m_F) children under ``base``.

        Only operates on base levels (``sublevel == 0``). Returns the list of
        newly created ``Level`` objects and appends them to ``base.children``.
        """
        if getattr(base, "sublevel", 0) != 0:
            return []

        meta = base.meta or {}
        element = meta.get("element")
        isotope = meta.get("isotope")
        term = meta.get("term")
        if term is None and base.label:
            parts = base.label.split()
            if len(parts) >= 2:
                term = parts[1]

        j_val_opt = meta.get("J")
        j_val = (
            float(Fraction(str(j_val_opt))) if j_val_opt is not None else _parse_j_from_label(base.label)
        )
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
                meta={
                    **meta,
                    "I": self.i_nuc,
                    "J": j_val,
                    "F": f_val,
                    "A_MHz": a_mhz,
                    "B_MHz": b_mhz,
                    "magnifier": self.magnifier,
                    "term": term,
                    "element": element,
                    "isotope": isotope,
                    "color": self.f_colors.get(str(int(f_val))),
                },
            )
            base.children.append(f_level)
            kids.append(f_level)

            if self.make_mf:
                # mF values: -F, -F+1, ..., +F (half-integers allowed)
                m2_min, m2_max = int(round(-2 * f_val)), int(round(2 * f_val))
                for m2 in range(m2_min, m2_max + 1, 2):
                    m_f = m2 / 2.0
                    mf_label = f"{f_label}, m_f={m_f:g}"
                    mf_level = type(base)(
                        label=mf_label,
                        energy=energy_f,  # B=0 → degenerate
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
