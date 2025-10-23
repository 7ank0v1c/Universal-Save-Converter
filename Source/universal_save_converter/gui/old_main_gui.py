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
    DARK_ARROW_COLOUR,
    LIGHT_ARROW_COLOUR,
    DARK_GUI_TEXT_COLOUR,
    LIGHT_GUI_TEXT_COLOUR,
    BACK_BUTTON_FONT,
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

        # Update current frame background
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
        self._apply_root_background()  # <- add this line       
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
            lbl.config(bg=self.colours["hover_btn"] if self._current_theme == "dark" else LIGHT_HOVER_BUTTON_COLOUR)
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

        theme = self._current_theme
        bg_colour = DARK_GUI_BACKGROUND_COLOUR if theme == "dark" else LIGHT_GUI_BACKGROUND_COLOUR
        text_colour = DARK_GUI_TEXT_COLOUR if theme == "dark" else LIGHT_GUI_TEXT_COLOUR
        base_logo_bg = DARK_BASE_LOGO_COLOUR if theme == "dark" else LIGHT_BASE_LOGO_COLOUR
        hover_logo_bg = DARK_HOVER_LOGO_COLOUR if theme == "dark" else LIGHT_HOVER_LOGO_COLOUR
        base_btn_bg = DARK_BASE_BUTTON_COLOUR if theme == "dark" else LIGHT_BASE_BUTTON_COLOUR
        hover_btn_bg = DARK_HOVER_BUTTON_COLOUR if theme == "dark" else LIGHT_HOVER_BUTTON_COLOUR
        text_btn_colour = DARK_BUTTON_TEXT_COLOUR if theme == "dark" else LIGHT_BUTTON_TEXT_COLOUR
        arrow_colour = DARK_ARROW_COLOUR if theme == "dark" else LIGHT_ARROW_COLOUR

        def apply_recursive(widget):
            """Apply theme to this widget and its children."""
            if not widget.winfo_exists():
                return
            try:
                # Generic background / text
                if isinstance(widget, (tk.Frame, tk.Toplevel)):
                    widget.config(bg=bg_colour)
                elif isinstance(widget, tk.Label):
                    widget.config(bg=base_btn_bg, fg=text_btn_colour)
                elif isinstance(widget, tk.Canvas):
                    widget.config(bg=base_logo_bg)
            except Exception:
                pass
            for child in widget.winfo_children():
                apply_recursive(child)

        apply_recursive(self.current_frame)

        # Update arrows explicitly
        if self.prev_arrow and self.prev_arrow.winfo_exists():
            self.prev_arrow.config(bg=base_btn_bg, fg=arrow_colour)
            add_hover(self.prev_arrow, base_btn_bg, hover_btn_bg)

        if self.next_arrow and self.next_arrow.winfo_exists():
            self.next_arrow.config(bg=base_btn_bg, fg=arrow_colour)
            add_hover(self.next_arrow, base_btn_bg, hover_btn_bg)

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
            fg=self.colours["btn_text"] if self._current_theme == "dark" else LIGHT_BUTTON_TEXT_COLOUR,
            bg=self.colours["bg"]
        ).pack()

        # ----------------- Taskbar / window icon -----------------
        taskbar_logo_path = os.path.join(os.path.dirname(__file__), "..", "resources", "usc_logo.png")
        try:
            taskbar_logo = tk.PhotoImage(file=taskbar_logo_path)
            self.root.iconphoto(False, taskbar_logo)
            self.taskbar_logo = taskbar_logo  # keep a reference
        except Exception:
            pass

    # ---------------- Helpers ----------------
    def _create_back_button(self, parent, command, row=None, colspan=4):
        btn = Label(
            parent,
            text="Back",
            width=BACK_BUTTON_SIZE[0] // 10,
            height=BACK_BUTTON_SIZE[1] // 20,
            bg=self.colours["base_btn"] if self._current_theme == "dark" else LIGHT_BASE_BUTTON_COLOUR,
            fg=self.colours["btn_text"] if self._current_theme == "dark" else LIGHT_BUTTON_TEXT_COLOUR,
            font=BACK_BUTTON_FONT,
            bd=0,               # remove border
            relief="flat"
        )

        # Hover effect
        def on_enter(e, b=btn):
            b.config(bg=self.colours["hover_btn"] if self._current_theme == "dark" else LIGHT_HOVER_BUTTON_COLOUR)
        def on_leave(e, b=btn):
            b.config(bg=self.colours["base_btn"] if self._current_theme == "dark" else LIGHT_BASE_BUTTON_COLOUR)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        # Click effect
        def on_click(e):
            btn.config(bg=self.colours["hover_btn"] if self._current_theme == "dark" else LIGHT_HOVER_BUTTON_COLOUR)
            command()
            btn.config(bg=self.colours["base_btn"] if self._current_theme == "dark" else LIGHT_BASE_BUTTON_COLOUR)

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

        # Keep polling every second
        self.root.after(1000, self._poll_theme)
        
    def _refresh_logos_for_theme(self):
        if not self.current_frame or not self.current_frame.winfo_exists():
            return

        theme = "dark" if is_dark_mode() else "light"
        bg_colour = DARK_GUI_BACKGROUND_COLOUR if theme == "dark" else LIGHT_GUI_BACKGROUND_COLOUR
        base_logo_bg = DARK_BASE_LOGO_COLOUR if theme == "dark" else LIGHT_BASE_LOGO_COLOUR
        hover_logo_bg = DARK_HOVER_LOGO_COLOUR if theme == "dark" else LIGHT_HOVER_LOGO_COLOUR
        base_btn_bg = DARK_BASE_BUTTON_COLOUR if theme == "dark" else LIGHT_BASE_BUTTON_COLOUR
        hover_btn_bg = DARK_HOVER_BUTTON_COLOUR if theme == "dark" else LIGHT_HOVER_BUTTON_COLOUR
        arrow_colour = DARK_ARROW_COLOUR if theme == "dark" else LIGHT_ARROW_COLOUR

        # --- NEW: Apply theme recursively ---
        def apply_theme_recursive(widget):
            if not widget.winfo_exists():
                return
            try:
                widget.config(bg=bg_colour)
            except Exception:
                pass
            for child in widget.winfo_children():
                apply_theme_recursive(child)

        apply_theme_recursive(self.root)
        # --- END NEW ---

        # Update frame background
        self.current_frame.config(bg=bg_colour)

        # --- Brand logos ---
        for widget in self.current_frame.winfo_children():
            if not widget.winfo_exists():
                continue

            if isinstance(widget, tk.Label) and hasattr(widget, "brand_name"):
                brand_name = widget.brand_name
                logo = self.all_logos.get(brand_name, {}).get(theme, {}).get("normal")
                if logo:
                    widget.config(image=logo, bg=base_logo_bg)
                    widget.image = logo

            elif isinstance(widget, tk.Label) and not hasattr(widget, "brand_name"):
                widget.config(bg=base_btn_bg, fg=self.colours["btn_text"] if theme == "dark" else LIGHT_BUTTON_TEXT_COLOUR)

        # --- Console logos ---
        for widget in self.current_frame.winfo_children():
            if not widget.winfo_exists():
                continue

            if isinstance(widget, tk.Canvas) and hasattr(widget, "console_name"):
                console_name = widget.console_name
                logo = self.console_logos.get(console_name, {}).get(theme, {}).get("normal")
                widget.config(bg=base_logo_bg)
                widget.delete("all")
                widget.create_rectangle(0, 0, widget.winfo_width(), widget.winfo_height(), fill=base_logo_bg, outline="")
                if logo:
                    widget.create_image(widget.winfo_width() // 2, widget.winfo_height() // 2, anchor="center", image=logo)
                    widget.image = logo

            elif isinstance(widget, tk.Label) and not hasattr(widget, "console_name"):
                widget.config(bg=base_btn_bg, fg=self.colours["btn_text"] if theme == "dark" else LIGHT_BUTTON_TEXT_COLOUR)

        # --- Arrows ---
        if hasattr(self, "prev_arrow") and self.prev_arrow and self.prev_arrow.winfo_exists():
            self.prev_arrow.config(bg=base_btn_bg, fg=arrow_colour)
            add_hover(self.prev_arrow, base_btn_bg, hover_btn_bg)

        if hasattr(self, "next_arrow") and self.next_arrow and self.next_arrow.winfo_exists():
            self.next_arrow.config(bg=base_btn_bg, fg=arrow_colour)
            add_hover(self.next_arrow, base_btn_bg, hover_btn_bg)

        
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
            fg=self.colours["text"] if self._current_theme == "dark" else LIGHT_GUI_TEXT_COLOUR,
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
                bg_colour = self.colours["base_logo"] if self._current_theme == "dark" else LIGHT_BASE_LOGO_COLOUR
                hover_bg = self.colours["hover_logo"] if self._current_theme == "dark" else LIGHT_HOVER_LOGO_COLOUR

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
                    bg=self.colours["base_btn"] if self._current_theme == "dark" else LIGHT_BASE_BUTTON_COLOUR,
                    fg=self.colours["btn_text"] if self._current_theme == "dark" else LIGHT_BUTTON_TEXT_COLOUR,
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
                fg=self.colours["text"] if self._current_theme == "dark" else LIGHT_GUI_TEXT_COLOUR,
                bg=self._apply_root_background()
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
        theme = self._current_theme
        logos = self.console_logos.get(console_name, {}).get(theme, {})
        normal_img = logos.get("normal")

        base_bg = DARK_BASE_LOGO_COLOUR if theme == "dark" else LIGHT_BASE_LOGO_COLOUR
        hover_bg = DARK_HOVER_LOGO_COLOUR if theme == "dark" else LIGHT_HOVER_LOGO_COLOUR
        base_btn_bg = DARK_BASE_BUTTON_COLOUR if theme == "dark" else LIGHT_BASE_BUTTON_COLOUR
        hover_btn_bg = DARK_HOVER_BUTTON_COLOUR if theme == "dark" else LIGHT_HOVER_BUTTON_COLOUR
        text_fg = DARK_BUTTON_TEXT_COLOUR if theme == "dark" else LIGHT_BUTTON_TEXT_COLOUR

        if normal_img:
            canvas = tk.Canvas(
                parent,
                width=CONSOLE_CANVAS_WIDTH,
                height=CONSOLE_CANVAS_HEIGHT,
                highlightthickness=0,
                bg=base_bg
            )
            canvas.grid_propagate(False)

            # Draw background rectangle
            canvas.create_rectangle(0, 0, CONSOLE_CANVAS_WIDTH, CONSOLE_CANVAS_HEIGHT, fill=base_bg, outline="")

            # Always center the image
            canvas_img = canvas.create_image(
                CONSOLE_CANVAS_WIDTH // 2,
                CONSOLE_CANVAS_HEIGHT // 2,
                anchor="center",
                image=normal_img
            )

            canvas.console_name = console_name  # attach name for theme refresh
            canvas.image = normal_img  # keep reference for Tkinter

            # Store reference for theme updates
            if not hasattr(self, "console_logo_labels"):
                self.console_logo_labels = []
            self.console_logo_labels.append(canvas)

            # Hover effect
            def on_enter(e, c=canvas):
                c.config(bg=hover_bg)
            def on_leave(e, c=canvas):
                c.config(bg=base_bg)

            canvas.bind("<Enter>", on_enter)
            canvas.bind("<Leave>", on_leave)
            canvas.bind("<Button-1>", lambda e, c=console_name: self._open_console_gui(c))

            return canvas
        else:
            # Fallback text button
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

            # Hover effect
            def on_enter(e, l=lbl):
                l.config(bg=hover_btn_bg)
            def on_leave(e, l=lbl):
                l.config(bg=base_btn_bg)

            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)
            lbl.bind("<Button-1>", lambda e, c=console_name: self._open_console_gui(c))

            # Store reference for theme updates
            if not hasattr(self, "console_logo_labels"):
                self.console_logo_labels = []
            self.console_logo_labels.append(lbl)

            return lbl


    # ---------------- Render Console Page ----------------
    def _render_console_page(self, parent, consoles):
        # Destroy previous console widgets except label/back button
        for widget in list(parent.winfo_children()):
            if widget not in (self.console_manu_label, self.back_button):
                if widget.winfo_exists():
                    widget.destroy()

        # Destroy arrows safely
        if hasattr(self, "prev_arrow") and self.prev_arrow and self.prev_arrow.winfo_exists():
            self.prev_arrow.destroy()
        if hasattr(self, "next_arrow") and self.next_arrow and self.next_arrow.winfo_exists():
            self.next_arrow.destroy()

        # Reset console logo references
        self.console_logo_labels = []

        # Configure grid columns
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

            # Padding for logos vs fallback buttons
            if hasattr(btn, "console_name"):  # logo canvas
                padx = CONSOLE_LOGO_PADDING_X
                pady = CONSOLE_LOGO_PADDING_Y
            else:
                padx = CONSOLE_BUTTON_PADDING_X
                pady = CONSOLE_BUTTON_PADDING_Y

            btn.grid(row=row, column=col, columnspan=columnspan, padx=padx, pady=pady, sticky="n")

        # Setup navigation arrows
        theme = self._current_theme
        base_btn_bg = DARK_BASE_BUTTON_COLOUR if theme == "dark" else LIGHT_BASE_BUTTON_COLOUR
        hover_btn_bg = DARK_HOVER_BUTTON_COLOUR if theme == "dark" else LIGHT_HOVER_BUTTON_COLOUR
        arrow_colour = DARK_ARROW_COLOUR if theme == "dark" else LIGHT_ARROW_COLOUR

        if self.current_page_index > 0:
            self.prev_arrow = Label(
                parent,
                text="<",
                font=ARROW_FONT,
                bg=base_btn_bg,
                fg=arrow_colour,
                height=ARROW_BUTTON_HEIGHT,
                width=ARROW_BUTTON_WIDTH
            )
            self.prev_arrow.place(relx=0.00 - ARROW_BUTTON_PADDING_X, rely=0.5 + ARROW_BUTTON_PADDING_Y, anchor="w")
            add_hover(self.prev_arrow, base_btn_bg, hover_btn_bg)
            self.prev_arrow.bind("<Button-1>", lambda e: self._prev_page())

        if self.current_page_index < len(self.pages) - 1:
            self.next_arrow = Label(
                parent,
                text=">",
                font=ARROW_FONT,
                bg=base_btn_bg,
                fg=arrow_colour,
                height=ARROW_BUTTON_HEIGHT,
                width=ARROW_BUTTON_WIDTH
            )
            self.next_arrow.place(relx=1.0 + ARROW_BUTTON_PADDING_X, rely=0.5 + ARROW_BUTTON_PADDING_Y, anchor="e")
            add_hover(self.next_arrow, base_btn_bg, hover_btn_bg)
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
            fg=self.colours["text"] if self._current_theme == "dark" else LIGHT_GUI_TEXT_COLOUR,
            bg=self.colours["bg"]
        ).pack(anchor="n", pady=50)

        # Back button
        back_btn = Label(
            self.current_frame,
            text="Back",
            width=BACK_BUTTON_SIZE[0] // 10,
            height=BACK_BUTTON_SIZE[1] // 20,
            bg=self.colours["base_btn"] if self._current_theme == "dark" else LIGHT_BASE_BUTTON_COLOUR,
            fg=self.colours["btn_text"] if self._current_theme == "dark" else LIGHT_BUTTON_TEXT_COLOUR,
            font=BACK_BUTTON_FONT,
            bd=0,
            relief="flat",
            anchor="center",
            justify="center"
        )

        def safe_config(widget, **kwargs):
            """Safely configure a widget if it still exists."""
            if widget and widget.winfo_exists():
                widget.config(**kwargs)

        def on_enter(e):
            safe_config(back_btn, bg=self.colours["hover_btn"] if self._current_theme == "dark" else LIGHT_HOVER_BUTTON_COLOUR)

        def on_leave(e):
            safe_config(back_btn, bg=self.colours["base_btn"] if self._current_theme == "dark" else LIGHT_BASE_BUTTON_COLOUR)

        def on_click(e):
            # Temporarily show pressed color
            safe_config(back_btn, bg=self.colours["hover_btn"] if self._current_theme == "dark" else LIGHT_HOVER_BUTTON_COLOUR)
            self.show_brands_gui(self._current_manu)
            # Don’t call config again here — widget is destroyed after navigation

        back_btn.bind("<Enter>", on_enter)
        back_btn.bind("<Leave>", on_leave)
        back_btn.bind("<Button-1>", on_click)
        back_btn.pack(anchor="n", pady=20)

if __name__ == "__main__":
    TopLevelGUI()