import curses
import textwrap

from tui.constants import (
    STEPS, HINT_NAV, HINT_INPUT,
    C_NORMAL, C_HIGHLIGHT, C_MUTED, C_ACCENT, C_LABEL, C_ERROR,
)
from tui.drawing import (
    safe_addstr, draw_banner, draw_breadcrumb, draw_progress_bar,
    draw_box, draw_hint,
)


def select_menu(stdscr, title, options, descriptions=None, step_idx=0):
    items = [o if isinstance(o, tuple) else (o, o) for o in options]
    cursor, scroll = 0, 0

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        banner_end   = draw_banner(stdscr, 1)
        draw_breadcrumb(stdscr, step_idx, banner_end + 1)
        draw_progress_bar(stdscr, step_idx + 1, len(STEPS), banner_end + 3)

        box_y        = banner_end + 6
        box_w        = min(70, w - 4)
        visible_rows = max(1, h - box_y - 6)
        box_h        = visible_rows + 2
        box_x        = (w - box_w) // 2
        draw_box(stdscr, box_y, box_x, box_h, box_w, title)

        if cursor < scroll:
            scroll = cursor
        if cursor >= scroll + visible_rows:
            scroll = cursor - visible_rows + 1

        for i in range(visible_rows):
            idx = scroll + i
            if idx >= len(items):
                break
            _, label  = items[idx]
            row_y     = box_y + 1 + i
            indicator = "  ❯ " if idx == cursor else "    "
            if idx == cursor:
                attr = curses.color_pair(C_HIGHLIGHT) | curses.A_BOLD
                safe_addstr(stdscr, row_y, box_x + 1, " " * (box_w - 2), attr)
            else:
                attr = curses.color_pair(C_NORMAL)
            safe_addstr(stdscr, row_y, box_x + 2, indicator + label, attr)

        if descriptions and 0 <= cursor < len(descriptions):
            desc_y = box_y + box_h + 2
            if desc_y < h - 2:
                for li, line in enumerate(
                        textwrap.wrap(descriptions[cursor], box_w - 4)[:2]):
                    safe_addstr(stdscr, desc_y + li, box_x + 2, line,
                                curses.color_pair(C_MUTED) | curses.A_ITALIC)

        draw_hint(stdscr, HINT_NAV)
        stdscr.refresh()

        key = stdscr.getch()
        if key in (curses.KEY_UP, ord('k')):
            cursor = (cursor - 1) % len(items)
        elif key in (curses.KEY_DOWN, ord('j')):
            cursor = (cursor + 1) % len(items)
        elif key in (curses.KEY_ENTER, 10, 13):
            return items[cursor][0]
        elif key in (ord('q'), ord('Q'), 27):
            raise SystemExit(0)


def text_input(stdscr, title, prompt, validator=None, placeholder="", step_idx=0):
    buf, error = list(placeholder), ""

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        banner_end = draw_banner(stdscr, 1)
        draw_breadcrumb(stdscr, step_idx, banner_end + 1)
        draw_progress_bar(stdscr, step_idx + 1, len(STEPS), banner_end + 3)

        box_y = banner_end + 6
        box_w = min(70, w - 4)
        box_x = (w - box_w) // 2
        draw_box(stdscr, box_y, box_x, 5, box_w, title)

        safe_addstr(stdscr, box_y + 2, box_x + 3,
                    prompt + "  ", curses.color_pair(C_LABEL) | curses.A_BOLD)
        px      = box_x + 3 + len(prompt) + 2
        field_w = max(1, box_w - (px - box_x) - 3)
        display = "".join(buf)[-field_w:]
        safe_addstr(stdscr, box_y + 2, px, display,
                    curses.color_pair(C_ACCENT) | curses.A_UNDERLINE)

        if error:
            safe_addstr(stdscr, box_y + 4, box_x + 3,
                        "⚠  " + error, curses.color_pair(C_ERROR))

        draw_hint(stdscr, HINT_INPUT)
        curses.curs_set(1)
        try:
            stdscr.move(box_y + 2, min(px + len(display), w - 2))
        except curses.error:
            pass
        stdscr.refresh()

        key = stdscr.getch()
        if key in (curses.KEY_ENTER, 10, 13):
            value = "".join(buf).strip()
            if validator:
                err = validator(value)
                if err:
                    error = err
                    continue
            curses.curs_set(0)
            return value
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if buf:
                buf.pop()
            error = ""
        elif key in (ord('q'), ord('Q'), 27) and not buf:
            curses.curs_set(0)
            raise SystemExit(0)
        elif 32 <= key <= 126:
            buf.append(chr(key))
            error = ""


def number_input(stdscr, title, prompt, min_val=1, max_val=9999, step_idx=0):
    def validate(v):
        if not v.isdigit():
            return "Please enter a whole number."
        if not (min_val <= int(v) <= max_val):
            return f"Must be between {min_val} and {max_val}."
        return ""
    return int(text_input(stdscr, title, prompt,
                          validator=validate, step_idx=step_idx))
