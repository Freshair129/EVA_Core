"""
PhysioCore: Endocrine Controller
Version: v9.0 (post Blood–Endocrine separation)

Role:
- Orchestrate endocrine glands
- Maintain gland states
- Convert stimuli → hormone mass output (pg)

Explicitly NOT responsible for:
- Blood transport
- Plasma concentration
- Clearance / decay
- Hemodynamics
"""

from typing import Dict, Any
from .glands import EndocrineGland


class EndocrineController:
    """
    Endocrine = production + regulation layer
    """

    def __init__(self, glands: Dict[str, EndocrineGland]):
        """
        glands:
            {
              hormone_id: EndocrineGland(...)
            }
        """
        self.glands: Dict[str, EndocrineGland] = glands

        # Internal gland states (pure endocrine state)
        self.states: Dict[str, dict] = {
            h_id: gland.create_initial_state()
            for h_id, gland in glands.items()
        }

    # =====================================================
    # Core step
    # =====================================================

    def step(
        self,
        stimuli: Dict[str, float],
        dt: float
    ) -> Dict[str, Any]:
        """
        Run one endocrine step.

        Args:
            stimuli:
                { hormone_id: stimulus_intensity (0–1) }
            dt:
                delta time (seconds)

        Returns:
            {
              "released_pg": { hormone_id: mass_pg },
              "gland_state": { hormone_id: state_dict }
            }
        """

        released_pg: Dict[str, float] = {}

        for h_id, gland in self.glands.items():
            stimulus = float(stimuli.get(h_id, 0.0))
            state = self.states[h_id]

            # ---- Acute response (nerve surge) ----
            surge_pg, state = gland.trigger_nerve_surge(
                state=state,
                stimulus_intensity=stimulus
            )

            # ---- Normal tonic secretion ----
            flux_pg, state = gland.process_step(
                state=state,
                stimulus=stimulus,
                dt=dt
            )

            total_pg = surge_pg + flux_pg
            if total_pg > 0.0:
                released_pg[h_id] = total_pg

            # persist updated state
            self.states[h_id] = state

        return {
            "released_pg": released_pg,
            "gland_state": self.states
        }

    # =====================================================
    # State accessors
    # =====================================================

    def get_gland_state(self, hormone_id: str) -> dict:
        return self.states.get(hormone_id, {}).copy()

    def get_all_states(self) -> Dict[str, dict]:
        return {
            h_id: state.copy()
            for h_id, state in self.states.items()
        }

    # =====================================================
    # Persistence helpers (optional)
    # =====================================================

    def load_states(self, state_map: Dict[str, dict]):
        """
        Restore gland states from external storage (JSON, DB, etc.)
        """
        for h_id, state in state_map.items():
            if h_id in self.states:
                self.states[h_id] = state.copy()

    def export_states(self) -> Dict[str, dict]:
        """
        Export gland states for persistence
        """
        return {
            h_id: state.copy()
            for h_id, state in self.states.items()
        }

    # =====================================================
    # Debug / monitoring
    # =====================================================

    def get_status_report(self) -> Dict[str, dict]:
        """
        Human-readable gland status (for UI / logs)
        """
        report = {}
        for h_id, gland in self.glands.items():
            report[h_id] = gland.get_status(self.states[h_id])
        return report
