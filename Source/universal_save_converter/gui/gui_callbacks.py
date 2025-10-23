# gui/gui_callbacks.py

import os
from PIL import Image, ImageTk
from core.theme_utils import BRAND_LOGOS, CONSOLE_LOGOS
from .theme_constants import DARK_HOVER_BG_COLOUR, LIGHT_HOVER_BG_COLOUR, BUTTON_TEXT_COLOUR
from .gui_constants import CONSOLE_LOGO_SIZE
import tkinter as tk

def resize_preserve_aspect_ratio(img: Image.Image, max_size):
    max_w, max_h = max_size
    w, h = img.size
    ratio = min(max_w / w, max_h / h)
    new_w, new_h = int(w * ratio), int(h * ratio)
    resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", max_size, (0, 0, 0, 0))
    offset_x = (max_w - new_w) // 2
    offset_y = (max_h - new_h) // 2
    canvas.paste(resized_img, (offset_x, offset_y), resized_img)
    return canvas

def preload_console_logos(console_logos):
    for console, themes in CONSOLE_LOGOS.items():
        console_logos[console] = {}
        for theme, filename in themes.items():
            folder = "white" if theme == "dark" else "black"
            path = os.path.join(
                os.path.dirname(__file__),
                "..", "resources", "console_logos", folder, filename
            )
            console_logos[console][theme] = {"normal": None}
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGBA")
                    resized_img = resize_preserve_aspect_ratio(img, CONSOLE_LOGO_SIZE)
                    console_logos[console][theme]["normal"] = ImageTk.PhotoImage(resized_img)
                except Exception as e:
                    print(f"Failed to load {filename} for {console}: {e}")
            else:
                print(f"Logo not found: {path}")

def preload_brand_logos(all_logos):
    for manu, themes in BRAND_LOGOS.items():
        all_logos[manu] = {}
        for theme, filename in themes.items():
            folder = "white" if theme == "dark" else "black"
            path = os.path.join(
                os.path.dirname(__file__),
                "..", "resources", "brands_logos", folder, filename
            )
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGBA")
                    img_resized = resize_preserve_aspect_ratio(img, (300, 80))
                    all_logos[manu][theme] = ImageTk.PhotoImage(img_resized)
                except Exception as e:
                    print(f"Failed to load {filename} for {manu}: {e}")
            else:
                all_logos[manu][theme] = None

def add_hover(widget, base_bg, hover_bg):
    # Works for both Button and Frame
    def on_enter(e):
        try:
            widget.config(bg=hover_bg, activebackground=hover_bg)
        except tk.TclError:
            widget.config(bg=hover_bg)
    def on_leave(e):
        try:
            widget.config(bg=base_bg, activebackground=base_bg)
        except tk.TclError:
            widget.config(bg=base_bg)
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def center_window(win, width, height):
    x = (win.winfo_screenwidth() - width) // 2
    y = (win.winfo_screenheight() - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

def text_button(parent, text, command, width=15, height=2, bg="#3A5C8A", fg=BUTTON_TEXT_COLOUR):
    return tk.Button(parent, text=text, width=width, height=height, bg=bg, fg=fg, command=command, relief="flat")

def back_button(parent, command, width=10, height=1, bg="#3A5C8A", fg=BUTTON_TEXT_COLOUR):
    return tk.Button(parent, text="Back", width=width, height=height, bg=bg, fg=fg, command=command, relief="flat")

def create_pages(items, per_page=6):
    return [items[i:i + per_page] for i in range(0, len(items), per_page)]