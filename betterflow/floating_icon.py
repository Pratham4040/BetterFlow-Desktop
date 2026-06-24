"""
Floating animated icon — always-on-screen draggable orb.

States:
  - idle: gentle breathing glow with coffee cup
  - listening: pulsing red ring with mic icon
  - transcribing: spinning yellow dots
"""

import math
from typing import Optional, Callable

from betterflow import COLORS


class FloatingIcon:
    """A small draggable always-on-top animated circle widget using tkinter."""

    SIZE = 80       # Total widget size (px) — gives room for animations
    ICON_SIZE = 48  # Inner circle diameter

    def __init__(self, on_click: Optional[Callable] = None,
                 on_right_click: Optional[Callable] = None):
        import tkinter as tk
        self.tk = tk
        self.on_click = on_click
        self.on_right_click = on_right_click
        self.state = "idle"
        self._animation_frame = 0
        self._drag_data = {"x": 0, "y": 0}

        # Hidden root window (tkinter requires one)
        self.root = tk.Tk()
        self.root.withdraw()

        # Floating window — borderless, always on top
        self.win = tk.Toplevel(self.root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.92)
        try:
            self.win.attributes("-transparentcolor", "#010101")
        except Exception:
            pass

        # Position: bottom-right corner
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        x = sw - self.SIZE - 80
        y = sh - self.SIZE - 120
        self.win.geometry(f"{self.SIZE}x{self.SIZE}+{x}+{y}")


        # Canvas for drawing
        self.canvas = tk.Canvas(
            self.win, width=self.SIZE, height=self.SIZE,
            bg="#010101", highlightthickness=0, bd=0,
        )
        self.canvas.pack(fill="both", expand=True)

        # Bind mouse events
        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Button-3>", self._on_right_click_event)

        self._draw_frame()
        self._animate()

    # ---- Mouse interaction ----

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

    def _on_right_click_event(self, event):
        if self.on_right_click:
            self.on_right_click(event)

    # ---- State ----

    def set_state(self, state: str):
        """Update the visual state: 'idle', 'listening', or 'transcribing'."""
        self.state = state


    # ---- Animation ----

    def _draw_frame(self):
        """Render one animation frame based on current state."""
        self.canvas.delete("all")
        cx, cy = self.SIZE // 2, self.SIZE // 2
        r = self.ICON_SIZE // 2
        frame = self._animation_frame

        if self.state == "idle":
            pulse = 0.5 + 0.5 * math.sin(frame * 0.05)
            glow_r = r + 2 + pulse * 3
            self.canvas.create_oval(
                cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r,
                fill="", outline=COLORS["accent"], width=1,
            )
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=COLORS["bg_card"], outline=COLORS["accent"], width=2,
            )
            self._draw_coffee(cx, cy)

        elif self.state == "listening":
            pulse = 0.5 + 0.5 * math.sin(frame * 0.15)
            glow_r = min(r + 4 + pulse * 6, (self.SIZE // 2) - 2)
            self.canvas.create_oval(
                cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r,
                fill="", outline=COLORS["recording"], width=2,
            )
            inner_r = r + 1 + pulse * 2
            self.canvas.create_oval(
                cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r,
                fill="", outline=COLORS["recording"], width=1,
            )
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=COLORS["bg_card"], outline=COLORS["recording"], width=3,
            )
            self._draw_mic(cx, cy)

        elif self.state == "transcribing":
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=COLORS["bg_card"], outline=COLORS["transcribing"], width=2,
            )
            orbit_r = r - 10
            for i in range(3):
                angle = (frame * 0.1) + (i * 2.094)
                dx = math.cos(angle) * orbit_r
                dy = math.sin(angle) * orbit_r
                dot_r = 4
                self.canvas.create_oval(
                    cx + dx - dot_r, cy + dy - dot_r,
                    cx + dx + dot_r, cy + dy + dot_r,
                    fill=COLORS["transcribing"], outline="",
                )


    def _draw_coffee(self, cx, cy):
        """Draw a coffee cup icon inside the circle."""
        self.canvas.create_rectangle(
            cx - 7, cy - 4, cx + 5, cy + 8,
            fill=COLORS["accent"], outline=COLORS["accent_light"], width=1,
        )
        self.canvas.create_arc(
            cx + 4, cy - 1, cx + 11, cy + 6,
            start=270, extent=180,
            outline=COLORS["accent_light"], width=1, style="arc",
        )
        # Animated steam
        for i, sx in enumerate([cx - 4, cx - 1, cx + 2]):
            offset = math.sin(self._animation_frame * 0.08 + i) * 1.5
            self.canvas.create_line(
                sx, cy - 5, sx + offset, cy - 10,
                fill=COLORS["text_dim"], width=1,
            )

    def _draw_mic(self, cx, cy):
        """Draw a microphone icon inside the circle."""
        self.canvas.create_oval(
            cx - 5, cy - 10, cx + 5, cy + 2,
            fill=COLORS["recording"], outline="",
        )
        self.canvas.create_line(cx, cy + 2, cx, cy + 8, fill=COLORS["recording"], width=2)
        self.canvas.create_line(cx - 5, cy + 8, cx + 5, cy + 8, fill=COLORS["recording"], width=2)

    def _animate(self):
        """Advance to the next animation frame."""
        self._animation_frame += 1
        self._draw_frame()
        delay = 50 if self.state != "idle" else 80
        self.root.after(delay, self._animate)

    # ---- Lifecycle ----

    def run(self):
        """Start the tkinter mainloop (blocks)."""
        self.root.mainloop()

    def quit(self):
        """Destroy the widget and exit the mainloop."""
        try:
            self.root.after(0, self.root.destroy)
        except Exception:
            pass
