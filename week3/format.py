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


import re
from typing import Union
from models import Level

# regex to pull out multiplicity, term letter, numerator & denominator
_TERM_RE = re.compile(r"(\d+)([A-Za-z])(\d+)/(\d+)")

# maps for superscript & subscript digits
_SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
_SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

def format_term_symbol(label: Union[str, Level]) -> str:
    """
    Convert a raw label like '5s 2S1/2' (or a Level instance) into
    a Unicode string like '5²S₁∕₂' (no mathtext).
    """
    text = label.label if isinstance(label, Level) else label
    parts = text.split(maxsplit=1)
    if len(parts) != 2:
        return text

    orb, term = parts
    m = _TERM_RE.match(term)
    if not m:
        return text

    multiplicity, L, num, den = m.groups()
    sup = multiplicity.translate(_SUP)
    sub_num = num.translate(_SUB)
    sub_den = den.translate(_SUB)

    # Use U+2044 FRACTION SLASH (⁄) as subscript for a more fraction-like appearance
    frac_slash_sub = "\u2044".translate(_SUB)
    return f"{orb}{sup}{L}{sub_num}{frac_slash_sub}{sub_den}"
