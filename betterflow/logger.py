"""
Logging setup — writes to file and stdout.
"""

import sys
import logging

from betterflow.config import CONFIG_DIR, LOG_FILE


def setup_logging() -> logging.Logger:
    """Create and configure the app-wide logger."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("betterflow")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger

    # File handler
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)

    # Console handler
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(sh)

    return logger


log = setup_logging()
