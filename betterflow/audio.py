"""
Audio recording and sound effects.
"""

import threading
import numpy as np
import sounddevice as sd


class AudioRecorder:
    """Records microphone audio into a numpy array until stop() is called."""

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.frames: list[np.ndarray] = []
        self.stream = None
        self._lock = threading.Lock()

    def start(self):
        """Begin recording from the default microphone."""
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
        """Stop recording and return all captured audio as a flat array."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        with self._lock:
            if not self.frames:
                return np.array([], dtype="float32")
            return np.concatenate(self.frames, axis=0).flatten()

    def get_rms(self) -> float:
        """Return the RMS amplitude of the most recent audio chunk."""
        with self._lock:
            if not self.frames:
                return 0.0
            last = self.frames[-1]
        return float(np.sqrt(np.mean(last ** 2)))


def beep(freq: float = 660, duration: float = 0.15, volume: float = 0.3):
    """Play a short sine-wave beep for audio feedback."""
    try:
        sr = 44100
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        wave = volume * np.sin(2 * np.pi * freq * t).astype(np.float32)
        sd.play(wave, sr)
        sd.wait()
    except Exception:
        pass
