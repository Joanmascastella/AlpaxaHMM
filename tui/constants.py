from config.colors import RunTimeColorPallete
from config.options import RunTimeOptions

_cp = RunTimeColorPallete()
C_NORMAL    = _cp.C_NORMAL
C_TITLE     = _cp.C_TITLE
C_HIGHLIGHT = _cp.C_HIGHLIGHT
C_MUTED     = _cp.C_MUTED
C_SUCCESS   = _cp.C_SUCCESS
C_ACCENT    = _cp.C_ACCENT
C_BORDER    = _cp.C_BORDER
C_LABEL     = _cp.C_LABEL
C_ERROR     = _cp.C_ERROR
C_WARN      = _cp.C_WARN
C_HINT_BAR  = _cp.C_HINT_BAR

_op = RunTimeOptions()
INDEXES            = _op.indexes
SECTOR_ETFS        = _op.sector_etfs
COMMODITIES        = _op.commodities
DATA_CARDINALITIES = _op.data_cardinalities
INTERVALS          = _op.intervals
FEATURE_SETS       = _op.feature_sets
STEPS              = _op.steps
HINT_NAV           = _op.HINT_NAV
HINT_INPUT         = _op.HINT_INPUT
HINT_CHOOSE        = _op.HINT_CHOOSE
HINT_LOG           = _op.HINT_LOG

BANNER = r"""
   █████╗ ██╗     ██████╗  █████╗ ██╗  ██╗ █████╗ 
  ██╔══██╗██║     ██╔══██╗██╔══██╗╚██╗██╔╝██╔══██╗
  ███████║██║     ██████╔╝███████║ ╚███╔╝ ███████║
  ██╔══██║██║     ██╔═══╝ ██╔══██║ ██╔██╗ ██╔══██║
  ██║  ██║███████╗██║     ██║  ██║██╔╝ ██╗██║  ██║
  ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
        M A R K E T   R E G I M E   F R A M E W O R K   v1.0
"""

ANALYSIS_STAGES = [
    ("Fetching market data",          2.2),
    ("Cleaning & aligning series",    1.4),
    ("Computing feature matrix",      1.8),
    ("Normalising features",          0.8),
    ("Initialising HMM parameters",   0.6),
    ("Running Baum-Welch EM",         3.5),
    ("Decoding hidden state path",    1.2),
    ("Labelling regime periods",      0.9),
    ("Generating summary statistics", 0.7),
    ("Writing results to disk",       1.0),
]

LOG_COLORS = {
    "INFO":   C_MUTED,
    "OK":     C_SUCCESS,
    "WARN":   C_WARN,
    "ERROR":  C_ERROR,
    "HEADER": C_ACCENT,
}
