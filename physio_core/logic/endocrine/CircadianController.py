"""
CircadianController
Version: v9.0

Role:
- Circadian modulation of endocrine stimuli
- Light / activity driven
- Phase-based (24h)
- Output stimulus modifiers only

NO:
- hormone production
- blood / plasma mutation
"""

import math
from datetime import datetime
from typing import Dict


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


class CircadianController:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.circ = cfg["circadian"]

    # --------------------------------------------------
    # Main step
    # --------------------------------------------------

    def step(
        self,
        zeitgeber_inputs: Dict[str, float],
        now: datetime
    ) -> Dict[str, float]:
        """
        Returns:
          { hormone_id: stimulus_modifier }
        """

        hour = now.hour + now.minute / 60.0
        outputs: Dict[str, float] = {}

        # -------------------------------
        # Zeitgeber aggregation
        # -------------------------------
        z_drive = 0.0

        for group, signals in self.circ["zeitgebers"].items():
            for k, w in signals.items():
                gain = w.get("gain", 1.0) if isinstance(w, dict) else w
                z_drive += zeitgeber_inputs.get(k, 0.0) * gain

        # -------------------------------
        # Hormone modulation
        # -------------------------------
        for h_id, mod_cfg in self.circ["hormone_modulation"].items():
            value = 0.0

            # night / morning windows
            for window_name, win in mod_cfg.items():
                if not isinstance(win, dict):
                    continue

                if self._in_window(hour, win["start_hour"], win["end_hour"]):
                    value += win["amplitude"]

            value += z_drive
            value = clamp(
                value,
                self.circ["output"]["clamp"][0],
                self.circ["output"]["clamp"][1]
            )

            outputs[h_id] = value

        return outputs

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _in_window(self, hour, start, end):
        if start <= end:
            return start <= hour < end
        else:
            # wrap around midnight
            return hour >= start or hour < end
