## Fields

**Energy‑level diagram** files define the internal electronic structure of the ion, including electronic states, Zeeman sublevels, and allowed optical transitions. The json file fields are: 

| Concept        | You specify                                   | Output                                                                 |
|----------------|-----------------------------------------------|------------------------------------------------------------------------|
| **Level**      | `label` (e.g. "4d ²D₃/₂"), energy (typically in cm⁻¹, measured relative to the ground state), and optional tags such as `width`, `group`, or `zeeman`. | Horizontal bars grouped by manifold, representing the ion’s electronic energy levels. |
| **Transition** | The addressed states using `from`/`to` strings (including `mⱼ` values), optional `wavelength`/`frequency`, and optional `label`/`style` parameters. | Arrows between levels showing optical transitions, optionally annotated with labels or wavelengths.                |

---
## Example

Ready-made **examples** can be found in `energy_level_generator/data/strontium` e.g. 
```python
# energy_level_generator/data/strontium/continuous_sideband_cooling.json
{
  "title": "Continuous Sideband Cooling",
  "ion": "88Sr+",
  "unit": "cm$^{-1}$",

  "levels": [
    { "label": "5s  2S1/2", "energy": 0.0, "zeeman": true },
    { "label": "4d  2D3/2", "energy": 14647.0, "zeeman": true },
    { "label": "4d  2D5/2", "energy": 14995.0, "zeeman": true, "sideband": {"m_j": ["-5/2", "-3/2", "-1/2", "+1/2", "+3/2", "+5/2"] }},
    { "label": "5p  2P1/2", "energy": 23715.0, "zeeman": true },
    { "label": "5p  2P3/2", "energy": 24429.0, "zeeman": true }
  ],

  "transitions": [
    { "from": "5p  2P1/2, m_j=+1/2", "to": "5s  2S1/2, m_j=-1/2", "label": "Spontaneous Decay", "color": "gray", "style": "dashed", "reversible": false },
    { "from": "5p  2P1/2, m_j=-1/2", "to": "5s  2S1/2, m_j=-1/2", "color": "gray", "style": "dashed", "reversible": false },
  
    { "from": "5p  2P3/2, m_j=-3/2", "to": "5s  2S1/2, m_j=-1/2", "color": "#999999", "style": "dashed", "reversible": false },
    { "from": "5p  2P3/2, m_j=+3/2", "to": "5s  2S1/2, m_j=+1/2", "color": "#999999", "style": "dashed", "reversible": false },
    { "from": "5p  2P3/2, m_j=+1/2", "to": "5s  2S1/2, m_j=+1/2", "color": "#999999", "style": "dashed", "reversible": false },
    { "from": "5p  2P3/2, m_j=+1/2", "to": "5s  2S1/2, m_j=-1/2", "color": "#999999", "style": "dashed", "reversible": false },
    { "from": "5p  2P3/2, m_j=-1/2", "to": "5s  2S1/2, m_j=+1/2", "color": "#999999", "style": "dashed", "reversible": false },
    { "from": "5p  2P3/2, m_j=-1/2", "to": "5s  2S1/2, m_j=-1/2", "color": "#999999", "style": "dashed", "reversible": false },

    { "from": "5s  2S1/2, m_j=-1/2", "to": "4d  2D5/2, m_j=-5/2, red sideband", "label": "674 nm (detuned)", "color": "purple", "style": "solid", "reversible": false },
    
    { "from": "5p  2P1/2, m_j=-1/2", "to": "5s  2S1/2, m_j=+1/2", "label": "422 nm σ⁻", "color": "blue", "style": "solid" },

    { "from": "4d  2D5/2, m_j=-5/2, red sideband",  "to": "5p  2P3/2, m_j=-3/2", "label": "1033 nm", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=-5/2, blue sideband", "to": "5p  2P3/2, m_j=-3/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },

    { "from": "4d  2D5/2, m_j=-3/2, red sideband",  "to": "5p  2P3/2, m_j=-3/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=-3/2, blue sideband", "to": "5p  2P3/2, m_j=-3/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=-3/2, red sideband",  "to": "5p  2P3/2, m_j=-1/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=-3/2, blue sideband", "to": "5p  2P3/2, m_j=-1/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },

    { "from": "4d  2D5/2, m_j=-1/2, red sideband",  "to": "5p  2P3/2, m_j=-3/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=-1/2, blue sideband", "to": "5p  2P3/2, m_j=-3/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=-1/2, red sideband",  "to": "5p  2P3/2, m_j=-1/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=-1/2, blue sideband", "to": "5p  2P3/2, m_j=-1/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=-1/2, red sideband",  "to": "5p  2P3/2, m_j=+1/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=-1/2, blue sideband", "to": "5p  2P3/2, m_j=+1/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },

    { "from": "4d  2D5/2, m_j=+1/2, red sideband",  "to": "5p  2P3/2, m_j=-1/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=+1/2, blue sideband", "to": "5p  2P3/2, m_j=-1/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=+1/2, red sideband",  "to": "5p  2P3/2, m_j=+1/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=+1/2, blue sideband", "to": "5p  2P3/2, m_j=+1/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=+1/2, red sideband",  "to": "5p  2P3/2, m_j=+3/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=+1/2, blue sideband", "to": "5p  2P3/2, m_j=+3/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },

    { "from": "4d  2D5/2, m_j=+3/2, red sideband",  "to": "5p  2P3/2, m_j=+1/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=+3/2, blue sideband", "to": "5p  2P3/2, m_j=+1/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=+3/2, red sideband",  "to": "5p  2P3/2, m_j=+3/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=+3/2, blue sideband", "to": "5p  2P3/2, m_j=+3/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },

    { "from": "4d  2D5/2, m_j=+5/2, red sideband",  "to": "5p  2P3/2, m_j=+3/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },
    { "from": "4d  2D5/2, m_j=+5/2, blue sideband", "to": "5p  2P3/2, m_j=+3/2", "color": "goldenrod", "style": "solid", "alpha": 0.4 },

    { "from": "4d  2D3/2, m_j=-3/2", "to": "5p  2P1/2, m_j=-1/2", "label": "1092 nm", "color": "red", "style": "solid" },
    { "from": "4d  2D3/2, m_j=-1/2", "to": "5p  2P1/2, m_j=-1/2", "color": "red", "style": "solid" },
    { "from": "4d  2D3/2, m_j=-1/2", "to": "5p  2P1/2, m_j=+1/2", "color": "red", "style": "solid" },
    { "from": "4d  2D3/2, m_j=+1/2", "to": "5p  2P1/2, m_j=-1/2", "color": "red", "style": "solid" },
    { "from": "4d  2D3/2, m_j=+1/2", "to": "5p  2P1/2, m_j=+1/2", "color": "red", "style": "solid" },
    { "from": "4d  2D3/2, m_j=+3/2", "to": "5p  2P1/2, m_j=+1/2", "color": "red", "style": "solid" }


  ]
}
```

## Output 

<p align="center">
  <img src="../../assets/continuous_sideband_cooling_energy_level_diagram.png" alt="Continuous Sideband Cooling" width="100%">
</p>
