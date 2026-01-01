"""
ReceptorUnit
Full ligand–receptor interaction with plasticity
"""

import numpy as np
import time


class ReceptorUnit:
    def __init__(self, hormone_id: str, system_id: str, config):
        self.h_id = hormone_id
        self.s_id = system_id

        self.kd = config.get('kd', 50.0)
        self.bmax = config.get('max_density', 100.0)
        self.efficacy = config.get('efficacy', 1.0)
        self.hill_n = config.get('hill_n', 1.0)

        self.sensitization = 1.0
        self.occupation_rate = 0.0
        self.last_ts = time.time()

    def calculate_signal(self, concentration: float, dt: float) -> float:
        effective_conc = concentration * self.sensitization

        if effective_conc <= 0:
            self.occupation_rate = 0.0
            return 0.0

        occ = (effective_conc ** self.hill_n) / (
            self.kd ** self.hill_n + effective_conc ** self.hill_n
        )
        self.occupation_rate = occ

        signal = occ * self.bmax * self.efficacy

        self._update_plasticity(dt)
        return signal

    def _update_plasticity(self, dt):
        tau_down = 3600.0
        tau_up = 7200.0

        if self.occupation_rate > 0.7:
            target = max(0.2, 1.0 - (self.occupation_rate - 0.7))
            rate = 1.0 / tau_down
        else:
            target = 1.0
            rate = 1.0 / tau_up

        self.sensitization += (target - self.sensitization) * rate * dt
        self.sensitization = np.clip(self.sensitization, 0.1, 2.0)
