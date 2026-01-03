"""
Artifact Qualia System Engine (v8.1.0-R1)
Phenomenological Experience Integrator with State Bus support.
"""

from pathlib import Path
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from artifact_qualia.Artifact_Qualia import ArtifactQualiaCore, RIMSemantic, QualiaSnapshot


class ArtifactQualiaSystem:
    """
    Phenomenology Core System.
    Wraps ArtifactQualiaCore with system-level features:
    - State Bus (MSP) integration (Pull/Push)
    - Persistence to 10_state
    - Context-aware integration
    """

    def __init__(self, base_path: Path = None, msp=None):
        self.base_path = base_path or Path(".")
        self.msp = msp
        self.state_file = self.base_path / "consciousness/10_state/artifact_qualia_state.json"
        
        # Instance of pure logic
        self.core = ArtifactQualiaCore()
        self.last_qualia: Optional[QualiaSnapshot] = None

        self._load_state()
        print(f"[Artifact Qualia System] Initialized (Phenomenology Core)")

    def process_experience(
        self, 
        eva_state: Dict[str, float] = None, 
        rim_semantic: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Integrate psyche state and semantic impact to produce qualia.

        Args:
            eva_state: Optional override for psychological state (axes_9d). If None, pulled from MSP.
            rim_semantic: Optional override for RIM semantic impact.

        Returns:
            Dict representation of QualiaSnapshot.
        """
        # 1. PULL from State Bus if eva_state not provided
        if eva_state is None and self.msp:
            matrix_data = self.msp.get_active_state("matrix_state") or {}
            # Map axes_9d to expected flat dict for ArtifactQualiaCore
            axes = matrix_data.get("axes_9d", {})
            # ArtifactQualiaCore expects specific keys, let's provide mapping or defaults
            eva_state = {
                "baseline_arousal": axes.get("Alertness", 0.5),
                "emotional_tension": axes.get("Stress", 0.3),
                "coherence": axes.get("Groundedness", 0.6),
                "momentum": matrix_data.get("momentum", {}).get("total", 0.5),
                "calm_depth": axes.get("Openness", 0.4)
            }

        # 2. Default RIM Semantic if not provided
        if rim_semantic is None:
            # Placeholder/Simple heuristic for now
            rim_semantic = RIMSemantic(
                impact_level="low",
                impact_trend="stable",
                affected_domains=["ambient"]
            )
        else:
            # Convert dict to RIMSemantic object
            rim_semantic = RIMSemantic(
                impact_level=rim_semantic.get("impact_level", "low"),
                impact_trend=rim_semantic.get("impact_trend", "stable"),
                affected_domains=rim_semantic.get("affected_domains", ["ambient"])
            )

        # 3. Process via Core
        self.last_qualia = self.core.integrate(eva_state, rim_semantic)

        # 4. PUSH to State Bus
        result_dict = {
            "intensity": float(self.last_qualia.intensity),
            "tone": str(self.last_qualia.tone),
            "coherence": float(self.last_qualia.coherence),
            "depth": float(self.last_qualia.depth),
            "texture": {k: float(v) for k, v in self.last_qualia.texture.items()},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        if self.msp:
            self.msp.set_active_state("qualia_state", result_dict)

        self._save_state()
        return result_dict

    def get_full_state(self) -> Dict[str, Any]:
        """Return complete system state."""
        state = self.core.get_full_state()
        if self.last_qualia:
            state["last_snapshot"] = {
                "intensity": self.last_qualia.intensity,
                "tone": self.last_qualia.tone,
                "coherence": self.last_qualia.coherence,
                "depth": self.last_qualia.depth,
                "texture": self.last_qualia.texture
            }
        return state

    def _load_state(self):
        """Load internal core state from persistence."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.core.load_state(data)
                    print(f"[Artifact Qualia] Loaded state (Intensity: {data.get('last_intensity', 'N/A')})")
            except Exception as e:
                print(f"[Artifact Qualia] Warning: Could not load state: {e}")

    def _save_state(self):
        """Save internal core state to persistence."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.core.get_full_state(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Artifact Qualia] Warning: Could not save state: {e}")
