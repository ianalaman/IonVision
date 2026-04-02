
## Fields

**Pulse sequence diagram** files define the timing and order of laser pulses, repumping, detection windows, and other experiment stages. The json file fields are:

| Concept        | You specify                                   | Output                                                                 |
|----------------|-----------------------------------------------|------------------------------------------------------------------------|                
| **Channel**    |A named experimental `channel` such as "AOM 422 nm", plus display fields like color. | Horizontal lanes representing control channels across time.              |
| **Pulse**      | `t0` (start time), `dt` (duration), `channel` (the lane on which it appears), and optional label.                | Coloured rectangles showing when each laser or device is on.                 |
| **Stage/marker** | `label` and `time` defining key experimental boundaries such as “Doppler”, “Detect”.                             | Vertical lines marking important experimental stages or measurement points.                |

---
## Example

Ready-made **examples** can be found in `pulse_sequence_generator/data/strontium` e.g. 
```python
# pulse_sequence_generator/data/strontium/continuous_sideband_cooling.json
{
  "name": "ContinuousSidebandCooling",
  "title": "674 Qubit Scan of Strontium \nwith Continuous Sideband Cooling (88Sr+)",
  "pulses": [

    {
      "channel": "AOM 422nm σ⁻",
      "t0": 0,
      "dt": 30,
      "color": "#2E55D6"
    },

    {
      "channel": "AOM 1033nm",
      "t0": 0,
      "dt": 30,
      "color": "goldenrod",
      "label": "Clearout"
    },

    {
      "channel": "AOM 674nm",
      "t0": 30,
      "dt": 30,
      "color": "#B34ADC"
    },

    {
      "channel": "AOM 674nm",
      "t0": 90,
      "dt": 30,
      "color": "#B34ADC"
    },

    {
      "channel": "AOM 1033nm",
      "t0": 30,
      "dt": 30,
      "color": "goldenrod",
      "label": "Quench"
    },

    {
      "channel": "AOM 422nm σ⁻",
      "t0": 60,
      "dt": 30,
      "color": "#2E55D6"
    },

    {
      "channel": "AOM 1033nm",
      "t0": 60,
      "dt": 30,
      "color": "goldenrod",
      "label": "Clearout"
    },

    {
      "channel": "PMT",
      "t0": 120,
      "dt": 30,
      "color": "grey"
    },

    {
      "channel": "AOM 422nm",
      "t0": 120,
      "dt": 30,
      "color": "#2E55D6"
    },

    {
      "channel": "AOM 422nm",
      "t0": 150,
      "dt": 30,
      "color": "#2E55D6"
    },

    {
      "channel": "AOM 1033nm",
      "t0": 120,
      "dt": 60,
      "color": "goldenrod",
      "label": "Clearout"
    },

    {
      "channel": "AOM 1092",
      "t0": 0,
      "dt": 90,
      "color": "#DC514A"
    },

    {
      "channel": "AOM 1092",
      "t0": 120,
      "dt": 60,
      "color": "#DC514A"
    }

  ],
  "labels": [
    "$t_{\\mathrm{Prep |↓⟩}}$",
    "$t_{\\mathrm{SB & Quench}}$",
    "$t_{\\mathrm{Prep |↓⟩}}$",
    "$t_{\\mathrm{Prep |↑⟩}}$",
    "$t_{\\mathrm{Detect}}$",
    "$t_{\\mathrm{Doppler}}$"
  ],
  "time_boundaries": [
    0,
    30,
    60,
    90,
    120,
    150,
    180
  ]
}
```

## Output 

<p align="center">
  <img src="../../assets/continuous_sideband_cooling_pulse_sequence_diagram.png" alt="Continuous Sideband Cooling" width="100%">
</p>