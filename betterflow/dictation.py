"""
Dictation engine — orchestrates recording, transcription, and typing.
"""

import re
import time
import threading
from typing import Optional, Callable

import numpy as np

from betterflow.audio import AudioRecorder, beep
from betterflow.typer import Typer
from betterflow.whisper_engine import get_whisper_model
from betterflow.logger import log
from betterflow.stats import record_dictation
from betterflow.dashboard import print_dictation_result


# Phrases that trigger voice-activated stop
STOP_PHRASES = [
    "stop listening", "stop recording", "stop dictation",
    "stop listenings", "stop listen",
]


class DictationEngine:
    """
    Manages the full dictation lifecycle:
    1. Start recording (via hotkey or click)
    2. Listen for voice stop command in background
    3. Stop recording
    4. Transcribe with Whisper
    5. Type result into focused app
    """

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.recorder = AudioRecorder(sample_rate=cfg["sample_rate"])
        self.typer = Typer(delay=cfg.get("type_speed_delay", 0.0))
        self.is_recording = False
        self._lock = threading.Lock()
        self._stop_via_voice_command = False
        self.on_state_change: Optional[Callable[[str], None]] = None

    def _set_state(self, state: str):
        """Notify listeners of state change. States: idle, listening, transcribing"""
        if self.on_state_change:
            self.on_state_change(state)

    def toggle(self):
        """Toggle between recording and idle."""
        with self._lock:
            if self.is_recording:
                threading.Thread(target=self._stop_and_transcribe, daemon=True).start()
            else:
                threading.Thread(target=self._start, daemon=True).start()


    def _start(self):
        """Begin recording from the microphone."""
        try:
            # Check if model is still downloading
            from betterflow.whisper_engine import is_loading
            if is_loading():
                log.info("Model still downloading, please wait...")
                self._set_state("transcribing")  # show spinning animation
                # Wait for model to finish loading
                while is_loading():
                    time.sleep(0.5)
                self._set_state("idle")
                log.info("Model ready! Press hotkey again to start dictating.")
                return
            if self.cfg.get("play_sounds", True):
                beep(880, 0.1, 0.2)
            self.recorder.start()
            self.is_recording = True
            self._set_state("listening")
            log.info("Recording started")
            # Background thread watches for "stop listening" voice command
            threading.Thread(target=self._watch_voice_command, daemon=True).start()
        except Exception as e:
            log.error(f"Failed to start: {e}")
            self._set_state("idle")

    def _watch_voice_command(self):
        """
        Periodically transcribe the last ~2.5s of audio to detect
        a voice stop command like 'stop listening'.
        """
        time.sleep(0.5)
        model = get_whisper_model(self.cfg)
        while self.is_recording:
            time.sleep(0.5)
            if not self.is_recording:
                return
            # Grab the last ~3 seconds (each frame = 1024 samples @ 16kHz ≈ 64ms)
            with self.recorder._lock:
                if not self.recorder.frames:
                    continue
                recent = self.recorder.frames[-47:]
            if not recent:
                continue
            chunk = np.concatenate(recent, axis=0).flatten()
            # Skip if too quiet
            rms = float(np.sqrt(np.mean(chunk ** 2)))
            if rms < 0.005:
                continue
            try:
                segments, _ = model.transcribe(
                    chunk,
                    language=self.cfg.get("language"),
                    vad_filter=True,
                    without_timestamps=True,
                )
                tail_text = " ".join(seg.text.strip() for seg in segments).strip().lower()
                clean = tail_text.replace(".", "").replace(",", "").replace("!", "").replace("?", "").strip()
                if any(phrase in clean for phrase in STOP_PHRASES):
                    log.info(f"Voice command detected: '{tail_text}'")
                    self._stop_via_voice_command = True
                    # Stop directly instead of going through toggle() to avoid lock/thread issues
                    self._stop_and_transcribe()
                    return
            except Exception:
                pass


    def _stop_and_transcribe(self):
        """Stop recording, transcribe audio, and type the result."""
        try:
            self.is_recording = False
            self._set_state("transcribing")
            audio = self.recorder.stop()
            if self.cfg.get("play_sounds", True):
                beep(440, 0.15, 0.2)
            # Ignore recordings shorter than 0.1 seconds
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
            # Strip the stop command from the end if voice-triggered
            if self._stop_via_voice_command:
                self._stop_via_voice_command = False
                for phrase in STOP_PHRASES[:3]:
                    pattern = re.compile(re.escape(phrase) + r'[.!?,\s]*$', re.IGNORECASE)
                    text = pattern.sub('', text).strip()
            log.info(f"Transcribed in {time.time() - t0:.1f}s: {text[:80]}")
            self._set_state("idle")
            time.sleep(0.1)
            if text:
                record_dictation(text)
                duration = len(audio) / self.cfg["sample_rate"]
                print_dictation_result(text, duration, time.time() - t0)
                self.typer.type(text)
        except Exception as e:
            log.error(f"Transcription failed: {e}")
            self._set_state("idle")
