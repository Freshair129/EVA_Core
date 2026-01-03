"""
EVA Matrix System Engine
Psyche Core with state ownership and persistence.
"""

from pathlib import Path
import json
from datetime import datetime, timezone
from typing import Dict, Any


class EVAMatrixSystem:
    """
    Psyche Core System.
    Owns continuous emotional state (axes_9d) and momentum.

    This is a SYSTEM with internal state management:
    - Maintains continuous state across turns
    - Persists state to disk
    - Owns the matrix_state slot
    - Uses internal calculation logic
    """

    def __init__(self, base_path: Path = None, msp=None):
        self.base_path = base_path or Path(".")
        self.msp = msp
        self.state_file = self.base_path / "consciousness/10_state/eva_matrix_state.json"

        # Owned state (system authority)
        self.axes_9d = {}
        self.momentum = {}
        self.emotion_label = "Neutral"

        self._load_state()
        print(f"[EVA Matrix System] Initialized (Psyche Core)")
    
    def process_signals(self, signals: Dict[str, float]) -> Dict[str, Any]:
        """
        Process neural signals and update psyche state.

        Args:
            signals: Neural signals from receptor layer

        Returns:
            Dict containing axes_9d, emotion_label, etc.
        """
        # Use internal calculation method
        result = self._calculate_state_transition(signals)

        # Update owned state
        self.axes_9d = result.get("axes_9d", {})
        self.emotion_label = result.get("emotion_label", "Neutral")
        self.momentum = result.get("momentum", {})

        self._save_state()
        return result

    def _calculate_state_transition(self, signals: Dict[str, float]) -> Dict[str, Any]:
        """
        Internal state transition calculation.
        Uses simplified logic without external library dependency.

        Args:
            signals: Neural signals from receptor layer

        Returns:
            Dict containing updated axes_9d, emotion_label, momentum
        """
        # Simplified state calculation
        # For now, maintain current state with minor updates
        # TODO: Implement full 9D matrix transformation logic when needed

        # Update axes_9d based on signals (simplified)
        updated_axes = self.axes_9d.copy()

        # Basic emotion classification based on signals
        emotion = "Neutral"
        if signals:
            # Simple heuristic: classify based on dominant signal
            max_signal = max(signals.items(), key=lambda x: abs(x[1]), default=("neutral", 0))
            if max_signal[1] > 0.7:
                emotion = max_signal[0].title()

        return {
            "axes_9d": updated_axes,
            "emotion_label": emotion,
            "momentum": self.momentum
        }
    
    def get_full_state(self) -> Dict[str, Any]:
        """Return complete psyche state."""
        return {
            "axes_9d": self.axes_9d,
            "momentum": self.momentum,
            "emotion_label": self.emotion_label
        }
    
    def load_state(self, state_data: Dict[str, Any]):
        """
        Load state from external source (e.g., MSP).
        
        Args:
            state_data: Dict containing axes_9d, momentum, emotion_label
        """
        if state_data:
            self.axes_9d = state_data.get("axes_9d", {})
            self.momentum = state_data.get("momentum", {})
            self.emotion_label = state_data.get("emotion_label", "Neutral")
            print(f"[EVA Matrix] Loaded external state: {self.emotion_label}")
    
    def set_state(self, state_data: Dict[str, Any]):
        """Alias for load_state (for backward compatibility)."""
        self.load_state(state_data)
    
    def _load_state(self):
        """Load state from persistence."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.axes_9d = data.get("axes_9d", {})
                    self.momentum = data.get("momentum", {})
                    self.emotion_label = data.get("emotion_label", "Neutral")
                    print(f"[EVA Matrix] Loaded state: {self.emotion_label}")
            except Exception as e:
                print(f"[EVA Matrix] Warning: Could not load state: {e}")
    
    def _save_state(self):
        """Save state to persistence."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "axes_9d": self.axes_9d,
                    "momentum": self.momentum,
                    "emotion_label": self.emotion_label,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[EVA Matrix] Warning: Could not save state: {e}")
