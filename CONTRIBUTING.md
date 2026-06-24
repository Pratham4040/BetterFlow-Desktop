# Contributing to BetterFlow Desktop

Thanks for your interest in contributing! BetterFlow is an open-source voice dictation tool for Windows, and every contribution — whether it's code, bug reports, feature ideas, or just feedback — makes it better for everyone.

---

## 🤝 Ways to Contribute

You don't need to write code to help. Here are all the ways you can contribute:

### 🐛 Report Bugs
Found something broken? Open an issue with the `bug` label.

**Include:**
- What you expected to happen
- What actually happened
- Steps to reproduce
- Your OS version and Python version
- Any error messages from the terminal

### 💡 Request Features
Have an idea? Open an issue with the `feature-request` label.

**Include:**
- What problem it solves
- How you'd like it to work
- Why it matters to you

### 📝 Give Feedback
Just using the app and sharing your experience helps. Open an issue with the `feedback` label:
- Is the setup process smooth?
- Is the UI intuitive?
- How's the transcription accuracy for your language?
- Any confusion or friction points?

### 🔧 Submit Code
Fix a bug, add a feature, improve performance, clean up code — PRs are welcome.

### 📖 Improve Documentation
- Fix typos in README or docs
- Add examples or clarify instructions
- Translate docs to other languages
- Write tutorials or guides

---

## 🏷️ Issue Labels

We use these labels to organize work:

| Label | Description |
|-------|-------------|
| `bug` | Something is broken |
| `feature-request` | A new feature idea |
| `enhancement` | Improvement to an existing feature |
| `good-first-issue` | Great for newcomers |
| `help-wanted` | We'd love community help on this |
| `documentation` | Docs improvements |
| `feedback` | General user feedback |
| `performance` | Speed/memory improvements |
| `ui` | Floating icon or settings UI related |
| `audio` | Microphone/recording related |
| `whisper` | Transcription model related |

---

## 🛠️ Development Setup

### Prerequisites
- Python 3.10 or newer
- Git
- A microphone (for testing)

### Getting Started

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/BetterFlow-Desktop.git
cd BetterFlow-Desktop

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the app
python betterflow_desktop.py
```

---

## 📁 Project Structure

```
betterflow-desktop/
├── betterflow/                 # Main package
│   ├── __init__.py             # App metadata, colors
│   ├── app.py                  # Main controller (mediator)
│   ├── audio.py                # Mic recording + beep sounds
│   ├── config.py               # Config load/save/defaults
│   ├── dictation.py            # Recording → transcription → typing
│   ├── floating_icon.py        # Animated floating widget
│   ├── hotkey.py               # Hotkey parsing
│   ├── logger.py               # Logging setup
│   ├── settings_ui.py          # Settings GUI window
│   ├── typer.py                # Types text into focused app
│   └── whisper_engine.py       # Whisper model loading
├── betterflow_desktop.py       # Entry point
├── requirements.txt
├── config.example.json
├── install.bat / install.sh
├── run.bat / run.sh
└── README.md
```

---

## 📐 Code Style & Conventions

- **Language:** Python 3.10+
- **Formatting:** 4 spaces indentation, no tabs
- **Naming:**
  - Classes: `PascalCase` (e.g., `DictationEngine`)
  - Functions/methods: `snake_case` (e.g., `get_whisper_model`)
  - Private: prefix with `_` (e.g., `_stop_and_transcribe`)
  - Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_CONFIG`)
- **Docstrings:** Required for all public classes and functions
- **Type hints:** Use them for function signatures
- **Imports:** Standard library → third-party → local (separated by blank lines)
- **One module = one responsibility**

---

## 🔀 Pull Request Process

### 1. Create a branch

```bash
git checkout -b feat/your-feature-name
# or
git checkout -b fix/bug-description
```

**Branch naming:**
- `feat/` — new feature
- `fix/` — bug fix
- `docs/` — documentation
- `refactor/` — code restructuring
- `perf/` — performance improvement

### 2. Make your changes

- Keep changes focused — one PR per logical change
- Add docstrings to new functions/classes
- Test your changes manually (run the app, try the feature)
- Make sure the app still starts and records/transcribes correctly

### 3. Commit with a clear message

```
feat: add clipboard mode for dictation
fix: resolve hotkey not working on Windows 11
docs: add macOS setup instructions
refactor: extract voice command detection to separate module
```

### 4. Push and create a PR

```bash
git push -u origin feat/your-feature-name
```

Then open a Pull Request on GitHub with:
- A clear title (under 70 chars)
- Description of what changed and why
- Screenshots if it's a UI change
- Steps to test it

### 5. Review

- A maintainer will review your PR
- Address any feedback
- Once approved, it'll be merged

---

## ✅ PR Checklist

Before submitting, make sure:

- [ ] App starts without errors (`python betterflow_desktop.py`)
- [ ] Your feature/fix works as intended
- [ ] No secrets, API keys, or personal paths in the code
- [ ] New functions have docstrings
- [ ] Commit message follows the format above
- [ ] You've tested on your OS

---

## 🚫 Rules

- **No breaking changes** without discussion first (open an issue)
- **No large refactors** without maintainer approval
- **Never commit** `.env`, `config.json`, `.venv/`, model files, or secrets
- **Keep it offline** — BetterFlow must never require internet after first model download
- **Keep it free** — no paywalls, subscriptions, or telemetry
- **Be respectful** — treat everyone with kindness in issues and PRs

---

## 💬 Communication

- **Issues:** For bugs, features, and feedback
- **Pull Requests:** For code contributions
- **Discussions:** (if enabled) For general questions and ideas

---

## 🎯 Areas Where Help is Needed

Here are things we'd especially love help with:

- **macOS testing** — We develop on Windows, need macOS testers
- **Linux testing** — Different distros have different audio setups
- **Language accuracy** — Test transcription in non-English languages
- **Performance** — Faster transcription, lower CPU during recording
- **Accessibility** — Keyboard navigation, screen reader support
- **Packaging** — PyInstaller builds, system installers
- **UI polish** — Better animations, theming, HiDPI support

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for making BetterFlow better! ☕🎙️
