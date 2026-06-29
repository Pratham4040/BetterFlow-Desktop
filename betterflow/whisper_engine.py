"""
Whisper model loading — lazy-loaded and cached after first use.
"""

import os
import time
import threading
from betterflow.logger import log

# Suppress noisy huggingface warnings in terminal
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Global cached model instance
_WHISPER_MODEL = None
_CURRENT_MODEL_SIZE = None
_LOAD_LOCK = threading.Lock()
_IS_LOADING = False


def is_loading() -> bool:
    """Check if a model is currently being downloaded/loaded."""
    return _IS_LOADING


def get_whisper_model(cfg: dict):
    """Load the Whisper model (downloads on first run). Cached after first call."""
    global _WHISPER_MODEL, _CURRENT_MODEL_SIZE, _IS_LOADING

    # If already loaded with the right model, return immediately
    if _WHISPER_MODEL is not None and _CURRENT_MODEL_SIZE == cfg["model_size"]:
        return _WHISPER_MODEL

    # Only one thread downloads at a time
    with _LOAD_LOCK:
        # Double-check after acquiring lock (another thread may have loaded it)
        if _WHISPER_MODEL is not None and _CURRENT_MODEL_SIZE == cfg["model_size"]:
            return _WHISPER_MODEL

        from faster_whisper import WhisperModel
        from huggingface_hub import snapshot_download

        _IS_LOADING = True
        model_name = f"Systran/faster-whisper-{cfg['model_size']}"
        log.info(f"Downloading/loading Whisper model '{cfg['model_size']}'...")

        # Download silently (progress goes to log file, not terminal)
        import logging as _logging
        import warnings as _warnings
        _logging.getLogger("huggingface_hub").setLevel(_logging.WARNING)
        _warnings.filterwarnings("ignore", module="huggingface_hub")

        from betterflow.dashboard import print_status
        print_status(f"Loading model '{cfg['model_size']}'...", style="#ffd93d")

        try:
            snapshot_download(model_name, local_dir=None)
        except Exception:
            pass

        log.info(f"Loading Whisper model '{cfg['model_size']}' on {cfg['device']}...")
        t0 = time.time()
        _WHISPER_MODEL = WhisperModel(
            cfg["model_size"],
            device=cfg["device"],
            compute_type=cfg["compute_type"],
        )
        _CURRENT_MODEL_SIZE = cfg["model_size"]
        _IS_LOADING = False
        log.info(f"Whisper '{cfg['model_size']}' loaded in {time.time() - t0:.1f}s")
        print_status(f"Model '{cfg['model_size']}' ready ✓", style="#7bc47f")
        return _WHISPER_MODEL


def reload_model():
    """Clear the cached model so the next get_whisper_model() loads fresh."""
    global _WHISPER_MODEL, _CURRENT_MODEL_SIZE
    _WHISPER_MODEL = None
    _CURRENT_MODEL_SIZE = None
    log.info("Whisper model cache cleared — will reload on next use.")
