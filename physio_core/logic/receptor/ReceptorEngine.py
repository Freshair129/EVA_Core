"""
ReceptorEngine
Ligand–Receptor Signal Transduction Layer (Full Implementation)
"""

from typing import Dict, Any
from .receptor_unit import ReceptorUnit


class ReceptorEngine:
    def __init__(self, full_config: Dict[str, Any]):
        self.receptors: Dict[str, Dict[str, ReceptorUnit]] = {}
        self._build_engine(full_config)

    def _build_engine(self, config):
        mapping = config.get('receptor_mapping', {})
        for h_id, systems in mapping.items():
            self.receptors[h_id] = {}
            for s_id, spec in systems.items():
                self.receptors[h_id][s_id] = ReceptorUnit(h_id, s_id, spec)

    def step(self, blood_concentrations: Dict[str, float], dt: float = 1.0, nerve_surges: Dict[str, float] = None):
        if nerve_surges is None:
            nerve_surges = {}

        results = {
            "signals": {},
            "sensitization": {},
            "occupation": {}
        }

        for h_id, systems in self.receptors.items():
            conc = blood_concentrations.get(h_id, 0.0)
            surge = nerve_surges.get(h_id, 0.0)

            for s_id, unit in systems.items():
                isr = unit.calculate_signal(conc, dt)
                total = isr + surge

                results.setdefault("signals", {}).setdefault(s_id, {})[h_id] = total
                results["sensitization"][f"{s_id}_{h_id}"] = unit.sensitization
                results["occupation"][f"{s_id}_{h_id}"] = unit.occupation_rate

        return results
