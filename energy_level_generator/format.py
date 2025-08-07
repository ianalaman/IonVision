# format.py

import re
from typing import Union
from models import Level

# Pre-compile regex patterns for efficiency
_ISOTOPE_RE = re.compile(r"(\d+)([A-Za-z]+)([+-]\d*|\+|-)?")
_TERM_RE    = re.compile(r"(\d)([SPDF])(\d)/(\d)")


def format_ion_label(ion: str) -> str:
    """
    Convert a string like '88Sr+' into a LaTeX-formatted
    superscript label for matplotlib, e.g. '$^{88}\\mathrm{Sr}^{+}$'.
    """
    m = _ISOTOPE_RE.match(ion)
    if not m:
        return ion

    isotope, element, charge = m.groups()
    charge = charge or ""
    # produce something like "$^{88}\mathrm{Sr}^{+}$"
    return f"$^{{{isotope}}}\\mathrm{{{element}}}^{{{charge}}}$"


# regex to pull out multiplicity, term letter, numerator & denominator
_TERM_RE = re.compile(r"(\d+)([A-Za-z])(\d+)/(\d+)")

def format_term_symbol(label: Union[str, Level]) -> str:
    """
    Convert '5s 2S1/2' (or a Level) into a single math‐text string,
    e.g. '$5s^{2}S_{\\tfrac{1}{2}}$'.
    """
    text = label.label if isinstance(label, Level) else label
    parts = text.split(maxsplit=1)
    if len(parts) != 2:
        return text  # nothing to format

    orb, term = parts
    m = _TERM_RE.match(term)
    if not m:
        return text  # doesn’t match our pattern

    multiplicity, L, num, den = m.groups()

    # Build a pure‐mathtext string:
    #  - \mathrm{5s} makes "5s" upright
    #  - ^{2}S gives the term symbol multiplicity
    #  - _{\frac{1}{2}} gives a small built‐in fraction in the subscript (mathtext supports \frac)
    math = (
        r"$"
        rf"\mathrm{{{orb}}}^{{{multiplicity}}} {L}_{{{num}/{den}}}"
        r"$"
    )
    return math
