<!-- Hero logo (large, centered). The header still shows the small logo. -->
<p align="center">
  <img src="assets/NQCC_logo.png" alt="NQCC logo" width="55%">
</p>

# Home

This site documents the **Energy Level and Pulse Sequence Diagram Generator** for ion-trap quantum computers.  

- Installation, usage, and examples  
- Design notes and references  
- (Optional) auto-generated API docs  

## Table Of Contents

1. [Tutorials](tutorials.md)  
2. [How-To Guides](how-to-guides.md)  
3. [Reference](reference.md)  
4. [Explanation](explanation.md)  

Quickly find what you need based on your use case by jumping to the relevant section above.

---

## Project Overview

The **diagram generator** provides a unified way to create **energy level diagrams** and **pulse sequence timelines** for trapped-ion quantum computing experiments.  

The package takes a **structured JSON description** of experimental stages (ion levels, transitions, pulses, timings, and channels) and outputs **static diagrams (PNG)** suitable for:  

- Researchers documenting experiments  
- Educators introducing trapped-ion quantum computing concepts  

### Core Features

- **Energy Level Diagrams**  
  Generate annotated level structures showing qubit encodings, optical pumping, repumping, cooling, and readout transitions.  

- **Pulse Sequence Diagrams**  
  Render Gantt-style time charts of experimental control pulses, with color-coded channels, labels, and stage markers.  

- **Ion Species Agnostic**  
  The JSON schema can describe any ion species. Example notebooks are included for **⁴⁰Ca⁺** and **⁸⁸Sr⁺**, demonstrating sequences such as SPAM operations and sideband cooling.  

- **Publication-Ready Output**  
  All diagrams export as static PNG images, making them easy to include in papers, talks, or lab documentation.  

---


## Acknowledgements

This project was developed during a **summer placement at the National Quantum Computing Centre (NQCC)**.  
I would like to thank my project supervisor (Daisy Smith) and the Ion Trap Team for their guidance and support throughout the work.  

---

<sub>Maintained at [github.com/ianalaman/NQCC](https://github.com/ianalaman)</sub>


---

