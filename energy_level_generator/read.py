"""Load Sr+ ion level data from JSON into Level objects."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from energy_level_generator.models import Level


def load_ion_data(path: str) -> dict[str, Any]:
    """
    Read sr_plus_data.json and return a dict ready for plot_energy_levels.

    Returns:
        {
            "title": str,
            "ion": str,
            "unit": str,
            "levels": list[Level],
            "transitions": list[dict],
        }
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
