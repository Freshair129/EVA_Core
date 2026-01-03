"""
AutonomicResponseEngine (ANS Layer)
Integrates receptor signals (ISR) and reflex surges (IRE)
into autonomic nervous system states.
"""

from typing import Dict
import numpy as np


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


class AutonomicResponseEngine:
    def __init__(self, config: dict):
        self.cfg = config
        self.weights = config.get("weights", {})
        self.state = {
            "sympathetic": 0.0,
            "parasympathetic": 0.0
        }

    def get_state(self) -> Dict[str, float]:
        """Return current autonomic state."""
        return self.state

    def step(
        self,
        receptor_signals: Dict[str, Dict[str, float]],
        reflex_surges: Dict[str, float],
        dt: float
    ) -> Dict[str, float]:
        """
        Args:
            receptor_signals: { system_id: { hormone_id: signal } }
            reflex_surges: { hormone_or_receptor: surge_value }
        Returns:
            Autonomic state vector
        """

        symp = 0.0
        para = 0.0

        # --- Integrate receptor-based signals (slow) ---
        for system, signals in receptor_signals.items():
            for h_id, val in signals.items():
                w = self.weights.get(h_id, {})
                symp += val * w.get("sympathetic", 0.0)
                para += val * w.get("parasympathetic", 0.0)

        # --- Integrate reflex surges (fast) ---
        for h_id, surge in reflex_surges.items():
            w = self.weights.get(h_id, {})
            symp += surge * w.get("sympathetic", 0.0)
            para += surge * w.get("parasympathetic", 0.0)

        # --- Normalize and smooth ---
        symp = clamp(symp, 0.0, 1.0)
        para = clamp(para, 0.0, 1.0)

        alpha = self.cfg.get("smoothing", {}).get("alpha", 0.2)
        self.state["sympathetic"] = (alpha * symp) + ((1 - alpha) * self.state["sympathetic"])
        self.state["parasympathetic"] = (alpha * para) + ((1 - alpha) * self.state["parasympathetic"])

        return dict(self.state)

    def get_state(self):
        return dict(self.state)
