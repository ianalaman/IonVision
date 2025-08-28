# Design Choices

## Visual Style & Precedents

The visual style of the toolkit draws inspiration from:

- **Daisy Smith** – provided layout ideas for pulse-sequence diagrams  
- **Scott Thomas** – contributed examples for both energy-level and pulse-sequence figures  
- **Jochen Wolf** – influenced the consistent style used for energy-level diagrams



> **Goals:** clarity, consistency, and lab-readiness (ready to drop into papers, talks, and lab posters).

---

## Toolkit Architecture

The toolkit exposes **two main functions**:

| Function | Required Input | Optional Inputs | Output |
|----------|----------------|-----------------|---------|
| `generate_energy_diagram(data, style=None, save_path=None)` | JSON describing levels, sublevels, transitions | JSON for custom styling (colors, fonts), output file path | Static PNG energy-level diagram |
| `generate_pulse_sequence(data, style=None, save_path=None)` | JSON describing pulse timings, channels | JSON for custom styling, output file path | Static PNG pulse-sequence timeline |

---



## Why JSON?

Using **JSON** as the input and style format keeps the toolkit simple and adaptable:

- **Readable and self-describing:** JSON makes it easy to see at a glance which levels, transitions, or pulse timings are being defined.  
- **Collaboration-friendly:** Works well with version control (e.g., Git), making diffs and peer reviews straightforward.  
- **Auditable separation:** Keeps the **physics content** (levels and pulses) clearly separated from the **rendering instructions**, so diagrams are reproducible and easy to verify.  
- **Flexible and reusable:** The same format works across different ion species and protocols; no hard-coding or manual diagram tweaks needed.

