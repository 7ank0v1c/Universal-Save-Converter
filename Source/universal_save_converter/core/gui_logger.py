from datetime import datetime
from core.log_utils import gui_log, PASTEL_GUI_COLORS
from core.theme_utils import current_mode

# Global reference to the active Text widget
log_widget = None

def set_log_widget(widget):
    """Assign the GUI log Text widget for logging."""
    global log_widget
    log_widget = widget

    # Set initial background based on theme
    update_log_bg()

    # Configure pastel color tags (foreground only, bg handled by widget)
    for tag, color in PASTEL_GUI_COLORS.items():
        log_widget.tag_config(tag, foreground=color)

def update_log_bg():
    """Update logger background based on current theme."""
    if not log_widget:
        return
    # Replace with your dark/light mode detection
    bg_color = "#1E1E1E" if current_mode == "dark" else "#FFFFFF"
    log_widget.config(bg=bg_color)

def _log(msg, level="level_info"):
    """Internal helper to log with timestamp to the global log widget."""
    if not log_widget:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_widget.insert("end", f"[{timestamp}] ", "timestamp")  # timestamp tag
    gui_log(log_widget, msg, level=level)                     # message with tag

# Convenience functions
def info(msg):       _log(msg, level="level_info")
def success(msg):    _log(msg, level="level_success")
def warn(msg):       _log(msg, level="level_warn")
def error(msg):      _log(msg, level="level_error")
def conversion(msg): _log(msg, level="level_conversion")