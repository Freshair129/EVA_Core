import numpy as np
import yaml
import os
from typing import Dict, Any, List

class RIEngine:
    """
    Resonance Intelligence (RI) Engine (v8.0)
    Calculates cognitive resonance across emotional, intentional, 
    semantic, and contextual layers.
    """

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "configs", "ri_config.yaml")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            self.weights = config["weights"]

    def compute_ER(self, user_emotion: Dict[str, float], eva_emotion: Dict[str, float]) -> float:
        """Emotional Resonance: Match between user and EVA's expected emotional state."""
        keys = ["arousal", "valence", "tension"]
        diffs = []
        for k in keys:
            u_val = user_emotion.get(k, 0.0)
            e_val = eva_emotion.get(k, 0.0)
            diffs.append(abs(u_val - e_val))
        
        er = 1.0 - (sum(diffs) / len(diffs)) if diffs else 1.0
        return float(np.clip(er, 0.0, 1.0))

    def compute_IF(self, intent: str, clarity: float, tension: float) -> float:
        """Intent Fit: How well the dialogue intent aligns with cognitive state."""
        if intent in ["DEFINE", "EXPLAIN", "ANALYZE"]:
            return float(clarity)
        elif intent in ["REASSURE", "SAFETY"]:
            return float(1.0 - tension)
        return float((clarity + (1.0 - tension)) / 2.0)

    def compute_SR(self, summary_vec: List[float], episodic_vec: List[float]) -> float:
        """Semantic Resonance: Cosine similarity between LLM summary and episodic memory."""
        a = np.array(summary_vec)
        b = np.array(episodic_vec)
        
        if a.size == 0 or b.size == 0 or a.shape != b.shape:
            return 0.0
            
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        denom = norm_a * norm_b
        
        if denom < 1e-8:
            return 0.0
            
        sr = float(np.dot(a, b) / denom)
        return float(np.clip(sr, 0.0, 1.0))

    def compute_CR(self, flow_score: float, personalization_score: float) -> float:
        """Contextual Resonance: Social and conversational flow."""
        cr = (flow_score * 0.6) + (personalization_score * 0.4)
        return float(np.clip(cr, 0.0, 1.0))

    def compute_RI(self, inputs: Dict[str, Any]) -> Dict[str, float]:
        """
        Main interface to compute total Cognitive Resonance.
        """
        er = self.compute_ER(inputs.get("user_emotion", {}), inputs.get("llm_emotion_estimate", {}))
        if_val = self.compute_IF(inputs.get("intent", ""), inputs.get("clarity", 0.5), inputs.get("tension", 0.5))
        sr = self.compute_SR(inputs.get("llm_summary_vector", []), inputs.get("episodic_context_vector", []))
        cr = self.compute_CR(inputs.get("flow_score", 0.5), inputs.get("personalization_score", 0.5))

        total_ri = (
            er * self.weights["ER"] +
            if_val * self.weights["IF"] +
            sr * self.weights["SR"] +
            cr * self.weights["CR"]
        )

        return {
            "ER": er,
            "IF": if_val,
            "SR": sr,
            "CR": cr,
            "RI_total": float(np.clip(total_ri, 0.0, 1.0))
        }
