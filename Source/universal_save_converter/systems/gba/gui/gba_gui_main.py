# systems/gba/gui/gba_gui_main.py

import os
import threading
from tkinter import PhotoImage, Label, Button, Frame, Text, Scrollbar, LEFT, RIGHT, BOTH, Y
from tkinter import ttk

# --- gba Constants ---
from systems.gba.gba_constants import SOURCE_LIST, TARGET_LIST

# --- Utilities ---
from core.gui_logger import set_log_widget
from core.theme_utils import apply_theme, start_polling
from systems.gba.gba_utils import determine_valid_target_types, is_byteswap_allowed
from systems.gba.gui import gba_gui_vars as gui_vars
from gui.gui_utils import GUIResetManager

# --- Callbacks ---
from systems.gba.gui import gba_callbacks

# --- Modularised modules ---
from systems.gba.gui.gba_gui_widgets import (
    create_file_selection,
    create_source_target_widgets,
    create_pad_trim_checkbox,
    create_byteswap_menu
)
from systems.gba.gui.gba_gui_logic import setup_target_type_trace, setup_byteswap_trace, evaluate_byteswap_default

# --------------------------
# Constants
# --------------------------
BASE_WIDTH = 730
EXPANDED_WIDTH = 1000
HEIGHT = 380
VERTICAL_OFFSET = 35


def setup_gba_gui(parent):
    """Set up the gba GUI inside the given parent frame or Tk instance."""
    gui_vars.init_vars(parent)
    log_visible = True

    # Disable resizing
    parent.resizable(False, False)

    # --------------------------
    # Center Window Slightly Higher
    # --------------------------
    def center_window(width, height, vertical_offset=VERTICAL_OFFSET):
        parent.update_idletasks()
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2) - vertical_offset
        parent.geometry(f"{width}x{height}+{x}+{y}")
        return x, y

    center_window(EXPANDED_WIDTH, HEIGHT)

    # --------------------------
    # Load gba Logo
    # --------------------------
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        logo_path = os.path.join(project_root, "resources", "gba_logo.png")
        parent.gba_logo_img = PhotoImage(file=logo_path)
        logo_img = parent.gba_logo_img
        parent.iconphoto(True, logo_img)
    except Exception as e:
        print(f"Could not load logo: {e}")
        logo_img = None

    logo_label = Label(
        parent,
        image=logo_img if logo_img else None,
        text="gba Logo" if not logo_img else "",
        compound="top"
    )
    logo_label.grid(row=7, column=2, padx=10, pady=10, sticky="E")

    # -----------------
    # File Selection Widgets
    # -----------------
    directory_entry = create_file_selection(
        parent,
        gui_vars.input_path,
        gui_vars.source_type_var,
        gba_callbacks.browse_file
    )

    def scroll_to_end(*args):
        parent.after_idle(lambda: directory_entry.xview_moveto(1))

    gui_vars.input_path.trace_add("write", scroll_to_end)
    directory_entry.bind("<KeyRelease>", lambda e: directory_entry.xview_moveto(1))
    directory_entry.bind("<<Paste>>", lambda e: parent.after_idle(lambda: directory_entry.xview_moveto(1)))

    # --------------------------
    # Inline Log Frame
    # --------------------------
    log_frame = Frame(parent)
    log_frame.grid(row=0, column=3, rowspan=9, sticky="nsew", padx=5, pady=5)
    parent.grid_columnconfigure(3, weight=1)

    log_label = Label(log_frame, text="Conversion Log:")
    log_label.pack(anchor="w", padx=5, pady=(5, 0))

    log_text_frame = Frame(log_frame, height=200)
    log_text_frame.pack(fill=BOTH, expand=False, padx=5, pady=5)

    log_box = Text(log_text_frame, height=25, width=50, wrap="word")
    log_box.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar = Scrollbar(log_text_frame, command=log_box.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    log_box.config(yscrollcommand=scrollbar.set)

    set_log_widget(log_box)

    # --------------------------
    # Toggle Log Visibility
    # --------------------------
    def toggle_log_window():
        nonlocal log_visible
        if log_visible:
            log_frame.grid_remove()
            center_window(BASE_WIDTH, HEIGHT)
            log_visible = False
        else:
            log_frame.grid()
            center_window(EXPANDED_WIDTH, HEIGHT)
            log_visible = True

    toggle_btn = Button(parent, text="Show/Hide Log", command=toggle_log_window)
    toggle_btn.grid(row=7, column=0, pady=15, padx=5)

    # --------------------------
    # Source/Target Widgets
    # --------------------------
    source_menu, target_menu, target_type_menu = create_source_target_widgets(
        parent,
        gui_vars.source_var,
        gui_vars.target_var,
        gui_vars.target_type_var,
        gui_vars.source_type_var
    )

    # --------------------------
    # Pad/Trim Checkbox
    # --------------------------
    pad_trim_chk = create_pad_trim_checkbox(parent, gui_vars.trim_pad_var)

    # --------------------------
    # Byte Swap Menu
    # --------------------------
    byteswap_menu = create_byteswap_menu(parent, gui_vars.byteswap_var)
    gui_vars.byteswap_var.set("default")

    # --------------------------
    # Start Conversion (Threaded)
    # --------------------------
    def start_conversion():
        threading.Thread(
            target=gba_callbacks.convert_save_gba,
            kwargs={
                "input_path": gui_vars.input_path,
                "source_var": gui_vars.source_var,
                "source_type_var": gui_vars.source_type_var,
                "target_var": gui_vars.target_var,
                "target_type_var": gui_vars.target_type_var,
                "byteswap_var": gui_vars.byteswap_var,
                "trim_pad_var": gui_vars.trim_pad_var,
                "log_box": log_box
            },
            daemon=True
        ).start()

    convert_btn = Button(parent, text="Convert", width=20, command=start_conversion, state="disabled")
    convert_btn.grid(row=7, column=1, pady=15)

    # --------------------------
    # Convert Button Enable Logic
    # --------------------------
    def update_convert_button(*args):
        if gui_vars.source_var.get() and gui_vars.target_var.get() and gui_vars.target_type_var.get():
            convert_btn.config(state="normal")
        else:
            convert_btn.config(state="disabled")

    gui_vars.source_var.trace_add("write", update_convert_button)
    gui_vars.target_var.trace_add("write", update_convert_button)
    gui_vars.target_type_var.trace_add("write", update_convert_button)

    # --------------------------
    # GUI Reset Manager
    # --------------------------
    def reset_byteswap(_):
        evaluate_byteswap_default(gui_vars.input_path, gui_vars.byteswap_var)

    reset_manager = GUIResetManager()
    reset_manager.add_dependency(
        gui_vars.input_path,
        [
            gui_vars.source_var,
            gui_vars.target_var,
            gui_vars.target_type_var,
            gui_vars.byteswap_var,
            gui_vars.trim_pad_var
        ],
        custom_resets={id(gui_vars.byteswap_var): reset_byteswap}
    )

    # --------------------------
    # GUI Logic Traces
    # --------------------------
    setup_target_type_trace(
        gui_vars.source_var,
        gui_vars.source_type_var,
        gui_vars.target_var,
        gui_vars.target_type_var,
        target_type_menu,
        determine_valid_target_types,
        input_path_var=gui_vars.input_path,
        convert_button=convert_btn
    )

    setup_byteswap_trace(
        gui_vars.source_type_var,
        gui_vars.target_type_var,
        gui_vars.byteswap_var,
        byteswap_menu,
        is_byteswap_allowed,
        input_path_var=gui_vars.input_path
    )

    # --------------------------
    # Auto-select RetroArch as source for SRM files
    # --------------------------
    def auto_select_retroarch(*args):
        path = gui_vars.input_path.get()
        if path.lower().endswith(".srm"):
            parent.after_idle(lambda: gui_vars.source_var.set("RetroArch"))

    gui_vars.input_path.trace_add("write", auto_select_retroarch)

    # --------------------------
    # Apply Theme and Start Polling
    # --------------------------
    apply_theme(parent)
    start_polling(parent)