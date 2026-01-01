"""
EVA Matrix System Engine
Psyche Core with state ownership and persistence.
"""

from pathlib import Path
import json
from datetime import datetime, timezone
from typing import Dict, Any

# Import stateless calculator from lib
try:
    from eva_matrix import EVAMatrixEngine as MatrixCalculator
except ImportError:
    # Fallback if lib structure is different
    import sys
    lib_path = Path(__file__).parent.parent.parent / "lib" / "lib-eva-matrix"
    sys.path.insert(0, str(lib_path))
    from eva_matrix import EVAMatrixEngine as MatrixCalculator


class EVAMatrixSystem:
    """
    Psyche Core System.
    Owns continuous emotional state (axes_9d) and momentum.
    
    This is a SYSTEM, not a library:
    - Maintains continuous state across turns
    - Persists state to disk
    - Owns the matrix_state slot
    
    Uses lib-eva-matrix as a stateless calculator.
    """
    
    def __init__(self, base_path: Path = None, msp=None):
        self.base_path = base_path or Path(".")
        self.msp = msp
        self.state_file = self.base_path / "Consciousness/10_state/eva_matrix_state.json"
        
        # Stateless calculator (from lib)
        self.calculator = MatrixCalculator()
        
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
        # Use calculator to compute new state
        result = self.calculator.process_signals(signals)
        
        # Update owned state
        self.axes_9d = result.get("axes_9d", {})
        self.emotion_label = result.get("emotion_label", "Neutral")
        
        # Update momentum if calculator provides it
        if hasattr(self.calculator, 'momentum'):
            self.momentum = self.calculator.momentum
        
        self._save_state()
        return result
    
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
