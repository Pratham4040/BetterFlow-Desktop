"""
Settings window — cozy dark-themed GUI for configuring BetterFlow.
"""

from typing import Optional, Callable

from betterflow import APP_NAME, COLORS
from betterflow.config import MODELS, LANGUAGES, save_config
from betterflow.logger import log


class SettingsWindow:
    """A warm, cozy settings panel built with tkinter."""

    def __init__(self, cfg: dict, on_save: Optional[Callable] = None,
                 parent_root=None):
        import tkinter as tk
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

        main = tk.Frame(self.win, bg=COLORS["bg_dark"], padx=24, pady=16)
        main.pack(fill="both", expand=True)

        # Title
        tk.Label(
            main, text=f"☕ {APP_NAME} Settings",
            font=("Segoe UI", 16, "bold"),
            fg=COLORS["accent"], bg=COLORS["bg_dark"],
        ).pack(anchor="w", pady=(0, 16))

        # --- Model ---
        self._section(main, tk, "🤖 Whisper Model")
        model_frame = tk.Frame(main, bg=COLORS["bg_card"])
        model_frame.pack(fill="x", pady=(0, 12))
        self.model_var = tk.StringVar(value=cfg["model_size"])
        for m in MODELS:
            tk.Radiobutton(
                model_frame, text=m.capitalize(),
                variable=self.model_var, value=m,
                font=("Segoe UI", 10),
                fg=COLORS["text"], bg=COLORS["bg_card"],
                selectcolor=COLORS["bg_hover"],
                activebackground=COLORS["bg_card"],
                activeforeground=COLORS["accent"],
                highlightthickness=0,
            ).pack(anchor="w", padx=12, pady=2)


        # --- Language ---
        self._section(main, tk, "🌍 Language")
        lang_frame = tk.Frame(main, bg=COLORS["bg_card"])
        lang_frame.pack(fill="x", pady=(0, 12))
        current_lang = cfg.get("language") or "Auto-detect"
        self.lang_var = tk.StringVar(value=current_lang)
        lang_menu = tk.OptionMenu(lang_frame, self.lang_var, *[l[0] for l in LANGUAGES])
        lang_menu.config(
            font=("Segoe UI", 10), fg=COLORS["text"], bg=COLORS["bg_hover"],
            activebackground=COLORS["accent"], highlightthickness=0, bd=0,
        )
        lang_menu["menu"].config(font=("Segoe UI", 10), fg=COLORS["text"], bg=COLORS["bg_card"])
        lang_menu.pack(padx=12, pady=8, anchor="w")

        # --- Hotkey ---
        self._section(main, tk, "⌨️ Hotkey")
        hotkey_frame = tk.Frame(main, bg=COLORS["bg_card"])
        hotkey_frame.pack(fill="x", pady=(0, 12))
        self.hotkey_var = tk.StringVar(value=cfg["hotkey"])
        tk.Entry(
            hotkey_frame, textvariable=self.hotkey_var,
            font=("Segoe UI", 11), fg=COLORS["text"], bg=COLORS["bg_hover"],
            insertbackground=COLORS["accent"],
            highlightthickness=1, highlightcolor=COLORS["accent"], bd=0,
        ).pack(padx=12, pady=8, fill="x")

        # --- Device ---
        self._section(main, tk, "💻 Device")
        device_frame = tk.Frame(main, bg=COLORS["bg_card"])
        device_frame.pack(fill="x", pady=(0, 12))
        self.device_var = tk.StringVar(value=cfg["device"])
        for d in ["cpu", "cuda"]:
            tk.Radiobutton(
                device_frame, text=d.upper(),
                variable=self.device_var, value=d,
                font=("Segoe UI", 10), fg=COLORS["text"], bg=COLORS["bg_card"],
                selectcolor=COLORS["bg_hover"],
                activebackground=COLORS["bg_card"],
                activeforeground=COLORS["accent"],
                highlightthickness=0,
            ).pack(side="left", padx=12, pady=8)

        # --- Silence timeout ---
        self._section(main, tk, "🔇 Silence Timeout (seconds)")
        timeout_frame = tk.Frame(main, bg=COLORS["bg_card"])
        timeout_frame.pack(fill="x", pady=(0, 12))
        self.timeout_var = tk.DoubleVar(value=cfg.get("silence_timeout_sec", 2.0))
        tk.Scale(
            timeout_frame, from_=0.5, to=10.0, resolution=0.5,
            orient="horizontal", variable=self.timeout_var,
            font=("Segoe UI", 9), fg=COLORS["text"], bg=COLORS["bg_card"],
            troughcolor=COLORS["bg_hover"], activebackground=COLORS["accent"],
            highlightthickness=0, bd=0,
        ).pack(padx=12, pady=8, fill="x")


        # --- Toggles ---
        toggles_frame = tk.Frame(main, bg=COLORS["bg_card"])
        toggles_frame.pack(fill="x", pady=(0, 12))
        self.sounds_var = tk.BooleanVar(value=cfg.get("play_sounds", True))
        tk.Checkbutton(
            toggles_frame, text="🔊 Play sounds", variable=self.sounds_var,
            font=("Segoe UI", 10), fg=COLORS["text"], bg=COLORS["bg_card"],
            selectcolor=COLORS["bg_hover"], activebackground=COLORS["bg_card"],
            highlightthickness=0,
        ).pack(anchor="w", padx=12, pady=4)
        self.overlay_var = tk.BooleanVar(value=cfg.get("show_overlay", True))
        tk.Checkbutton(
            toggles_frame, text="👁️ Show listening overlay", variable=self.overlay_var,
            font=("Segoe UI", 10), fg=COLORS["text"], bg=COLORS["bg_card"],
            selectcolor=COLORS["bg_hover"], activebackground=COLORS["bg_card"],
            highlightthickness=0,
        ).pack(anchor="w", padx=12, pady=4)

        # --- Save button ---
        tk.Button(
            main, text="💾  Save & Restart",
            font=("Segoe UI", 11, "bold"),
            fg=COLORS["text"], bg=COLORS["accent"],
            activebackground=COLORS["accent_light"],
            activeforeground=COLORS["text"],
            bd=0, padx=20, pady=10, cursor="hand2",
            command=self._save,
        ).pack(pady=(16, 0))

    def _section(self, parent, tk, text: str):
        """Render a section header label."""
        tk.Label(
            parent, text=text,
            font=("Segoe UI", 11, "bold"),
            fg=COLORS["text_dim"], bg=COLORS["bg_dark"],
        ).pack(anchor="w", pady=(8, 4))

    def _save(self):
        """Gather values from the UI, save config, and notify callback."""
        lang_code = None
        for name, code in LANGUAGES:
            if name == self.lang_var.get():
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
