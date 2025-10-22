# systems/gba/gui/gba_gui_vars.py

from tkinter import StringVar, BooleanVar

# Variables will be created after the root window exists
input_path = None
source_type_var = None
source_var = None
target_var = None
target_type_var = None
trim_pad_var = None
byteswap_var = None

def init_vars(master):
    """
    Initialize Tkinter variables with a reference to the root window.
    Call this AFTER creating the Tk root.
    """
    global input_path, source_type_var, source_var, target_var
    global target_type_var, trim_pad_var, byteswap_var

    input_path = StringVar(master=master)
    source_type_var = StringVar(master=master)
    source_var = StringVar(master=master)
    target_var = StringVar(master=master)
    target_type_var = StringVar(master=master)
    trim_pad_var = BooleanVar(master=master)
    byteswap_var = StringVar(master=master, value="None")