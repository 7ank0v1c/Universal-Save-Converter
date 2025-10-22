# gui/gui_utils.py
import tkinter as tk
from PIL import Image

def center_window(win, width, height):
    x = (win.winfo_screenwidth() - width) // 2
    y = (win.winfo_screenheight() - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

def add_hover(widget, normal_bg, hover_bg):
    widget.bind("<Enter>", lambda e: widget.config(bg=hover_bg))
    widget.bind("<Leave>", lambda e: widget.config(bg=normal_bg))

class GUIResetManager:
    def __init__(self):
        # internal dict: id(upstream_var) -> (upstream_var_obj, list of (downstream_var, custom_reset_func))
        self.dependencies = {}

    def add_dependency(self, upstream_var, downstream_vars, custom_resets=None):
        """
        downstream_vars: list of variables to reset
        custom_resets: dict {id(var): callable} for custom reset logic
        """
        key = id(upstream_var)
        if key not in self.dependencies:
            self.dependencies[key] = (upstream_var, [])

        for var in downstream_vars:
            reset_func = None
            if custom_resets and id(var) in custom_resets:
                reset_func = custom_resets[id(var)]
            self.dependencies[key][1].append((var, reset_func))

        # Attach trace
        upstream_var.trace_add("write", lambda *args, k=key: self.reset_downstream(k))

    def reset_downstream(self, key):
        upstream_var, downstream_list = self.dependencies.get(key, (None, []))
        for var, reset_func in downstream_list:
            if reset_func:
                reset_func(var)
            else:
                # default generic reset
                if isinstance(var, (tk.StringVar, tk.IntVar, tk.DoubleVar)):
                    var.set("")
                elif isinstance(var, tk.BooleanVar):
                    var.set(False)