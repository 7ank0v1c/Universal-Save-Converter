# systems/n64/gui/n64_gui_logic.py

def setup_target_type_trace(
    source_var, source_type_var, target_var, target_type_var, target_type_menu,
    determine_valid_target_types, input_path_var=None, convert_button=None
):
    """
    Updates target_type_menu based on current source and target selections.
    Auto-selects first valid target type for all sources except RetroArch SRM files.
    Optionally disables convert_button until a valid selection is made.
    """
    def update_target_type_menu(*args):
        valid_output_types = determine_valid_target_types(
            source_var.get(), source_type_var.get(), target_var.get()
        )
        target_type_menu['values'] = valid_output_types

        # Detect RetroArch SRM file
        is_retroarch_srm = (
            source_var.get() == "RetroArch" or
            (input_path_var and input_path_var.get().lower().endswith(".srm"))
        )

        if is_retroarch_srm:
            if target_type_var.get() not in valid_output_types:
                target_type_var.set("")
        else:
            if target_type_var.get() not in valid_output_types:
                target_type_var.set(valid_output_types[0] if valid_output_types else "")

        if convert_button:
            if target_type_var.get() and valid_output_types:
                convert_button.config(state="normal")
            else:
                convert_button.config(state="disabled")

    # Attach trace callbacks
    source_var.trace_add("write", update_target_type_menu)
    source_type_var.trace_add("write", update_target_type_menu)
    target_var.trace_add("write", update_target_type_menu)
    if input_path_var:
        input_path_var.trace_add("write", update_target_type_menu)

    # Initial call
    update_target_type_menu()


def evaluate_byteswap_default(input_path_var, byteswap_var):
    path = input_path_var.get()
    # Always show "Default" in the GUI
    byteswap_var.set("Default")


def setup_byteswap_trace(source_type_var, target_type_var, byteswap_var, byteswap_menu, is_byteswap_allowed, input_path_var=None):
    """
    Enables/disables byte swap options based on source type.
    Sets initial default based on system-specific logic if input_path_var is provided.
    """
    def update_byteswap_menu(*args):
        if is_byteswap_allowed(source_type_var.get()):
            byteswap_menu.config(state="readonly")
        else:
            byteswap_menu.config(state="disabled")
            byteswap_var.set("Default")

        # Evaluate N64-specific default if input path is provided
        if input_path_var:
            evaluate_byteswap_default(input_path_var, byteswap_var)

    # Initial default
    if input_path_var:
        evaluate_byteswap_default(input_path_var, byteswap_var)
    else:
        byteswap_var.set("Default")

    source_type_var.trace_add("write", update_byteswap_menu)
    target_type_var.trace_add("write", update_byteswap_menu)
    if input_path_var:
        input_path_var.trace_add("write", update_byteswap_menu)