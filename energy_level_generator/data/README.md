# JSON Format for Energy Level Diagrams

This directory contains JSON files describing energy levels and allowed transitions for ions such as **88Sr⁺**. These files are used for plotting level diagrams in the `energy_level_generator` module.

## File Structure

Each JSON file follows a structured format with the following top-level fields:

---

### 🔹 `title` (string)
A short description of the diagram (e.g., `"Detect"` or `"Optical Pumping (Prep |↓⟩)"`).

### 🔹 `ion` (string)
Specifies the ion (e.g., `"88Sr+"`).

### 🔹 `unit` (string)
Unit of energy levels (supports LaTeX-style math notation), e.g., `"cm$^{-1}$"`.

---

## Energy Levels

```json
"levels": [
  {
    "label": "5s  2S1/2",
    "energy": 0.0,
    "zeeman": true
  },
  ...
]
"transitions": [
  {
    "from": "5p  2P1/2, m=+1/2",
    "to":   "5s  2S1/2, m=+1/2",
    "color": "blue",
    "style": "solid",
    "label": "422 nm",
    "reversible": false
  },
  ...
]
