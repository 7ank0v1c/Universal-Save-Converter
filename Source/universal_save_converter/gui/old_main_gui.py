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

        for child in self.root.winfo_children():
            if isinstance(child, (tk.Frame, tk.Label, tk.Canvas)):
                try:
                    child.config(bg=bg_colour)
                except Exception:
                    pass

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
        self._current_manu = None
        self.console_manu_label = None
        self.pages = []
        self.current_page_index = 0
        self.prev_arrow = None
        self.next_arrow = None
        self._hover_initialized = False

        preload_brand_logos(self.all_logos)
        preload_console_logos(self.console_logos)

        self._setup_logo()
        self.show_brands_selection()
        self._apply_root_background()    
        self.root.bind("<FocusIn>", lambda e: self._reactivate_hover_state())
        self.root.after(1000, self._mark_hover_ready)
        self.root.after(1000, self._poll_theme)
        self.root.mainloop()

    def _mark_hover_ready(self):
        """Allow hover reactivation only after first second of runtime."""
        self._hover_initialized = True

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
            lbl.config(bg=self.colours["base_btn"])

        lbl.bind("<Enter>", on_enter)
        lbl.bind("<Leave>", on_leave)

        # Click effect
        lbl.bind("<Button-1>", lambda e: command())

        return lbl

    def bind_hover(widget, base_colour, hover_colour, rect_id=None):
        """
        Bind enter/leave hover effect to a widget.
        If rect_id is provided, it refers to a canvas rectangle.
        """
        def on_enter(e):
            if rect_id is not None:
                widget.itemconfig(rect_id, fill=hover_colour)
            else:
                widget.config(bg=hover_colour)

        def on_leave(e):
            if rect_id is not None:
                widget.itemconfig(rect_id, fill=base_colour)
            else:
                widget.config(bg=base_colour)

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def _apply_theme_to_current_frame(self):
        """Apply theme colors and hover to all widgets in current frame, safely."""
        if not self.current_frame or not self.current_frame.winfo_exists():
            return
        # Schedule actual refresh after the frame is realized
        self.root.after_idle(self._refresh_logos_for_theme)

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

        # ---------------- Helper to bind hover ----------------
        def bind_hover(widget, rect=None):
            """Bind hover to a widget or canvas rectangle."""
            base = self.colours["base_logo"] if rect else self.colours["base_btn"]
            hover = self.colours["hover_logo"] if rect else self.colours["hover_btn"]

            def on_enter(e, w=widget):
                if rect:
                    w.itemconfig(rect, fill=hover)
                else:
                    w.config(bg=hover)

            def on_leave(e, w=widget):
                if rect:
                    w.itemconfig(rect, fill=base)
                else:
                    w.config(bg=base)

            widget.unbind("<Enter>")
            widget.unbind("<Leave>")
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        # ---------------- Recursive background update ----------------
        def apply_bg_recursive(widget):
            if not widget.winfo_exists():
                return
            try:
                widget.config(bg=self.colours["bg"])
            except Exception:
                pass
            for child in widget.winfo_children():
                apply_bg_recursive(child)

        apply_bg_recursive(self.root)
        self.current_frame.config(bg=self.colours["bg"])

        # ---------------- Update all widgets ----------------
        for widget in self.current_frame.winfo_children():
            # ---------------- Handle widgets marked _no_hover ----------------
            if getattr(widget, "_no_hover", False):
                widget.config(bg=self.colours["bg"], fg=self.colours["text"])
                
                # Special case: top brand/logo on console page
                if widget == getattr(self, "console_manu_label", None):
                    brand_name = self._current_manu
                    if brand_name:
                        # Get the theme-specific logo
                        logo_img = self.all_logos.get(brand_name, {}).get(self._current_theme)
                        if logo_img:
                            widget.config(image=logo_img)
                            widget.image = logo_img
                continue

            # Brand logos / buttons (brands page)
            if hasattr(widget, "brand_name") and getattr(widget, "_is_brand_button", False):
                # Directly get the PhotoImage for current theme
                logo = self.all_logos.get(widget.brand_name, {}).get(self._current_theme)

                if logo and isinstance(widget, tk.Canvas):
                    widget.delete("all")
                    # Draw background rectangle
                    rect_id = widget.create_rectangle(
                        0, 0, BRAND_LOGO_SIZE[0], BRAND_LOGO_SIZE[1],
                        fill=self.colours["base_logo"],
                        outline=""
                    )
                    widget._bg_rect_id = rect_id

                    # Place the logo
                    widget.create_image(BRAND_LOGO_SIZE[0] // 2, BRAND_LOGO_SIZE[1] // 2,
                                        anchor="center", image=logo)
                    widget.image = logo

                    # Bind hover
                    def on_enter(e, c=widget):
                        c.itemconfig(c._bg_rect_id, fill=self.colours["hover_logo"])
                    def on_leave(e, c=widget):
                        c.itemconfig(c._bg_rect_id, fill=self.colours["base_logo"])
                    widget.bind("<Enter>", on_enter)
                    widget.bind("<Leave>", on_leave)

                elif isinstance(widget, tk.Label):
                    # fallback button
                    widget.config(bg=self.colours["base_btn"], fg=self.colours["btn_text"])
                    bind_hover(widget)

            # Console logos (Canvas with console_name)
            elif isinstance(widget, tk.Canvas) and hasattr(widget, "console_name"):
                console_name = widget.console_name
                logo = self.console_logos.get(console_name, {}).get(self._current_theme, {}).get("normal")

                widget.delete("all")  # clear old items

                # Draw background rectangle
                rect_id = widget.create_rectangle(
                    0, 0,
                    widget.winfo_width() or CONSOLE_CANVAS_WIDTH,
                    widget.winfo_height() or CONSOLE_CANVAS_HEIGHT,
                    fill=self.colours["base_logo"],
                    outline=""
                )
                widget._bg_rect_id = rect_id

                # Draw logo image if available
                if logo:
                    widget.create_image(
                        widget.winfo_width() // 2,
                        widget.winfo_height() // 2,
                        anchor="center",
                        image=logo
                    )
                    widget.image = logo

                # Bind hover on rectangle
                bind_hover(widget, rect=rect_id)
                widget.unbind("<Button-1>")
                widget.bind("<Button-1>", lambda e, c=console_name: self._open_console_gui(c))

            # Fallback Labels / Buttons
            elif isinstance(widget, tk.Label):
                widget.config(bg=self.colours["base_btn"], fg=self.colours["btn_text"])
                bind_hover(widget)

        # ---------------- Update navigation arrows ----------------
        for arrow in (self.prev_arrow, self.next_arrow):
            if arrow and arrow.winfo_exists():
                arrow.config(bg=self.colours["base_btn"], fg=self.colours["arrow"])
                add_hover(arrow, self.colours["base_btn"], self.colours["hover_btn"])
                
    def _reactivate_hover_state(self):
        """Prevent premature hover activation at startup."""
        if not getattr(self, "_hover_initialized", False):
            return  # 👈 skip during startup
        try:
            # Gather all potential hover widgets in the current frame
            def gather_hover_widgets(widget):
                widgets = []
                for child in widget.winfo_children():
                    # Only consider widgets that actually exist
                    if not child.winfo_exists():
                        continue
                    # Heuristic: labels or canvases we assigned hover to
                    if isinstance(child, (tk.Label, tk.Canvas)):
                        widgets.append(child)
                    # Recurse
                    widgets.extend(gather_hover_widgets(child))
                return widgets

            hover_widgets = gather_hover_widgets(self.current_frame)

            # Simulate hover on all
            for w in hover_widgets:
                try:
                    # Use current pointer position relative to widget
                    x_root, y_root = self.root.winfo_pointerx(), self.root.winfo_pointery()
                    rel_x = x_root - w.winfo_rootx()
                    rel_y = y_root - w.winfo_rooty()
                    # Clamp inside widget bounds
                    w_w, w_h = max(w.winfo_width(), 1), max(w.winfo_height(), 1)
                    rel_x = max(0, min(rel_x, w_w - 1))
                    rel_y = max(0, min(rel_y, w_h - 1))

                    # Trigger enter/leave/motion to refresh hover
                    w.event_generate("<Leave>")
                    w.event_generate("<Enter>")
                    w.event_generate("<Motion>", x=rel_x, y=rel_y)
                except Exception:
                    continue
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
        title_lbl = Label(
            self.current_frame,
            text="Which System Is Your Save For?",
            font=("Arial", 22, "bold"),
            fg=self.colours["text"],
            bg=self.colours["bg"]
        )
        title_lbl._no_hover = True  # <-- mark it
        title_lbl.grid(row=0, column=0, columnspan=4, pady=(20, 30))

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
                    bg=self.colours["bg"],  # base background same as root
                )
                canvas.grid(
                    row=row,
                    column=col,
                    columnspan=columnspan,
                    padx=BRAND_LOGO_PADDING_X,
                    pady=BRAND_LOGO_PADDING_Y,
                    sticky="n"
                )

                # Draw background rectangle for hover effect
                rect_id = canvas.create_rectangle(
                    0, 0, BRAND_LOGO_SIZE[0], BRAND_LOGO_SIZE[1],
                    fill=self.colours["base_logo"], outline=""
                )
                canvas._bg_rect_id = rect_id

                # Place the logo
                canvas.create_image(BRAND_LOGO_SIZE[0] // 2, BRAND_LOGO_SIZE[1] // 2, anchor="center", image=img)
                canvas.image = img

                # Store reference to all theme images for future theme refresh
                canvas.brand_name = manu
                canvas._is_brand_button = True
                canvas._theme_images = img

                # Hover effect
                def on_enter(e, c=canvas):
                    c.itemconfig(c._bg_rect_id, fill=self.colours["hover_logo"])
                def on_leave(e, c=canvas):
                    c.itemconfig(c._bg_rect_id, fill=self.colours["base_logo"])

                canvas.bind("<Enter>", on_enter)
                canvas.bind("<Leave>", on_leave)
                canvas.bind("<Button-1>", lambda e, m=manu: self.show_brands_gui(m))
                
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

                # Mark for theme refresh
                lbl.brand_name = manu
                lbl._is_brand_button = True  # <-- mark as brand button

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
            manu_label._no_hover = True
            manu_label.brand_name = manu
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
            manu_label._no_hover = True
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
        coming_lbl = Label(
            self.current_frame,
            text=f"{console_name} is Coming Soon...",
            font=("Arial", 24, "bold"),
            fg=self.colours["text"],
            bg=self.colours["bg"]
        )
        coming_lbl._no_hover = True  # mark it to skip hover
        coming_lbl.pack(anchor="n", pady=50)

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