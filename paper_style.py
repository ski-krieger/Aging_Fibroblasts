"""
Shared house style for all main-text figure panels (Figures 1-5+).

Import this once at the top of every panel script:

    import paper_style as style
    style.apply()

*** IMPORTANT: this file is shared and edited from MULTIPLE separate
conversation threads (one per figure, sometimes more than one per figure).
Before editing it, re-read the CURRENT copy on disk -- do not edit a
locally-cached version from earlier in your own conversation, since another
thread may have added things since you last looked. (This file was
reconstructed on 2026-09-02 after exactly that mistake happened once
already: an edit from a Figure-1 thread overwrote several functions/colors
a Figure-3 thread had added, without ever re-reading the file first. The
fix was to grep every fig*.py in every FigureN/ folder for `style\\.` usage
and rebuild from what the actual panel code required -- which is why that's
now also the recommended way to verify this file's completeness after any
edit, not just this once.) ***

Design goals (per project style rules):
  - All type set in Helvetica. True Helvetica isn't a freely redistributable
    font, so we point matplotlib at "TeX Gyre Heros" first -- it's a metrically
    identical, freely licensed clone (URW Nimbus Sans lineage) that is the
    standard Helvetica stand-in in scientific typesetting. On a machine that
    *does* have real Helvetica or Arial installed, matplotlib will still find
    those first since they're listed ahead of the fallback.
  - Vector-safe, editable text in exported PDFs/SVGs (fonttype 42 / 'none'),
    not text-as-outlines -- so a journal's production team (or a reader in
    Illustrator) can still select/edit the text.
  - A clean, deliberately-not-default look: no seaborn darkgrid/whitegrid,
    thin spines, outward ticks, restrained gridlines used only where they aid
    reading (e.g. dense scatters), and a small fixed set of hand-picked
    colors reused across panels instead of seaborn/matplotlib's default color
    cycle.

Cross-figure color-reuse rule (clarified while building Figure 2/3): the
"don't reuse a color" caution is about two panels WITHIN THE SAME FIGURE,
not the whole paper. A reader compares panels side-by-side within one
figure, not across figures, so e.g. ink_blue legitimately means four
different things across Fig1 A / Fig2 E / Fig2 F / Fig3 C -- that's fine.
Check the per-figure usage log below before assigning a color, and only
worry about collisions against OTHER panels in the SAME figure.

Other standing conventions established while building Figures 2-5 (apply
these in every new panel module, not just where first introduced):
  - Never default a function parameter straight to a mutable module-level
    object (e.g. `def f(x=SOME_DICT):`). A default value is bound once, at
    `def` time -- re-running just one cell after %autoreload reloads the
    module, or after a kernel restart with cells re-run out of order, can
    bind against a stale/not-yet-defined object. Default to None and
    resolve the real value inside the function body instead.
  - Rasterize any literal, undownsampled scatter/density layer (`rasterized
    =True`) -- still a real vector PDF overall, but keeps file size sane
    when a layer has thousands of points; reserve full vector rendering for
    the handful of elements someone might actually want to nudge by hand
    later (highlighted points, annotations, fit lines).
  - For any two-condition comparison, encode the condition redundantly:
    color AND marker-shape (or linestyle for a line/KDE), so the panel still
    reads correctly in grayscale or at a legend glance, not just by color.
  - A sequential (single-direction) quantity gets a sequential colormap
    (`sequential_accent_cmap`); a genuinely signed/diverging quantity (a
    real zero or neutral point in the middle of its range) gets a diverging
    one (`diverging_cmap` / `diverging_corr_cmap`). Using the wrong shape
    colormap for the underlying quantity is a real (if subtle) misreading
    risk, not just a style nit -- confirmed as an actual bug on two
    different panels (Fig5 C had a diverging cmap on a one-directional
    quantity; Fig5 D had, in the original scanpy code it replaced, a
    sequential cmap on a genuinely signed quantity).
"""

import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, to_hex

# ---- Fonts -------------------------------------------------------------
# Order of preference: real Helvetica/Arial if present on this machine,
# otherwise the free TeX Gyre Heros clone, otherwise Liberation Sans (also
# metrically compatible with Arial), otherwise whatever matplotlib's
# built-in default is so we never hard-fail.
FONT_STACK = [
    "Helvetica",
    "Arial",
    "TeX Gyre Heros",
    "Nimbus Sans",
    "Liberation Sans",
    "DejaVu Sans",
]

# ---- House color palette -------------------------------------------------
# Colorblind-checked, deliberately not seaborn/matplotlib's default cycles.
#
# Design principle for keeping ONE figure's panels cohesive *without*
# looking repetitive: SLATE is the shared "raw individual observations /
# neutral bookkeeping" color -- reuse it for a low-level data cloud (a
# scatter, a strip plot) or for a legend/axis element that's explanatory
# rather than headline data, so the eye recognizes "that's the baseline"
# consistently. Then pick ONE new ACCENT per panel for whatever's
# foregrounded there, from the curated set below -- see the cross-figure
# reuse rule above for how far "don't repeat" actually extends.
SLATE = "#6B7280"        # shared neutral: raw/individual observations, or
                          # bookkeeping (e.g. a size-legend swatch)
INK_BLUE = "#2B4C6F"
TERRACOTTA = "#D1603D"
GOLD = "#C08A2E"
MOSS = "#3F6B4C"
TEAL = "#1E6E77"
PLUM = "#7A4C6E"
INDIGO = "#4B4E8F"       # added for Fig1 D_right's two-line comparison; see
                          # VIOLET below -- D_right no longer uses this one,
                          # kept in case another panel wants it
VIOLET = "#9970C9"       # replaces indigo as Fig1 D_right's "reconstruction"
                          # color, paired with moss. Reason: moss/indigo have
                          # decent hue separation but nearly identical
                          # lightness (L*=41.4 vs 35.8 in CIE Lab, a gap of
                          # only ~5.6), and both sit inside a cluster of 5 of
                          # 7 house accents that are all L*=31-42 -- any two
                          # of those read as "same visual weight" regardless
                          # of hue, which is what the user was flagging.
                          # violet's L*=54.6 gives a ~13-point gap above moss
                          # and raises the CIEDE2000 color-distance from moss
                          # (36.4 normal vision -> 41.0; 32.1 -> 35.2 under
                          # simulated deuteranopia; 35.0 -> 38.6 under
                          # simulated protanopia), while its chroma (~53)
                          # stays within the house "muted, not neon" range
                          # already set by terracotta/gold (~55-59).

ACCENTS = {
    "ink_blue": INK_BLUE,
    "terracotta": TERRACOTTA,
    "gold": GOLD,
    "moss": MOSS,
    "teal": TEAL,
    "plum": PLUM,
    "indigo": INDIGO,
    "violet": VIOLET,
}
PALETTE_2 = [INK_BLUE, TERRACOTTA]  # kept for backwards-compat (Fig1 panel A)

# A perceptually-spread ordering of the accents above, used to build smooth
# multi-color ramps (see gene_importance_gradient) -- roughly hue-ordered
# (blue -> cyan-green -> green -> yellow -> orange-red -> magenta -> violet)
# so an interpolated ramp through it doesn't produce muddy in-between hues.
_GRADIENT_ORDER = [INK_BLUE, TEAL, MOSS, GOLD, TERRACOTTA, PLUM, INDIGO]

# Convention: a reference/threshold line or shape (a cutoff, x=0, a
# dendrogram, etc. -- something that's an annotation rather than a data
# series) is always this neutral gray, never one of the ACCENTS above, so
# "colored = data" and "gray = reference" reads consistently across every
# panel and every figure.
REFERENCE_LINE_COLOR = "#999999"

# A second, deliberately separate annotation color: a clean editorial red for
# a "these points correspond to one another across panels" callout ring (e.g.
# Fig1 D_left/D_middle's red circles marking a shared spatial cluster of
# timepoints in two different delay embeddings). Kept out of ACCENTS and
# never used for a data series -- like REFERENCE_LINE_COLOR, it's a
# structural/editorial marker, just a different one (a callout rather than a
# neutral threshold), so it needs its own un-mistakable color rather than
# reusing the gray. Deliberately a true red, not an orange-red, so it reads
# as distinct from TERRACOTTA wherever both appear on the same page.
HIGHLIGHT_RING_COLOR = "#C81E3A"

# A second callout-ring color, for panels highlighting more than one
# corresponding cluster at once (e.g. Fig1 D_left/D_middle showing two
# separate clusters that each match up between the two embeddings). Picked
# to be unambiguous against BOTH HIGHLIGHT_RING_COLOR and the multihue time
# gradient the scatter points themselves are colored with (so a ring never
# reads as "maybe just a same-colored data point") -- verified colorblind-safe
# against HIGHLIGHT_RING_COLOR under simulated deuteranopia/protanopia
# (CIEDE2000 ~36-50 across normal/deuteranopia/protanopia, all well above the
# ~2.3 just-noticeable-difference threshold). Also encode which ring is which
# by LINESTYLE, not color alone, when using more than one ring in one panel
# (see highlight_ring_3d's `linestyle` arg) -- the project's usual redundant-
# encoding convention, and it directly hedges against red/[this color] being
# a red-green-adjacent pair for some viewers.
HIGHLIGHT_RING_COLOR_ALT = "#2A7DB0"

# Per-figure color usage log -- check the relevant figure's entries before
# assigning a color to a new panel IN THAT FIGURE (collisions only matter
# within one figure -- see the cross-figure reuse rule in the module
# docstring above).
#
# Fig1: A (demographics, sex hue) = ink_blue/terracotta.
#       B (COL3A1 vs age) = slate (points) + gold (fit lines).
#       C (age-score histogram) = plum, zero-line = REFERENCE_LINE_COLOR.
#       D_right (COL1A2 vs FN1-cross-mapped reconstruction) = moss
#           (observed) + violet (reconstruction) -- a real 2-way
#           comparison, gets its own pair like panel A. (Originally
#           moss+indigo; swapped to violet after user feedback that the
#           pair looked "too similar" -- moss/indigo had a good hue split
#           but almost no lightness split, see VIOLET's comment above.)
#       D_left/D_middle (COL1A2 / FN1 delay embeddings) = points colored by
#           sequential_multihue_cmap() (time index, shared across both
#           panels on purpose -- makes the same timepoint recognizable by
#           tone in either embedding), slate trajectory line,
#           HIGHLIGHT_RING_COLOR (solid) for the first corresponding-cluster
#           ring and HIGHLIGHT_RING_COLOR_ALT (dashed) for a second one when
#           two clusters are shown at once -- neither is an ACCENT, this is
#           the callout-ring convention, same category as REFERENCE_LINE_COLOR
#           but distinct, deliberately un-mistakable colors for a "these
#           correspond" annotation rather than a neutral threshold.
#       E (BioGRID citations histogram, log-scale) = teal, x=1 line =
#           REFERENCE_LINE_COLOR.
# Fig2: A (MasterScore waterfall) = slate (points).
#       C (UMAP schematic) = a dedicated dark charcoal-navy "#232733" for
#           'old' (deliberately NOT slate -- read as generic gray at KDE
#           alpha) + gold for 'young'; the 5 Reactome categories use
#           ink_blue/terracotta/moss/plum/teal.
#       E (precision, true-vs-null) = ink_blue (true) / gold (random) +
#           moss/terracotta/plum for 3 alternative method point-estimates.
#       F (Fisher odds vs p) = ink_blue (all genes) / terracotta (viral DE
#           removed).
# Fig3: B (RNAYS waterfall) = slate (points); black highlights for OLD/
#           YOUNG reference genes.
#       C (ribo/mito vs YouthScore, twin axes) = black/"#1a1a1a" (ribo,
#           matches the original) + ink_blue (mito).
#       D (feature importance + Reactome inset) = gene_importance_gradient
#           (multi-color ramp) for bars, gold for the Reactome inset
#           (explicitly not terracotta, which Panel E already uses in this
#           same figure).
#       E (RankScore vs YouthScore) = slate (entire dataset) / terracotta
#           (significant subset).
#       F (rejuvenative fraction violins) = teal -- the one house accent
#           not otherwise used in Figure 3.
# Fig5: A (correlation clustermap) = diverging_corr_cmap() (teal/white/
#           terracotta), dendrogram = REFERENCE_LINE_COLOR.
#       C (CCM ablation scatter) = sequential_accent_cmap(terracotta) for
#           the OddsRatio color axis, slate for the size-legend swatches.
#       D (UMAP, Node2Vec) = diverging_cmap(plum, gold) for the signed
#           slope color axis -- plum/gold rather than diverging_corr_cmap's
#           teal/terracotta, to avoid reusing Fig5 A's already-meaningful
#           correlation colors for an unrelated diverging quantity within
#           the same figure.


def _first_available_font(candidates):
    """First name in `candidates` that's actually installed, so mathtext
    (which -- unlike font.sans-serif -- doesn't take a fallback list) still
    resolves to our real Helvetica stand-in instead of silently falling
    back to matplotlib's default serif math font."""
    installed = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in installed:
            return name
    return candidates[-1]


def apply(base_font_size: int = 11) -> None:
    """Set matplotlib rcParams for all panels in this figure set."""
    mathtext_font = _first_available_font(FONT_STACK)
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": FONT_STACK,
            "font.size": base_font_size,
            "axes.titlesize": base_font_size + 1,
            # Axis labels and tick labels: bold, and +2 over their previous
            # sizes (axes.labelsize was base_font_size / xtick+ytick.labelsize
            # were base_font_size - 1) -- per 2026-09-02 feedback that, side
            # by side at matched pixel size, house-style panels read
            # noticeably thinner/smaller than the original (hand-styled,
            # pre-house-style) Fig2 composite for these two text roles
            # specifically. `axes.labelweight` is a real rcParam and bolds
            # xlabel/ylabel outright; matplotlib has NO equivalent rcParam
            # for tick-label weight (checked: no xtick.labelweight/
            # ytick.labelweight key exists, and the only global lever,
            # font.weight, would also bold legends and any ax.text()
            # annotation that doesn't set its own weight -- broader than
            # what was asked for). So tick-label bolding is applied in
            # despine_clean() below instead, which every panel in this
            # project already calls -- see that function's docstring.
            "axes.labelweight": "bold",
            "axes.labelsize": base_font_size + 10,
            "axes.titlesize": base_font_size+10,
            "axes.titleweight": "bold",
            "xtick.labelsize": base_font_size + 1,
            "ytick.labelsize": base_font_size + 1,
            "legend.fontsize": base_font_size - 1,
            "legend.title_fontsize": base_font_size - 1,
            # Keep text as real, editable text in vector output.
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            # Match mathtext (used for e.g. a superscripted "$^{*}$" in a
            # legend label, bold-rho/italic-p Pearson annotations via
            # fmt_pearson(), or a Greek rho) to the same sans font family --
            # matplotlib's mathtext default is a serif ("cm") face, which
            # would visibly clash with Helvetica/TeX Gyre Heros everywhere
            # else on the page.
            "mathtext.fontset": "custom",
            "mathtext.rm": mathtext_font,
            "mathtext.it": mathtext_font + ":italic",
            "mathtext.bf": mathtext_font + ":bold",
            "mathtext.default": "regular",
            # Clean axes: thin spines, outward ticks, no top/right border.
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.8,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
            "axes.edgecolor": "#333333",
            "text.color": "#1a1a1a",
            "axes.labelcolor": "#1a1a1a",
            "xtick.color": "#333333",
            "ytick.color": "#333333",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "legend.frameon": False,
        }
    )


def despine_clean(ax, extra=()):
    """Belt-and-suspenders despine for axes built outside rcParams control
    (e.g. seaborn axes-level functions sometimes re-add spines).

    Also force-syncs this axes' tick labels AND axis (x/y) labels to the
    house bold/size settings (2026-09-02). Tick labels: bolded here because
    matplotlib has no rcParam for tick-label font weight at all -- checked,
    there is no xtick.labelweight/ytick.labelweight key -- so per-Text via
    get_xticklabels()/get_yticklabels() is the only way, and that needs a
    live Axes to call on.

    Axis labels (xlabel/ylabel) get the same "call it directly on the Text
    object" treatment, even though axes.labelsize/axes.labelweight ARE real
    rcParams -- because of a sharp, non-obvious matplotlib gotcha found
    2026-09-02: an Axis's label Text object is only fully (re)styled from
    current rcParams at certain internal reset points (effectively: whenever
    the Axes itself is created/cleared), NOT on every set_xlabel()/
    set_ylabel() call. So "call style.apply() once, then plot" only works if
    every single fig/ax gets created AFTER that apply() call, in that
    session -- if a panel's `fig, ax = plt.subplots()` line ever runs before
    the current apply() (e.g. reusing axes across notebook cells, or a
    different call order in some helper), the label silently keeps stale
    font properties even though rcParams themselves are correct, changing
    the label's TEXT but not its size/weight. Confirmed by direct test: with
    axes.labelsize/axes.labelweight changed AFTER plt.subplots() but before
    set_xlabel(), the resulting label came back at the OLD default size/
    weight, not the new one -- this is what caused axes.labelsize bumped by
    +50 to visibly do nothing in testing, even after re-importing the style
    module, because re-importing/re-calling apply() does not retroactively
    fix labels on Axes objects that already exist. Setting the Text
    properties directly here, unconditionally, every time a panel finishes
    plotting (rather than trusting rcParams to have been "seen" at the right
    moment) sidesteps the ordering trap entirely -- the same reason tick-
    label bolding above works via direct Text mutation rather than an
    rcParam. axes.labelsize/axes.labelweight in apply() are kept anyway,
    both as the single documented source of truth this function reads from
    and as a belt-and-suspenders in case some Text elsewhere legitimately
    does pick them up fresh.

    Since every panel in this project already calls despine_clean(ax),
    folding both fixes in here means no panel file needs its own separate
    call for this -- EXCEPT a panel that draws its own axis/tick labels but
    never calls despine_clean at all (e.g. a raw/third-party plotting call
    not routed through this project's usual panel-function pattern -- worth
    checking Fig2 Panel C's UMAP code specifically). Such a panel needs its
    own explicit
    `for lbl in ax.get_xticklabels() + ax.get_yticklabels(): lbl.set_fontweight("bold")`
    plus the xaxis/yaxis.label size+weight lines below, or simply a call to
    despine_clean(ax) even if it has no spines to hide.
    """
    for side in ("top", "right", *extra):
        if side in ax.spines:
            ax.spines[side].set_visible(False)
    ax.tick_params(direction="out")
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontweight("normal")
    label_size = mpl.rcParams["axes.labelsize"]
    label_weight = mpl.rcParams["axes.labelweight"]
    for axis_label in (ax.xaxis.label, ax.yaxis.label):
        axis_label.set_fontsize(label_size)
        axis_label.set_fontweight(label_weight)


def despine_twin(ax, ax2, color1, color2):
    """Despine + color-code a twinx() pair so each axis visually announces
    which series it belongs to: `ax` (primary/left) gets its left spine,
    ticks, and y-label colored `color1`; `ax2` (secondary/right) gets its
    right spine, ticks, and y-label colored `color2`. Both top spines are
    hidden; the "wrong-side" spine on each axes (ax's right, ax2's left) is
    hidden too, since twinx() otherwise leaves both visible in the default
    axes-edge color.
    """
    for a in (ax, ax2):
        a.spines["top"].set_visible(False)

    ax.spines["left"].set_color(color1)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="y", colors=color1)
    ax.yaxis.label.set_color(color1)
    ax.tick_params(axis="x", direction="out")

    ax2.spines["right"].set_color(color2)
    ax2.spines["left"].set_visible(False)
    ax2.tick_params(axis="y", colors=color2)
    ax2.yaxis.label.set_color(color2)


def darken(hex_color: str, amount: float = 0.3) -> str:
    """Return `hex_color` blended toward black by `amount` (0-1). Handy for
    a bar/marker edge color that's a darker shade of its own fill rather
    than flat black -- reads as more deliberate than the seaborn/matplotlib
    default black edge."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    r, g, b = (int(c * (1 - amount)) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def fmt_pearson(rho: float, p: float) -> str:
    """Shared house format for an on-plot Pearson annotation: bold rho,
    italic p, two lines, via mathtext -- e.g.:

        ρ = 0.63          (bold)
        p = 0.002         (italic "p"; "< 0.001" below that threshold)

    Used identically everywhere a panel reports rho/p directly on the plot
    (rather than only in a caption), so every panel's stats annotation
    looks and rounds the same way. Depends on apply() having been called
    first, for the bold/italic mathtext fonts to resolve to the house sans
    face rather than matplotlib's default serif math font.
    """
    if p < 0.001:
        p_part = r"$\mathit{p}$ < 0.001"
    else:
        p_part = rf"$\mathit{{p}}$ = {p:.3f}"
    rho_part = rf"$\mathbf{{\rho}}$ = {rho:.2f}"
    return rho_part + "\n" + p_part


def _to_hex_list(colors):
    return [to_hex(c) for c in colors]


def diverging_cmap(low_color: str, high_color: str, mid_color: str = "#ffffff", n: int = 256):
    """A diverging colormap: low_color -> mid_color (white by default) ->
    high_color. Use for any genuinely signed/two-directional quantity with
    a meaningful neutral point at the middle of its range (e.g. a
    correlation, a slope that can be positive or negative). For a
    quantity that only ever moves in one direction, use
    sequential_accent_cmap instead -- see the module docstring's note on
    two real bugs this distinction caught.
    """
    return LinearSegmentedColormap.from_list(
        "house_diverging", [low_color, mid_color, high_color], N=n
    )


def diverging_corr_cmap(n: int = 256):
    """The house diverging colormap for Pearson-correlation-shaped
    quantities specifically: TEAL (negative) / white / TERRACOTTA
    (positive). A dedicated wrapper (rather than always spelling out
    `diverging_cmap(style.TEAL, style.TERRACOTTA)`) so every correlation
    matrix/heatmap in the project uses the exact same two colors without
    each panel re-deciding which house accents "mean" correlation.
    """
    return diverging_cmap(TEAL, TERRACOTTA, n=n)


def sequential_accent_cmap(accent_color: str, low_color: str = "#ffffff", n: int = 256):
    """A sequential colormap: low_color (white by default) -> accent_color.
    Use for any one-directional quantity (a count, an odds ratio, a
    p-value magnitude) -- NOT for a genuinely signed/diverging quantity,
    which should use diverging_cmap instead (see module docstring).
    """
    return LinearSegmentedColormap.from_list(
        "house_sequential", [low_color, accent_color], N=n
    )


def sequential_multihue_cmap(colors=None, n: int = 256):
    """A continuous, multi-hue sequential colormap built from an ORDERED list
    of colors (house ACCENTS in _GRADIENT_ORDER by default) -- for a
    sequential quantity (e.g. a time/quasi-time index) where a single-hue
    ramp (sequential_accent_cmap's white->one-accent) would compress too much
    of the visible range into similar-looking tones. This is the same
    underlying palette as gene_importance_gradient, just returned as a
    continuous Colormap object (usable directly as `c=values, cmap=...`)
    rather than a pre-sampled discrete list of hex colors -- use this one
    when you have a continuous/many-valued quantity to color by (e.g. one
    color per point along a 0..N timepoint axis), and gene_importance_gradient
    when you need a fixed small number of maximally-distinct categorical
    swatches (e.g. one per cluster/community).

    Still a genuinely SEQUENTIAL shape (colors are traversed in one fixed
    order, no meaningful "zero" in the middle) -- don't reach for this on a
    signed/diverging quantity; use diverging_cmap for that instead.
    """
    if colors is None:
        colors = _GRADIENT_ORDER
    return LinearSegmentedColormap.from_list(
        "house_multihue_sequential", _to_hex_list(colors), N=n
    )


def clean_3d_axes(ax, pane_color="white", grid_color="#dddddd", grid_linewidth=0.4):
    """House cleanup for a 3D (mplot3d) axes: replaces the default gray
    shaded panes + heavy gridlines with plain white panes and faint,
    restrained gridlines (matching this project's "gridlines only where they
    aid reading, never the seaborn/matplotlib default gray" convention for
    2D axes -- mplot3d just needs its own explicit version of the same
    idea, since none of the usual rcParams in apply() reach Axes3D's panes).
    """
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor(pane_color)
        axis.pane.set_edgecolor(pane_color)
        axis._axinfo["grid"]["color"] = grid_color
        axis._axinfo["grid"]["linewidth"] = grid_linewidth


def highlight_ring_3d(
    ax,
    points,
    cluster_mask,
    elev,
    azim,
    pad: float = 1.5,
    extra_margin_frac: float = 0.10,
    n: int = 200,
    color=None,
    linestyle: str = "solid",
    linewidth: float = 2.2,
    zorder: int = 10,
):
    """Draw a flat elliptical ring in 3D, in the viewing plane for the given
    `elev`/`azim` (the same numbers passed to `ax.view_init`), fit to enclose
    `points[cluster_mask]` -- the programmatic version of hand-tracing a red
    ellipse around a spatially-close cluster of points in a 3D delay
    embedding (Fig1 D_left/D_middle). Because the ring is built to lie
    exactly in the plane perpendicular to the chosen view direction, it
    renders as a clean ellipse from that view regardless of the cluster's
    actual 3D shape -- draw it AFTER calling `ax.view_init(elev, azim)` with
    the same elev/azim, and don't change the view afterward. Safe to call
    more than once on the same axes (different `cluster_mask`/`color`
    /`linestyle` each time) to highlight several clusters in one panel --
    pass a different `linestyle` per ring (e.g. "solid" / "dashed") in
    addition to a different `color`, so which ring is which still reads
    correctly in grayscale or for a colorblind viewer (the project's usual
    redundant-encoding convention).

    `points` is the full (n_points, 3) array used for the panel's delay
    embedding (already in whatever units/scale -- e.g. log10 -- the panel
    plots), NOT just the cluster's own points -- the full set is used to
    estimate the panel's overall scale for `extra_margin_frac` (see below).
    `cluster_mask` is a boolean mask selecting the highlighted points.

    Sizing the ellipse -- two components, both matter:
      - `pad` (>1): multiplies the ellipse up from the tightest enclosing
        size (fit to the cluster's own point CENTERS). By itself this isn't
        enough for a visibly clean ring: a very tight cluster's centers-only
        footprint can be smaller than the plotted marker dots and time-index
        labels themselves, so a ring sized only to the centers can slice
        right through a data point's circle or its label text.
      - `extra_margin_frac`: an ADDITIVE margin, as a fraction of the whole
        panel's own on-screen spread (estimated from ALL of `points`, not
        just the cluster) -- this is what actually guarantees clearance
        around marker dots and labels regardless of how tight the cluster
        is, and it scales automatically with each panel's own data range
        rather than needing a hand-tuned absolute number. Raise this (or
        `pad`) if a ring is still clipping a point/label at your marker size
        /label offset; the defaults here were tuned against this project's
        own point_size/label settings in fig1_panelD_leftmiddle_delay_embedding.py.

    Uses HIGHLIGHT_RING_COLOR by default -- pass `color` to override (e.g.
    HIGHLIGHT_RING_COLOR_ALT for a second ring in the same panel), but see
    those constants' docstrings for why they're kept separate from ACCENTS
    and REFERENCE_LINE_COLOR.

    The view-direction math assumes the standard mplot3d spherical
    convention (elev = angle above the xy-plane, azim = rotation about z);
    confirmed against `ax.get_proj()` under `ax.set_proj_type('ortho')`, and
    intended for use with an orthographic 3D axes (a perspective projection
    will still look reasonable but is not the geometry this was verified
    against).
    """
    color = color or HIGHLIGHT_RING_COLOR
    points = np.asarray(points, dtype=float)
    cluster_mask = np.asarray(cluster_mask, dtype=bool)
    cluster_pts = points[cluster_mask]

    elev_r, azim_r = np.radians(elev), np.radians(azim)
    v = np.array(
        [np.cos(elev_r) * np.cos(azim_r), np.cos(elev_r) * np.sin(azim_r), np.sin(elev_r)]
    )
    z_hat = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(v, z_hat)) > 0.999:
        z_hat = np.array([0.0, 1.0, 0.0])
    r_hat = np.cross(v, z_hat)
    r_hat /= np.linalg.norm(r_hat)
    u_hat = np.cross(r_hat, v)
    u_hat /= np.linalg.norm(u_hat)

    # Overall panel spread (ALL points, not just the cluster) in this same
    # view plane -- the scale that extra_margin_frac is a fraction of.
    all_rel = points - points.mean(axis=0)
    all_proj2d = np.column_stack([all_rel @ r_hat, all_rel @ u_hat])
    overall_scale = all_proj2d.max(axis=0) - all_proj2d.min(axis=0)
    extra_margin = extra_margin_frac * overall_scale.mean()

    centroid = cluster_pts.mean(axis=0)
    rel = cluster_pts - centroid
    proj2d = np.column_stack([rel @ r_hat, rel @ u_hat])

    # PCA in the (r_hat, u_hat) view plane -- ellipse axes follow the
    # cluster's actual in-view spread rather than an axis-aligned box, and
    # each semi-axis is sized to the max projection onto it (times `pad`,
    # plus the flat extra_margin above), guaranteeing every cluster point
    # -- and a visible gap beyond it -- is enclosed, not just the centers.
    cov = np.cov(proj2d.T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    order = np.argsort(eigvals)[::-1]
    eigvecs = eigvecs[:, order]
    proj_pc = proj2d @ eigvecs
    semi_axes = np.abs(proj_pc).max(axis=0) * pad + extra_margin
    semi_axes = np.maximum(semi_axes, 1e-6)

    theta = np.linspace(0, 2 * np.pi, n)
    ring_pc = np.column_stack([semi_axes[0] * np.cos(theta), semi_axes[1] * np.sin(theta)])
    ring_2d = ring_pc @ eigvecs.T  # back into the (r_hat, u_hat) frame
    ring_3d = centroid + ring_2d[:, [0]] * r_hat + ring_2d[:, [1]] * u_hat

    ax.plot(
        ring_3d[:, 0],
        ring_3d[:, 1],
        ring_3d[:, 2],
        color=color,
        linestyle=linestyle,
        linewidth=linewidth,
        zorder=zorder,
        solid_capstyle="round",
    )


def gene_importance_gradient(n: int):
    """Return `n` colors sampled evenly along a smooth ramp built from the
    house ACCENTS (in _GRADIENT_ORDER) -- for panels that need many
    distinct categorical colors (e.g. one per gene cluster/community) while
    still reading as part of the same coordinated palette as every other
    panel, rather than a literal rainbow / default categorical cycle.
    """
    if n <= 0:
        return []
    cmap = LinearSegmentedColormap.from_list("gene_importance", _GRADIENT_ORDER)
    if n == 1:
        return [to_hex(cmap(0.5))]
    return _to_hex_list(cmap(t) for t in np.linspace(0.0, 1.0, n))
