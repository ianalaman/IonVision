<!-- Hero logo (large, centered). The header still shows the small logo. -->
<p align="center">
  <img src="assets/NQCC_logo.png" alt="NQCC logo" width="55%">
</p>

# Energy Level & Pulse Sequence Generator

A compact toolkit from the **National Quantum Computing Centre (NQCC)** for
**describing and visualising trapped-ion experiments**.  
It turns a structured description of **ion levels, transitions, and control pulses**
into **publication-ready diagrams**.

---

## What you can do

- **Energy-level diagrams**  
  Show qubit encodings, pumping/repumping paths, cooling and readout transitions.

- **Pulse-sequence timelines**  
  Render SPAM, Doppler, sideband cooling, and custom control sequences with
  labelled hardware channels and time stage markers.

- **Reproducible, shareable outputs**  
  Export static PNGs aligned with NQCC colours for papers, talks, and lab notes.

!!! tip "Who is this for?"

    Experimental ion-trap physicists writing reports, students learning about pulse sequences, and anyone who needs **clear, consistent diagrams** for trapped-ion control.



---

## How the toolkit is structured

Two small libraries power everything:

- **Energy Level Generator** (`energy_level_generator/`) — Set of tools to display energy levels neatly and add labels and arrows to show transitions between them.
- **Pulse Sequence Generator** (`pulse_sequence_generator/`) — Set of tools to display pulse sequence diagrams neatly and with configurable timings and apparatus control lanes.

In both cases you describe the diagram using a **simple schema** (Python dict/JSON). The reference pages list **every field, unit, and default**.

| Concept        | You specify                                  | Output                              |
|----------------|----------------------------------------------|-------------------------------------|
| *Level*        | `label`, `energy`, (optional) width/group    | horizontal bars grouped by manifold |
|                |                                              |                                     |  
| *Transition*   | source → target, wavelength/freq, `label`    | arrows with labels                  |
| *Channel*      | name (e.g. “422 nm”), colour, lane order     | timeline lanes                      |
| *Pulse*        | `t0`, `dt`, `channel`, `label`               | rectangles on the lane              |
| *Stage/marker* | label + time                                 | vertical guide lines                |

See **Reference → [Parameters & Config Options](reference/config.md)** and **Reference → [Sequence Syntax](reference/sequences.md)**.

---

## Learn by example

### NQCC Ion Traps
- **[Sr-88 SPAM & Sideband Cooling](notebooks/02_sr88.md)**
- **[Ca⁺ SPAM & Sideband Cooling](notebooks/03_ca.md)**

These notebooks show the exact inputs and rendered outputs for each species.

---

## Typical workflows

**Energy-level diagram**
1. Define levels and transitions for your species.  
2. Choose layout (columns, spacing, grouping).  
3. Render → PNG.

**Pulse-sequence timeline**
1. Declare channels (e.g. AOMs/PMTs) and colours.  
2. Add pulses with `t0`, `dt`, and labels; add stage markers.  
3. Render → PNG.

---

## Where to go next

- **Getting Started** → [Installation & Quickstart](notebooks/01_quickstart.md)  
- **Tutorials** → full examples for Sr-88 and Ca⁺  
- **How-To Guides** → customise sequences, extend level models  
- **Reference** → config parameters and sequence syntax  
- **API** → auto-generated docs from the code


## Acknowledgements

Developed during a summer placement at the National Quantum Computing Centre (NQCC).  
Thanks to Daisy Smith and the Ion Trap Team for guidance and support.

<small>Source & issues: <https://github.com/ianalaman/NQCC></small>
