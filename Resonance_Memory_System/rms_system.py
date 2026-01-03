"""
Resonance Memory System (RMS) Engine (v8.1.0-R1)
Memory encoding with State Bus support.
"""

from pathlib import Path
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from resonance_memory_system.rms_v6 import RMSEngineV6


class RMSSystem:
    """
    Memory Encoding Core System.
    Wraps RMSEngineV6 with system-level features:
    - State Bus (MSP) integration (Pull/Push)
    - Persistence to 10_state
    - Context-aware processing for Episodic Memory
    """

    def __init__(self, base_path: Path = None, msp=None):
        self.base_path = base_path or Path(".")
        self.msp = msp
        self.state_file = self.base_path / "consciousness/10_state/rms_state.json"
        
        # Instance of pure logic
        self.engine = RMSEngineV6()
        self.last_encoding: Optional[Dict[str, Any]] = None

        self._load_state()
        print(f"[RMS System] Initialized (Memory Encoding Core)")

    def process_encoding(
        self,
        matrix_state: Dict[str, Any] = None,
        qualia_state: Dict[str, Any] = None,
        reflex_state: Dict[str, float] = None,
        ri_total: float = 0.0
    ) -> Dict[str, Any]:
        """
        Process psychological and phenomenological states into a memory snapshot.

        Args:
            matrix_state: Result from EVA Matrix (axes_9d). Pulls from MSP if None.
            qualia_state: Result from Artifact Qualia. Pulls from MSP if None.
            reflex_state: Snapshot of threat/reflex directives. Pulls from MSP if None.
            ri_total: Resonance Intelligence score (default 0.0).

        Returns:
            Dict representation of the encoding buffer.
        """
        # 1. PULL from State Bus if dependencies not provided
        if self.msp:
            if matrix_state is None:
                matrix_data = self.msp.get_active_state("matrix_state") or {}
                # RMS Engine expects specific keys (stress_load, social_warmth, etc.)
                # Mapping from 9D axes for standard RMS ingestion:
                axes = matrix_data.get("axes_9d", {})
                matrix_state = {
                    "stress_load": axes.get("Stress", 0.3),
                    "social_warmth": axes.get("Warmth", 0.5),
                    "drive_level": axes.get("Drive", 0.4),
                    "cognitive_clarity": axes.get("Clarity", 0.6),
                    "affective_stability": axes.get("Groundedness", 0.5),
                    "joy_level": axes.get("Joy", 0.5),
                    "emotion_label": matrix_data.get("emotion_label", "Neutral")
                }

            if qualia_state is None:
                qualia_state = self.msp.get_active_state("qualia_state") or {"intensity": 0.5}

            if reflex_state is None:
                reflex_state = self.msp.get_active_state("reflex_directives") or {"threat_level": 0.0}

        # 2. Process via Engine
        # RMS v6.2 Engine.process expects (eva_matrix, rim_output, reflex_state, ri_total)
        # We pass qualia_state as rim_output equivalent (containing intensity/impact)
        rim_equivalent = {
            "impact_level": "high" if qualia_state.get("intensity", 0) > 0.8 else ("medium" if qualia_state.get("intensity", 0) > 0.4 else "low"),
            "impact_trend": "stable" # RMS uses trend for mod
        }

        self.last_encoding = self.engine.process(
            eva_matrix=matrix_state,
            rim_output=rim_equivalent,
            reflex_state=reflex_state,
            ri_total=ri_total
        )

        # 3. PUSH to State Bus
        if self.msp:
            self.msp.set_active_state("encoding_buffer", self.last_encoding)
            self.msp.set_active_state("core_color", self.last_encoding.get("memory_color", "#808080"))
            self.msp.set_active_state("resonance_textures", self.last_encoding.get("resonance_texture", {}))

        self._save_state()
        return self.last_encoding

    def get_full_state(self) -> Dict[str, Any]:
        """Return complete system state."""
        return self.engine.get_full_state()

    def _load_state(self):
        """Load internal core state from persistence."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.engine.load_state(data)
                    print(f"[RMS System] Loaded state (Intensity: {data.get('last_intensity', 'N/A')})")
            except Exception as e:
                print(f"[RMS System] Warning: Could not load state: {e}")

    def _save_state(self):
        """Save internal core state to persistence."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.engine.get_full_state(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[RMS System] Warning: Could not save state: {e}")
