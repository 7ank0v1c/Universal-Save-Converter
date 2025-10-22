# gui/config_manager.py

import json
import os
import sys

class ConfigManager:
    def __init__(self, filename="gui_config.json"):
        # Determine path next to executable or script
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller executable
            self.config_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            self.config_dir = os.path.dirname(os.path.abspath(__file__))

        self.config_path = os.path.join(self.config_dir, filename)
        self.config = {}
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    self.config = json.load(f)
            except Exception:
                self.config = {}
        else:
            self.config = {}

    def save_config(self):
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception:
            pass

    def get_log_visible(self, default=True):
        return self.config.get("log_visible", default)

    def set_log_visible(self, visible: bool):
        self.config["log_visible"] = visible
        self.save_config()