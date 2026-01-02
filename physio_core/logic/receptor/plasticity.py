"""
ReceptorPlasticity
Bmax adaptation layer
"""

class ReceptorPlasticity:
    def __init__(self, base_configs):
        self.base_configs = base_configs
        self.states = {k: 1.0 for k in base_configs}

    def update(self, occupancy, dt):
        for k, occ in occupancy.items():
            mod = self.states.get(k, 1.0)
            if occ > 0.7:
                target = max(0.2, 1.0 - (occ - 0.7) * 2.0)
                rate = 0.05
            elif occ < 0.1:
                target = min(1.5, 1.0 + (0.1 - occ) * 2.0)
                rate = 0.02
            else:
                target = 1.0
                rate = 0.01

            self.states[k] = mod + (target - mod) * rate * dt

    def get_modifier(self, receptor_id):
        return self.states.get(receptor_id, 1.0)
