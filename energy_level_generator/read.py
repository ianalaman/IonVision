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
"""Utility to load Sr+ ion level data from JSON into Level objects."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from energy_level_generator.models import Level


def load_ion_data(path: str) -> dict[str, Any]:
    """Load ion data from a JSON file for plotting.

    Reads the JSON at `path` and constructs Level instances.

    Args:
        path: Path to the JSON file.

    Returns:
        A dictionary with keys:
            - title (str): Plot title.
            - ion (str): Ion label.
            - unit (str): Energy unit.
            - levels (list[Level]): Energy levels as Level objects.
            - transitions (list[dict]): Optional transition definitions.
    """
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    levels = [Level(**entry) for entry in raw["levels"]]
    return {
        "title": raw.get("title", ""),
        "ion": raw["ion"],
        "unit": raw["unit"],
        "levels": levels,
        "transitions": raw.get("transitions", []),
    }
