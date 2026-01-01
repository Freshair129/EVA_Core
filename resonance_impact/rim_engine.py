from dataclasses import dataclass, asdict
from typing import Dict, List, Any
import math
import yaml
import os

@dataclass
class RIMResult:
    rim_value: float
    confidence: float
    components: Dict[str, float]
    impact_level: str
    impact_trend: str
    affected_domains: List[str]

class RIMEngine:
    """
    Resonance Intelligence Matrix (RIM) v8.0
    Evaluates the experiential impact of interaction on EVA's biological and psychic substrate.
    """

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "configs", "rim_config.yaml")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            self.baseline = config["baseline"]
            self.decay_halflife = config["decay_halflife_sec"]
            self.weights = config["weights"]
            
        self._last_rim_value = self.baseline

    def _mean_abs(self, d: Dict[str, float]) -> float:
        if not d: return 0.0
        return sum(abs(v) for v in d.values()) / len(d)

    def evaluate(self, 
                 qualia_delta: Dict[str, float], 
                 reflex_delta: Dict[str, float], 
                 ri_delta: float, 
                 time_delta_sec: float) -> Dict[str, Any]:
        
        # 1. Magnitudes
        q_mag = self._mean_abs(qualia_delta)
        r_mag = self._mean_abs(reflex_delta)
        rel_mag = abs(ri_delta)

        # 2. Temporal Decay (exp(-t/tau))
        tau = self.decay_halflife / 0.693
        time_factor = math.exp(-time_delta_sec / tau)
        time_factor = max(0.2, min(1.0, time_factor))

        # 3. Weighted Impact
        rim_raw = (
            q_mag * self.weights["qualia"] +
            r_mag * self.weights["reflex"] +
            rel_mag * self.weights["relational"]
        ) * time_factor
        
        rim_value = max(0.0, min(1.0, rim_raw))

        # 4. Confidence
        # Higher activity in qualia/reflex increases confidence of the impact estimate
        confidence = max(0.0, min(1.0, 0.4 + (q_mag * 0.6) + (r_mag * 0.4)))

        # 5. Semantic Mapping
        level = "low"
        if rim_value > 0.60: level = "high"
        elif rim_value > 0.25: level = "medium"

        dv = rim_value - self._last_rim_value
        trend = "stable"
        if dv > 0.05: trend = "rising"
        elif dv < -0.05: trend = "fading"

        domains = []
        if q_mag > 0.25: domains.append("emotional")
        if r_mag > 0.25: domains.append("identity")
        if rel_mag > 0.20: domains.append("relational")
        if not domains: domains.append("ambient")

        self._last_rim_value = rim_value

        result = RIMResult(
            rim_value=float(rim_value),
            confidence=float(confidence),
            components={
                "qualia": float(q_mag),
                "reflex": float(r_mag),
                "relational": float(rel_mag),
                "temporal": float(time_factor)
            },
            impact_level=level,
            impact_trend=trend,
            affected_domains=domains
        )
        
        return asdict(result)

    def get_full_state(self):
        return {"last_rim_value": self._last_rim_value}

    def load_state(self, state_dict):
        self._last_rim_value = state_dict.get("last_rim_value", self.baseline)
