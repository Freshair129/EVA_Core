# ============================================================
# BloodEngine.py
# Compatible with:
# Circulation & Blood Physiology Configuration (cleaned v1.2)
# ============================================================

import time
import math
import yaml
from collections import defaultdict
from typing import Any, Dict, List

LN2 = math.log(2)


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


class BloodEngine:
    def __init__(self, config: dict, msp: Any = None):
        self.cfg = config
        self.msp = msp

        # ---------------- Runtime ----------------
        rt = self.cfg["runtime"]
        self.max_dt = rt["max_dt_sec"]
        self.lazy_eval = rt.get("lazy_evaluation", True)

        self.last_update_ts = time.time()

        # ---------------- Blood ------------------
        blood_cfg = self.cfg["blood"]
        self.total_blood_ml = float(blood_cfg["total_volume_ml"])

        # ---------------- Flow -------------------
        flow_cfg = self.cfg["flow"]
        self.base_flow_ml_sec = float(flow_cfg["base_cardiac_output_ml_sec"])
        self.min_flow = flow_cfg["safety"]["min_flow_ml_sec"]
        self.max_flow = flow_cfg["safety"]["max_flow_ml_sec"]

        # ---------------- Hormone Transport ------
        ht = self.cfg["hormone_transport"]
        self.dist_volume_ml = ht["distribution_volume_ml"]
        self.clearance_cfg = ht["clearance"]

        # ---------------- Safety ----------------
        safety = self.cfg["safety"]["concentration"]
        self.conc_min = float(safety["min_floor"])
        self.conc_max = float(safety["max_cap"])

        # ---------------- Plasma State ----------
        self.plasma = defaultdict(float)          # hormone_id -> concentration
        self.last_decay_ts = defaultdict(lambda: time.time())

        # injected externally
        self.hormone_specs = {}

        # Dashboard streaming
        self.CORE_HORMONES = [
            "ESC_H01_ADRENALINE",
            "ESC_H02_CORTISOL",
            "ESC_H05_DOPAMINE",
            "ESC_H06_SEROTONIN",
            "ESC_H09_OXYTOCIN"
        ]

    # ========================================================
    # External Setup
    # ========================================================
    def load_hormone_specs(self, hormone_specs: dict):
        """
        hormone_specs[hormone_id] = {
            "baseline": float,
            "half_life_sec": float
        }
        """
        self.hormone_specs = hormone_specs
        now = time.time()

        for h_id, spec in hormone_specs.items():
            self.plasma[h_id] = float(spec.get("baseline", 0.0))
            self.last_decay_ts[h_id] = now

    # ========================================================
    # Core Update
    # ========================================================
    def step(self, dt: float, flow_factor: float = 1.0):
        """
        dt: time delta in seconds
        flow_factor: external modifier
        """
        now = time.time()
        self.last_update_ts = now

        # ---- clamp flow ----
        eff_flow = clamp(
            self.base_flow_ml_sec * flow_factor,
            self.min_flow,
            self.max_flow
        )

        # ---- passive decay ----
        for h_id in list(self.plasma.keys()):
            # Using external dt for more predictable simulation
            self._apply_decay_with_dt(h_id, now, eff_flow, dt)

        # ---- Dashboard Streaming (MSP) ----
        if self.msp:
            for h_id in self.CORE_HORMONES:
                if h_id in self.plasma:
                    self.msp.register_dashboard_metric(
                        metric_id=h_id,
                        value=self.plasma[h_id],
                        category="physiological_stream"
                    )

        return {
            "timestamp": now,
            "effective_flow_ml_sec": eff_flow,
            "plasma": dict(self.plasma)
        }

    def update(self, flow_factor: float = 1.0):
        """Legacy / BG loop update"""
        now = time.time()
        dt = clamp(now - self.last_update_ts, 0.0, self.max_dt)
        return self.step(dt, flow_factor)

    # ========================================================
    # Hormone Influx (from organs)
    # ========================================================
    def apply_hormone_influx(self, hormone_id: str, mass_pg: float):
        """
        Inject hormone mass into blood plasma.
        """
        now = time.time()
        self._apply_decay(hormone_id, now, flow=self.base_flow_ml_sec)

        delta_conc = mass_pg / self.dist_volume_ml
        self.plasma[hormone_id] += delta_conc

        self.plasma[hormone_id] = clamp(
            self.plasma[hormone_id],
            self.conc_min,
            self.conc_max
        )

    # ========================================================
    # Read API
    # ========================================================
    def get_concentrations(self) -> Dict[str, float]:
        """
        Return all hormone concentrations after decay update.
        """
        now = time.time()
        for h_id in list(self.plasma.keys()):
            self._apply_decay(h_id, now, flow=self.base_flow_ml_sec)
        return dict(self.plasma)

    def read_hormone(self, hormone_id: str) -> float:
        now = time.time()
        self._apply_decay(hormone_id, now, flow=self.base_flow_ml_sec)
        return float(self.plasma.get(hormone_id, 0.0))

    # ========================================================
    # Internal: Decay / Clearance
    # ========================================================
    def _apply_decay(self, hormone_id: str, now: float, flow: float):
        last_ts = self.last_decay_ts[hormone_id]
        dt = now - last_ts
        self._apply_decay_with_dt(hormone_id, now, flow, dt)

    def _apply_decay_with_dt(self, hormone_id: str, now: float, flow: float, dt: float):
        spec = self.hormone_specs.get(hormone_id)
        if not spec:
            return
        
        if dt <= 0:
            return

        baseline = float(spec.get("baseline", 0.0))
        half_life = max(1.0, float(spec.get("half_life_sec", 300.0)))

        # ---- clearance rate ----
        k = LN2 / half_life

        # optional: flow-coupled clearance
        if self.clearance_cfg.get("clearance_flow_coupling", False):
            flow_norm = clamp(flow / self.base_flow_ml_sec, 0.5, 2.0)
            k *= flow_norm

        current = self.plasma[hormone_id]

        if current > baseline:
            excess = current - baseline
            current = baseline + excess * math.exp(-k * dt)
        elif current < baseline:
            recovery_k = k * 0.2
            current += (baseline - current) * (1 - math.exp(-recovery_k * dt))

        self.plasma[hormone_id] = clamp(
            current,
            self.conc_min,
            self.conc_max
        )
        self.last_decay_ts[hormone_id] = now
