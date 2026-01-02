"""
PhysioCore: Endocrine Glands
Version: v9.0 (post Blood–Endocrine separation)

Responsibilities:
- Inventory management
- Adaptation / fatigue
- Hormone mass production (pg)
- Nerve surge (acute response)

Explicitly NOT responsible for:
- Blood concentration
- Clearance / decay
- Half-life
- Hemodynamics
"""

import math
from .constants import (
    LOG_2,
    STATE_ACTIVE,
    STATE_FATIGUE,
    STATE_EXHAUSTED,
    ADAPTATION_MIN,
    ADAPTATION_MAX,
    DRIVE_MIN,
    DRIVE_MAX,
    FATIGUE_THRESHOLD_PCT,
    EXHAUSTED_THRESHOLD_PCT,
)

# =========================================================
# Endocrine Gland
# =========================================================

class EndocrineGland:
    def __init__(self, h_id: str, spec: dict):
        self.h_id = h_id
        self.name = spec.get("name", h_id)

        # ---- Static config from spec ----
        inv_cfg = spec.get("inventory", {})
        sec_cfg = spec.get("secretion", {})

        self.inventory_max = float(inv_cfg.get("max_capacity", 1000.0))
        self.refill_rate = float(inv_cfg.get("refill_rate_base", 1.0))

        self.max_rate_sec = float(sec_cfg.get("max_output_dt", 10.0))
        self.latency_tau = max(1.0, float(sec_cfg.get("latency_sec", 10.0)))

        # drive accumulator cap (emotional / stimulus drive)
        self.drive_cap = DRIVE_MAX

    # =====================================================
    # Internal response model
    # =====================================================

    def _hill_response(self, x: float) -> float:
        """
        Hill-Langmuir response:
        maps drive level → secretion intensity (0–1)
        """
        if x <= 0.0:
            return 0.0

        k = 2.5   # midpoint
        n = 3.0   # slope
        return (x ** n) / (k ** n + x ** n)

    # =====================================================
    # State helpers
    # =====================================================

    def create_initial_state(self) -> dict:
        return {
            "inventory": self.inventory_max,
            "adaptation": 1.0,
            "drive": 0.0,
            "last_flux_pg": 0.0,
        }

    # =====================================================
    # Acute response (Nerve Surge)
    # =====================================================

    def trigger_nerve_surge(
        self,
        state: dict,
        stimulus_intensity: float
    ) -> tuple[float, dict]:
        """
        Immediate hormone release for strong stimulus.
        Returns (released_pg, new_state)
        """

        if stimulus_intensity < 0.8:
            return 0.0, state

        new_state = state.copy()

        # release up to 40% of current inventory
        surge_fraction = 0.40 * stimulus_intensity
        potential_pg = new_state["inventory"] * surge_fraction

        released_pg = potential_pg * new_state["adaptation"]
        released_pg = min(released_pg, new_state["inventory"])

        # update state
        new_state["inventory"] -= released_pg
        new_state["drive"] = min(
            self.drive_cap,
            new_state["drive"] + stimulus_intensity * 5.0
        )

        # rapid adaptation drop
        new_state["adaptation"] = max(
            ADAPTATION_MIN,
            new_state["adaptation"] - stimulus_intensity * 0.15
        )

        new_state["last_flux_pg"] = released_pg

        return released_pg, new_state

    # =====================================================
    # Tonic secretion (normal operation)
    # =====================================================

    def process_step(
        self,
        state: dict,
        stimulus: float,
        dt: float
    ) -> tuple[float, dict]:
        """
        Normal secretion over dt.
        Returns (released_pg, new_state)
        """

        new_state = state.copy()

        # ---- Refill inventory ----
        new_state["inventory"] = min(
            self.inventory_max,
            new_state["inventory"] + self.refill_rate * dt
        )

        # ---- Adaptation & drive ----
        if stimulus > 0.05:
            # fatigue / desensitization
            new_state["adaptation"] = max(
                ADAPTATION_MIN,
                new_state["adaptation"] - stimulus * 0.05 * dt
            )

            new_state["drive"] = min(
                self.drive_cap,
                new_state["drive"] + stimulus * dt * 2.0
            )
        else:
            # recovery
            new_state["adaptation"] = min(
                ADAPTATION_MAX,
                new_state["adaptation"] + 0.02 * dt
            )

        # ---- Secretion calculation ----
        intensity = self._hill_response(new_state["drive"])
        potential_pg = self.max_rate_sec * intensity * new_state["adaptation"] * dt

        released_pg = min(potential_pg, new_state["inventory"])
        new_state["inventory"] -= released_pg
        new_state["last_flux_pg"] = released_pg

        # ---- Drive decay (latency) ----
        decay_k = 1.0 / self.latency_tau
        new_state["drive"] *= math.exp(-decay_k * dt)

        if new_state["drive"] < 1e-4:
            new_state["drive"] = 0.0

        return released_pg, new_state

    # =====================================================
    # Readable status (UI / debug)
    # =====================================================

    def get_status(self, state: dict) -> dict:
        inv_pct = state["inventory"] / max(1.0, self.inventory_max)

        if inv_pct <= EXHAUSTED_THRESHOLD_PCT:
            label = STATE_EXHAUSTED
        elif inv_pct <= FATIGUE_THRESHOLD_PCT:
            label = STATE_FATIGUE
        else:
            label = STATE_ACTIVE

        return {
            "hormone": self.h_id,
            "inventory_pct": round(inv_pct * 100.0, 2),
            "adaptation": round(state["adaptation"], 3),
            "drive": round(state["drive"], 3),
            "last_flux_pg": round(state["last_flux_pg"], 4),
            "state": label,
        }
