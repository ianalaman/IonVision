import matplotlib.pyplot as plt
import numpy as np
import re
from matplotlib.patches import FancyArrowPatch
import math

from scipy.constants import physical_constants, h, c

# Bohr magneton (J/T) and h·c (J·m)
μB = physical_constants["Bohr magneton"][0]
hc = h * c
# Constants
LETTER_TO_COL = {'S': 0, 'P': 0, 'D': 2, 'F': 3}


##### ---------- HELPER FUNCTIONS ----------#######

# ---------- Formatting Text Functions ----------
    
def format_ion_label(ion: str) -> str:
    """
    Convert a string like '88Sr+' into LaTeX-formatted
    superscript label for matplotlib, e.g. '$^{88}\\mathrm{Sr}^{+}$'
    """
    import re
    match = re.match(r"(\d+)([A-Za-z]+)([+-]\d*|\+|-)?", ion)
    if match:
        isotope, element, charge = match.groups()
        charge = charge or ""
        return fr"$^{{{isotope}}}\mathrm{{{element}}}^{{{charge}}}$"
    else:
        return ion


def format_term_symbol(label: str) -> str:
    """
    Convert a raw label like '5s 2S1/2' into a
    Matplotlib math-text string for proper typesetting.
    """
    try:
        orb, term = label.split(maxsplit=1)
        m = re.match(r"(\d)([SPDF])(\d)/(\d)", term)
        if not m:
            return label
        multiplicity, L, num, den = m.groups()
        return rf"${orb}\,^{multiplicity}{L}_{{{num}/{den}}}$"
    except ValueError:
        return label

# ---------- Column Inference Functions ----------

def infer_column(label: str, mapping: dict = LETTER_TO_COL) -> int:
    """
    Extract the term-symbol letter from a spectroscopic label
    (e.g. '5p 2P3/2') and return its column index.
    """
    try:
        letter = label.split()[1][1]
        return mapping.get(letter, 0)
    except (IndexError, KeyError):
        return 0
    

def group_levels_by_column(levels: list) -> dict:
    """
    Group a list of level dicts by their column index.
    Returns mapping: column_index -> [levels].
    """
    cols = {}
    for lvl in levels:
        col = infer_column(lvl['label'])
        cols.setdefault(col, []).append(lvl)
    return cols

# ---------- Mapping Functions ----------
def compute_x_map(groups: dict, spacing: float, bar_half: float, x_jitter: float) -> dict:
    """
    Spread the *sub*-levels horizontally, but keep the base-level
    exactly at the column center.
    """
    x_map = {}
    for col, lvls in groups.items():
        base_x = 0.25 * col * spacing

        # split into “base” vs “sub” (m_j) levels
        base_lvls = [l for l in lvls if ', m=' not in l['label']]
        sub_lvls  = [l for l in lvls if ', m='    in l['label']]

        # all base levels sit at base_x
        for lvl in base_lvls:
            x_map[lvl['label']] = base_x

        # spread sub-levels in [-x_jitter, +x_jitter]
        if sub_lvls:
            offsets = np.linspace(-bar_half *0.75, 0.75*bar_half, len(sub_lvls))
            for lvl, off in zip(sub_lvls, offsets):
                x_map[lvl['label']] = base_x + off

    return x_map


def compute_y_map(groups: dict,
                  bar_half: float,
                  y_jitter_normal: float = 200.0,
                  # y_jitter_zeeman is now just a scale on ΔE, if you still want it:
                  y_scale_zeeman: float   = 1.0) -> dict:
    y_map = {}

    for lvls in groups.values():
        # 1) Base levels (no “, m=”)
        normals = [l for l in lvls if ', m=' not in l['label']]
        if normals:
            E = np.array([l['energy'] for l in normals])
            n = len(normals)
            jit = bar_half * y_jitter_normal
            offs = np.linspace(-jit, +jit, n) if n>1 else [0]
            order = np.argsort(E)
            for i, idx in enumerate(order):
                lbl = normals[idx]['label']
                y_map[lbl] = E[idx] + offs[i]

        # 2) Zeeman sub‐levels ride on top of their base‐bar
        subs = [l for l in lvls if ', m=' in l['label']]
        for sub in subs:
            base_lbl = sub['label'].split(',')[0]
            # ΔE relative to the parent energy
            ΔE = sub['energy'] - next(l['energy']
                                      for l in normals
                                      if l['label']==base_lbl)
            # place the tick at (base_y + scaled ΔE)
            y_map[sub['label']] = y_map[base_lbl] + ΔE * y_scale_zeeman

    return y_map




# ---------- Splitting Functions ----------

def lande_g_factor(L: float, S: float, J: float) -> float:
    """
    Landé g_J = 3/2 + [S(S+1) − L(L+1)] / [2 J(J+1)]
    """
    return 1.5 + (S*(S+1) - L*(L+1)) / (2 * J * (J+1))


def zeeman_split(level: dict, B: float, unit: str = "cm^-1") -> list[dict]:
    """
    Given one base level:
      { "label": "5p 2P3/2", "energy": E0 }
    and a magnetic field B (in Tesla),
    return a list of 2J+1 sub-levels:
      [
        { "label": "5p 2P3/2, m=+3/2", "energy": E0 + ΔE(+3/2), "m":+1.5 },
        { "label": "5p 2P3/2, m=+1/2", "energy": E0 + ΔE(+1/2), "m":+0.5 },
        …
      ]
    """

    parent = level["label"]
    E0     = level["energy"]

    # parse term-symbol: orb term e.g. "5p 2P3/2"
    term = parent.split()[1]
    m = re.match(r"(\d+)([SPDF])(\d)/(\d)", term)
    if not m:
        # not a standard term, just return the base level
        return [level.copy()]

    mult, Lsym, num, den = m.groups()
    J = int(num)/int(den)
    S = (int(mult)-1)/2
    L = {"S":0,"P":1,"D":2,"F":3}[Lsym]

    # compute gJ and Zeeman factor in same units as E0
    gJ     = lande_g_factor(L, S, J)
    # ΔE_Joule per mJ = gJ·μB·B
    # convert to cm^-1 via dividing by (h·c) and multiplying by 1e2
    conv   = (gJ * μB * B) / hc * 1e2

    out = []
    for mJ in np.arange(-J, J+1, 1):
        ΔE    = conv * mJ
        out.append({
        "label":  f"{parent}, m={mJ:+.1f}",
         "energy": E0 + ΔE,
         "m":       mJ
        })

    return out


# ---------- Plotting Function ----------

def draw_levels(ax, x_map, y_map):
    pad = 0.02
    tick_half = draw_levels.bar_half * 0.3

    # 1) base‐bars + labels
    for base, is_z in draw_levels.zeeman_map.items():
        x = x_map[base]
        y = y_map[base]

        if is_z and draw_levels.B>0:
            # dotted grey line
            ax.hlines(y,
                      x - draw_levels.bar_half,
                      x + draw_levels.bar_half,
                      color='grey',
                      lw=2,
                      linestyle=':')
        else:
            # solid black line
            ax.hlines(y,
                      x - draw_levels.bar_half,
                      x + draw_levels.bar_half,
                      color='k',
                      lw=0.5)

        # term‐symbol label
        ax.text(
            x + draw_levels.bar_half + pad,
            y,
            format_term_symbol(base),
            va='center', ha='left', fontsize=9
        )


    # 2) on top of that, for each zeeman‐true base, draw its m‐ticks
    if draw_levels.B>0:
        for base, lvl in draw_levels.level_lookup.items():
            if not draw_levels.zeeman_map.get(base, False):
                continue
            subs = zeeman_split(lvl, draw_levels.B)
            for sub in subs:
                sub_lbl = sub['label']
                x_sub   = x_map[sub_lbl]
                y_sub   = y_map[sub_lbl]
                m       = sub['m']
                ax.hlines(y_sub, x_sub - tick_half, x_sub + tick_half,
                          color='red', lw=0.5)
                ax.text(x_sub + pad*1.75, y_sub,
                        f"{m:+g}",
                        va='center', ha='left', fontsize=6)



def draw_transitions(ax, transitions, x_map, y_map):
    """
    Draw arrows or lines between energy levels with labels.
    """
    for t in transitions:
        x1, y1 = x_map[t['from']], y_map[t['from']]
        x2, y2 = x_map[t['to']],   y_map[t['to']]
        color = t.get('color', 'k')
        rev = t.get('reversible', False)
        ls = '-' if t.get('style','solid') == 'solid' else ':'

        if rev:
            ax.plot([x1, x2], [y1, y2], linestyle=ls, color=color, lw=2)
        else:
            arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='->',
                                     mutation_scale=10, color=color,
                                     lw=2, linestyle=ls)
            ax.add_patch(arrow)

        mx, my = (x1 + x2)/2, (y1 + y2)/2
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        ux, uy = dx/L, dy/L
        px, py = -uy, ux
        shift = 0.035
        ax.text(
            mx + px*shift,
            my + py*shift,
            t.get('label',''),
            va='center', ha='center', fontsize=8
        )


def configure_axes(ax, data, x_map, y_map, spacing, show_axis, title_pad, ylabel_pad, left_margin):
    """
    Apply titles, labels, limits, and cosmetic settings to the plot axes.
    """ 
    ion = data.get('ion', '')
    ion_label = format_ion_label(ion)
    ax.set_title(f"{ion_label} Energy Levels", pad=title_pad)
    ax.set_ylabel(f"Energy ({data.get('unit','cm$^{-1}$')})", labelpad=ylabel_pad)
    ax.set_xticks([])

    y_vals = list(y_map.values())
    ax.set_ylim(min(y_vals) - spacing, max(y_vals) + spacing)
    x_vals = list(x_map.values())
    ax.set_xlim(min(x_vals) - spacing/2, max(x_vals) + spacing/2)

    if show_axis:
        for side in ['top','right','bottom']:
            ax.spines[side].set_visible(False)
        ax.spines['left'].set_visible(True)
        ax.yaxis.set_visible(True)
    else:
        ax.axis('off')

    fig = ax.get_figure()
    fig.subplots_adjust(left=left_margin)
    fig.tight_layout()


def plot_energy_levels(data, B=0.0,
                       spacing=0.5, bar_half= 0.1,
                       x_jitter=0.2,
                       y_jitter_normal=20000.0,
                       y_jitter_zeeman=10.0,
                       show_axis=False,
                       title_pad=20,
                       ylabel_pad=15,
                       left_margin=0.2):
    # expand levels
    flat = []
    for lvl in data['levels']:
        flat.append(lvl)
        if lvl.get('zeeman', False) and B>0:
            flat.extend(zeeman_split(lvl, B))

    # build lookups
    draw_levels.zeeman_map   = {lvl['label']: lvl.get('zeeman', False)
                                for lvl in data['levels']}
    draw_levels.level_lookup = {lvl['label']: lvl
                                for lvl in data['levels']}
    draw_levels.B            = B
    draw_levels.bar_half     = bar_half

    # map columns → x/y
    cols  = group_levels_by_column(flat)
    x_map = compute_x_map(cols, spacing, bar_half, x_jitter)
    y_map = compute_y_map(cols,
                      bar_half,
                      y_jitter_normal=20000.0,  # or whatever
                      y_scale_zeeman=1.0)       # tweak to exaggerate splitting
    # plot
    fig, ax = plt.subplots(figsize=(8,5))
    draw_levels(ax, x_map, y_map)
    draw_transitions(ax, data.get('transitions', []), x_map, y_map)
    configure_axes(ax, data, x_map, y_map,
                   spacing,
                   show_axis,
                   title_pad,
                   ylabel_pad,
                   left_margin)
    plt.show()

