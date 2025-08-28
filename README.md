# IonVision

Python Package to (1) render atomic/ionic **energy-level diagrams** from structured JSON and
(2) draw **pulse-sequence timelines** for experiments (e.g., 88Sr⁺, Ca⁺).
The code is split into two small, focused packages:

- `energy_level_generator/` – levels, layouts, splitters (Zeeman, sidebands), plotting.
- `pulse_sequence_generator/` – sequence model, styling, Matplotlib plotting.

Documentation is built with **MkDocs + Material** and includes runnable demo notebooks.

---

## Features

- **Physics-aware levels**
  - LS term parsing (e.g. `5s 2S1/2`)
  - Zeeman sublevels (m\_j), optional motional sidebands
  - Deterministic x/y layout (columns by term, grouped energies)
  - Clean Matplotlib plotter with term symbols and sublevel labels

- **Pulse sequences**
  - Minimal `Sequence` model (channels, time blocks, labels)
  - Configurable channel order and colors
  - Publication-ready static timelines

- **Docs & demos**
  - Notebooks for Sr⁺ level diagrams and pulse sequences
  - API pages generated directly from docstrings (Google style)

---

## Install

```bash
# Create a virtual environment (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install library + docs dependencies
pip install -r requirements.txt
