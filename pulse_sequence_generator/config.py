# ===== pulseplot/config.py =====
"""
Default configuration for pulse‐sequence plotting:
  - Channel definitions (order & colors)
  - Global Matplotlib styling
  - Pulse‐specific styling (bars, baselines, separators)
  - Annotation/text styling (for pulse labels, arrows, etc.)
"""

# 1. Channel definitions
# ────────────────────────────────────────────────────────────────────────────────
# Order in which channels are drawn (if not overridden per‐plot).
DEFAULT_CHANNEL_ORDER = ['MW', 'EOM', 'PMT', 'AOM']

# Default fill colors for each channel (HTML hex or Matplotlib‐compatible strings).
DEFAULT_COLORS = {
    'MW':  '#B0B0B0',
    'EOM': '#A0D468',
    'PMT': '#4C4C4C',
    'AOM': '#4A89DC',
}


# 2. Global Matplotlib style overrides
# ────────────────────────────────────────────────────────────────────────────────
# Applies to all figures: font sizes, axes labels, tick labels, etc.
RC_PARAMS = {
    'font.size':       16,  # Base font size for all text elements
    'axes.titlesize':  18,  # Axes titles
    'axes.labelsize':  16,  # X/Y axis labels
    'xtick.labelsize': 16,  # Tick labels
    'ytick.labelsize': 16,
}


# 3. Pulse/bar plotting style
# ────────────────────────────────────────────────────────────────────────────────
# Height of each pulse bar drawn via broken_barh.
BASELINE_HEIGHT = 0.4

# Style for the dashed separators between time‐intervals
SEPARATOR_STYLE = dict(
    linestyle='--',
    linewidth=0.8,
    color='grey',
)

# Style for the time‐axis arrow in draw_time_axis()
TIME_AXIS_PROPS = dict(
    arrowstyle='->',
    lw=1.5,
    color='black',
)


# 4. Annotation / text styling for pulse labels
# ────────────────────────────────────────────────────────────────────────────────
# Font properties for labels placed on pulses
FONT_SIZE   = 12        # fontsize for pulse‐label text
FONT_FAMILY = 'Cambria' # family/name of the font
FONT_COLOR  = 'white'   # text color for high contrast

# Horizontal & vertical offsets to fine‐tune label placement
HORIZONTAL_SHIFT = 0.0  # added to (t0 + dt/2)
VERTICAL_SHIFT   = 0.0  # added to (y − 0.5·BASELINE_HEIGHT)
