"""
Configuration management — load, save, and defaults.
"""

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".betterflow"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_FILE = CONFIG_DIR / "betterflow.log"

DEFAULT_CONFIG = {
    "hotkey": "ctrl+shift+space",
    "model_size": "base",
    "language": None,
    "device": "cpu",
    "compute_type": "int8",
    "silence_timeout_sec": 2.0,
    "max_recording_sec": 60,
    "sample_rate": 16000,
    "auto_punctuate": True,
    "type_speed_delay": 0.0,
    "show_overlay": True,
    "play_sounds": True,
}

MODELS = ["tiny", "base", "small", "medium", "large-v3"]

LANGUAGES = [
    ("Auto-detect", None),
    ("English", "en"),
    ("Hindi", "hi"),
    ("Spanish", "es"),
    ("French", "fr"),
    ("German", "de"),
    ("Chinese", "zh"),
    ("Japanese", "ja"),
    ("Korean", "ko"),
    ("Portuguese", "pt"),
    ("Russian", "ru"),
    ("Arabic", "ar"),
    ("Italian", "it"),
    ("Dutch", "nl"),
    ("Turkish", "tr"),
    ("Polish", "pl"),
]


def load_config() -> dict:
    """Load user config from disk, falling back to defaults."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            return {**DEFAULT_CONFIG, **user_cfg}
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict) -> None:
    """Write config to disk."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
