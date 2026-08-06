import json
from pathlib import Path

SETTINGS_FILE = Path("data/settings.json")

def load_settings():
    if not SETTINGS_FILE.exists():
        return {
            "last_project": "",
            "last_credentials": "",
            "last_build_type": "aab",
            "clean_before_build": True,
            "remove_cmake_cache": False
        }
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "last_project": "",
            "last_credentials": "",
            "last_build_type": "aab",
            "clean_before_build": True,
            "remove_cmake_cache": False
        }

def save_settings(settings):
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)
