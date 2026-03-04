import curses
import queue
import threading
import time
from typing import List, Tuple

from tui.constants import (
    ANALYSIS_STAGES, LOG_COLORS, HINT_LOG, HINT_CHOOSE,
    C_MUTED, C_SUCCESS, C_ACCENT, C_LABEL, C_NORMAL, C_HIGHLIGHT,
)
from tui.drawing import safe_addstr, draw_banner, draw_box, draw_hint

from pipeline.data import Data
from pipeline.hmm import HMMPipeline

d = Data()
hmm_pipeline = HMMPipeline()

def _run_analysis(cfg, log_q: queue.Queue, progress_q: queue.Queue):
    log_q.put(("HEADER", "─" * 58))
    log_q.put(("HEADER", f"  Market Regime Analysis  ·  {cfg.ticker}"))
    log_q.put(("HEADER", "─" * 58))
    log_q.put(("INFO",   f"  Asset type        {cfg.asset_type.title()}"))
    log_q.put(("INFO",   f"  Start date        {cfg.start_date}"))
    log_q.put(("INFO",   f"  End date          {cfg.end_date}"))
    log_q.put(("INFO",   f"  Data cardinality  {cfg.data_cardinality_label}  (yfinance: '{cfg.data_cardinality}')"))
    log_q.put(("INFO",   f"  Features          {cfg.feature_set}"))
    log_q.put(("INFO",   f"  Obs. interval     {cfg.regime_interval}"))
    log_q.put(("INFO",   f"  Output            {cfg.output_path}"))
    log_q.put(("HEADER", "─" * 58))

    log_q.put(("INFO", "  [01/02]  Retrieving market & macro data…"))
    data = d.run(cfg)

    if data is None:
        log_q.put(("WARN", "  ⚠  Data retrieval returned empty — nothing saved"))
        progress_q.put(1.0)
        progress_q.put(None)
        return

    log_q.put(("OK", f"  ✓  Data retrieved  ({len(data)} rows)"))
    progress_q.put(0.5)

    log_q.put(("INFO", "  [02/02]  Fitting rolling window HMM…"))
    results = hmm_pipeline.run(data=data, config=cfg)

    if results is None:
        log_q.put(("WARN", "  ⚠  HMM produced no results — nothing saved"))
        progress_q.put(1.0)
        progress_q.put(None)
        return

    try:
        results.to_csv(cfg.output_path)
        log_q.put(("OK", f"  ✓  {len(results)} regime records computed"))
        log_q.put(("OK", f"  ✓  Saved → {cfg.output_path}"))
    except Exception as exc:
        log_q.put(("WARN", f"  ⚠  Could not save results: {exc}"))

    log_q.put(("HEADER", "─" * 58))
    log_q.put(("OK",     "  ✔  Analysis complete"))
    log_q.put(("HEADER", "─" * 58))
    progress_q.put(1.0)
    progress_q.put(None)


def progress_screen(stdscr, cfg):
    log_q      = queue.Queue()
    progress_q = queue.Queue()
    log_lines: List[Tuple[str, str]] = []
    progress   = 0.0
    done       = False
    log_scroll = 0

    threading.Thread(
        target=_run_analysis,
        args=(cfg, log_q, progress_q),
        daemon=True,
    ).start()

    stdscr.nodelay(True)
    SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    while True:
        while not progress_q.empty():
            val = progress_q.get_nowait()
            if val is None:
                done = True
            else:
                progress = val
        while not log_q.empty():
            log_lines.append(log_q.get_nowait())

        stdscr.erase()
        h, w = stdscr.getmaxyx()

        banner_end = draw_banner(stdscr, 1)

        title = ("  ✔  Analysis Complete  " if done
                 else "  Running HMM Analysis…  ")
        safe_addstr(stdscr, banner_end + 1,
                    (w - len(title)) // 2, title,
                    curses.color_pair(C_LABEL) | curses.A_BOLD)

        pb_y   = banner_end + 3
        pb_w   = min(64, w - 8)
        pb_x   = (w - pb_w) // 2
        filled = int(pb_w * progress)
        bar    = "█" * filled + "░" * (pb_w - filled)
        pct    = int(progress * 100)

        safe_addstr(stdscr, pb_y, pb_x, bar,
                    curses.color_pair(C_SUCCESS if done else C_ACCENT))
        indicator = ("✔" if done
                     else SPINNER[int(time.time() * 10) % len(SPINNER)])
        safe_addstr(stdscr, pb_y, pb_x + pb_w + 2, indicator,
                    curses.color_pair(C_SUCCESS if done else C_ACCENT) | curses.A_BOLD)
        pct_label = f" {pct}% "
        safe_addstr(stdscr, pb_y + 1,
                    (w - len(pct_label)) // 2, pct_label,
                    curses.color_pair(C_MUTED))

        log_y  = pb_y + 3
        log_bw = min(pb_w + 12, w - 4)
        log_bx = (w - log_bw) // 2
        log_h  = max(2, h - log_y - 4)

        draw_box(stdscr, log_y, log_bx, log_h + 1, log_bw, "  Event Log  ")

        max_scroll = max(0, len(log_lines) - log_h)
        if log_scroll >= max_scroll - 1:
            log_scroll = max_scroll

        visible = log_lines[log_scroll: log_scroll + log_h]
        for i, (level, text) in enumerate(visible):
            color = curses.color_pair(LOG_COLORS.get(level, C_NORMAL))
            if level in ("HEADER", "OK"):
                color |= curses.A_BOLD
            safe_addstr(stdscr, log_y + 1 + i, log_bx + 2, text, color)

        if len(log_lines) > log_h:
            badge = (f" ↑↓  {log_scroll+1}–"
                     f"{min(log_scroll+log_h, len(log_lines))}"
                     f"/{len(log_lines)} ")
            safe_addstr(stdscr, log_y + log_h,
                        log_bx + log_bw - len(badge) - 1,
                        badge, curses.color_pair(C_MUTED))

        if done:
            draw_hint(stdscr, HINT_LOG)
        else:
            draw_hint(stdscr,
                      [("↑↓", "Scroll log"), ("", "Running — please wait")])

        stdscr.refresh()

        key = stdscr.getch()
        if key in (curses.KEY_UP, ord('k')):
            log_scroll = max(0, log_scroll - 1)
        elif key in (curses.KEY_DOWN, ord('j')):
            log_scroll = min(max_scroll, log_scroll + 1)
        elif key in (ord('q'), ord('Q')) and done:
            break

        time.sleep(0.08)

    stdscr.nodelay(False)


def confirm_screen(stdscr, config: dict):
    cursor = 0
    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        banner_end = draw_banner(stdscr, 1)
        box_w = min(76, w - 4)
        box_x = (w - box_w) // 2
        box_y = banner_end + 3
        rows  = list(config.items())
        box_h = len(rows) + 4
        draw_box(stdscr, box_y, box_x, box_h, box_w, "  Configuration Summary  ")

        for i, (k, v) in enumerate(rows):
            ky = box_y + 2 + i
            safe_addstr(stdscr, ky, box_x + 3,
                        f"{k:<24}", curses.color_pair(C_MUTED))
            safe_addstr(stdscr, ky, box_x + 28,
                        str(v), curses.color_pair(C_ACCENT) | curses.A_BOLD)

        btn_y   = box_y + box_h + 2
        buttons = ["  ✔  Run Analysis  ", "  ✗  Go Back  "]
        total_w = sum(len(b) for b in buttons) + 6
        bx      = (w - total_w) // 2
        for bi, btn in enumerate(buttons):
            attr = (curses.color_pair(C_HIGHLIGHT) | curses.A_BOLD
                    if bi == cursor else curses.color_pair(C_MUTED))
            safe_addstr(stdscr, btn_y, bx, btn, attr)
            bx += len(btn) + 3

        draw_hint(stdscr, HINT_CHOOSE)
        stdscr.refresh()

        key = stdscr.getch()
        if key in (curses.KEY_LEFT,  ord('h')): cursor = 0
        elif key in (curses.KEY_RIGHT, ord('l')): cursor = 1
        elif key in (curses.KEY_ENTER, 10, 13):  return cursor == 0
        elif key in (ord('q'), ord('Q'), 27):    raise SystemExit(0)
