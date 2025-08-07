# ===== pulseplot/io.py =====
"""
Input/output utilities: save or load sequences to/from JSON or other formats.
"""
import json
from core import Sequence, Pulse


def save_sequence_json(seq: Sequence, filename: str) -> None:
    """
    Save a Sequence to a JSON file.

    Parameters
    ----------
    seq : Sequence
        Sequence to serialize.
    filename : str
        Path to output JSON file.
    """
    data = []
    for p in seq.pulses:
        data.append({
            'channel': p.channel,
            't0': p.t0,
            'dt': p.dt,
            'color': p.color,
            'label': p.label,
        })
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def load_sequence_json(filename: str) -> Sequence:
    """
    Load a Sequence from a JSON file.

    Parameters
    ----------
    filename : str
        Path to JSON file created by `save_sequence_json`.

    Returns
    -------
    Sequence
        Reconstructed Sequence object.
    """
    with open(filename) as f:
        data = json.load(f)
    seq = Sequence()
    for item in data:
        seq.add(Pulse(
            channel=item['channel'],
            t0=item['t0'],
            dt=item['dt'],
            color=item.get('color', ''),
            label=item.get('label', '')
        ))
    return seq