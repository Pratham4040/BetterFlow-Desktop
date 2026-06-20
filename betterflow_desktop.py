"""
BetterFlow Desktop — System-wide voice dictation
=================================================

A cozy desktop app with a floating animated icon and settings UI.
Press a hotkey, speak, and your words get typed into ANY app.

License: MIT — free forever.
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
import math
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd
from pynput import keyboard
from pynput.keyboard import Controller as KeyboardController, Key
from PIL import Image, ImageDraw, ImageTk

# Whisper is imported lazily on first use so the app starts fast
WHISPER_MODEL = None

# ============================================================================
# Configuration
# ============================================================================

APP_NAME = "BetterFlow"
APP_VERSION = "2.0.0"
APP_TAGLINE = "Voice dictation, anywhere."

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

# Colors — cozy warm palette
COLORS = {
    "bg_dark": "#1e1511",
    "bg_card": "#2a1f1a",
    "bg_hover": "#3d2e25",
    "accent": "#d97757",
    "accent_light": "#e89071",
    "accent_glow": "#ff9a6c",
    "text": "#fff5e6",
    "text_dim": "#b8a99e",
    "success": "#7bc47f",
    "recording": "#ff6b6b",
    "transcribing": "#ffd93d",
}


def load_config() -> dict:
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
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


# ============================================================================
# Logging
# ============================================================================

def setup_logging() -> logging.Logger:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("betterflow")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(sh)
    return logger


log = setup_logging()


# ============================================================================
# Whisper loader (lazy)
# ============================================================================

def get_whisper_model(cfg: dict):
    global WHISPER_MODEL
    if WHISPER_MODEL is not None:
        return WHISPER_MODEL
    from faster_whisper import WhisperModel
    log.info(f"Loading Whisper model '{cfg['model_size']}' on {cfg['device']}...")
    t0 = time.time()
    WHISPER_MODEL = WhisperModel(
        cfg["model_size"],
        device=cfg["device"],
        compute_type=cfg["compute_type"],
    )
    log.info(f"Whisper loaded in {time.time() - t0:.1f}s")
    return WHISPER_MODEL


# ============================================================================
# Audio recorder
# ============================================================================

class AudioRecorder:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.frames: list[np.ndarray] = []
        self.stream = None
        self._lock = threading.Lock()

    def start(self):
        self.frames = []
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=self._callback,
            blocksize=1024,
        )
        self.stream.start()

    def _callback(self, indata, frames, time_info, status):
        with self._lock:
            self.frames.append(indata.copy())

    def stop(self) -> np.ndarray:
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        with self._lock:
            if not self.frames:
                return np.array([], dtype="float32")
            return np.concatenate(self.frames, axis=0).flatten()


    def get_rms(self) -> float:
        with self._lock:
            if not self.frames:
                return 0.0
            last = self.frames[-1]
        return float(np.sqrt(np.mean(last ** 2)))


# ============================================================================
# Text typer
# ============================================================================

class Typer:
    def __init__(self, delay: float = 0.0):
        self.kb = KeyboardController()
        self.delay = delay

    def type(self, text: str):
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


# ============================================================================
# Beep sounds
# ============================================================================

def beep(freq=660, duration=0.15, volume=0.3):
    try:
        sr = 44100
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        wave_ = volume * np.sin(2 * np.pi * freq * t).astype(np.float32)
        sd.play(wave_, sr)
        sd.wait()
    except Exception:
        pass


# ============================================================================
# Dictation engine
# ============================================================================

class DictationEngine:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.recorder = AudioRecorder(sample_rate=cfg["sample_rate"])
        self.typer = Typer(delay=cfg.get("type_speed_delay", 0.0))
        self.is_recording = False
        self._lock = threading.Lock()
        self.on_state_change = None  # callback: (state) -> None

    def _set_state(self, state: str):
        """States: idle, listening, transcribing"""
        if self.on_state_change:
            self.on_state_change(state)

    def toggle(self):
        with self._lock:
            if self.is_recording:
                threading.Thread(target=self._stop_and_transcribe, daemon=True).start()
            else:
                threading.Thread(target=self._start, daemon=True).start()

    def _start(self):
        try:
            if self.cfg.get("play_sounds", True):
                beep(880, 0.1, 0.2)
            self.recorder.start()
            self.is_recording = True
            self._set_state("listening")
            log.info("Recording started")
            threading.Thread(target=self._watch_silence, daemon=True).start()
        except Exception as e:
            log.error(f"Failed to start: {e}")
            self._set_state("idle")

    def _watch_silence(self):
        timeout = self.cfg.get("silence_timeout_sec", 2.0)
        silence_start = None
        max_rec = self.cfg.get("max_recording_sec", 60)
        start_time = time.time()
        while self.is_recording:
            time.sleep(0.1)
            if not self.is_recording:
                return
            rms = self.recorder.get_rms()
            if rms < 0.01:
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > timeout:
                    log.info("Auto-stop: silence")
                    self.toggle()
                    return
            else:
                silence_start = None
            if time.time() - start_time > max_rec:
                log.info("Auto-stop: max time")
                self.toggle()
                return


    def _stop_and_transcribe(self):
        try:
            self.is_recording = False
            self._set_state("transcribing")
            audio = self.recorder.stop()
            if self.cfg.get("play_sounds", True):
                beep(440, 0.15, 0.2)
            if len(audio) < self.cfg["sample_rate"] * 0.1:
                log.info("Recording too short, ignoring")
                self._set_state("idle")
                return
            log.info(f"Recorded {len(audio) / self.cfg['sample_rate']:.1f}s")
            t0 = time.time()
            model = get_whisper_model(self.cfg)
            segments, info = model.transcribe(
                audio,
                language=self.cfg.get("language"),
                vad_filter=True,
                without_timestamps=True,
            )
            text = " ".join(seg.text.strip() for seg in segments).strip()
            log.info(f"Transcribed in {time.time() - t0:.1f}s: {text[:80]}")
            self._set_state("idle")
            time.sleep(0.1)
            if text:
                self.typer.type(text)
        except Exception as e:
            log.error(f"Transcription failed: {e}")
            self._set_state("idle")


# ============================================================================
# Hotkey parser
# ============================================================================

def parse_hotkey(hotkey_str: str) -> set:
    parts = [p.strip().lower() for p in hotkey_str.split("+")]
    keys = set()
    for p in parts:
        if p in {"ctrl", "control"}:
            keys.add(Key.ctrl)
        elif p in {"cmd", "cmd_l", "cmd_r", "win", "super"}:
            keys.add(Key.cmd)
        elif p in {"alt", "alt_l", "alt_gr"}:
            keys.add(Key.alt)
        elif p == "shift":
            keys.add(Key.shift)
        elif p == "space":
            keys.add(Key.space)
        elif p == "enter":
            keys.add(Key.enter)
        elif p == "tab":
            keys.add(Key.tab)
        elif p == "esc":
            keys.add(Key.esc)
        elif len(p) == 1:
            keys.add(p)
        else:
            try:
                keys.add(getattr(Key, p))
            except AttributeError:
                keys.add(p)
    return keys


def normalize_key(key):
    """Normalize left/right key variants to generic keys."""
    try:
        name = key.name if hasattr(key, 'name') else str(key)
    except Exception:
        return key
    if name in ('ctrl_l', 'ctrl_r'):
        return Key.ctrl
    elif name in ('shift_l', 'shift_r'):
        return Key.shift
    elif name in ('alt_l', 'alt_r', 'alt_gr'):
        return Key.alt
    elif name in ('cmd_l', 'cmd_r'):
        return Key.cmd
    return key


# ============================================================================
# Floating Icon Widget — always-on-screen animated orb
# ============================================================================

class FloatingIcon:
    """A small draggable always-on-top animated circle widget."""

    SIZE = 56
    ICON_SIZE = 48

    def __init__(self, on_click=None, on_right_click=None):
        import tkinter as tk
        self.tk = tk
        self.on_click = on_click
        self.on_right_click = on_right_click
        self.state = "idle"  # idle, listening, transcribing
        self._animation_frame = 0
        self._drag_data = {"x": 0, "y": 0}

        self.root = tk.Tk()
        self.root.withdraw()  # hidden main window

        # Floating window
        self.win = tk.Toplevel(self.root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.92)
        try:
            self.win.attributes("-transparentcolor", "#010101")
        except Exception:
            pass


        # Position bottom-right of screen
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        x = sw - self.SIZE - 80
        y = sh - self.SIZE - 120
        self.win.geometry(f"{self.SIZE}x{self.SIZE}+{x}+{y}")

        self.canvas = tk.Canvas(
            self.win,
            width=self.SIZE,
            height=self.SIZE,
            bg="#010101",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)

        # Bind events
        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Button-3>", self._on_right_click)

        self._draw_frame()
        self._animate()

    def _on_press(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self._drag_data["moved"] = False

    def _on_drag(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        x = self.win.winfo_x() + dx
        y = self.win.winfo_y() + dy
        self.win.geometry(f"+{x}+{y}")
        if abs(dx) > 3 or abs(dy) > 3:
            self._drag_data["moved"] = True

    def _on_release(self, event):
        if not self._drag_data.get("moved", False):
            if self.on_click:
                self.on_click()

    def _on_right_click(self, event):
        if self.on_right_click:
            self.on_right_click(event)


    def set_state(self, state: str):
        self.state = state

    def _draw_frame(self):
        """Draw one frame of the animated icon."""
        self.canvas.delete("all")
        cx, cy = self.SIZE // 2, self.SIZE // 2
        r = self.ICON_SIZE // 2
        frame = self._animation_frame

        if self.state == "idle":
            # Gentle breathing glow
            pulse = 0.5 + 0.5 * math.sin(frame * 0.05)
            glow_r = r + 2 + pulse * 2
            # Outer glow
            self.canvas.create_oval(
                cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r,
                fill="", outline=COLORS["accent"], width=1,
            )
            # Main circle
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=COLORS["bg_card"], outline=COLORS["accent"], width=2,
            )
            # Coffee cup icon (simple)
            self._draw_coffee(cx, cy)

        elif self.state == "listening":
            # Pulsing red ring
            pulse = 0.5 + 0.5 * math.sin(frame * 0.15)
            glow_r = r + 3 + pulse * 4
            self.canvas.create_oval(
                cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r,
                fill="", outline=COLORS["recording"], width=2,
            )
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=COLORS["bg_card"], outline=COLORS["recording"], width=3,
            )
            # Mic icon
            self._draw_mic(cx, cy, pulse)

        elif self.state == "transcribing":
            # Spinning dots
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=COLORS["bg_card"], outline=COLORS["transcribing"], width=2,
            )
            # Three orbiting dots
            for i in range(3):
                angle = (frame * 0.1) + (i * 2.094)  # 120 degrees apart
                dx = math.cos(angle) * (r - 8)
                dy = math.sin(angle) * (r - 8)
                dot_r = 3
                self.canvas.create_oval(
                    cx + dx - dot_r, cy + dy - dot_r,
                    cx + dx + dot_r, cy + dy + dot_r,
                    fill=COLORS["transcribing"], outline="",
                )


    def _draw_coffee(self, cx, cy):
        """Draw a simple coffee cup icon."""
        # Cup body
        self.canvas.create_rectangle(
            cx - 7, cy - 4, cx + 5, cy + 8,
            fill=COLORS["accent"], outline=COLORS["accent_light"], width=1,
        )
        # Handle
        self.canvas.create_arc(
            cx + 4, cy - 1, cx + 11, cy + 6,
            start=270, extent=180,
            outline=COLORS["accent_light"], width=1, style="arc",
        )
        # Steam lines
        for i, sx in enumerate([cx - 4, cx - 1, cx + 2]):
            offset = math.sin(self._animation_frame * 0.08 + i) * 1.5
            self.canvas.create_line(
                sx, cy - 5, sx + offset, cy - 10,
                fill=COLORS["text_dim"], width=1,
            )

    def _draw_mic(self, cx, cy, pulse):
        """Draw a microphone icon."""
        # Mic body
        self.canvas.create_oval(
            cx - 5, cy - 10, cx + 5, cy + 2,
            fill=COLORS["recording"], outline="",
        )
        # Mic stand
        self.canvas.create_line(
            cx, cy + 2, cx, cy + 8,
            fill=COLORS["recording"], width=2,
        )
        # Base
        self.canvas.create_line(
            cx - 5, cy + 8, cx + 5, cy + 8,
            fill=COLORS["recording"], width=2,
        )
        # Sound waves
        wave_alpha = int(pulse * 3)
        for i in range(wave_alpha):
            wr = 9 + i * 4
            self.canvas.create_arc(
                cx - wr, cy - 5 - wr // 2, cx + wr, cy - 5 + wr // 2,
                start=30, extent=120,
                outline=COLORS["recording"], width=1, style="arc",
            )

    def _animate(self):
        self._animation_frame += 1
        self._draw_frame()
        delay = 50 if self.state != "idle" else 80
        self.root.after(delay, self._animate)

    def run(self):
        self.root.mainloop()

    def quit(self):
        try:
            self.root.after(0, self.root.destroy)
        except Exception:
            pass


# ============================================================================
# Settings Window — cozy UI
# ============================================================================

class SettingsWindow:
    """A warm, cozy settings panel."""

    def __init__(self, cfg: dict, on_save=None, parent_root=None):
        import tkinter as tk
        from tkinter import ttk
        self.tk = tk
        self.cfg = cfg.copy()
        self.on_save = on_save

        self.win = tk.Toplevel(parent_root) if parent_root else tk.Tk()
        self.win.title(f"{APP_NAME} — Settings")
        self.win.geometry("480x620")
        self.win.configure(bg=COLORS["bg_dark"])
        self.win.resizable(False, False)
        try:
            self.win.attributes("-topmost", True)
        except Exception:
            pass

        # Main frame with padding
        main = tk.Frame(self.win, bg=COLORS["bg_dark"], padx=24, pady=16)
        main.pack(fill="both", expand=True)

        # Title
        tk.Label(
            main, text=f"☕ {APP_NAME} Settings",
            font=("Segoe UI", 16, "bold"),
            fg=COLORS["accent"], bg=COLORS["bg_dark"],
        ).pack(anchor="w", pady=(0, 16))

        # --- Model section ---
        self._section(main, "🤖 Whisper Model")
        model_frame = tk.Frame(main, bg=COLORS["bg_card"])
        model_frame.pack(fill="x", pady=(0, 12))

        self.model_var = tk.StringVar(value=cfg["model_size"])
        for m in MODELS:
            rb = tk.Radiobutton(
                model_frame, text=m.capitalize(),
                variable=self.model_var, value=m,
                font=("Segoe UI", 10),
                fg=COLORS["text"], bg=COLORS["bg_card"],
                selectcolor=COLORS["bg_hover"],
                activebackground=COLORS["bg_card"],
                activeforeground=COLORS["accent"],
                highlightthickness=0,
            )
            rb.pack(anchor="w", padx=12, pady=2)


        # --- Language section ---
        self._section(main, "🌍 Language")
        lang_frame = tk.Frame(main, bg=COLORS["bg_card"])
        lang_frame.pack(fill="x", pady=(0, 12))

        current_lang = cfg.get("language") or "Auto-detect"
        self.lang_var = tk.StringVar(value=current_lang)
        lang_names = [l[0] for l in LANGUAGES]
        lang_menu = tk.OptionMenu(lang_frame, self.lang_var, *lang_names)
        lang_menu.config(
            font=("Segoe UI", 10),
            fg=COLORS["text"], bg=COLORS["bg_hover"],
            activebackground=COLORS["accent"],
            highlightthickness=0, bd=0,
        )
        lang_menu["menu"].config(
            font=("Segoe UI", 10),
            fg=COLORS["text"], bg=COLORS["bg_card"],
        )
        lang_menu.pack(padx=12, pady=8, anchor="w")

        # --- Hotkey section ---
        self._section(main, "⌨️ Hotkey")
        hotkey_frame = tk.Frame(main, bg=COLORS["bg_card"])
        hotkey_frame.pack(fill="x", pady=(0, 12))

        self.hotkey_var = tk.StringVar(value=cfg["hotkey"])
        hotkey_entry = tk.Entry(
            hotkey_frame, textvariable=self.hotkey_var,
            font=("Segoe UI", 11),
            fg=COLORS["text"], bg=COLORS["bg_hover"],
            insertbackground=COLORS["accent"],
            highlightthickness=1, highlightcolor=COLORS["accent"],
            bd=0,
        )
        hotkey_entry.pack(padx=12, pady=8, fill="x")

        # --- Device section ---
        self._section(main, "💻 Device")
        device_frame = tk.Frame(main, bg=COLORS["bg_card"])
        device_frame.pack(fill="x", pady=(0, 12))

        self.device_var = tk.StringVar(value=cfg["device"])
        for d in ["cpu", "cuda"]:
            rb = tk.Radiobutton(
                device_frame, text=d.upper(),
                variable=self.device_var, value=d,
                font=("Segoe UI", 10),
                fg=COLORS["text"], bg=COLORS["bg_card"],
                selectcolor=COLORS["bg_hover"],
                activebackground=COLORS["bg_card"],
                activeforeground=COLORS["accent"],
                highlightthickness=0,
            )
            rb.pack(side="left", padx=12, pady=8)


        # --- Silence timeout ---
        self._section(main, "🔇 Silence Timeout (seconds)")
        timeout_frame = tk.Frame(main, bg=COLORS["bg_card"])
        timeout_frame.pack(fill="x", pady=(0, 12))

        self.timeout_var = tk.DoubleVar(value=cfg.get("silence_timeout_sec", 2.0))
        timeout_scale = tk.Scale(
            timeout_frame, from_=0.5, to=10.0, resolution=0.5,
            orient="horizontal", variable=self.timeout_var,
            font=("Segoe UI", 9),
            fg=COLORS["text"], bg=COLORS["bg_card"],
            troughcolor=COLORS["bg_hover"],
            activebackground=COLORS["accent"],
            highlightthickness=0, bd=0,
        )
        timeout_scale.pack(padx=12, pady=8, fill="x")

        # --- Toggles ---
        toggles_frame = tk.Frame(main, bg=COLORS["bg_card"])
        toggles_frame.pack(fill="x", pady=(0, 12))

        self.sounds_var = tk.BooleanVar(value=cfg.get("play_sounds", True))
        tk.Checkbutton(
            toggles_frame, text="🔊 Play sounds",
            variable=self.sounds_var,
            font=("Segoe UI", 10),
            fg=COLORS["text"], bg=COLORS["bg_card"],
            selectcolor=COLORS["bg_hover"],
            activebackground=COLORS["bg_card"],
            highlightthickness=0,
        ).pack(anchor="w", padx=12, pady=4)

        self.overlay_var = tk.BooleanVar(value=cfg.get("show_overlay", True))
        tk.Checkbutton(
            toggles_frame, text="👁️ Show listening overlay",
            variable=self.overlay_var,
            font=("Segoe UI", 10),
            fg=COLORS["text"], bg=COLORS["bg_card"],
            selectcolor=COLORS["bg_hover"],
            activebackground=COLORS["bg_card"],
            highlightthickness=0,
        ).pack(anchor="w", padx=12, pady=4)

        # --- Save button ---
        save_btn = tk.Button(
            main, text="💾  Save & Restart",
            font=("Segoe UI", 11, "bold"),
            fg=COLORS["text"], bg=COLORS["accent"],
            activebackground=COLORS["accent_light"],
            activeforeground=COLORS["text"],
            bd=0, padx=20, pady=10,
            cursor="hand2",
            command=self._save,
        )
        save_btn.pack(pady=(16, 0))


    def _section(self, parent, text):
        import tkinter as tk
        tk.Label(
            parent, text=text,
            font=("Segoe UI", 11, "bold"),
            fg=COLORS["text_dim"], bg=COLORS["bg_dark"],
        ).pack(anchor="w", pady=(8, 4))

    def _save(self):
        # Map language name back to code
        lang_name = self.lang_var.get()
        lang_code = None
        for name, code in LANGUAGES:
            if name == lang_name:
                lang_code = code
                break

        new_cfg = {
            **self.cfg,
            "model_size": self.model_var.get(),
            "language": lang_code,
            "hotkey": self.hotkey_var.get(),
            "device": self.device_var.get(),
            "silence_timeout_sec": self.timeout_var.get(),
            "play_sounds": self.sounds_var.get(),
            "show_overlay": self.overlay_var.get(),
        }
        save_config(new_cfg)
        log.info("Settings saved. Restart required for some changes.")
        self.win.destroy()
        if self.on_save:
            self.on_save(new_cfg)


# ============================================================================
# Main App — ties everything together
# ============================================================================

class BetterFlowApp:
    def __init__(self):
        self.cfg = load_config()
        self.engine = DictationEngine(self.cfg)
        self.engine.on_state_change = self._on_state_change
        self.current_keys: set = set()
        self.target_keys = parse_hotkey(self.cfg["hotkey"])
        self._listener = None
        self.floating_icon = None

    def _on_state_change(self, state: str):
        if self.floating_icon:
            self.floating_icon.set_state(state)

    def _on_icon_click(self):
        threading.Thread(target=self.engine.toggle, daemon=True).start()

    def _on_icon_right_click(self, event):
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
        SettingsWindow(self.cfg, on_save=self._on_settings_saved,
                       parent_root=self.floating_icon.root)

    def _on_settings_saved(self, new_cfg):
        log.info("Restarting with new config...")
        self._quit()
        # Restart the process
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

    def run(self):
        log.info(f"{APP_NAME} {APP_VERSION} starting")
        log.info(f"Hotkey: {self.cfg['hotkey']}")
        log.info(f"Model: {self.cfg['model_size']} on {self.cfg['device']}")
        log.info(f"Config: {CONFIG_FILE}")

        # Start hotkey listener
        self._listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self._listener.start()

        # Pre-load whisper model
        log.info("Pre-loading Whisper model in background...")
        threading.Thread(target=lambda: get_whisper_model(self.cfg), daemon=True).start()

        # Start floating icon (this blocks — tkinter mainloop)
        log.info("Starting floating icon. Click it or press hotkey to dictate.")
        self.floating_icon = FloatingIcon(
            on_click=self._on_icon_click,
            on_right_click=self._on_icon_right_click,
        )
        self.floating_icon.run()


# ============================================================================
# Entry point
# ============================================================================

def main():
    print(f"\n  ☕  {APP_NAME} {APP_VERSION}  —  {APP_TAGLINE}\n")
    app = BetterFlowApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
