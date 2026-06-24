"""
Text typer — types transcribed text into the currently focused app.
"""

import time
from pynput.keyboard import Controller as KeyboardController
from betterflow.logger import log


class Typer:
    """Types text into whatever app currently has focus, using pynput."""

    def __init__(self, delay: float = 0.0):
        self.kb = KeyboardController()
        self.delay = delay

    def type(self, text: str):
        """Type the given text. Adds a trailing space for natural flow."""
        text = text.strip()
        if not text:
            return
        text = text + " "
        log.info(f"Typing {len(text)} chars...")
        if self.delay <= 0:
            self.kb.type(text)
        else:
            for ch in text:
                self.kb.type(ch)
                time.sleep(self.delay)
