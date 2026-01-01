"""
HPARegulator
Version: v9.0

Role:
- Model HPA axis (Stress → CRH → ACTH → Cortisol)
- Produce stimulus modifier for Cortisol gland ONLY
- Read-only access to plasma snapshot (optional)

NO:
- hormone production
- gland state mutation
- blood interaction
"""

import math
from typing import Dict


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


class HPARegulator:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.hpa = cfg["HPA_axis"]

        self.alpha = cfg["global"]["smoothing"]["alpha"]

        # internal virtual hormone states
        self._crh = 0.0
        self._acth = 0.0

    # --------------------------------------------------
    # Main step
    # --------------------------------------------------

    def step(
        self,
        stress_inputs: Dict[str, float],
        plasma_snapshot: Dict[str, float] | None,
        dt: float
    ) -> Dict[str, float]:
        """
        Returns:
          { "COR": stimulus_modifier }
        """

        # -------------------------------
        # 1) Hypothalamus (Stress → CRH)
        # -------------------------------
        hypo_cfg = self.hpa["dynamics"]["hypothalamus"]

        drive = 0.0
        for k, w in hypo_cfg["input"].items():
            drive += stress_inputs.get(k, 0.0) * w

        target_crh = hypo_cfg["baseline"] + hypo_cfg["gain"] * drive
        self._crh = self._ema(self._crh, target_crh)

        # -------------------------------
        # 2) Pituitary (CRH → ACTH)
        # -------------------------------
        pit_cfg = self.hpa["dynamics"]["pituitary"]
        target_acth = self._crh * pit_cfg["gain"]
        self._acth = self._ema(self._acth, target_acth)

        # -------------------------------
        # 3) Adrenal drive (ACTH → COR)
        # -------------------------------
        adrenal_cfg = self.hpa["dynamics"]["adrenal"]
        cortisol_drive = self._acth * adrenal_cfg["gain"]

        # -------------------------------
        # 4) Negative feedback (COR ⟂ HPA)
        # -------------------------------
        if plasma_snapshot:
            fb_cfg = self.hpa["negative_feedback"]["cortisol_inhibition"]
            cor_level = plasma_snapshot.get("COR", 0.0)

            threshold = fb_cfg["threshold"]
            strength = fb_cfg["strength"]

            inhibition = sigmoid((cor_level - threshold) * 5.0)
            cortisol_drive *= (1.0 - strength * inhibition)

        cortisol_drive = clamp(
            cortisol_drive,
            self.cfg["global"]["clamp"]["stimulus_min"],
            self.cfg["global"]["clamp"]["stimulus_max"],
        )

        return {"COR": cortisol_drive}

    # --------------------------------------------------
    # Internal
    # --------------------------------------------------

    def _ema(self, prev, target):
        return (self.alpha * target) + ((1 - self.alpha) * prev)
