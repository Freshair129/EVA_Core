# =============================================================================
# RMS ENGINE v6.2 (Merged & Standardized)
# Resonance Memory System (EVA_Matrix–based)
# =============================================================================

import math
from typing import Dict, Any, List

# -----------------------------------------------------------------------------
# Utils
# -----------------------------------------------------------------------------

def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def smooth(prev: float, now: float, alpha: float = 0.7) -> float:
    return (alpha * prev) + ((1.0 - alpha) * now)

# -----------------------------------------------------------------------------
# RMS Engine
# -----------------------------------------------------------------------------

class RMSEngineV6:
    """
    Resonance Memory System v6.2
    - Merged with logicupdate.py
    - Output aligned with Episodic Memory Schema
    """

    def __init__(self):
        # Internal smoothing memory
        self._last_color_axes = {
            "stress": 0.2,
            "warmth": 0.5,
            "clarity": 0.5,
            "drive": 0.3,
            "calm": 0.4,
        }
        self._last_intensity = 0.3

    def process(
        self,
        eva_matrix: Dict[str, Any],
        rim_output: Dict[str, Any],
        reflex_state: Dict[str, float],
        ri_total: float = 0.0
    ) -> Dict[str, Any]:
        """
        Process internal states into a memory-ready snapshot.
        
        Args:
            eva_matrix: Output from lib-eva-matrix (must contain stress_load, etc.)
            rim_output: Output from lib-resonance RIMEngine (contains impact_level, impact_trend)
            reflex_state: Snapshot containing threat_level
            ri_total: Global Resonance Intelligence score
        """
        # 1. Trauma Detection (from v6.0 core)
        threat = reflex_state.get("threat_level", 0.0)
        trauma_flag = threat > 0.85

        # 2. Color Generation (from logicupdate.py mapping)
        raw_color_axes = self._generate_color_axes(eva_matrix)
        
        # 3. Intensity Calculation (from logicupdate.py mapping)
        raw_intensity = self._compute_intensity(eva_matrix, rim_output)

        # 4. Trauma Protection
        if trauma_flag:
            # Dims color by 45% and intensity by 50% as per interface contract
            raw_color_axes = {k: v * 0.55 for k, v in raw_color_axes.items()}
            raw_intensity *= 0.5

        # 5. Smoothing (Temporal Continuity)
        color_axes = {
            k: smooth(self._last_color_axes[k], v, alpha=0.65)
            for k, v in raw_color_axes.items()
        }
        intensity = smooth(self._last_intensity, raw_intensity, alpha=0.7)

        # Update last state
        self._last_color_axes = color_axes
        self._last_intensity = intensity

        # 6. Formatting for Episodic Memory Snapshot
        return self._package_output(eva_matrix, ri_total, intensity, color_axes, threat, trauma_flag)

    # -------------------------------------------------------------------------
    # Internal Logic
    # -------------------------------------------------------------------------

    def _generate_color_axes(self, eva: Dict[str, Any]) -> Dict[str, float]:
        """Mapping 9D Axes -> 5 RMS Color Axes"""
        return {
            "stress": clamp(eva.get("stress_load", 0.0)),
            "warmth": clamp(eva.get("social_warmth", 0.5)),
            "clarity": clamp(eva.get("cognitive_clarity", 0.5)),
            "drive": clamp(eva.get("drive_level", 0.3)),
            "calm": clamp(eva.get("affective_stability", 0.5))
        }

    def _compute_intensity(self, eva: Dict[str, Any], rim: Dict[str, Any]) -> float:
        """Overall affective intensity based on load and resonance impact"""
        base = clamp(eva.get("stress_load", 0.0) + eva.get("drive_level", 0.0))
        
        impact_boost = {"low": 0.0, "medium": 0.1, "high": 0.25}.get(rim.get("impact_level"), 0.1)
        trend_mod = {"rising": 1.1, "stable": 1.0, "fading": 0.85}.get(rim.get("impact_trend"), 1.0)

        return clamp((base + impact_boost) * trend_mod)

    def _package_output(self, 
                       eva: Dict[str, Any], 
                       ri: float, 
                       intensity: float, 
                       color_axes: Dict[str, float], 
                       threat: float,
                       trauma: bool) -> Dict[str, Any]:
        """Aligns output with episodic_memory_spec.yaml state_snapshot structure"""
        
        # Determine memory_encoding_level (L0-L4)
        if trauma:
            level = "L4_trauma"
        elif intensity < 0.2:
            level = "L0_trace"
        elif intensity < 0.4:
            level = "L1_light"
        elif intensity < 0.7:
            level = "L2_standard"
        else:
            level = "L3_deep"

        # 7. Convert 5D Texture axes to Hex Color (The "Passport" Visual)
        r_val = color_axes.get("stress", 0.0) * 255
        g_val = color_axes.get("calm", 0.0) * 200 + color_axes.get("clarity", 0.0) * 55
        b_val = color_axes.get("warmth", 0.0) * 150 + color_axes.get("calm", 0.0) * 100
        r_val += color_axes.get("warmth", 0.0) * 50
        
        multiplier = (intensity * 0.5) + (color_axes.get("clarity", 0.5) * 0.5)
        
        final_r = int(max(0, min(255, r_val * multiplier)))
        final_g = int(max(0, min(255, g_val * multiplier)))
        final_b = int(max(0, min(255, b_val * multiplier)))
        hex_color = f"#{final_r:02x}{final_g:02x}{final_b:02x}"

        return {
            "EVA_matrix": {
                "stress_load": float(eva.get("stress_load", 0.0)),
                "social_warmth": float(eva.get("social_warmth", 0.0)),
                "drive_level": float(eva.get("drive_level", 0.0)),
                "cognitive_clarity": float(eva.get("cognitive_clarity", 0.0)),
                "joy_level": float(eva.get("joy_level", 0.0)),
                "emotion_label": str(eva.get("emotion_label", "Unknown"))
            },
            "Resonance_index": float(ri),
            "memory_encoding_level": level,
            "memory_color": hex_color,
            "resonance_texture": {k: float(v) for k, v in color_axes.items()},
            "qualia": {
                "intensity": float(intensity)
            },
            "reflex": {
                "threat_level": float(threat)
            },
            "trauma_flag": trauma
        }

    def get_full_state(self) -> Dict[str, Any]:
        return {
            "last_color_axes": {k: float(v) for k, v in self._last_color_axes.items()},
            "last_intensity": float(self._last_intensity)
        }

    def load_state(self, state_dict: Dict[str, Any]):
        if "last_color_axes" in state_dict:
            self._last_color_axes.update(state_dict["last_color_axes"])
        self._last_intensity = state_dict.get("last_intensity", 0.3)

# -----------------------------------------------------------------------------
# Example Usage (Mock Only for Standalone Test)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    rms = RMSEngineV6()
    
    # Mock Data
    mock_eva = {
        "stress_load": 0.4,
        "social_warmth": 0.7,
        "drive_level": 0.5,
        "cognitive_clarity": 0.8,
        "affective_stability": 0.6,
        "joy_level": 0.2,
        "emotion_label": "Content"
    }
    mock_rim = {"impact_level": "medium", "impact_trend": "stable"}
    mock_reflex = {"threat_level": 0.15}
    
    import json
    result = rms.process(mock_eva, mock_rim, mock_reflex, ri_total=0.75)
    
    print(json.dumps(result, indent=2))
