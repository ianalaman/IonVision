# Background

The ion-trap team at the **National Quantum Computing Centre (NQCC)** frequently requires:

- **Energy level diagrams** – showing actual sublevels and transitions used in protocols.  
- **Pulse-sequence timelines** – Gantt-style plots for experiment stages.

These diagrams are needed for **internal documentation, experiment planning, talks, and publications**, but manually redrawing them in vector tools or powerpoint is **time-consuming and inconsistent**.

---

## Project Motivation

This toolkit was developed during a **summer placement with the NQCC ion-trap team** to address these issues by:

- Standardising the appearance of diagrams across the lab.  
- Saving researchers time on routine figure creation.  
- Providing ready-to-use figures for **wall/poster references** in the lab.  
- Allowing the team to focus on the **underlying physics**, not formatting.

---

## Key Contributions

A major part of the project involved **identifying the exact energy levels and transitions used in real experimental protocols** (e.g. SPAM, Doppler/sideband cooling, shelving/readout), ensuring figures reflect **actual lab practice rather than generic textbook sketches**.

Example Jupyter notebooks demonstrate this mapping explicitly for **⁸⁸Sr⁺** and **⁴³Ca⁺** which shows a glimpse of what is done at the NQCC.

---

## Toolkit Output

The toolkit produces:

- **Energy level diagrams**: annotated with sublevels and transition labels.  
- **Pulse-sequence timelines**: with channel names, stage markers, and optional detuning annotations.

All outputs are **static PNGs**, ready to drop directly into lab notes, slides, or publications.
