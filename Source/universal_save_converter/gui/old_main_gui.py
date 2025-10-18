import os
import tkinter as tk
from tkinter import Frame, Label, Button

# --- Console GUI Imports ---
from systems.n64.gui.n64_gui_main import setup_n64_gui
from systems.gba.gui.gba_gui_main import setup_gba_gui

# Theme import
from core.theme_utils import is_dark_mode

# --- Manufacturer → Consoles Map ---
MANUFACTURERS = {
    "Nintendo": [
        "NES / Famicom",
        "SNES / Super Famicom",
        "Nintendo 64",
        "Nintendo Virtual Boy",
        "Nintendo Gamcube",
        "Game Boy / Color",
        "Game Boy Advance",
        "Nintendo DS / DSi"
    ],
    "Sega": [
        "Sega Master System",
        "Sega Genesis/Megadrive",
        "Sega Saturn",
        "Sega Dreamcast",
        "Sega GameGear"
    ],
    "Sony": [
        "PlayStation 1",
        "PlayStation 2",
        "PlayStation 3",
        "PlayStation Portable",
        "PlayStation Vita"
    ],
    "Microsoft": [
        "Xbox",
        "Xbox 360"
    ],
    "Other": [
        "Atari Jaguar",
        "Atari Lynx"
    ]
}

CONSOLE_GUI_MAP = {
    "NES / Famicom": None,
    "SNES / Super Famicom": None,
    "Nintendo 64": setup_n64_gui,
    "Nintendo Virtual Boy": None,
    "Nintendo Gamcube": None,
    "Game Boy / Color": None,
    "Game Boy Advance": setup_gba_gui,
    "Nintendo DS / DSi": None,
    "Sega Master System": None,
    "Sega Genesis/Megadrive": None,
    "Sega Saturn": None,
    "Sega Dreamcast": None,
    "Sega GameGear": None,
    "PlayStation 1": None,
    "PlayStation 2": None,
    "PlayStation 3": None,
    "PlayStation Portable": None,
    "PlayStation Vita": None,
    "Xbox": None,
    "Xbox 360": None,
    "Atari Jaguar": None,
    "Atari Lynx": None
}

# --- Colors ---
PASTEL_DARK_BLUE = "#4A6FA5"
TEXT_COLOR = "#1E3A5F"

class TopLevelGUI:
    WIDTH = 1000
    HEIGHT = 580

    CONSOLE_GEOMETRY_MAP = {
        "NES / Famicom": (800, 600),
        "SNES / Super Famicom": (800, 600),
        "Nintendo 64": (1000, 580),
        "Nintendo Virtual Boy": (800, 600),
        "Nintendo Gamcube": (800, 600),
        "Game Boy / Color": (800, 600),
        "Game Boy Advance": (900, 400),
        "Nintendo DS / DSi": (800, 600),
        "Sega Master System": (800, 600),
        "Sega Genesis/Megadrive": (800, 600),
        "Sega Saturn": (800, 600),
        "Sega Dreamcast": (900, 500),
        "Sega GameGear": (800, 600),
        "PlayStation 1": (900, 500),
        "PlayStation 2": (900, 500),
        "PlayStation 3": (1000, 600),
        "PlayStation Portable": (900, 400),
        "PlayStation Vita": (900, 400),
        "Xbox": (1000, 500),
        "Xbox 360": (1000, 500),
        "Atari Jaguar": (800, 600),
        "Atari Lynx": (800, 600)
    }

    # ---------------- Reusable Back Button ----------------
    def _create_back_button(self, parent_frame, command, row=None):
        """Reusable back button identical to console selection screen"""
        hover_bg = "#3A5C8A" if self._current_theme == "dark" else "#d0d0d0"
        back_btn = Button(
            parent_frame,
            text="Back",
            width=10,
            height=2,
            bg=PASTEL_DARK_BLUE,
            fg=TEXT_COLOR,
            command=command,
            relief="flat"
        )
        if row is None:
            row = parent_frame.grid_size()[1]  # default to next available row
        back_btn.grid(row=row, column=0, columnspan=2, pady=20)
        self._add_hover(back_btn, PASTEL_DARK_BLUE, hover_bg)
        return back_btn

    # ---------------- Init ----------------
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Universal Save Converter")
        self.root.resizable(False, False)
        self._center_window(self.root, self.WIDTH, self.HEIGHT)

        self.current_frame = None
        self.all_logos = {}
        self.manufacturer_labels = {}
        self._current_theme = "dark" if is_dark_mode() else "light"
        self._current_manu = None

        self._preload_logos()
        self.setup_logo()
        self.show_manufacturer_selection()

        self.root.after(1000, self._poll_theme)
        self.root.mainloop()

    # ---------------- Window Helpers ----------------
    def _center_window(self, win, width, height):
        x = (win.winfo_screenwidth() - width) // 2
        y = (win.winfo_screenheight() - height) // 2
        win.geometry(f"{width}x{height}+{x}+{y}")

    def _clear_current_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None

    # ---------------- Hover Helpers ----------------
    def _add_hover(self, widget, normal_bg, hover_bg):
        widget.bind("<Enter>", lambda e: widget.config(bg=hover_bg))
        widget.bind("<Leave>", lambda e: widget.config(bg=normal_bg))

    def _add_logo_hover(self, label, manu):
        label.unbind("<Button-1>")
        label.bind("<Button-1>", lambda e, m=manu: self.show_manufacturer_gui(m))
        normal_bg = self.current_frame.cget("bg")
        hover_bg = "#2e2e2e" if self._current_theme == "dark" else "#f5f5f5"
        self._add_hover(label, normal_bg, hover_bg)
        label.image = self.all_logos.get(manu, {}).get(self._current_theme)

    # ---------------- Logos ----------------
    def setup_logo(self):
        self.logo_frame = Frame(self.root)
        self.logo_frame.pack(side="top", pady=(5, 0))
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "..", "resources", "new_usc_logo.png")
            self.logo_img = tk.PhotoImage(file=logo_path)
        except Exception:
            self.logo_img = None

        Label(
            self.logo_frame,
            image=self.logo_img,
            text="Universal Save Converter" if not self.logo_img else "",
            font=("Arial", 20, "bold"),
            compound="top"
        ).pack()

    def _preload_logos(self):
        logos = {
            "Nintendo": {"dark": "nintendo_white_logo.png", "light": "nintendo_black_logo.png"},
            "Sega": {"dark": "sega_white_logo.png", "light": "sega_black_logo.png"},
            "Sony": {"dark": "playstation_white_logo.png", "light": "playstation_black_logo.png"},
            "Microsoft": {"dark": "xbox_white_logo.png", "light": "xbox_black_logo.png"},
        }
        for manu, themes in logos.items():
            self.all_logos[manu] = {}
            for theme, filename in themes.items():
                path = os.path.join(os.path.dirname(__file__), "..", "resources", filename)
                if os.path.exists(path):
                    try:
                        self.all_logos[manu][theme] = tk.PhotoImage(file=path)
                    except Exception as e:
                        print(f"Failed to load {filename}: {e}")

    # ---------------- Theme Polling ----------------
    def _poll_theme(self):
        theme = "dark" if is_dark_mode() else "light"
        if theme != self._current_theme:
            self._current_theme = theme
            self._reload_manufacturer_logos()
        self.root.after(1000, self._poll_theme)

    def _reload_manufacturer_logos(self):
        for manu, label in self.manufacturer_labels.items():
            img = self.all_logos.get(manu, {}).get(self._current_theme)
            if img:
                label.config(image=img)
                label.image = img
            label.config(bg=self.current_frame.cget("bg"))
            self._add_logo_hover(label, manu)

    # ---------------- Manufacturer Selection ----------------
    def show_manufacturer_selection(self):
        self._clear_current_frame()
        self.current_frame = Frame(self.root)
        self.current_frame.pack(expand=True, fill="both")

        Label(
            self.current_frame,
            text="Choose Your 'Saves' System Brand:",
            font=("Arial", 21)
        ).grid(row=0, column=0, columnspan=2, pady=(0, 40))

        self.current_frame.grid_columnconfigure(0, weight=1)
        self.current_frame.grid_columnconfigure(1, weight=1)

        manufacturers = list(MANUFACTURERS.keys())
        total = len(manufacturers)

        for idx, manu in enumerate(manufacturers):
            row = idx // 2 + 1
            if total % 2 == 1 and idx == total - 1:
                col = 0
                columnspan = 2
                sticky = ""
            else:
                col = idx % 2
                columnspan = 1
                sticky = "ew"

            img = self.all_logos.get(manu, {}).get(self._current_theme)
            if img:
                label = Label(self.current_frame, image=img, bg=self.current_frame.cget("bg"))
                self._add_logo_hover(label, manu)
                label.grid(row=row, column=col, columnspan=columnspan, padx=20, pady=10, sticky=sticky)
                self.manufacturer_labels[manu] = label
            else:
                btn = self._text_button(manu)
                btn.grid(row=row, column=col, columnspan=columnspan, padx=20, pady=40, sticky=sticky)

    # ---------------- Text Button Helper ----------------
    def _text_button(self, manu):
        btn = Button(
            self.current_frame,
            text=manu,
            width=15,
            height=2,
            bg=PASTEL_DARK_BLUE,
            fg=TEXT_COLOR,
            command=lambda m=manu: self.show_manufacturer_gui(m),
            relief="flat"
        )
        hover_bg = "#3A5C8A" if self._current_theme == "dark" else "#d0d0d0"
        self._add_hover(btn, PASTEL_DARK_BLUE, hover_bg)
        return btn

    # ---------------- Console Selection ----------------
    def show_manufacturer_gui(self, manu):
        self._current_manu = manu
        self._clear_current_frame()
        self.current_frame = Frame(self.root)
        self.current_frame.pack(expand=True, fill="both", padx=50, pady=20)

        if manu != "Other" and self.all_logos.get(manu, {}).get(self._current_theme):
            logo_img = self.all_logos[manu][self._current_theme]
            manu_label = Label(
                self.current_frame,
                image=logo_img,
                bg=self.current_frame.cget("bg")
            )
            manu_label.image = logo_img
            manu_label.grid(row=0, column=0, columnspan=2, pady=10)
        else:
            Label(self.current_frame, text=manu, font=("Arial", 28, "bold")).grid(
                row=0, column=0, columnspan=2, pady=10
            )

        consoles = MANUFACTURERS[manu]
        self.current_frame.grid_columnconfigure(0, weight=1)
        self.current_frame.grid_columnconfigure(1, weight=1)

        total = len(consoles)
        for idx, console in enumerate(consoles):
            row = (idx // 2) + 1
            if total % 2 == 1 and idx == total - 1:
                col = 0
                columnspan = 2
                sticky = ""
            else:
                col = idx % 2
                columnspan = 1
                sticky = "ew"

            btn = Button(
                self.current_frame,
                text=console,
                width=30,
                height=2,
                bg=PASTEL_DARK_BLUE,
                fg=TEXT_COLOR,
                command=lambda c=console: self._open_console_gui(c),
                relief="flat"
            )
            btn.grid(row=row, column=col, columnspan=columnspan, padx=20, pady=5, sticky=sticky)
            hover_bg = "#3A5C8A" if self._current_theme == "dark" else "#d0d0d0"
            self._add_hover(btn, PASTEL_DARK_BLUE, hover_bg)

        # Back button identical to console selection
        back_row = (total + 1) // 2 + 1
        self._create_back_button(self.current_frame, lambda: self.show_manufacturer_selection(), row=back_row)

    # ---------------- Open Console GUI ----------------
    def _open_console_gui(self, console_name):
        gui_func = CONSOLE_GUI_MAP.get(console_name)

        # Resize window if GUI exists
        if gui_func:
            width, height = self.CONSOLE_GEOMETRY_MAP.get(console_name, (self.WIDTH, self.HEIGHT))
            self._center_window(self.root, width, height)

        self._clear_current_frame()
        self.current_frame = Frame(self.root)
        self.current_frame.pack(expand=True, fill="both", padx=10, pady=20)
        self.current_frame.grid_columnconfigure(0, weight=1)
        self.current_frame.grid_columnconfigure(1, weight=1)

        if gui_func:
            # Wrap N64 GUI in a separate container to avoid grid/pack conflicts
            container = Frame(self.current_frame)
            container.pack(expand=True, fill="both")
            gui_func(container)
            # GUI handles its own back button
        else:
            # Coming Soon screen using grid only
            coming_label = Label(
                self.current_frame,
                text=f"{console_name} Coming Soon...",
                font=("Arial", 24),
                wraplength=self.WIDTH - 100,
                justify="center"
            )
            coming_label.grid(row=0, column=0, columnspan=2, pady=(50, 20))

            # Pixel-perfect back button
            self._create_back_button(
                self.current_frame,
                lambda: self.show_manufacturer_gui(self._current_manu),
                row=1
            )

if __name__ == "__main__":
    TopLevelGUI()