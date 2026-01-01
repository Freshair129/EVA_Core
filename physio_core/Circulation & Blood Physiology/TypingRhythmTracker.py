# ============================================================
# TypingRhythmTracker.py
# ============================================================

import time
from collections import deque

def clamp(x, lo, hi):
    return max(lo, min(hi, x))


class TypingRhythmTracker:
    def __init__(self, cfg):
        tr = cfg["typing_rhythm"]
        self.window = tr["sampling_window_sec"]
        self.alpha = tr["ema_alpha"]

        self.fast_iki = tr["thresholds"]["fast_iki_ms"]
        self.slow_iki = tr["thresholds"]["slow_iki_ms"]

        self.timestamps = deque()
        self.speed_ema = 0.0
        self.burst_ema = 0.0
        self.last_key_ts = None

    def on_key(self):
        now = time.time()
        self.timestamps.append(now)

        if self.last_key_ts:
            iki_ms = (now - self.last_key_ts) * 1000
            speed = clamp(
                (self.slow_iki - iki_ms) / (self.slow_iki - self.fast_iki),
                0.0, 1.0
            )
            self.speed_ema = self.alpha * speed + (1 - self.alpha) * self.speed_ema

        self.last_key_ts = now
        self._cleanup()

    def _cleanup(self):
        now = time.time()
        while self.timestamps and now - self.timestamps[0] > self.window:
            self.timestamps.popleft()

        burst = len(self.timestamps) / max(1.0, self.window)
        self.burst_ema = self.alpha * burst + (1 - self.alpha) * self.burst_ema

    def get_focus(self) -> float:
        return clamp(
            0.5 * self.speed_ema + 0.5 * self.burst_ema,
            0.0, 1.0
        )
