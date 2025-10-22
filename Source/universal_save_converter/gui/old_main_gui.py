# gui/main_gui.py

import os
import tkinter as tk
from tkinter import Frame, Label, Button

# --- GUI Helpers ---
from .gui_utils import center_window, add_hover
from .gui_callbacks import preload_brand_logos, preload_console_logos, add_logo_hover, text_button

# --- Constants ---
from .gui_constants import (
    BRANDS,
    CONSOLE_GUI_MAP,
    BRAND_LOGO_SIZE,
    CONSOLE_PADDING_X,
    CONSOLE_PADDING_Y,
    BRAND_PADDING_X,
    BRAND_PADDING_Y,
    TEXT_BUTTON_WIDTH,
    TEXT_BUTTON_HEIGHT,
    ARROW_BUTTON_WIDTH,
    ARROW_BUTTON_HEIGHT,
    ARROW_HORIZONTAL_PADDING,
    CONSOLE_CANVAS_HEIGHT,
    CONSOLE_CANVAS_WIDTH,
)
from core.theme_utils import (
    is_dark_mode, 
    DARK_HOVER_BG_COLOR, 
    LIGHT_HOVER_BG_COLOR, 
    BUTTON_TEXT_COLOUR, 
    BASE_BUTTON_COLOR, 
    HOVER_BUTTON_COLOR,
    ARROW_FONT,
    DARK_ARROW_COLOUR,
    LIGHT_ARROW_COLOUR,
    DARK_GUI_TEXT_COLOUR,
    LIGHT_GUI_TEXT_COLOUR,
    BRAND_LOGOS,
    CONSOLE_LOGOS,
)

DEFAULT_WIDTH = 1000
DEFAULT_HEIGHT = 620


class TopLevelGUI:
    WIDTH = DEFAULT_WIDTH
    HEIGHT = DEFAULT_HEIGHT

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Universal Save Converter")
        self.root.resizable(False, False)
        center_window(self.root, self.WIDTH, self.HEIGHT)

        self.current_frame = None
        self.console_logos = {}
        self.all_logos = {}
        self.brands_labels = {}
        self._current_theme = "dark" if is_dark_mode() else "light"
        self._current_manu = None
        self.console_manu_label = None
        self.pages = []
        self.current_page_index = 0
        self.prev_arrow = None
        self.next_arrow = None

        preload_brand_logos(self.all_logos)
        preload_console_logos(self.console_logos)

        self._setup_logo()
        self.show_brands_selection()
        self.root.after(1000, self._poll_theme)
        self.root.mainloop()

    # ---------------- Logo ----------------
    def _setup_logo(self):
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
            compound="top",
            fg=BUTTON_TEXT_COLOUR,
            bg=self.logo_frame.cget("bg")
        ).pack()

    # ---------------- Helpers ----------------
    def _clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None
            self.console_manu_label = None
        if self.prev_arrow:
            self.prev_arrow.destroy()
            self.prev_arrow = None
        if self.next_arrow:
            self.next_arrow.destroy()
            self.next_arrow = None

    def _create_back_button(self, parent, command, row=None, colspan=4):
        btn = Label(
            parent,
            text="Back",
            width=10,
            height=1,
            bg=BASE_BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOUR,
            bd=0,               # remove border
            relief="flat"
        )

        # Hover effect
        def on_enter(e, b=btn):
            b.config(bg=HOVER_BUTTON_COLOR)
        def on_leave(e, b=btn):
            b.config(bg=BASE_BUTTON_COLOR)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        # Click effect
        def on_click(e):
            btn.config(bg=HOVER_BUTTON_COLOR)
            command()
            btn.config(bg=BASE_BUTTON_COLOR)

        btn.bind("<Button-1>", on_click)

        if row is None:
            row = parent.grid_size()[1]
        btn.grid(row=row, column=0, columnspan=colspan, pady=20)

        return btn

    # ---------------- Theme ----------------
    def _poll_theme(self):
        if not getattr(self, "_polling_active", True):
            self.root.after(1000, self._poll_theme)
            return

        current_theme = "dark" if is_dark_mode() else "light"
        if current_theme != self._current_theme:
            self._current_theme = current_theme
            self._apply_theme_to_current_frame()
            self._refresh_logos_for_theme()
        self.root.after(1000, self._poll_theme)

    def _refresh_logos_for_theme(self):
        if not self.current_frame or not self.current_frame.winfo_exists():
            return

        theme = "dark" if is_dark_mode() else "light"
        bg_color = "#000" if theme == "dark" else "#fff"

        # --- Brand logos ---
        for widget in self.current_frame.winfo_children():
            if isinstance(widget, tk.Label) and hasattr(widget, "brand_name"):
                brand_name = widget.brand_name
                logo = self.all_logos.get(brand_name, {}).get(theme, {}).get("normal")
                if logo:
                    widget.config(image=logo)
                    widget.image = logo

        # --- Console logos ---
        for widget in self.current_frame.winfo_children():
            if isinstance(widget, tk.Canvas) and hasattr(widget, "console_name"):
                console_name = widget.console_name
                logo = self.console_logos.get(console_name, {}).get(theme, {}).get("normal")
                if logo:
                    widget.configure(bg=bg_color)
                    widget.delete("all")
                    # Ensure the rectangle fully fills the canvas
                    widget.create_rectangle(0, 0, CONSOLE_CANVAS_WIDTH, CONSOLE_CANVAS_HEIGHT,
                                            fill=bg_color, outline="")
                    widget.create_image(
                        CONSOLE_CANVAS_WIDTH // 2,
                        CONSOLE_CANVAS_HEIGHT // 2,
                        anchor="center",
                        image=logo
                    )
                    widget.image = logo

        # --- Update arrows safely ---
        if hasattr(self, "prev_arrow") and self.prev_arrow and self.prev_arrow.winfo_exists():
            self.prev_arrow.configure(bg=bg, fg=arrow_colour)
            add_hover(self.prev_arrow, bg, hover_bg)

        if hasattr(self, "next_arrow") and self.next_arrow and self.next_arrow.winfo_exists():
            self.next_arrow.configure(bg=bg, fg=arrow_colour)
            add_hover(self.next_arrow, bg, hover_bg)

    def _refresh_logos_for_theme(self):
        if not self.current_frame or not self.current_frame.winfo_exists():
            return

        theme = "dark" if is_dark_mode() else "light"

        # --- Brand logos ---
        for widget in self.current_frame.winfo_children():
            if not widget.winfo_exists():
                continue

            if isinstance(widget, tk.Label) and hasattr(widget, "brand_name"):
                brand_name = widget.brand_name
                logo = self.all_logos.get(brand_name, {}).get(theme, {}).get("normal")
                if logo:
                    try:
                        widget.config(image=logo)
                        widget.image = logo
                    except tk.TclError:
                        continue

        # --- Console logos ---
        for widget in self.current_frame.winfo_children():
            if not widget.winfo_exists():
                continue

            if isinstance(widget, tk.Canvas) and hasattr(widget, "console_name"):
                console_name = widget.console_name
                logo = self.console_logos.get(console_name, {}).get(theme, {}).get("normal")
                if logo:
                    try:
                        widget.delete("all")
                        widget.create_image(
                            widget.winfo_width() // 2,
                            widget.winfo_height() // 2,
                            anchor="center",
                            image=logo
                        )
                        widget.image = logo
                    except tk.TclError:
                        continue

    # ---------------- Frame Clearing ----------------
    def _clear_frame(self):
        self._polling_active = False  # temporarily pause theme polling
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None
            self.console_manu_label = None
        if self.prev_arrow and self.prev_arrow.winfo_exists():
            self.prev_arrow.destroy()
            self.prev_arrow = None
        if self.next_arrow and self.next_arrow.winfo_exists():
            self.next_arrow.destroy()
            self.next_arrow = None
        self.console_logo_labels = []  # clear stored references
        self._polling_active = True

    # ---------------- Brands Selection ----------------
    def show_brands_selection(self):
        self._clear_frame()
        self.current_frame = Frame(self.root)
        self.current_frame.pack(expand=True, fill="both")

        # Title
        Label(
            self.current_frame,
            text="Which System Is Your Save For?",
            font=("Arial", 22, "bold"),
            fg=DARK_GUI_TEXT_COLOUR if self._current_theme == "dark" else LIGHT_GUI_TEXT_COLOUR,
            bg=self.current_frame.cget("bg")
        ).grid(row=0, column=0, columnspan=4, pady=(20, 30))

        # Configure grid columns
        for i in range(4):
            self.current_frame.grid_columnconfigure(i, weight=1 if i in (0, 3) else 3, uniform="brand_col")

        brands_list = list(BRANDS.keys())
        total = len(brands_list)

        for idx, manu in enumerate(brands_list):
            row = idx // 2 + 1
            col = idx % 2 + 1
            columnspan = 1
            if total % 2 == 1 and idx == total - 1:
                col = 1
                columnspan = 2

            img = self.all_logos.get(manu, {}).get(self._current_theme)
            if img:
                bg_color = self.current_frame.cget("bg") or ("#000" if self._current_theme == "dark" else "#fff")
                hover_bg = DARK_HOVER_BG_COLOR if self._current_theme == "dark" else LIGHT_HOVER_BG_COLOR

                canvas = tk.Canvas(
                    self.current_frame,
                    width=BRAND_LOGO_SIZE[0],
                    height=BRAND_LOGO_SIZE[1],
                    highlightthickness=0,
                    bg=bg_color
                )
                canvas.grid(
                    row=row,
                    column=col,
                    columnspan=columnspan,
                    padx=BRAND_PADDING_X,
                    pady=BRAND_PADDING_Y,
                    sticky="n"
                )

                canvas_img = canvas.create_image(0, 0, anchor="nw", image=img)

                def on_enter(e, c=canvas):
                    c.config(bg=hover_bg)
                def on_leave(e, c=canvas):
                    c.config(bg=bg_color)

                canvas.bind("<Enter>", on_enter)
                canvas.bind("<Leave>", on_leave)
                canvas.bind("<Button-1>", lambda e, m=manu: self.show_brands_gui(m))

                self.brands_labels[manu] = canvas

            else:
                btn = text_button(
                    parent=self.current_frame,
                    text=manu,
                    command=lambda m=manu: self.show_brands_gui(m),
                    width=TEXT_BUTTON_WIDTH,
                    height=TEXT_BUTTON_HEIGHT,
                    bg=BASE_BUTTON_COLOR,
                    fg=BUTTON_TEXT_COLOUR
                )
                add_hover(btn, BASE_BUTTON_COLOR, HOVER_BUTTON_COLOR)
                btn.grid(
                    row=row,
                    column=col,
                    columnspan=columnspan,
                    padx=BRAND_PADDING_X,
                    pady=BRAND_PADDING_Y,
                    sticky="n"
                )

    # ---------------- Brands GUI ----------------
    def show_brands_gui(self, manu):
        self._current_manu = manu
        self._clear_frame()
        self.current_frame = Frame(self.root, padx=50, pady=10)
        self.current_frame.pack(expand=True, fill="both")

        logo_img = self.all_logos.get(manu, {}).get(self._current_theme)
        if manu != "Other" and logo_img:
            manu_label = Label(self.current_frame, image=logo_img, bg=self.current_frame.cget("bg"))
            manu_label.image = logo_img
            manu_label.grid(row=0, column=0, columnspan=4, pady=(1, 20))
            self.console_manu_label = manu_label
        else:
            manu_label = Label(
                self.current_frame,
                text=manu,
                font=("Arial", 28, "bold"),
                fg=DARK_GUI_TEXT_COLOUR if self._current_theme == "dark" else LIGHT_GUI_TEXT_COLOUR,
                bg=self.current_frame.cget("bg")
            )
            manu_label.grid(
                row=0,
                column=0,
                columnspan=4,   # span all columns to center
                pady=(1, 20),
                sticky="n"      # stick to top (like logos), horizontal centering is automatic
            )
            self.console_manu_label = manu_label

        consoles = BRANDS[manu]
        self.pages = [consoles[i:i + 6] for i in range(0, len(consoles), 6)]
        self.current_page_index = 0

        self.back_button = self._create_back_button(self.current_frame,
                                                    lambda: self.show_brands_selection(),
                                                    row=((len(self.pages[0]) + 1) // 2) + 1)

        self._render_console_page(self.current_frame, self.pages[self.current_page_index])

    # ---------------- Console Button ----------------
    def _console_button(self, parent, console_name):
        logos = self.console_logos.get(console_name, {}).get(self._current_theme, {})
        normal_img = logos.get("normal")
        hover_bg = HOVER_BUTTON_COLOR
        base_bg = BASE_BUTTON_COLOR

        if normal_img:
            canvas = tk.Canvas(
                parent,
                width=CONSOLE_CANVAS_WIDTH,
                height=CONSOLE_CANVAS_HEIGHT,
                highlightthickness=0,
                bg=base_bg
            )
            canvas.grid_propagate(False)

            # Always center the image
            canvas_img = canvas.create_image(
                CONSOLE_CANVAS_WIDTH // 2,
                CONSOLE_CANVAS_HEIGHT // 2,
                anchor="center",
                image=normal_img
            )

            canvas.console_name = console_name  # attach name for theme refresh

            # Store reference for hover/theme updates
            if not hasattr(self, "console_logo_labels"):
                self.console_logo_labels = []
            self.console_logo_labels.append(canvas)

            def on_enter(e, c=canvas):
                c.config(bg=hover_bg)
            def on_leave(e, c=canvas):
                c.config(bg=base_bg)

            canvas.bind("<Enter>", on_enter)
            canvas.bind("<Leave>", on_leave)
            canvas.bind("<Button-1>", lambda e, c=console_name: self._open_console_gui(c))

            return canvas
        else:
            btn = text_button(
                parent=self.current_frame,
                text=console_name,
                command=lambda m=console_name: self._open_console_gui(m),
                width=TEXT_BUTTON_WIDTH,
                height=TEXT_BUTTON_HEIGHT,
                bg=BASE_BUTTON_COLOR,       # consistent
                fg=BUTTON_TEXT_COLOUR       # consistent
            )
            add_hover(btn, BASE_BUTTON_COLOR, HOVER_BUTTON_COLOR)  # consistent hover
            return btn
        
    # ---------------- Page Navigation ----------------
    def _next_page(self):
        if self.current_page_index < len(self.pages) - 1:
            self.current_page_index += 1
            self._render_console_page(self.current_frame, self.pages[self.current_page_index])

    def _prev_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self._render_console_page(self.current_frame, self.pages[self.current_page_index])

    # ---------------- Render Console Page ----------------
    def _render_console_page(self, parent, consoles):
        # Destroy previous console widgets except label/back button
        for widget in list(parent.winfo_children()):
            if widget not in (self.console_manu_label, self.back_button):
                if widget.winfo_exists():
                    widget.destroy()

        # Destroy arrows safely
        if self.prev_arrow and self.prev_arrow.winfo_exists():
            self.prev_arrow.destroy()
        if self.next_arrow and self.next_arrow.winfo_exists():
            self.next_arrow.destroy()

        # Reset console logo references
        self.console_logo_labels = []

        for i in range(4):
            parent.grid_columnconfigure(i, weight=1 if i in (0, 3) else 6, uniform="console_col")

        total = len(consoles)
        for idx, console in enumerate(consoles):
            row = idx // 2 + 1
            col = idx % 2 + 1
            columnspan = 1
            if total % 2 == 1 and idx == total - 1:
                col = 1
                columnspan = 2
            btn = self._console_button(parent, console)
            btn.grid(row=row, column=col, columnspan=columnspan,
                    padx=CONSOLE_PADDING_X, pady=CONSOLE_PADDING_Y, sticky="n")

        hover_bg = DARK_HOVER_BG_COLOR if self._current_theme == "dark" else LIGHT_HOVER_BG_COLOR
        arrow_colour = DARK_ARROW_COLOUR if self._current_theme == "dark" else LIGHT_ARROW_COLOUR

        if self.current_page_index > 0:
            self.prev_arrow = Label(
                parent,
                text="<",
                font=ARROW_FONT,
                bg=parent.cget("bg"),
                fg=arrow_colour,
                height=ARROW_BUTTON_HEIGHT,
                width=ARROW_BUTTON_WIDTH
            )
            self.prev_arrow.place(relx=0.00 - ARROW_HORIZONTAL_PADDING, rely=0.5, anchor="w")
            add_hover(self.prev_arrow, parent.cget("bg"), hover_bg)
            self.prev_arrow.bind("<Button-1>", lambda e: self._prev_page())

        if self.current_page_index < len(self.pages) - 1:
            self.next_arrow = Label(
                parent,
                text=">",
                font=ARROW_FONT,
                bg=parent.cget("bg"),
                fg=arrow_colour,
                height=ARROW_BUTTON_HEIGHT,
                width=ARROW_BUTTON_WIDTH
            )
            self.next_arrow.place(relx=1.0 + ARROW_HORIZONTAL_PADDING, rely=0.5, anchor="e")
            add_hover(self.next_arrow, parent.cget("bg"), hover_bg)
            self.next_arrow.bind("<Button-1>", lambda e: self._next_page())
            
    # ---------------- Open Console GUI ----------------
    def _open_console_gui(self, console_name):
        gui_class = CONSOLE_GUI_MAP.get(console_name)

        if callable(gui_class):
            # Create a new frame for the console GUI
            self._clear_frame()
            console_frame = Frame(self.root, padx=20, pady=20)
            console_frame.pack(expand=True, fill="both")

            # Pass the frame to the GUI setup function
            gui_class(console_frame)
        else:
            self._show_coming_soon(console_name)

    def _show_coming_soon(self, console_name):
        self._clear_frame()
        self.current_frame = Frame(self.root, padx=50, pady=50)
        self.current_frame.pack(expand=True, fill="both")

        # Label at the top
        Label(
            self.current_frame,
            text=f"{console_name} is Coming Soon...",
            font=("Arial", 24, "bold"),
            fg=DARK_GUI_TEXT_COLOUR if self._current_theme == "dark" else LIGHT_GUI_TEXT_COLOUR,
            bg=self.current_frame.cget("bg")
        ).pack(anchor="n", pady=50)

        # Back button using pack instead of grid
        back_btn = Button(
            self.current_frame,
            text="Back",
            width=10,
            height=1,
            bg=BASE_BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOUR,
            relief="flat",
            command=lambda: self.show_brands_gui(self._current_manu)
        )
        add_hover(back_btn, BASE_BUTTON_COLOR, HOVER_BUTTON_COLOR)
        back_btn.pack(anchor="n", pady=20)  # or use anchor="s" if you want it lower

if __name__ == "__main__":
    TopLevelGUI()