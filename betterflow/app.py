"""
Main application — ties all components together.
"""

import os
import sys
import time
import threading

from pynput import keyboard

from betterflow import APP_NAME, APP_VERSION, COLORS
from betterflow.config import CONFIG_FILE, load_config
from betterflow.logger import log
from betterflow.dictation import DictationEngine
from betterflow.hotkey import parse_hotkey, normalize_key
from betterflow.floating_icon import FloatingIcon
from betterflow.settings_ui import SettingsWindow
from betterflow.whisper_engine import get_whisper_model


class BetterFlowApp:
    """
    The main app controller. Responsibilities:
    - Manages the floating icon (UI)
    - Listens for global hotkey
    - Delegates dictation to DictationEngine
    - Opens settings window on right-click
    """

    def __init__(self):
        self.cfg = load_config()
        self.engine = DictationEngine(self.cfg)
        self.engine.on_state_change = self._on_state_change
        self.current_keys: set = set()
        self.target_keys = parse_hotkey(self.cfg["hotkey"])
        self._listener = None
        self.floating_icon = None

    def _on_state_change(self, state: str):
        """Forward engine state changes to the floating icon."""
        if self.floating_icon:
            self.floating_icon.set_state(state)

    def _on_icon_click(self):
        """Left-click on icon: toggle dictation."""
        threading.Thread(target=self.engine.toggle, daemon=True).start()

    def _on_icon_right_click(self, event):
        """Right-click on icon: show context menu."""
        import tkinter as tk
        menu = tk.Menu(self.floating_icon.win, tearoff=0)
        menu.configure(
            font=("Segoe UI", 10),
            fg=COLORS["text"], bg=COLORS["bg_card"],
            activebackground=COLORS["accent"],
            activeforeground=COLORS["text"],
        )
        menu.add_command(label="⚙️  Settings", command=self._open_settings)
        menu.add_command(label="📋  Test Typing", command=self._test_type)
        menu.add_separator()
        menu.add_command(label="❌  Quit", command=self._quit)
        menu.tk_popup(event.x_root, event.y_root)


    def _open_settings(self):
        SettingsWindow(
            self.cfg,
            on_save=self._on_settings_saved,
            parent_root=self.floating_icon.root,
        )

    def _on_settings_saved(self, new_cfg):
        log.info("Restarting with new config...")
        self._quit()
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def _test_type(self):
        def _do():
            time.sleep(0.5)
            self.engine.typer.type("Hello from BetterFlow! ☕🎙️")
        threading.Thread(target=_do, daemon=True).start()

    def _quit(self):
        log.info("BetterFlow quitting")
        if self._listener:
            self._listener.stop()
        if self.floating_icon:
            self.floating_icon.quit()

    # ---- Hotkey handling ----

    def _on_key_press(self, key):
        try:
            self.current_keys.add(key)
            self.current_keys.add(normalize_key(key))
            if self.target_keys.issubset(self.current_keys):
                self.engine.toggle()
                self.current_keys.clear()
        except Exception as e:
            log.error(f"Hotkey error: {e}")

    def _on_key_release(self, key):
        try:
            self.current_keys.discard(key)
            self.current_keys.discard(normalize_key(key))
        except Exception:
            pass

    # ---- Run ----

    def run(self):
        """Start the app — this blocks until quit."""
        log.info(f"{APP_NAME} {APP_VERSION} starting")
        log.info(f"Hotkey: {self.cfg['hotkey']}")
        log.info(f"Model: {self.cfg['model_size']} on {self.cfg['device']}")
        log.info(f"Config: {CONFIG_FILE}")

        # Global hotkey listener
        self._listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self._listener.start()

        # Pre-load whisper in background
        log.info("Pre-loading Whisper model in background...")
        threading.Thread(target=lambda: get_whisper_model(self.cfg), daemon=True).start()

        # Start the floating icon (blocks in tkinter mainloop)
        log.info("Starting floating icon. Click it or press hotkey to dictate.")
        self.floating_icon = FloatingIcon(
            on_click=self._on_icon_click,
            on_right_click=self._on_icon_right_click,
        )
        self.floating_icon.run()
