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
        self.root.bind("<FocusIn>", lambda e: self._reactivate_hover_state())
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
            bg=self.colours["base_btn"],
            fg=self.colours["btn_text"],
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

        def apply_recursive(widget):
            """Apply theme to this widget and its children."""
            if not widget.winfo_exists():
                return
            try:
                if isinstance(widget, (tk.Frame, tk.Toplevel)):
                    widget.config(bg=self.colours["bg"])
                elif isinstance(widget, tk.Label):
                    widget.config(bg=self.colours["base_btn"], fg=self.colours["btn_text"])
                elif isinstance(widget, tk.Canvas):
                    widget.config(bg=self.colours["base_logo"])
            except Exception:
                pass
            for child in widget.winfo_children():
                apply_recursive(child)

        apply_recursive(self.current_frame)

        # Update arrows explicitly
        for arrow in (self.prev_arrow, self.next_arrow):
            if arrow and arrow.winfo_exists():
                arrow.config(bg=self.colours["base_btn"], fg=self.colours["arrow"])
                add_hover(arrow, self.colours["base_btn"], self.colours["hover_btn"])

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
            bg=self.colours["base_btn"],
            fg=self.colours["btn_text"],
            font=BACK_BUTTON_FONT,
            bd=0,          
            relief="flat"
        )

        # Hover effect
        def on_enter(e, b=btn):
            b.config(bg=self.colours["hover_btn"])
        def on_leave(e, b=btn):
            b.config(bg=self.colours["base_btn"])

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        # Click effect
        def on_click(e):
            btn.config(bg=self.colours["hover_btn"])
            command()
            try:
                btn.config(bg=self.colours["base_btn"])
            except tk.TclError:
                # Button was destroyed or window closed — ignore
                pass

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

        # Make whole window use background color
        def apply_theme_recursive(widget):
            if not widget.winfo_exists():
                return
            try:
                widget.config(bg=self.colours["bg"])
            except Exception:
                pass
            for child in widget.winfo_children():
                apply_theme_recursive(child)

        apply_theme_recursive(self.root)
        self.current_frame.config(bg=self.colours["bg"])

        # --- Brand and Console logos + fallback text buttons ---
        for widget in self.current_frame.winfo_children():
            if not widget.winfo_exists():
                continue

            # Brand logo labels (image)
            if isinstance(widget, tk.Label) and hasattr(widget, "brand_name"):
                brand_name = widget.brand_name
                logo = self.all_logos.get(brand_name, {}).get(self._current_theme, {}).get("normal")
                if logo:
                    widget.config(image=logo, bg=self.colours["base_logo"])
                    widget.image = logo

            # Fallback text labels/buttons (brands or other labels)
            elif isinstance(widget, tk.Label) and not hasattr(widget, "brand_name") and not hasattr(widget, "console_name"):
                widget.config(bg=self.colours["base_btn"], fg=self.colours["btn_text"])

                # Rebind hover handlers using current colours
                widget.unbind("<Enter>")
                widget.unbind("<Leave>")

                def _lbl_on_enter(e, w=widget):
                    # Use current colours at time of event
                    w.config(bg=self.colours["hover_btn"])
                def _lbl_on_leave(e, w=widget):
                    w.config(bg=self.colours["base_btn"])

                widget.bind("<Enter>", _lbl_on_enter)
                widget.bind("<Leave>", _lbl_on_leave)

            # Console logo canvases
            elif isinstance(widget, tk.Canvas) and hasattr(widget, "console_name"):
                console_name = widget.console_name
                logo = self.console_logos.get(console_name, {}).get(self._current_theme, {}).get("normal")

                # Clear and recreate background rectangle and image
                widget.delete("all")
                rect_id = widget.create_rectangle(
                    0, 0, widget.winfo_width() or CONSOLE_CANVAS_WIDTH, widget.winfo_height() or CONSOLE_CANVAS_HEIGHT,
                    fill=self.colours["base_logo"],
                    outline=""
                )
                widget._bg_rect_id = rect_id

                if logo:
                    widget.create_image(widget.winfo_width() // 2, widget.winfo_height() // 2, anchor="center", image=logo)
                    widget.image = logo

                # Rebind hover handlers to update the rectangle fill
                widget.unbind("<Enter>")
                widget.unbind("<Leave>")

                def _canvas_on_enter(e, w=widget):
                    rid = getattr(w, "_bg_rect_id", None)
                    if rid is not None:
                        try:
                            w.itemconfig(rid, fill=self.colours["hover_logo"])
                        except Exception:
                            pass
                def _canvas_on_leave(e, w=widget):
                    rid = getattr(w, "_bg_rect_id", None)
                    if rid is not None:
                        try:
                            w.itemconfig(rid, fill=self.colours["base_logo"])
                        except Exception:
                            pass

                widget.bind("<Enter>", _canvas_on_enter)
                widget.bind("<Leave>", _canvas_on_leave)

            # Other labels (e.g. console fallback labels) — ensure they use colours and hover
            elif isinstance(widget, tk.Label) and not hasattr(widget, "console_name"):
                widget.config(bg=self.colours["base_btn"], fg=self.colours["btn_text"])

                widget.unbind("<Enter>")
                widget.unbind("<Leave>")

                def _lbl2_on_enter(e, w=widget):
                    w.config(bg=self.colours["hover_btn"])
                def _lbl2_on_leave(e, w=widget):
                    w.config(bg=self.colours["base_btn"])

                widget.bind("<Enter>", _lbl2_on_enter)
                widget.bind("<Leave>", _lbl2_on_leave)

        # --- Arrows ---
        for arrow in (self.prev_arrow, self.next_arrow):
            if arrow and arrow.winfo_exists():
                arrow.config(bg=self.colours["base_btn"], fg=self.colours["arrow"])
                add_hover(arrow, self.colours["base_btn"], self.colours["hover_btn"])

        # Finally, force a motion event on the widget under the pointer so hover becomes active immediately
        self._reactivate_hover_state()

    def _reactivate_hover_state(self):
        """
        Fix hover issue after theme change or window refocus.
        Strategy:
        - Find the widget under pointer (if any) and simulate <Leave> + <Enter>.
        - Works even if pointer just re-entered window after being outside.
        """
        try:
            x_root = self.root.winfo_pointerx()
            y_root = self.root.winfo_pointery()
            widget = self.root.winfo_containing(x_root, y_root)
            if not widget:
                return

            # Compute relative coordinates
            rel_x = x_root - widget.winfo_rootx()
            rel_y = y_root - widget.winfo_rooty()

            # Clamp within widget bounds
            w_w = widget.winfo_width() or 1
            w_h = widget.winfo_height() or 1
            rel_x = max(0, min(rel_x, w_w - 1))
            rel_y = max(0, min(rel_y, w_h - 1))

            # Generate leave + enter + motion
            widget.event_generate("<Leave>")
            widget.event_generate("<Enter>")
            widget.event_generate("<Motion>", x=rel_x, y=rel_y)
            widget.update_idletasks()
        except Exception as e:
            print(f"[HoverFix] _reactivate_hover_state failed: {e}")
            
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
                canvas = tk.Canvas(
                    self.current_frame,
                    width=BRAND_LOGO_SIZE[0],
                    height=BRAND_LOGO_SIZE[1],
                    highlightthickness=0,
                    bg=self.colours["base_logo"],
                )
                canvas.grid(
                    row=row,
                    column=col,
                    columnspan=columnspan,
                    padx=BRAND_LOGO_PADDING_X,
                    pady=BRAND_LOGO_PADDING_Y,
                    sticky="n"
                )

                canvas.create_image(0, 0, anchor="nw", image=img)
                canvas.image = img  # prevent GC

                def on_enter(e, c=canvas):
                    c.config(bg=self.colours["hover_logo"])
                def on_leave(e, c=canvas):
                    c.config(bg=self.colours["base_logo"])

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
        theme = self._current_theme
        logos = self.console_logos.get(console_name, {}).get(theme, {})
        normal_img = logos.get("normal")

        if normal_img:
            canvas = tk.Canvas(
                parent,
                width=CONSOLE_CANVAS_WIDTH,
                height=CONSOLE_CANVAS_HEIGHT,
                highlightthickness=0,
                bg=self.colours["base_logo"]
            )
            canvas.grid_propagate(False)

            # Draw background rectangle and keep reference
            rect = canvas.create_rectangle(
                0, 0, CONSOLE_CANVAS_WIDTH, CONSOLE_CANVAS_HEIGHT,
                fill=self.colours["base_logo"],
                outline=""
            )

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

            # Hover effect updates the rectangle fill
            def on_enter(e, r=rect):
                canvas.itemconfig(r, fill=self.colours["hover_logo"])
            def on_leave(e, r=rect):
                canvas.itemconfig(r, fill=self.colours["base_logo"])

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
                bg=self.colours["base_btn"],
                fg=self.colours["btn_text"],
                font=("Arial", 16, "bold"),
                bd=0,
                relief="flat",
                anchor="center",
                justify="center"
            )

            # Hover effect
            def on_enter(e, l=lbl):
                l.config(bg=self.colours["hover_btn"])
            def on_leave(e, l=lbl):
                l.config(bg=self.colours["base_btn"])

            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)
            lbl.bind("<Button-1>", lambda e, c=console_name: self._open_console_gui(c))

            # Store reference for theme updates
            if not hasattr(self, "console_logo_labels"):
                self.console_logo_labels = []
            self.console_logo_labels.append(lbl)

            return lbl

    # ---------------- Page Navigation ----------------
    def _next_page(self):
        """Go to the next page of consoles."""
        if self.current_page_index < len(self.pages) - 1:
            self.current_page_index += 1
            self._render_console_page(self.current_frame, self.pages[self.current_page_index])

    def _prev_page(self):
        """Go to the previous page of consoles."""
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
        if self.current_page_index > 0:
            self.prev_arrow = Label(
                parent,
                text="<",
                font=ARROW_FONT,
                bg=self.colours["base_btn"],
                fg=self.colours["arrow"],
                height=ARROW_BUTTON_HEIGHT,
                width=ARROW_BUTTON_WIDTH
            )
            self.prev_arrow.place(relx=0.00 - ARROW_BUTTON_PADDING_X, rely=0.5 + ARROW_BUTTON_PADDING_Y, anchor="w")
            add_hover(self.prev_arrow, self.colours["base_btn"], self.colours["hover_btn"])
            self.prev_arrow.bind("<Button-1>", lambda e: self._prev_page())

        if self.current_page_index < len(self.pages) - 1:
            self.next_arrow = Label(
                parent,
                text=">",
                font=ARROW_FONT,
                bg=self.colours["base_btn"],
                fg=self.colours["arrow"],
                height=ARROW_BUTTON_HEIGHT,
                width=ARROW_BUTTON_WIDTH
            )
            self.next_arrow.place(relx=1.0 + ARROW_BUTTON_PADDING_X, rely=0.5 + ARROW_BUTTON_PADDING_Y, anchor="e")
            add_hover(self.next_arrow, self.colours["base_btn"], self.colours["hover_btn"])
            self.next_arrow.bind("<Button-1>", lambda e: self._next_page())
                        
    # ---------------- Open Console GUI ----------------
    def _open_console_gui(self, console_name):
        gui_class = CONSOLE_GUI_MAP.get(console_name)

        if callable(gui_class):
            # Create a new frame for the console GUI
            self._clear_frame()
            console_frame = Frame(self.root, padx=20, pady=20, bg=self.colours["bg"])
            console_frame.pack(expand=True, fill="both")
            gui_class(console_frame)
        else:
            self._show_coming_soon(console_name)

    # - Show Coming Soon -
    def _show_coming_soon(self, console_name):
        self._clear_frame()
        self.current_frame = Frame(self.root, padx=50, pady=50, bg=self.colours["bg"])
        self.current_frame.pack(expand=True, fill="both")

        # Label at the top
        Label(
            self.current_frame,
            text=f"{console_name} is Coming Soon...",
            font=("Arial", 24, "bold"),
            fg=self.colours["text"],
            bg=self.colours["bg"]
        ).pack(anchor="n", pady=50)

        # Back button
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
            """Safely configure a widget if it still exists."""
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