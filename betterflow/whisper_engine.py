"""
Whisper model loading — lazy-loaded and cached after first use.
"""

import time
from betterflow.logger import log

# Global cached model instance
_WHISPER_MODEL = None


def get_whisper_model(cfg: dict):
    """Load the Whisper model (downloads on first run). Cached after first call."""
    global _WHISPER_MODEL
    if _WHISPER_MODEL is not None:
        return _WHISPER_MODEL

    from faster_whisper import WhisperModel

    log.info(f"Loading Whisper model '{cfg['model_size']}' on {cfg['device']}...")
    t0 = time.time()
    _WHISPER_MODEL = WhisperModel(
        cfg["model_size"],
        device=cfg["device"],
        compute_type=cfg["compute_type"],
    )
    log.info(f"Whisper loaded in {time.time() - t0:.1f}s")
    return _WHISPER_MODEL
