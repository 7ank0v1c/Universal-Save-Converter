# core/file_utils.py
import os
from datetime import datetime
from tkinter import messagebox
from systems.n64.n64_constants import (
    EEP_EXT, SRA_EXT, FLA_EXT, MPK_EXT, SRM_EXT,
    SIZE_EEP, SIZE_SRA, SIZE_FLA, SIZE_MPK, SIZE_SRM,
    EEP_LABEL, SRA_LABEL, FLA_LABEL, MPK_LABEL, SRM_LABEL,
    NATIVE_LABEL, PJ64_LABEL, RA_LABEL, WII_LABEL,
    FILE_TYPES, SOURCE_LIST, TARGET_LIST
)

def detect_file_type(filename: str) -> str | None:
    """Detect the type of N64 save file based on extension."""
    ext = os.path.splitext(filename)[1].lower()
    return {
        EEP_EXT: EEP_LABEL,
        SRA_EXT: SRA_LABEL,
        FLA_EXT: FLA_LABEL,
        MPK_EXT: MPK_LABEL,
        SRM_EXT: SRM_LABEL
    }.get(ext, None)


def read_bytes(path: str) -> bytes | None:
    """Read binary data from a file, return None if error occurs."""
    try:
        with open(path, "rb") as f:
            return f.read()
    except Exception:
        messagebox.showerror("Error", f"Could not read file: {path}")
        return None


def write_bytes(data: bytes, path: str) -> bool:
    """Write binary data to a file, return True on success, False on failure."""
    try:
        with open(path, "wb") as f:
            f.write(data)
        return True
    except Exception:
        messagebox.showerror("Error", f"Could not write file: {path}")
        return False


def resize_bytes(data: bytes, new_size: int, offset: int = 0) -> bytes:
    """
    Resize data to new_size bytes.

    Positive offset: copy data starting at offset in new array.
    Negative offset: trim data from the start.
    """
    if offset < 0:
        data = data[abs(offset):]
        offset = 0

    result = bytearray(new_size)
    for i in range(len(data)):
        dest_index = i + offset
        if 0 <= dest_index < new_size:
            result[dest_index] = data[i]
    return bytes(result)


def new_filename(filename: str, extension: str, prefix: str = "Converted_") -> str:
    """
    Generate a new filename with a timestamp and optional prefix.
    Example: MySave.sra → Converted_20251014-153245_MySave.sra
    """
    base, _ = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{prefix}{timestamp}_{base}{extension}"
