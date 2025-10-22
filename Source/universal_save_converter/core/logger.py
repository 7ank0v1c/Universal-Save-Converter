# core/logger.py

import os
from datetime import datetime
from core.log_utils import TermColors, gui_log
from core.gui_logger import log_widget as global_log_widget, PASTEL_GUI_COLORS

LOG_FILE = "conversion_log.txt"

def setup_logging():
    """Ensure the log file exists."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("=== Conversion Log Initialized ===\n")

def log(message, *, level="INFO", log_box=None):
    """
    Logs a message to:
    1. Terminal (with color)
    2. GUI Text widget (if provided or global)
    3. File
    Supports custom levels for future expandability.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] [{level}] {message}"

    # --- Terminal logging ---
    term_colors = {
        "INFO": TermColors.WHITE,
        "WARN": TermColors.YELLOW,
        "ERROR": TermColors.RED,
        "SUCCESS": TermColors.GREEN,
        "CONVERSION": TermColors.CYAN
    }
    color = term_colors.get(level, TermColors.WHITE)
    print(f"{TermColors.ORANGE}[{timestamp}]{TermColors.RESET} {color}{message}{TermColors.RESET}", flush=True)

    # --- GUI logging ---
    active_log_box = log_box or global_log_widget
    if active_log_box:
        # Insert timestamp separately (always orange)
        active_log_box.insert("end", f"[{timestamp}] ", "timestamp")
        # Insert message with level tag
        level_map = {
            "INFO": "level_info",
            "WARN": "level_warn",
            "ERROR": "level_error",
            "SUCCESS": "level_success",
            "CONVERSION": "level_conversion"
        }
        gui_level = level_map.get(level, "level_info")
        active_log_box.insert("end", f"{message}\n", gui_level)
        active_log_box.see("end")
        active_log_box.update_idletasks()

    # --- File logging ---
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_message + "\n")