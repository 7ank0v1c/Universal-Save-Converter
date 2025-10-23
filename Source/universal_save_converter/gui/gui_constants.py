# gui/gui_constants.py

# --- Imports ---
from systems.n64.gui.n64_gui_main import setup_n64_gui
from systems.gba.gui.gba_gui_main import setup_gba_gui

# ---------------- Brands → Consoles Map ----------------
BRANDS = {
    "Nintendo": [
        "NES / Famicom",
        "SNES / Super Famicom",
        "Nintendo 64",
        "Nintendo Virtual Boy",
        "Nintendo GameCube",
        "Nintendo Wii",
        "Game Boy / Color",
        "Game Boy Advance",
        "Nintendo DS / DSi",
        "Nintendo 3DS"
    ],
    "SEGA": [
        "Sega Master System",
        "Sega Genesis/Megadrive",
        "Sega Saturn",
        "Sega Dreamcast",
        "Sega GameGear"
    ],
    "PlayStation": [
        "PlayStation 1",
        "PlayStation 2",
        "PlayStation 3",
        "PlayStation Portable",
        "PlayStation Vita"
    ],
    "XBOX": [
        "Xbox",
        "Xbox 360"
    ],
    "Other": [
        "Atari Jaguar",
        "Atari Lynx"
    ]
}

# ---------------- Console GUI Map ----------------
CONSOLE_GUI_MAP = {
    "NES / Famicom": None,
    "SNES / Super Famicom": None,
    "Nintendo 64": setup_n64_gui,
    "Nintendo Virtual Boy": None,
    "Nintendo GameCube": None,
    "Nintendo Wii": None,
    "Game Boy / Color": None,
    "Game Boy Advance": None,
    "Nintendo DS / DSi": None,
    "Nintendo 3DS": None,
    "Sega Master System": None,
    "Sega Genesis/Megadrive": None,
    "Sega Saturn": None,
    "Sega Dreamcast": None,
    "Sega GameGear": None,
    "PlayStation 1": None,
    "PlayStation 2": None,
    "PlayStation 3": None,
    "PlayStation Portable": None,
    "PlayStation Vita": None,
    "Xbox": None,
    "Xbox 360": None,
    "Atari Jaguar": None,
    "Atari Lynx": None
}

# Logo Size
BRAND_LOGO_SIZE = (300, 80)
CONSOLE_LOGO_SIZE = (250, 55)
LOGO_HOVER_SIZE = (300, 80) # could confuse, try remove this later

# Button Size (Abscent of Logo)
BRAND_BUTTON_SIZE = (180, 50)
CONSOLE_BUTTON_SIZE = (290, 60)
BACK_BUTTON_SIZE = (230, 40)
ARROW_BUTTON_WIDTH = 2
ARROW_BUTTON_HEIGHT = 3

# Logo Padding
BRAND_LOGO_PADDING_X = 10   #horizontal
BRAND_LOGO_PADDING_Y = 22   #vertical
CONSOLE_LOGO_PADDING_X = 5   #horizontal
CONSOLE_LOGO_PADDING_Y = 6   #vertical

# Button Padding
BRAND_BUTTON_PADDING_X = 10   #horizontal
BRAND_BUTTON_PADDING_Y = 10   #vertical
CONSOLE_BUTTON_PADDING_X = 10   #horizontal
CONSOLE_BUTTON_PADDING_Y = 8   #vertical
ARROW_BUTTON_PADDING_X = 0.02  #horizontal
ARROW_BUTTON_PADDING_Y = 0.03   #vertical
 
CONSOLE_CANVAS_WIDTH = CONSOLE_LOGO_SIZE[0] + CONSOLE_LOGO_PADDING_X * 20  # width
CONSOLE_CANVAS_HEIGHT = CONSOLE_LOGO_SIZE[1] + CONSOLE_LOGO_PADDING_Y * 4  # height




