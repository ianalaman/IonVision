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
