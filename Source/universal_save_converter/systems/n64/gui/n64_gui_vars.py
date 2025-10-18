# systems/n64/gui/n64_gui_vars.py

from tkinter import StringVar, BooleanVar

# systems/n64/gui/n64_gui_vars.py

from tkinter import StringVar, BooleanVar

# Tkinter variables (initialized later)
input_path: StringVar
source_type_var: StringVar
source_var: StringVar
target_var: StringVar
target_type_var: StringVar
trim_pad_var: BooleanVar
byteswap_var: StringVar

def init_vars(master):
    """
    Initialize Tkinter variables with a reference to the root window.
    Must be called AFTER the Tk root window or parent frame exists.
    """
    global input_path, source_type_var, source_var, target_var
    global target_type_var, trim_pad_var, byteswap_var

    input_path = StringVar(master=master, value="")
    source_type_var = StringVar(master=master, value="")
    source_var = StringVar(master=master, value="")
    target_var = StringVar(master=master, value="")
    target_type_var = StringVar(master=master, value="")
    trim_pad_var = BooleanVar(master=master, value=False)
    byteswap_var = StringVar(master=master, value="default")