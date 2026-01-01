# ============================================================
# AdaptiveHzController.py
# Compatible with:
# Circulation & Blood Physiology Configuration (cleaned v1.2)
# ============================================================

def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def ema(prev, value, alpha):
    return (alpha * value) + ((1 - alpha) * prev)


class AdaptiveHzController:
    """
    Scheduler / Control Plane
    - Computes update Hz based on physiology + user context
    - No dependency on BloodEngine internals
    """

    def __init__(self, config: dict):
        """
        config: parsed YAML dict (v1.2)
        """
        sched = config["scheduler"]

        # ---- Hz bounds ----
        self.base_hz = float(sched["base_hz"])
        self.min_hz = float(sched["min_hz"])
        self.max_hz = float(sched["max_hz"])

        # ---- Adaptive weights ----
        ahz = sched["adaptive_hz"]
        self.w_stress = float(ahz["physiology_weights"]["stress"])
        self.w_flow = float(ahz["physiology_weights"]["flow"])

        # ---- User activity multipliers ----
        ua = ahz["user_activity"]
        self.activity_mult = {
            "active": float(ua["active"]),
            "idle": float(ua["idle"]),
            "inactive": float(ua["inactive"]),
        }

        # ---- Focus ----
        self.focus_weight = float(ahz.get("focus_weight", 0.0))

        # ---- Smoothing ----
        smooth = ahz["smoothing"]
        self.alpha = float(smooth.get("alpha", 0.2))

        # ---- Internal state ----
        self.current_hz = self.base_hz

    # --------------------------------------------------------
    # Main API
    # --------------------------------------------------------
    def compute_hz(
        self,
        *,
        stress: float,
        flow_factor: float,
        user_state: str = "idle",
        focus: float = 0.0
    ) -> float:
        """
        stress      : 0.0 – 1.0
        flow_factor : ~0.5 – 2.0
        user_state  : active | idle | inactive
        focus       : 0.0 – 1.0
        """

        # ---- clamp inputs ----
        stress = clamp(stress, 0.0, 1.0)
        focus = clamp(focus, 0.0, 1.0)
        flow_factor = clamp(flow_factor, 0.5, 2.0)

        # ----------------------------------------------------
        # 1) Physiology-driven Hz
        # ----------------------------------------------------
        phys_drive = (
            self.w_stress * stress +
            self.w_flow * (flow_factor - 1.0)
        )
        phys_drive = clamp(phys_drive, 0.0, 1.0)

        hz_phys = self.base_hz + (self.max_hz - self.base_hz) * phys_drive

        # ----------------------------------------------------
        # 2) User activity modifier
        # ----------------------------------------------------
        activity_multiplier = self.activity_mult.get(user_state, 1.0)

        # ----------------------------------------------------
        # 3) Focus fine-tuning (small influence only)
        # ----------------------------------------------------
        focus_multiplier = 1.0 + (self.focus_weight * focus)

        # ----------------------------------------------------
        # 4) Combine + clamp
        # ----------------------------------------------------
        target_hz = hz_phys * activity_multiplier * focus_multiplier
        target_hz = clamp(target_hz, self.min_hz, self.max_hz)

        # ----------------------------------------------------
        # 5) Smooth (EMA)
        # ----------------------------------------------------
        self.current_hz = ema(self.current_hz, target_hz, self.alpha)

        return self.current_hz
