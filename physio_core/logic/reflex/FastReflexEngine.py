"""
FastReflexEngine (IRE v7.1)
Immediate neural reflex surge engine
"""

import numpy as np
import yaml
import os
from typing import Dict


class FastReflexEngine:
    def __init__(self, config_path: str = None):
        if config_path is None:
            default_path = os.path.join(os.path.dirname(__file__), "reflex_config.yaml")
            if os.path.exists(default_path):
                config_path = default_path

        if config_path and os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {
                "tuning": {
                    "Gain_Factor": 2.5,
                    "Saturation_Cutoff": 1.2,
                    "Reflex_Decay_Rate": 0.9,
                    "Inhibition_Threshold": 0.05
                },
                "pathway_mapping": []
            }

        self.tuning = self.config.get("tuning", {})
        self.pathways = self.config.get("pathway_mapping", [])
        self.current_surges: Dict[str, float] = {}

    def calculate_surges(
        self,
        stimuli: Dict[str, float],
        gland_status: Dict[str, Dict[str, float]],
        dt: float
    ) -> Dict[str, float]:

        new_surges: Dict[str, float] = {}

        for path in self.pathways:
            stim_type = path.get("stimulus_type")
            target_receptor = path.get("target_receptor")
            modifier = path.get("gain_modifier", 1.0)

            intensity = stimuli.get(stim_type, 0.0)
            if intensity <= 0.0:
                continue

            status = gland_status.get(target_receptor, {})
            g_inv = status.get("G_inventory", 0.0)
            g_max = status.get("G_max", 1.0)

            threshold = self.tuning.get("Inhibition_Threshold", 0.05)
            if (g_inv / max(1e-6, g_max)) < threshold:
                surge = 0.0
            else:
                gain = self.tuning.get("Gain_Factor", 2.5) * modifier
                surge = (g_inv / max(1e-6, g_max)) * intensity * gain

            surge = min(surge, self.tuning.get("Saturation_Cutoff", 1.2))
            new_surges[target_receptor] = new_surges.get(target_receptor, 0.0) + surge

        decay = self.tuning.get("Reflex_Decay_Rate", 0.9)
        combined: Dict[str, float] = {}

        for r_id in set(self.current_surges) | set(new_surges):
            prev = self.current_surges.get(r_id, 0.0)
            inc = new_surges.get(r_id, 0.0)
            updated = inc + (prev * (decay ** dt))
            updated = min(updated, self.tuning.get("Saturation_Cutoff", 1.2))
            self.current_surges[r_id] = updated
            combined[r_id] = updated

        return combined

    def get_state(self) -> Dict[str, float]:
        return dict(self.current_surges)

    def load_state(self, state: Dict[str, float]):
        self.current_surges.update(state)
