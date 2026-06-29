"""
Logging setup — writes to file only (terminal is for the dashboard).
"""

import logging

from betterflow.config import CONFIG_DIR, LOG_FILE


def setup_logging() -> logging.Logger:
    """Create and configure the app-wide logger."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("betterflow")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger

    # File handler only — keep terminal clean for the dashboard
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)

    return logger


log = setup_logging()
