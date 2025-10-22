# systems/gba/gui/gba_callbacks.py

import os
from tkinter import filedialog
from systems.gba.gba_conversion_core import convert_save
from core.logger import log
from systems.gba.gba_constants import (
    EEP_EXT, SRA_EXT, FLA_EXT, MPK_EXT, SRM_EXT,
    EEP_LABEL, SRA_LABEL, FLA_LABEL, MPK_LABEL, SRM_LABEL
)

# Map file extensions to human-readable labels
EXT_TO_LABEL = {
    EEP_EXT: EEP_LABEL,
    SRA_EXT: SRA_LABEL,
    FLA_EXT: FLA_LABEL,
    MPK_EXT: MPK_LABEL,
    SRM_EXT: SRM_LABEL
}


def convert_save_gba(input_path, source_var, source_type_var,
                     target_var, target_type_var, byteswap_var,
                     trim_pad_var, log_box):
    """
    Thin wrapper for GUI button. Pulls variables and passes to system convert.
    Logs success if conversion completes without exceptions.
    """
    try:
        convert_save(
            path=input_path.get(),
            src=source_var.get(),
            src_type=source_type_var.get(),
            tgt=target_var.get(),
            tgt_type=target_type_var.get(),
            byteswap_option=byteswap_var.get(),
            trim_pad_option=trim_pad_var.get(),
            log_box=log_box
        )
        log("Conversion completed successfully!", log_box=log_box, level="SUCCESS")
    except Exception as e:
        log(f"Conversion failed: {e}", log_box=log_box, level="ERROR")


def browse_file(filetypes, path_var, type_var):
    """
    GUI file browser for gba save files. Updates path and sets human-readable source type.
    """
    filepath = filedialog.askopenfilename(filetypes=filetypes)
    if not filepath:
        return

    path_var.set(filepath)

    # Determine type based on extension and set label
    ext = os.path.splitext(filepath)[1].lower()
    type_var.set(EXT_TO_LABEL.get(ext, "Unknown"))