import json

def load_ion_levels(path):
    """
    Load ion energy level and transition data from a JSON file.

    Args:
        path (str): Path to the JSON file.

    Returns:
        dict: Parsed JSON data as a Python dictionary.
    """
    with open(path, "r") as f:
        data = json.load(f)
    return data

"""
Example JSON file content:
    {
        "ion": "88Sr+",
        "levels": [
            {"label": "5s 2S1/2", "energy": 0},
            {"label": "5p 2P1/2", "energy": 23715.19}
        ],
        "transitions": [
            {
                "from": "5s 2S1/2",
                "to": "5p 2P1/2",
                "wavelength": 422,
                "label": "Doppler cooling",
                "color": "blue"
            }
        ]
    }

    Example output:
    {
        'ion': '88Sr+',
        'levels': [{'label': '5s 2S1/2', 'energy': 0}, ...],
        'transitions': [{'from': '5s 2S1/2', 'to': '5p 2P1/2', ...}]
    }
"""