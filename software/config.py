"""
PC Link - Configuration & Theme Constants
"""
import os
import json
from pathlib import Path

# --- Visual Theme: Electric Green & Dark Forest Green ---
THEME = {
    "PRIMARY": "#00E676",          # Vivid electric green
    "PRIMARY_HOVER": "#00C853",    # Deep electric green hover
    "SECONDARY": "#0E2A1B",        # Dark forest green container
    "SECONDARY_BORDER": "#1B4D31", # Subtle emerald border
    "BG_DARK": "#0A0D0B",          # Deep obsidian black background
    "CARD_BG": "#131A15",          # Surface card dark green-black
    "CARD_BORDER": "#1F2B22",      # Card stroke
    "CARD_HOVER": "#1A241D",       # Interactive card hover
    "TEXT_MAIN": "#FFFFFF",        # Pure white text
    "TEXT_MUTED": "#9E9E9E",       # Light gray neutral
    "TEXT_SECONDARY": "#B0BEC5",   # Clean cool gray
    "ACCENT_GREEN": "#00FF66",     # High-contrast highlight
    "WARNING_AMBER": "#FFB300",    # Warning status
    "DANGER_RED": "#FF5252",       # Hardware fault / error
    "DISABLED": "#2A332C",         # Disabled control surface
    "DISABLED_TEXT": "#546E7A",    # Disabled text
}

APP_NAME = "PC Link"
TAGLINE = "DATA • POWER • TOGETHER."
VERSION = "1.0.0"

DEFAULT_SETTINGS = {
    "local_role": "PC A",            # "PC A" or "PC B"
    "connection_mode": "virtual",     # "virtual" (loopback daemon) or "serial"
    "serial_port": "AUTO",
    "baud_rate": 115200,
    "download_dir": str(Path.home() / "Downloads" / "PC_Link_Transfers"),
    "auto_connect": True,
    "chunk_size": 4096,
    "log_level": "INFO",
}

SETTINGS_FILE = Path(__file__).parent / "settings.json"

def load_settings() -> dict:
    settings = dict(DEFAULT_SETTINGS)
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                settings.update(saved)
        except Exception:
            pass
    # Ensure download folder exists
    try:
        os.makedirs(settings["download_dir"], exist_ok=True)
    except Exception:
        pass
    return settings

def save_settings(settings: dict):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")
