# core/theme_utils.py

import platform
import subprocess
import tkinter as tk

# --- Brand Logos ---
BRAND_LOGOS = {
    "Nintendo": {"dark": "nintendo_white_logo.png", "light": "nintendo_black_logo.png"},
    "SEGA": {"dark": "sega_white_logo.png", "light": "sega_black_logo.png"},
    "PlayStation": {"dark": "playstation_white_logo.png", "light": "playstation_black_logo.png"},
    "XBOX": {"dark": "xbox_white_logo.png", "light": "xbox_black_logo.png"},
}

# --- Console Logos (unchanged colours) ---
CONSOLE_LOGOS = {
    # Nintendo
    "NES / Famicom": {"dark": "nes_white_logo.png", "light": "nes_black_logo.png"},
    "SNES / Super Famicom": {"dark": "snes_white_logo.png", "light": "snes_black_logo.png"},
    "Nintendo 64": {"dark": "n64_white_logo.png", "light": "n64_black_logo.png"},
    "Nintendo Virtual Boy": {"dark": "vb_white_logo.png", "light": "vb_black_logo.png"},
    "Nintendo GameCube": {"dark": "gamecube_white_logo.png", "light": "gamecube_black_logo.png"},
    "Nintendo Wii": {"dark": "wii_white_logo.png", "light": "wii_black_logo.png"},
    "Game Boy / Color": {"dark": "gbc_white_logo.png", "light": "gb_black_logo.png"},
    "Game Boy Advance": {"dark": "gba_white_logo.png", "light": "gba_black_logo.png"},
    "Nintendo DS / DSi": {"dark": "dsi_white_logo.png", "light": "dsi_black_logo.png"},
    "Nintendo 3DS": {"dark": "3ds_white_logo.png", "light": "3ds_black_logo.png"},
    # SEGA
    "Sega Master System": {"dark": "sms_white_logo.png", "light": "sms_black_logo.png"},
    "Sega Genesis/Megadrive": {"dark": "megadrive_white_logo.png", "light": "megadrive_black_logo.png"},
    "Sega Saturn": {"dark": "saturn_white_logo.png", "light": "saturn_black_logo.png"},
    "Sega Dreamcast": {"dark": "dreamcast_white_logo.png", "light": "dreamcast_black_logo.png"},
    "Sega GameGear": {"dark": "gamegear_white_logo.png", "light": "gamegear_black_logo.png"},
    # PlayStation
    "PlayStation 1": {"dark": "ps1_white_logo.png", "light": "ps1_black_logo.png"},
    "PlayStation 2": {"dark": "ps2_white_logo.png", "light": "ps2_black_logo.png"},
    "PlayStation 3": {"dark": "ps3_white_logo.png", "light": "ps3_black_logo.png"},
    "PlayStation Portable": {"dark": "psp_white_logo.png", "light": "psp_black_logo.png"},
    "PlayStation Vita": {"dark": "vita_white_logo.png", "light": "vita_black_logo.png"},
    # XBOX
    "Xbox": {"dark": "xbox_white_logo.png", "light": "xbox_black_logo.png"},
    "Xbox 360": {"dark": "360_white_logo.png", "light": "360_black_logo.png"},
    # Other
    "Atari Jaguar": {"dark": "jaguar_white_logo.png", "light": "jaguar_black_logo.png"},
    "Atari Lynx": {"dark": "lynx_white_logo.png", "light": "lynx_black_logo.png"},
}


# Button Colours
BASE_BUTTON_COLOR = "#1e1e1e"  # normal background for all buttons
HOVER_BUTTON_COLOR = "#2e2e2e"  # hover background
BUTTON_TEXT_COLOUR = "#ffffff"

# Arrow Colours
ARROW_FONT = ("Arial", 50, "bold")
DARK_ARROW_COLOUR = "#ffffff"
LIGHT_ARROW_COLOUR = "#000000"



DARK_BASE_BG_COLOR = "#7c7c7c"
LIGHT_BASE_BG_COLOR = "#fff"
DARK_HOVER_BG_COLOR = "#2e2e2e"
LIGHT_HOVER_BG_COLOR = "#f2f2f2"

# GUI Text Colours
DARK_GUI_TEXT_COLOUR= "#ffffff"
LIGHT_GUI_TEXT_COLOUR = "#000000"


# ---------------- System Dark Mode Detection ----------------
def is_dark_mode():
    """Detect system dark mode on macOS. Defaults to False elsewhere."""
    if platform.system() == "Darwin":
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True, text=True
            )
            return result.stdout.strip().lower() == "dark"
        except Exception:
            return False
    return False

current_mode = is_dark_mode()

# ---------------- Widget Detection ----------------
def detect_widgets(root):
    """Detect labels, log boxes, and log frames automatically."""
    widgets = {"labels": [], "log_box": None, "log_frame": None, "log_label": None}

    def recurse(parent):
        for child in parent.winfo_children():
            if isinstance(child, tk.Label):
                widgets["labels"].append(child)
            elif isinstance(child, tk.Text):
                widgets["log_box"] = child
                widgets["log_frame"] = child.master
            recurse(child)

    recurse(root)

    # Detect label inside log frame
    if widgets["log_frame"]:
        for child in widgets["log_frame"].winfo_children():
            if isinstance(child, tk.Label):
                widgets["log_label"] = child
                break

    return widgets


# ---------------- Theme Application ----------------
def apply_theme(root, widgets=None, dark=None):
    """Apply light or dark mode styling to all text elements."""
    if widgets is None:
        widgets = detect_widgets(root)

    if dark is None:
        dark = is_dark_mode()

    # Adaptive colours for GUI (logos remain untouched)
    colors = {
        "bg": "#1c1c1c" if dark else "#ffffff",     # overall background
        "fg": "#ffffff" if dark else "#000000",     # text colour
        "log_bg": "#1c1c1c" if dark else "#ffffff",
        "log_fg": "#ffffff" if dark else "#000000",
        "tag_info": "#ffffff" if dark else "#000000",
        "tag_conversion": "#00ffff" if dark else "#006666",
        "tag_warn": "#ffcc00" if dark else "#b8860b",
        "tag_error": "#ff4500" if dark else "#b22222",
        "tag_timestamp": "#ffa500" if dark else "#ff8c00",
    }

    # Apply to root
    root.configure(bg=colors["bg"])

    # Labels
    for lbl in widgets.get("labels", []):
        lbl.configure(bg=colors["bg"], fg=colors["fg"])

    # Log frame + log box
    if widgets.get("log_frame"):
        widgets["log_frame"].configure(bg=colors["log_bg"], highlightthickness=0, bd=0)

    if widgets.get("log_box"):
        log_box = widgets["log_box"]
        log_box.configure(
            bg=colors["log_bg"],
            fg=colors["log_fg"],
            insertbackground=colors["log_fg"],
            highlightthickness=0,
            bd=0
        )
        log_box.tag_config("timestamp", foreground=colors["tag_timestamp"])
        log_box.tag_config("level_info", foreground=colors["tag_info"])
        log_box.tag_config("level_conversion", foreground=colors["tag_conversion"])
        log_box.tag_config("level_warn", foreground=colors["tag_warn"])
        log_box.tag_config("level_error", foreground=colors["tag_error"])

    if widgets.get("log_label"):
        widgets["log_label"].configure(bg=colors["log_bg"], fg=colors["log_fg"])


# ---------------- Theme Polling ----------------
def start_polling(root, widgets=None, interval=1000):
    """Poll system theme changes and reapply if switched."""
    global current_mode
    dark = is_dark_mode()
    if dark != current_mode:
        current_mode = dark
        apply_theme(root, widgets, dark)
    root.after(interval, start_polling, root, widgets, interval)