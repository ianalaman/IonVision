# Context

## Background

Ion-trap teams, including the team at the **National Quantum Computing Centre (NQCC)** frequently require:

- **Energy level diagrams** – showing actual sublevels and transitions used in protocols.  
- **Pulse-sequence diagrams** – showing the precise timings and hardware involved in experimental procedures.

These diagrams are needed for **internal documentation, experiment planning, talks, and publications**, but manually redrawing them in vector tools or powerpoint is **time-consuming and inconsistent**.

---

## Project Motivation

This toolkit was developed during a **summer placement with the NQCC ion-trap team** to address these issues by:

- Standardising the appearance of diagrams across the lab.  
- Saving researchers time on routine figure creation.  
- Providing ready-to-use figures for **posters**, **presentations** and **papers**.  
- Allowing the team to focus on the **underlying physics**, not formatting.

A major motivation of the project was to **identify the exact energy levels and transitions used in real experimental protocols** (e.g. SPAM, Doppler/Sideband cooling, Shelving/Readout), ensuring figures reflect **actual lab practice rather than generic textbook sketches**.

Example Jupyter notebooks demonstrate this mapping explicitly for **⁸⁸Sr⁺** with a package structure that is easily extendable to other ion types.

---

## Toolkit Output

The toolkit produces easily configurable:

- **Energy level diagrams**: annotated with sublevels and transition labels.  
- **Pulse-sequence diagrams**: with channel names, stage markers, and optional detuning annotations.

All outputs saved as **static PNGs or PDFs**, ready to drop directly into lab notes, slides, or publications.

