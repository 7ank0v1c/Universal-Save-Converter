# systems/n64/n64_utils.py

from systems.n64.n64_constants import (
    EEP_LABEL, SRA_LABEL, FLA_LABEL, MPK_LABEL, SRM_LABEL,
    NATIVE_LABEL, PJ64_LABEL, RA_LABEL, WII_LABEL
)

SWAPPABLE_TYPES = [SRA_LABEL, FLA_LABEL, MPK_LABEL, SRM_LABEL]

def determine_valid_target_types(src, src_type, tgt):
    """
    Returns a sorted list of valid target file types based on
    the source type, source, and target system.
    """
    valid_output_types = set()

    # --- SRM as source ---
    if src_type == SRM_LABEL:
        valid_output_types.update([EEP_LABEL, SRA_LABEL, FLA_LABEL, MPK_LABEL])

    # --- EEP/SRA/FLA/MPK as source ---
    elif src_type in [EEP_LABEL, SRA_LABEL, FLA_LABEL, MPK_LABEL]:
        if tgt in [PJ64_LABEL, WII_LABEL, NATIVE_LABEL]:
            valid_output_types.add(src_type)
        elif tgt == RA_LABEL:
            valid_output_types.add(SRM_LABEL)

    # --- Native as source ---
    elif src == NATIVE_LABEL:
        if src_type in [EEP_LABEL, SRA_LABEL, FLA_LABEL, MPK_LABEL]:
            valid_output_types.add(src_type)
        elif src_type == SRM_LABEL:
            valid_output_types.add(SRM_LABEL)

    # Sort the results
    return sorted(valid_output_types)



def is_byteswap_allowed(src_type):
    """Returns True if a byte-swap can be applied for this source type."""
    return src_type in SWAPPABLE_TYPES
