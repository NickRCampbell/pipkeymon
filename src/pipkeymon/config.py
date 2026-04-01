import json
import os
from pathlib import Path


APP_DIR_NAME = "PipKeyMon"
CONFIG_FILE_NAME = "config.json"


DEFAULT_CONFIG = {
    "selected_controller_index": 0,
    "poll_interval_ms": 8,
    "axis_deadzone": 0.25,
    "button_map": {
        "0": "SPACE",
        "1": "BACKSPACE",
        "2": "C",
        "3": "ENTER",
        "5": "ESCAPE",
        "6": "ESCAPE",
        "9": "E",
        "10": "F",
        "15": "C",
        "11": "UP",
        "12": "DOWN",
        "13": "LEFT",
        "14": "RIGHT",
    },
    "hat_map": {},
    "axis_map": {
        "0": {
            "negative": "LEFT",
            "positive": "RIGHT",
            "threshold": 0.5,
            "deadzone": 0.25,
        },
        "1": {
            "negative": "UP",
            "positive": "DOWN",
            "threshold": 0.5,
            "deadzone": 0.25,
        },
        "4": {
            "positive": "R",
            "threshold": 0.5,
            "deadzone": 0.25,
        },
        "5": {
            "positive": "V",
            "threshold": 0.5,
            "deadzone": 0.25,
        },
    },
}


def get_app_dir():
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        local_app_data = str(Path.home() / "AppData" / "Local")
    return Path(local_app_data) / APP_DIR_NAME


def get_config_path():
    return get_app_dir() / CONFIG_FILE_NAME


def ensure_config_exists():
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if not config_path.exists():
        config_path.write_text(json.dumps(DEFAULT_CONFIG, indent=2) + "\n", encoding="utf-8")
        print(f"Created default config: {config_path}")
    return config_path


def load_config():
    config_path = ensure_config_exists()
    with config_path.open("r", encoding="utf-8") as handle:
        return json.load(handle), config_path
