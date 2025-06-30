import json
from pathlib import Path
from week3.models import Level

def load_ion_data(path: str) -> dict:
    """
    Reads sr_plus_data.json and returns a dict ready for plot_energy_levels:
      {
        "ion": str,
        "unit": str,
        "levels": List[Level],
        "transitions": List[dict]
      }
    """
    raw = json.loads(Path(path).read_text())
    levels = [Level(**entry) for entry in raw["levels"]]
    return {
        "ion":         raw["ion"],
        "unit":        raw["unit"],
        "levels":      levels,
        "transitions": raw.get("transitions", [])
    }