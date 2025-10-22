import os
from tkinter import filedialog, messagebox
from core.file_utils import read_bytes, write_bytes, resize_bytes, new_filename
from core.swap_utils import byteswap, determine_swap_size
from core.logger import log
from .gba_conversion_table import conversion_table
from .gba_constants import *

def convert_save(path, src, src_type, tgt, tgt_type, byteswap_option, trim_pad_option, log_box=None):
    """
    System-specific gba save conversion.
    Returns path of saved file or None if cancelled/failed.
    """
    if not path or not os.path.exists(path):
        log("Invalid input path.", log_box=log_box, level="ERROR")
        messagebox.showerror("Error", "Please select a valid input file.")
        return None

    key = f"{src}-{src_type}-{tgt}-{tgt_type}"
    log(f"Starting conversion: {path}", log_box=log_box, level="INFO")

    data = read_bytes(path)
    if not data:
        log("Error reading input file.", log_box=log_box, level="ERROR")
        return None

    # Default conversion parameters
    tgt_size = len(data)
    offset = 0
    swap_required = False
    extension = os.path.splitext(path)[1]

    # --- Conversion table lookup ---
    conv = conversion_table.get(key)
    if conv:
        src_size, tgt_size, offset, swap_required, extension = conv
        log(f"Using conversion table entry: {key}", log_box=log_box, level="CONVERSION")
    else:
        log("No matching conversion found; using raw copy.", log_box=log_box, level="WARN")

    # Native target adjustments
    if tgt == NATIVE_LABEL:
        tgt_size = len(data)
        offset = 0
        swap_required = False
        extension = os.path.splitext(path)[1]
        log("Target is Native — using direct copy.", log_box=log_box, level="CONVERSION")

    # SRM-specific offsets
    if src_type == SRA_LABEL and tgt_type == SRM_LABEL:
        tgt_size = SIZE_SRM
        offset = SIZE_SRA_SRM_OFFSET
        swap_required = True
        extension = SRM_EXT
    elif src_type == FLA_LABEL and tgt_type == SRM_LABEL:
        tgt_size = SIZE_SRM
        offset = SIZE_FLA_SRM_OFFSET
        swap_required = True
        extension = SRM_EXT
    elif src_type == MPK_LABEL and tgt_type == SRM_LABEL:
        tgt_size = SIZE_SRM
        offset = SIZE_MPK_SRM_OFFSET
        swap_required = False
        extension = SRM_EXT
    elif src_type == SRM_LABEL:
        if tgt_type == SRA_LABEL:
            tgt_size = SIZE_SRA
            offset = -SIZE_SRA_SRM_OFFSET
            swap_required = True
            extension = SRA_EXT
        elif tgt_type == FLA_LABEL:
            tgt_size = SIZE_FLA
            offset = -SIZE_FLA_SRM_OFFSET
            swap_required = True
            extension = FLA_EXT
        elif tgt_type == MPK_LABEL:
            tgt_size = SIZE_MPK
            offset = -SIZE_MPK_SRM_OFFSET
            swap_required = False
            extension = MPK_EXT
        elif tgt_type == EEP_LABEL:
            tgt_size = SIZE_EEP
            offset = 0
            swap_required = False
            extension = EEP_EXT
    elif src_type == EEP_LABEL and tgt_type == SRM_LABEL:
        tgt_size = SIZE_SRM
        offset = 0
        swap_required = False
        extension = SRM_EXT

    log(f"Resizing data to {tgt_size} bytes (offset {offset})", log_box=log_box, level="CONVERSION")
    data = resize_bytes(data, tgt_size, offset)

    # --- Byte swap ---
    swap_size = determine_swap_size(swap_required_from_table=swap_required,
                                    user_choice=byteswap_option)
    if swap_size > 1:
        log(f"Applying {swap_size}-byte swap...", log_box=log_box, level="CONVERSION")
        data = byteswap(data, swap_size)
    else:
        log("No byte swap applied.", log_box=log_box, level="CONVERSION")

    # --- Determine output extension ---
    ext_map = {EEP_LABEL: EEP_EXT, SRA_LABEL: SRA_EXT, FLA_LABEL: FLA_EXT,
               MPK_LABEL: MPK_EXT, SRM_LABEL: SRM_EXT}
    out_ext = ext_map.get(tgt_type, extension)
    new_name = new_filename(os.path.basename(path), out_ext)

    # --- Save file dialog ---
    out_path = filedialog.asksaveasfilename(
        initialfile=new_name,
        defaultextension=out_ext,
        filetypes=[("gba Save Files", f"*{out_ext}")]
    )
    if not out_path:
        log("Save operation cancelled by user.", log_box=log_box, level="WARN")
        return None

    if write_bytes(data, out_path):
        log(f"File written successfully → {out_path}", log_box=log_box, level="SUCCESS")
        messagebox.showinfo("Success", f"File converted and saved as:\n{out_path}")
        return out_path
    else:
        log("Error writing file.", log_box=log_box, level="ERROR")
        return None
    