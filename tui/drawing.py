import curses
from typing import List, Tuple

from tui.constants import (
    BANNER, STEPS,
    C_TITLE, C_HIGHLIGHT, C_MUTED, C_SUCCESS,
    C_ACCENT, C_BORDER, C_LABEL, C_ERROR, C_WARN, C_HINT_BAR,
    C_NORMAL,
)


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    bg = -1
    curses.init_pair(C_NORMAL,    curses.COLOR_WHITE,  bg)
    curses.init_pair(C_TITLE,     curses.COLOR_CYAN,   bg)
    curses.init_pair(C_HIGHLIGHT, curses.COLOR_BLACK,  curses.COLOR_CYAN)
    curses.init_pair(C_MUTED,     8,                   bg)
    curses.init_pair(C_SUCCESS,   curses.COLOR_GREEN,  bg)
    curses.init_pair(C_ACCENT,    curses.COLOR_CYAN,   bg)
    curses.init_pair(C_BORDER,    curses.COLOR_CYAN,   bg)
    curses.init_pair(C_LABEL,     curses.COLOR_YELLOW, bg)
    curses.init_pair(C_ERROR,     curses.COLOR_RED,    bg)
    curses.init_pair(C_WARN,      curses.COLOR_YELLOW, bg)
    curses.init_pair(C_HINT_BAR,  curses.COLOR_WHITE,  curses.COLOR_BLACK)


def safe_addstr(win, y, x, text, attr=0):
    h, w = win.getmaxyx()
    if y < 0 or y >= h or x < 0 or x >= w:
        return
    available = w - x
    if y == h - 1:
        available = min(available, w - x - 1)
    if available <= 0:
        return
    try:
        win.addstr(y, x, text[:available], attr)
    except curses.error:
        pass


def draw_banner(win, start_y=0):
    lines = BANNER.strip("\n").split("\n")
    _, w  = win.getmaxyx()
    for i, line in enumerate(lines):
        x = max(0, (w - len(line)) // 2)
        safe_addstr(win, start_y + i, x, line,
                    curses.color_pair(C_TITLE) | curses.A_BOLD)
    return start_y + len(lines)


def draw_progress_bar(win, current_step, total_steps, y):
    _, w   = win.getmaxyx()
    bar_w  = min(60, w - 4)
    filled = int(bar_w * current_step / total_steps)
    label  = f" Step {current_step}/{total_steps} "
    bar    = "█" * filled + "░" * (bar_w - filled)
    x = (w - bar_w) // 2
    safe_addstr(win, y,     x, bar,   curses.color_pair(C_ACCENT))
    safe_addstr(win, y + 1, (w - len(label)) // 2, label,
                curses.color_pair(C_MUTED))


def draw_breadcrumb(win, current_idx, y):
    _, w  = win.getmaxyx()
    parts = []
    for i, name in enumerate(STEPS):
        if i < current_idx:
            parts.append(("✓ " + name, C_SUCCESS))
        elif i == current_idx:
            parts.append(("▶ " + name, C_LABEL))
        else:
            parts.append(("  " + name, C_MUTED))

    sep       = "  │  "
    total_len = sum(len(t) for t, _ in parts) + len(sep) * (len(parts) - 1)
    x = max(0, (w - total_len) // 2)
    for idx, (text, color) in enumerate(parts):
        attr = curses.color_pair(color)
        if color == C_LABEL:
            attr |= curses.A_BOLD
        safe_addstr(win, y, x, text, attr)
        x += len(text)
        if idx < len(parts) - 1:
            safe_addstr(win, y, x, sep, curses.color_pair(C_MUTED))
            x += len(sep)


def draw_box(win, y, x, h, w, title=""):
    attr = curses.color_pair(C_BORDER)
    safe_addstr(win, y,     x, "╭" + "─" * (w - 2) + "╮", attr)
    safe_addstr(win, y + h, x, "╰" + "─" * (w - 2) + "╯", attr)
    for row in range(1, h):
        safe_addstr(win, y + row, x,         "│", attr)
        safe_addstr(win, y + row, x + w - 1, "│", attr)
    if title:
        t  = f" {title} "
        tx = x + (w - len(t)) // 2
        safe_addstr(win, y, tx, t, curses.color_pair(C_LABEL) | curses.A_BOLD)


def draw_hint(win, segments: List[Tuple[str, str]]):
    h, w = win.getmaxyx()
    safe_addstr(win, h - 1, 0, " " * (w - 1), curses.color_pair(C_HINT_BAR))
    parts = [f"  {key}  {desc}  " for key, desc in segments]
    full  = "│".join(parts)
    x = max(0, (w - len(full)) // 2)
    for i, (key, desc) in enumerate(segments):
        seg_key  = f"  {key}"
        seg_desc = f"  {desc}  "
        safe_addstr(win, h - 1, x, seg_key,
                    curses.color_pair(C_HINT_BAR) | curses.A_BOLD)
        x += len(seg_key)
        safe_addstr(win, h - 1, x, seg_desc, curses.color_pair(C_HINT_BAR))
        x += len(seg_desc)
        if i < len(segments) - 1:
            safe_addstr(win, h - 1, x, "│", curses.color_pair(C_HINT_BAR))
            x += 1
