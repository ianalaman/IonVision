# format.py

import re
from typing import Union
from .models import Level

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


def format_term_symbol(label: Union[str, Level]) -> str:
    """
    Convert a raw label like '5s 2S1/2' (or a Level instance) into a
    Matplotlib math-text string for proper typesetting, e.g. '$5\\,^{2}S_{1/2}$'.
    """
    # accept either a raw string or a Level
    text = label.label if isinstance(label, Level) else label

    parts = text.split(maxsplit=1)
    if len(parts) != 2:
        return text

    orb, term = parts
    m = _TERM_RE.match(term)
    if not m:
        return text

    multiplicity, L, num, den = m.groups()
    # produce something like "$5\,^{2}S_{1/2}$"
    return f"${orb}\\,^{multiplicity}{L}_{{{num}/{den}}}$"
