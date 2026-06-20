# ☕ BetterFlow Desktop

**Voice dictation that works everywhere.**

A cozy desktop app with a floating animated icon. Press a hotkey or click the icon, speak, and your words get typed into any app — WhatsApp, Slack, Word, browser, terminal, anywhere.

100% free. 100% offline. 100% unlimited. Your audio never leaves your computer.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

---

## ✨ Features

- **System-wide dictation** — works in any app with a text field
- **Floating animated icon** — always on screen, draggable, shows recording state
- **Cozy settings UI** — change model, language, hotkey, and more from a warm GUI
- **Fully offline** — powered by OpenAI Whisper running locally
- **90+ languages** supported
- **Auto-stop on silence** — no need to press the hotkey again
- **Global hotkey** — `Ctrl+Shift+Space` (customizable)

---

## 🎯 How It Works

1. Click the floating icon or press `Ctrl+Shift+Space`
2. Speak naturally
3. Press the hotkey again (or stop talking for 2 seconds)
4. Your words are typed into the focused app

The floating icon animates to show state:
- ☕ **Idle** — gentle breathing glow
- 🎙️ **Listening** — pulsing red ring
- ⏳ **Transcribing** — spinning yellow dots

---

## 📦 Requirements

- **Python 3.10+** — https://www.python.org/downloads/
- **~200 MB disk** — for the Whisper model (downloads on first run)
- **A microphone**
- **OS**: Windows 10+, macOS 11+, or Linux (Ubuntu 22.04+)

---

## 🚀 Installation

### Windows

1. Install Python 3.10+ (check "Add Python to PATH")
2. Clone this repo or download and unzip
3. Double-click `install.bat`
4. Done!

### macOS / Linux

```bash
git clone https://github.com/yourname/betterflow-desktop.git
cd betterflow-desktop
bash install.sh
```

---

## 🎯 Running

### Windows

Double-click `run.bat` or run from terminal:

```bash
.venv\Scripts\activate
python betterflow_desktop.py
```

### macOS / Linux

```bash
bash run.sh
```

---

## 🖱️ Usage

| Action | What happens |
|--------|-------------|
| **Click** the floating icon | Start/stop dictation |
| **Right-click** the icon | Open menu (Settings, Test, Quit) |
| **Drag** the icon | Move it anywhere on screen |
| **Ctrl+Shift+Space** | Global hotkey (works even when icon isn't focused) |

---

## ⚙️ Settings

Right-click the floating icon → **Settings** to open the GUI, or edit manually:

- **Windows**: `C:\Users\YourName\.betterflow\config.json`
- **macOS / Linux**: `~/.betterflow/config.json`

### Available Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `hotkey` | `ctrl+shift+space` | Global trigger key combo |
| `model_size` | `base` | `tiny`, `base`, `small`, `medium`, `large-v3` |
| `language` | `null` | `null` = auto-detect, or `"en"`, `"hi"`, `"es"`, etc. |
| `device` | `cpu` | `cpu` or `cuda` (NVIDIA GPU) |
| `silence_timeout_sec` | `2.0` | Auto-stop after silence |
| `play_sounds` | `true` | Beep on start/stop |
| `show_overlay` | `true` | Show listening overlay |

### Model Comparison

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| `tiny` | ~75 MB | ⚡⚡⚡⚡⚡ | ★★ |
| `base` | ~150 MB | ⚡⚡⚡⚡ | ★★★ |
| `small` | ~500 MB | ⚡⚡⚡ | ★★★★ |
| `medium` | ~1.5 GB | ⚡⚡ | ★★★★★ |
| `large-v3` | ~3 GB | ⚡ | ★★★★★★ |

---

## 🧯 Troubleshooting

- **Hotkey doesn't work**: Try a different combo in Settings
- **Mic not working**: Check OS microphone permissions
- **Transcription slow**: Use a smaller model (`tiny` or `base`)
- **Transcription inaccurate**: Use a larger model, or set a specific language
- **Icon not visible**: It starts in bottom-right of screen; try dragging it

---

## 🔒 Privacy

- Audio is processed 100% locally with Whisper
- No data ever leaves your machine
- No accounts, API keys, or telemetry

---

## 🛠️ Tech Stack

- **faster-whisper** — Whisper inference via CTranslate2
- **pynput** — Global hotkey capture + text typing
- **sounddevice** — Microphone recording
- **tkinter** — Floating icon + settings UI
- **Pillow** — Icon rendering

---

## 📜 License

MIT — do whatever you want. Free forever.
