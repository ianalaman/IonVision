# ===== pulseplot/config.py =====
"""
Default configuration: channel orders, colors, and style constants.
"""

# Default display order for channels if none is provided.
DEFAULT_CHANNEL_ORDER = ['MW', 'EOM', 'PMT', 'AOM']

# Default colors for channels (HTML or Matplotlib).
DEFAULT_COLORS = {
    'MW':  '#B0B0B0',
    'EOM': '#A0D468',
    'PMT': '#4C4C4C',
    'AOM': '#4A89DC',
}

# Plot‐wide rcParams settings
RC_PARAMS = {
    'font.size':       16,  # base size for all text
    'axes.titlesize':  18,  # title
    'axes.labelsize':  16,  # x/y labels
    'xtick.labelsize': 16,  # tick labels
    'ytick.labelsize': 16,
}

# Style parameters for pulse baselines and separators
BASELINE_HEIGHT   = 0.4  # Height of pulse bars
SEPARATOR_STYLE   = dict(linestyle='--', linewidth=0.8, color='grey')
TIME_AXIS_PROPS   = dict(arrowstyle='->', lw=1.5, color='black')
