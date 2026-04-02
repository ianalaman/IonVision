# ---------------------------------------------------------------------
# Copyright 2026 UK Research and Innovation, Science and Technology Facilities Council
#
# [Authors: Daisy Smith, Ian Irwan Ambak]
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ---------------------------------------------------------------------
# format.py
"""
Formatting helpers for isotope and term labels for matplotlib mathtext.

Example:
 format_ion_label("88Sr+") -> "$^{88}\\mathrm{Sr}^{+}$"\n
 format_term_symbol("5s 2S1/2") -> "$\\mathrm{5s}^{2} S_{1/2}$"
"""

import re
from typing import Union
from energy_level_generator.models import Level

# Pre-compile regex patterns for performance
_ISOTOPE_RE = re.compile(r"(\d+)([A-Za-z]+)([+-]\d*|\+|-)?")
_TERM_RE = re.compile(r"(\d+)([A-Za-z])(\d+)/(\d+)")  # multiplicity, term letter, J fraction


def format_ion_label(ion: str) -> str:
    """Convert an ion string into LaTeX-like mathtext format.

    Parses an ion label like "88Sr+" into a LaTeX-compatible string
    suitable for matplotlib mathtext.

    Args:
        ion (str): Ion label in the format "<mass><element><charge>", e.g. "88Sr+".

    Returns:
        str: LaTeX mathtext string, e.g. "$^{88}\\mathrm{Sr}^{+}$".
             Returns the input unchanged if it doesn't match the expected pattern.

    Examples:
        >>> format_ion_label("88Sr+")
        '$^{88}\\mathrm{Sr}^{+}$'
    """
    m = _ISOTOPE_RE.match(ion)
    if not m:
        return ion

    isotope, element, charge = m.groups()
    charge = charge or ""
    return f"$^{{{isotope}}}\\mathrm{{{element}}}^{{{charge}}}$"


def format_term_symbol(label: Union[str, Level]) -> str:
    """Convert a term symbol into LaTeX-like mathtext format.

    Converts a term like "5s 2S1/2" or a Level object with such a label
    into a LaTeX-compatible string for matplotlib mathtext.

    Args:
        label (Union[str, Level]): Term label as a string or Level instance.
            Expected format: "<orbital> <multiplicity><term_letter><J_num>/<J_den>",
            e.g. "5s 2S1/2".

    Returns:
        str: LaTeX mathtext string, e.g. "$\\mathrm{5s}^{2} S_{1/2}$".
             Returns the input unchanged if it doesn't match the expected pattern.

    Examples:
        >>> format_term_symbol("5s 2S1/2")
        '$\\mathrm{5s}^{2} S_{1/2}$'
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
    return rf"$\mathrm{{{orb}}}^{{{multiplicity}}} {term_letter}_{{{num}/{den}}}$"
