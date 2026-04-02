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