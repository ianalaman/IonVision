# format.py
"""
Formatting helpers for isotope/term labels for matplotlib mathtext.

- format_ion_label("88Sr+") -> "$^{88}\\mathrm{Sr}^{+}$"
- format_term_symbol("5s 2S1/2") -> "$\\mathrm{5s}^{2} S_{1/2}$"
"""

import re
from typing import Union
from energy_level_generator.models import Level

# Pre-compile regex patterns
_ISOTOPE_RE = re.compile(r"(\d+)([A-Za-z]+)([+-]\d*|\+|-)?")
_TERM_RE    = re.compile(r"(\d+)([A-Za-z])(\d+)/(\d+)")  # multiplicity, term letter, J numerator/denominator


def format_ion_label(ion: str) -> str:
    """
    Convert '88Sr+' into LaTeX-like mathtext: '$^{88}\\mathrm{Sr}^{+}$'.
    """
    m = _ISOTOPE_RE.match(ion)
    if not m:
        return ion

    isotope, element, charge = m.groups()
    charge = charge or ""
    return f"$^{{{isotope}}}\\mathrm{{{element}}}^{{{charge}}}$"


def format_term_symbol(label: Union[str, Level]) -> str:
    """
    Convert '5s 2S1/2' (or Level.label) into a single mathtext string,
    e.g. '$\\mathrm{5s}^{2} S_{1/2}$'.
    """
    text = label.label if isinstance(label, Level) else label
    parts = text.split(maxsplit=1)
    if len(parts) != 2:
        return text

    orb, term = parts
    m = _TERM_RE.match(term)
    if not m:
        return text

    multiplicity, term_letter, num, den = m.groups()

    math = (
        r"$"
        rf"\mathrm{{{orb}}}^{{{multiplicity}}} {term_letter}_{{{num}/{den}}}"
        r"$"
    )
    return math
