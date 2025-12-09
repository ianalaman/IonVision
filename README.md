# IonVision  

IonVision is a Python package developed during my internship at the National Quantum Computing Centre (NQCC). It enables automated rendering of energy-level diagrams and generation of pulse-sequence timelines for trapped-ion quantum computing experiments.  

[View the documentation and demo site →](https://ianalaman.github.io/IonVision/)  

---

## Features  

- **Energy-Level Diagram Generator**  
  Generate publication-quality diagrams for arbitrary ionic or atomic level structures. Works with multi-level ions and supports configurable styling (colors, labels, transition strengths, etc.).  

- **Pulse-Sequence Builder**  
  Construct pulse sequences (laser or microwave pulses) from YAML-based configuration files. Automatically handles timing, level transitions, and supports multiple pulse types.  


---

##  Installation  

### Linux/Mac

```bash
git clone https://github.com/ianalaman/IonVision.git
cd IonVision
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows

```bash
git clone https://github.com/ianalaman/IonVision.git
cd IonVision
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
```