# Design Choices

## Visual Style & Precedents

The visual style of the toolkit draws inspiration from:

- **Daisy Smith Thesis** – provided layout ideas for pulse-sequence diagrams  
*Smith, Daisy (2025). Entanglement on a surface chip using scalable control technologies for trapped ion qubits. University of Sussex. Thesis. https://hdl.handle.net/10779/uos.28846232.v1*
- **Scott Thomas Thesis** – contributed examples for both energy-level and pulse-sequence figures  
*Thomas, Scott (2022). Quantum coherence of ions in a microfabricated trap. University of Strathclyde, Glasgow. Thesis. https://stax.strath.ac.uk/concern/theses/k643b1649*



> **Goals:** clarity, consistency, and lab-readiness (ready to drop into papers, talks, and lab posters).


## Why JSON?

Using **JSON** as the input and style format keeps the toolkit simple and adaptable:

- **Readable and self-describing:** JSON makes it easy to see at a glance which levels, transitions, or pulse timings are being defined.  
- **Collaboration-friendly:** Works well with version control (e.g., Git), making diffs and peer reviews straightforward.  
- **Auditable separation:** Keeps the **physics content** (levels and pulses) clearly separated from the **rendering instructions**, so diagrams are reproducible and easy to verify.  
- **Flexible and reusable:** The same format works across different ion species and protocols; no hard-coding or manual diagram tweaks needed.

