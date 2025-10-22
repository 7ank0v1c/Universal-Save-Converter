# systems/gba/gui/gba_gui_widgets.py

from tkinter import Label, Entry, Button, Checkbutton, Frame, Text, Scrollbar, LEFT, BOTH, Y, W, E
from tkinter import ttk
from systems.gba.gba_constants import SOURCE_LIST, TARGET_LIST
from systems.gba.gba_utils import determine_valid_target_types, is_byteswap_allowed

def create_file_selection(root, input_path, source_type_var, browse_callback):
    Label(root, text="Select GBA Save File:").grid(row=0, column=0, sticky=W, padx=10, pady=5)
    directory_entry = Entry(root, textvariable=input_path, width=45)
    directory_entry.grid(row=0, column=1, padx=10, pady=5)
    
    Button(
        root, text="Browse", 
        command=lambda: browse_callback(
            filetypes=[("gba Saves", "*.eep *.sra *.fla *.mpk *.srm")],
            path_var=input_path,
            type_var=source_type_var
        )
    ).grid(row=0, column=2, padx=10, pady=5)
    
    return directory_entry

def create_source_target_widgets(root, source_var, target_var, target_type_var, source_type_var):
    # Source File Type Label
    Label(root, text="Save File Source Type:").grid(row=1, column=0, sticky=W, padx=10, pady=5)
    source_type_label = Label(root, textvariable=source_type_var, relief="flat", width=22, anchor=W)
    source_type_label.grid(row=1, column=1, padx=10, pady=5)

    # Source Dropdown
    Label(root, text="Save File Source:").grid(row=2, column=0, sticky=W, padx=10, pady=5)
    source_menu = ttk.Combobox(root, textvariable=source_var, values=SOURCE_LIST, state="readonly")
    source_menu.grid(row=2, column=1, padx=10, pady=5)

    # Target Dropdown
    Label(root, text="Save File Target:").grid(row=3, column=0, sticky=W, padx=10, pady=5)
    target_menu = ttk.Combobox(root, textvariable=target_var, values=TARGET_LIST, state="readonly")
    target_menu.grid(row=3, column=1, padx=10, pady=5)

    # Target Type Dropdown
    Label(root, text="Save File Target Type:").grid(row=4, column=0, sticky=W, padx=10, pady=5)
    target_type_menu = ttk.Combobox(root, textvariable=target_type_var, state="readonly")
    target_type_menu.grid(row=4, column=1, padx=10, pady=5)

    return source_menu, target_menu, target_type_menu

def create_pad_trim_checkbox(root, trim_pad_var):
    Checkbutton(
        root,
        text="Pad/trim to standard file type size",
        variable=trim_pad_var,
        anchor="e",
        justify="center"
    ).grid(row=5, column=1, sticky="we", padx=100, pady=5)

def create_byteswap_menu(root, byteswap_var):
    Label(root, text="Force Byte Swap:").grid(row=6, column=0, sticky=W, padx=10, pady=5)
    byteswap_menu = ttk.Combobox(root, textvariable=byteswap_var, values=["Default", "2 bytes", "4 bytes"], state="readonly")
    byteswap_menu.grid(row=6, column=1, padx=10, pady=5)
    return byteswap_menu