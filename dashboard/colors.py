"""Color tokens, lifted from the dataviz skill's validated default palette
(light mode). Keep hues assigned by fixed role, never cycled or reassigned
by rank - see the skill's color-formula.md for why.
"""

# Categorical - fixed order, slots 1-4. Surfaces (Hard/Clay/Grass, rarely
# Carpet) fit inside the first 3 slots, which is the range validated for
# all-pairs comparison (bar charts put every category on screen at once).
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]

SURFACE_COLOR = {
    "Hard": CATEGORICAL[0],
    "Clay": CATEGORICAL[1],
    "Grass": CATEGORICAL[2],
    "Carpet": CATEGORICAL[3],
}

SEQUENTIAL_BLUE = "#2a78d6"

# Status colors are reserved for win/loss state, never reused as "series 4".
STATUS_GOOD = "#0ca30c"
STATUS_CRITICAL = "#d03b3b"

INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
CHART_SURFACE = "#fcfcfb"
