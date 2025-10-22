# core/log_utils.py
from datetime import datetime

# Terminal Colours
class TermColors:
    RESET = "\033[0m"
    RED = "\033[38;5;203m"       # pastel red
    GREEN = "\033[38;5;120m"     # soft green
    YELLOW = "\033[38;5;227m"    # pastel yellow
    BLUE = "\033[38;5;117m"      # pastel blue
    MAGENTA = "\033[38;5;177m"   # pastel magenta
    CYAN = "\033[38;5;159m"      # pastel cyan
    WHITE = "\033[38;5;255m"     # bright white
    ORANGE = "\033[38;5;215m"    # soft orange

PASTEL_GUI_COLORS = {
    "timestamp": "#FFAF5F",        # orange (TermColors.ORANGE)
    "level_info": "#FFFFFF",       # white (TermColors.WHITE)
    "level_warn": "#FFFFAF",       # yellow (TermColors.YELLOW)
    "level_error": "#FF87AF",      # red (TermColors.RED)
    "level_success": "#87FF87",    # green (TermColors.GREEN)
    "level_conversion": "#5FD7FF"  # cyan (TermColors.CYAN)
}

def gui_log(log_box, message, level="level_info"):
    """
    Inserts a message into the GUI log box with a specified tag.
    Assumes the Text widget already has tags configured from PASTEL_GUI_COLORS.
    """
    if not log_box:
        return

    log_box.insert("end", message + "\n", level)
    log_box.see("end")
    log_box.update_idletasks()
