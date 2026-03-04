import curses
import os

from config.regime import RegimeConfig
from utils.validators import RunTimeUtils
from tui.constants import DATA_CARDINALITIES, FEATURE_SETS, INDEXES, SECTOR_ETFS, COMMODITIES, INTERVALS
from tui.drawing import init_colors
from tui.widgets import select_menu, text_input
from tui.screens import confirm_screen, progress_screen

rtU = RunTimeUtils()


def run_flow(stdscr):
    curses.curs_set(0)
    init_colors()
    stdscr.keypad(True)
    cfg = RegimeConfig()

    # Step 1 — Asset Type
    cfg.asset_type = select_menu(
        stdscr, "Step 1 — Select Asset Type",
        [("equity",    "Equity  (individual stock)"),
         ("index",     "Index / Sector ETF"),
         ("commodity", "Commodity")],
        descriptions=[
            "Enter any listed equity ticker symbol on the next screen.",
            "Choose from a curated list of supported indexes and sector ETFs.",
            "Choose from a curated list of supported commodity instruments.",
        ],
        step_idx=0,
    )

    # Step 2 — Ticker
    if cfg.asset_type == "equity":
        cfg.ticker = text_input(
            stdscr, "Step 2 — Enter Equity Ticker", "Ticker symbol",
            validator=rtU.validate_ticker, step_idx=1).upper()
    elif cfg.asset_type == "index":
        cfg.ticker = select_menu(
            stdscr, "Step 2 — Select Index / Sector ETF",
            [(v, f"{v:<6}  {l}") for v, l in INDEXES + SECTOR_ETFS],
            step_idx=1)
    else:
        cfg.ticker = select_menu(
            stdscr, "Step 2 — Select Commodity",
            [(v, f"{v:<6}  {l}") for v, l in COMMODITIES],
            step_idx=1)

    # Step 3 — Time Window
    cfg.start_date = text_input(
        stdscr, "Step 3 — Enter Start Date", "Start date  (YYYY/MM/DD)",
        validator=rtU.validate_date, step_idx=2)

    cfg.end_date = text_input(
        stdscr, "Step 3 — Enter End Date", "End date    (YYYY/MM/DD)",
        validator=rtU.validate_date, step_idx=2)

    # Step 4 — Data Cardinality
    cfg.data_cardinality = select_menu(
        stdscr, "Step 4 — Select Data Cardinality",
        [(yf, f"{label:<12}  {desc}") for yf, label, desc in DATA_CARDINALITIES],
        descriptions=[desc for _, _, desc in DATA_CARDINALITIES],
        step_idx=3,
    )
    cfg.data_cardinality_label = next(
        label for yf, label, _ in DATA_CARDINALITIES
        if yf == cfg.data_cardinality
    )

    # Step 5 — Feature Set
    cfg.feature_set = select_menu(
        stdscr, "Step 5 — Select HMM Feature Set",
        [(v, label) for v, label, _ in FEATURE_SETS],
        descriptions=[d for _, _, d in FEATURE_SETS],
        step_idx=4)

    # Step 6 — Regime Observation Interval
    cfg.regime_interval = select_menu(
        stdscr, "Step 6 — Select Regime Observation Interval",
        INTERVALS, step_idx=5)

    # Step 7 — Output Path
    default_path = os.path.join(
        os.path.expanduser("~"), f"regime_{cfg.ticker.lower()}.csv")
    cfg.output_path = text_input(
        stdscr, "Step 7 — Output File Path", "Save path",
        validator=rtU.validate_path, placeholder=default_path, step_idx=6)

    # Confirm
    feature_label = next(l for v, l, _ in FEATURE_SETS if v == cfg.feature_set)
    summary = {
        "Asset":            cfg.ticker,
        "Asset Type":       cfg.asset_type.title(),
        "Start Date":       cfg.start_date,
        "End Date":         cfg.end_date,
        "Data Cardinality": f"{cfg.data_cardinality_label}  ('{cfg.data_cardinality}')",
        "HMM Features":     feature_label,
        "Regime Interval":  cfg.regime_interval,
        "Output Path":      cfg.output_path,
    }

    confirmed = confirm_screen(stdscr, summary)
    if not confirmed:
        return run_flow(stdscr)

    progress_screen(stdscr, cfg)
    return cfg
