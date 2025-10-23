# gui/main_gui.py

import os
import tkinter as tk
from tkinter import Frame, Label

# --- GUI Helpers ---
from .gui_utils import center_window, add_hover
from .gui_callbacks import preload_brand_logos, preload_console_logos

# --- Constants ---
from .gui_constants import (
    BRANDS,
    CONSOLE_GUI_MAP,
    BRAND_LOGO_SIZE,
    CONSOLE_LOGO_PADDING_X,
    CONSOLE_LOGO_PADDING_Y,
    BRAND_LOGO_PADDING_X,
    BRAND_LOGO_PADDING_Y,
    BRAND_BUTTON_PADDING_X,
    BRAND_BUTTON_PADDING_Y,
    CONSOLE_BUTTON_PADDING_X,
    CONSOLE_BUTTON_PADDING_Y,
    BRAND_BUTTON_SIZE,
    CONSOLE_BUTTON_SIZE,
    ARROW_BUTTON_WIDTH,
    ARROW_BUTTON_HEIGHT,
    ARROW_BUTTON_PADDING_X,
    ARROW_BUTTON_PADDING_Y,
    CONSOLE_CANVAS_HEIGHT,
    CONSOLE_CANVAS_WIDTH,
    BACK_BUTTON_SIZE,
)

from .theme_constants import (
    ARROW_FONT,
    BACK_BUTTON_FONT,
    DARK_ARROW_COLOUR,
    LIGHT_ARROW_COLOUR,
    DARK_GUI_TEXT_COLOUR,
    LIGHT_GUI_TEXT_COLOUR,
    DARK_BASE_LOGO_COLOUR,
    LIGHT_BASE_LOGO_COLOUR,
    DARK_HOVER_LOGO_COLOUR,
    LIGHT_HOVER_LOGO_COLOUR,
    LIGHT_BASE_BUTTON_COLOUR,
    LIGHT_HOVER_BUTTON_COLOUR,
    LIGHT_BUTTON_TEXT_COLOUR,
    DARK_BASE_BUTTON_COLOUR,
    DARK_HOVER_BUTTON_COLOUR,
    DARK_BUTTON_TEXT_COLOUR,
    DARK_GUI_BACKGROUND_COLOUR,
    LIGHT_GUI_BACKGROUND_COLOUR,
)

from core.theme_utils import (
    is_dark_mode,
)

DEFAULT_WIDTH = 1000
DEFAULT_HEIGHT = 620


class TopLevelGUI:
    WIDTH = DEFAULT_WIDTH
    HEIGHT = DEFAULT_HEIGHT

    def _apply_root_background(self):
        bg_colour = self.colours["bg"]
        self.root.config(bg=bg_colour)

        if self.current_frame and self.current_frame.winfo_exists():
            self.current_frame.config(bg=bg_colour)
        return bg_colour

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
        self._apply_root_background()
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

    @property
    def colours(self):
        """Return a dictionary of colours for the current theme."""
        if self._current_theme == "dark":
            return {
                "bg": DARK_GUI_BACKGROUND_COLOUR,
                "text": DARK_GUI_TEXT_COLOUR,
                "base_btn": DARK_BASE_BUTTON_COLOUR,
                "hover_btn": DARK_HOVER_BUTTON_COLOUR,
                "btn_text": DARK_BUTTON_TEXT_COLOUR,
                "base_logo": DARK_BASE_LOGO_COLOUR,
                "hover_logo": DARK_HOVER_LOGO_COLOUR,
                "arrow": DARK_ARROW_COLOUR,
            }
        else:
            return {
                "bg": LIGHT_GUI_BACKGROUND_COLOUR,
                "text": LIGHT_GUI_TEXT_COLOUR,
                "base_btn": LIGHT_BASE_BUTTON_COLOUR,
                "hover_btn": LIGHT_HOVER_BUTTON_COLOUR,
                "btn_text": LIGHT_BUTTON_TEXT_COLOUR,
                "base_logo": LIGHT_BASE_LOGO_COLOUR,
                "hover_logo": LIGHT_HOVER_LOGO_COLOUR,
                "arrow": LIGHT_ARROW_COLOUR,
            }

    def text_label(self, parent, text, command, width, height, bg, fg, font=("Arial", 16, "bold")):
        lbl = Label(
            parent,
            text=text,
            width=width,
            height=height,
            bg=self.colours["bg"],
            fg=fg,
            font=font,
            bd=0,
            relief="flat",
            anchor="center",
            justify="center"
        )

        # Hover effect
        def on_enter(e):
            lbl.config(bg=self.colours["hover_btn"])
        def on_leave(e):
            lbl.config(bg=self.colours["bg"])

        lbl.bind("<Enter>", on_enter)
        lbl.bind("<Leave>", on_leave)

        # Click effect
        lbl.bind("<Button-1>", lambda e: command())

        return lbl

    def _apply_theme_to_current_frame(self):
        """Reapply all colours and styles in the current frame when theme changes."""
        if not self.current_frame or not self.current_frame.winfo_exists():
            return

        theme_colours = self.colours

        def apply_recursive(widget):
            """Apply theme to this widget and its children."""
            if not widget.winfo_exists():
                return
            try:
                if isinstance(widget, (tk.Frame, tk.Toplevel)):
                    widget.config(bg=theme_colours["bg"])
                elif isinstance(widget, tk.Label):
                    widget.config(bg=theme_colours["base_btn"], fg=theme_colours["btn_text"])
                elif isinstance(widget, tk.Canvas):
                    widget.config(bg=theme_colours["base_logo"])
            except Exception:
                pass
            for child in widget.winfo_children():
                apply_recursive(child)

        apply_recursive(self.current_frame)

        # Update arrows explicitly
        for arrow in (self.prev_arrow, self.next_arrow):
            if arrow and arrow.winfo_exists():
                arrow.config(bg=theme_colours["base_btn"], fg=theme_colours["arrow"])
                add_hover(arrow, theme_colours["base_btn"], theme_colours["hover_btn"])

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
            fg=self.colours["btn_text"],
            bg=self.colours["bg"]
        ).pack()

        taskbar_logo_path = os.path.join(os.path.dirname(__file__), "..", "resources", "usc_logo.png")
        try:
            taskbar_logo = tk.PhotoImage(file=taskbar_logo_path)
            self.root.iconphoto(False, taskbar_logo)
            self.taskbar_logo = taskbar_logo
        except Exception:
            pass

    # ---------------- Helpers ----------------
    def _create_back_button(self, parent, command, row=None, colspan=4):
        theme_colours = self.colours
        btn = Label(
            parent,
            text="Back",
            width=BACK_BUTTON_SIZE[0] // 10,
            height=BACK_BUTTON_SIZE[1] // 20,
            bg=theme_colours["base_btn"],
            fg=theme_colours["btn_text"],
            font=BACK_BUTTON_FONT,
            bd=0,
            relief="flat"
        )

        # Hover effect
        def on_enter(e, b=btn):
            b.config(bg=theme_colours["hover_btn"])
        def on_leave(e, b=btn):
            b.config(bg=theme_colours["base_btn"])

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        # Click effect
        def on_click(e):
            btn.config(bg=theme_colours["hover_btn"])
            command()
            btn.config(bg=theme_colours["base_btn"])

        btn.bind("<Button-1>", on_click)

        if row is None:
            row = parent.grid_size()[1]
        btn.grid(row=row, column=0, columnspan=colspan, pady=20)

        return btn

    def _poll_theme(self):
        if not getattr(self, "_polling_active", True):
            self.root.after(1000, self._poll_theme)
            return

        current_theme = "dark" if is_dark_mode() else "light"
        if current_theme != self._current_theme:
            self._current_theme = current_theme
            self._apply_root_background()
            self._apply_theme_to_current_frame()
            self._refresh_logos_for_theme()

        self.root.after(1000, self._poll_theme)

    def _refresh_logos_for_theme(self):
        theme_colours = self.colours

        if not self.current_frame or not self.current_frame.winfo_exists():
            return

        def apply_theme_recursive(widget):
            if not widget.winfo_exists():
                return
            try:
                widget.config(bg=theme_colours["bg"])
            except Exception:
                pass
            for child in widget.winfo_children():
                apply_theme_recursive(child)

        apply_theme_recursive(self.root)
        self.current_frame.config(bg=theme_colours["bg"])

        # Update brand logos
        for widget in self.current_frame.winfo_children():
            if not widget.winfo_exists():
                continue
            if isinstance(widget, tk.Label) and hasattr(widget, "brand_name"):
                brand_name = widget.brand_name
                logo = self.all_logos.get(brand_name, {}).get(self._current_theme, {}).get("normal")
                if logo:
                    widget.config(image=logo, bg=theme_colours["base_logo"])
                    widget.image = logo
            elif isinstance(widget, tk.Label) and not hasattr(widget, "brand_name"):
                widget.config(bg=theme_colours["base_btn"], fg=theme_colours["btn_text"])

        # Update console logos
        for widget in self.current_frame.winfo_children():
            if not widget.winfo_exists():
                continue
            if isinstance(widget, tk.Canvas) and hasattr(widget, "console_name"):
                console_name = widget.console_name
                logo = self.console_logos.get(console_name, {}).get(self._current_theme, {}).get("normal")
                widget.config(bg=theme_colours["base_logo"])
                widget.delete("all")
                widget.create_rectangle(0, 0, widget.winfo_width(), widget.winfo_height(), fill=theme_colours["base_logo"], outline="")
                if logo:
                    widget.create_image(widget.winfo_width() // 2, widget.winfo_height() // 2, anchor="center", image=logo)
                    widget.image = logo
            elif isinstance(widget, tk.Label) and not hasattr(widget, "console_name"):
                widget.config(bg=theme_colours["base_btn"], fg=theme_colours["btn_text"])

        # Update arrows
        for arrow in (self.prev_arrow, self.next_arrow):
            if arrow and arrow.winfo_exists():
                arrow.config(bg=theme_colours["base_btn"], fg=theme_colours["arrow"])
                add_hover(arrow, theme_colours["base_btn"], theme_colours["hover_btn"])
        
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
        self.current_frame = Frame(self.root, bg=self.colours["bg"])
        self.current_frame.pack(expand=True, fill="both")

        # Title
        Label(
            self.current_frame,
            text="Which System Is Your Save For?",
            font=("Arial", 22, "bold"),
            fg=self.colours["text"],
            bg=self.colours["bg"]
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
                bg_colour = self.colours["base_logo"]
                hover_bg = self.colours["hover_logo"]

                canvas = tk.Canvas(
                    self.current_frame,
                    width=BRAND_LOGO_SIZE[0],
                    height=BRAND_LOGO_SIZE[1],
                    highlightthickness=0,
                    bg=bg_colour
                )
                canvas.grid(
                    row=row,
                    column=col,
                    columnspan=columnspan,
                    padx=BRAND_LOGO_PADDING_X,
                    pady=BRAND_LOGO_PADDING_Y,
                    sticky="n"
                )

                canvas_img = canvas.create_image(0, 0, anchor="nw", image=img)

                def on_enter(e, c=canvas):
                    c.config(bg=hover_bg)
                def on_leave(e, c=canvas):
                    c.config(bg=bg_colour)

                canvas.bind("<Enter>", on_enter)
                canvas.bind("<Leave>", on_leave)
                canvas.bind("<Button-1>", lambda e, m=manu: self.show_brands_gui(m))

                self.brands_labels[manu] = canvas

            else:
                lbl = self.text_label(
                    parent=self.current_frame,
                    text=manu,
                    command=lambda m=manu: self.show_brands_gui(m),
                    width=BRAND_BUTTON_SIZE[0] // 10,
                    height=BRAND_BUTTON_SIZE[1] // 20,
                    bg=self.colours["base_btn"],
                    fg=self.colours["btn_text"],
                    font=("Arial", 25, "bold")
                )
                lbl.grid(
                    row=row,
                    column=col,
                    columnspan=columnspan,
                    padx=BRAND_BUTTON_PADDING_X,
                    pady=BRAND_BUTTON_PADDING_Y,
                    sticky="n"
                )
                self.brands_labels[manu] = lbl

    # ---------------- Brands GUI ----------------
    def show_brands_gui(self, manu):
        self._current_manu = manu
        self._clear_frame()
        self.current_frame = Frame(self.root, padx=50, pady=10, bg=self.colours["bg"])
        self.current_frame.pack(expand=True, fill="both")

        logo_img = self.all_logos.get(manu, {}).get(self._current_theme)
        if manu != "Other" and logo_img:
            manu_label = Label(self.current_frame, image=logo_img, bg=self.colours["bg"])
            manu_label.image = logo_img
            manu_label.grid(row=0, column=0, columnspan=4, pady=(1, 20))
            self.console_manu_label = manu_label
        else:
            manu_label = Label(
                self.current_frame,
                text=manu,
                font=("Arial", 28, "bold"),
                fg=self.colours["text"],
                bg=self.colours["bg"]
            )
            manu_label.grid(row=0, column=0, columnspan=4, pady=(1, 20), sticky="n")
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

        base_bg = self.colours["base_logo"]
        hover_bg = self.colours["hover_logo"]
        base_btn_bg = self.colours["base_btn"]
        hover_btn_bg = self.colours["hover_btn"]
        text_fg = self.colours["btn_text"]

        if normal_img:
            canvas = tk.Canvas(
                parent,
                width=CONSOLE_CANVAS_WIDTH,
                height=CONSOLE_CANVAS_HEIGHT,
                highlightthickness=0,
                bg=base_bg
            )
            canvas.grid_propagate(False)
            canvas.create_rectangle(0, 0, CONSOLE_CANVAS_WIDTH, CONSOLE_CANVAS_HEIGHT, fill=base_bg, outline="")
            canvas_img = canvas.create_image(
                CONSOLE_CANVAS_WIDTH // 2,
                CONSOLE_CANVAS_HEIGHT // 2,
                anchor="center",
                image=normal_img
            )
            canvas.console_name = console_name
            canvas.image = normal_img
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
            lbl = tk.Label(
                parent,
                text=console_name,
                width=CONSOLE_BUTTON_SIZE[0] // 10,
                height=CONSOLE_BUTTON_SIZE[1] // 20,
                bg=base_btn_bg,
                fg=text_fg,
                font=("Arial", 16, "bold"),
                bd=0,
                relief="flat",
                anchor="center",
                justify="center"
            )

            def on_enter(e, l=lbl):
                l.config(bg=hover_btn_bg)
            def on_leave(e, l=lbl):
                l.config(bg=base_btn_bg)

            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)
            lbl.bind("<Button-1>", lambda e, c=console_name: self._open_console_gui(c))

            if not hasattr(self, "console_logo_labels"):
                self.console_logo_labels = []
            self.console_logo_labels.append(lbl)

            return lbl

    # ---------------- Show Coming Soon ----------------
    def _show_coming_soon(self, console_name):
        self._clear_frame()
        self.current_frame = Frame(self.root, padx=50, pady=50, bg=self.colours["bg"])
        self.current_frame.pack(expand=True, fill="both")

        Label(
            self.current_frame,
            text=f"{console_name} is Coming Soon...",
            font=("Arial", 24, "bold"),
            fg=self.colours["text"],
            bg=self.colours["bg"]
        ).pack(anchor="n", pady=50)

        back_btn = Label(
            self.current_frame,
            text="Back",
            width=BACK_BUTTON_SIZE[0] // 10,
            height=BACK_BUTTON_SIZE[1] // 20,
            bg=self.colours["base_btn"],
            fg=self.colours["btn_text"],
            font=BACK_BUTTON_FONT,
            bd=0,
            relief="flat",
            anchor="center",
            justify="center"
        )

        def safe_config(widget, **kwargs):
            if widget and widget.winfo_exists():
                widget.config(**kwargs)

        def on_enter(e):
            safe_config(back_btn, bg=self.colours["hover_btn"])
        def on_leave(e):
            safe_config(back_btn, bg=self.colours["base_btn"])
        def on_click(e):
            safe_config(back_btn, bg=self.colours["hover_btn"])
            self.show_brands_gui(self._current_manu)

        back_btn.bind("<Enter>", on_enter)
        back_btn.bind("<Leave>", on_leave)
        back_btn.bind("<Button-1>", on_click)
        back_btn.pack(anchor="n", pady=20)

if __name__ == "__main__":
    TopLevelGUI()