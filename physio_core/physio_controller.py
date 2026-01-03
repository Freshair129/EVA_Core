"""
PhysioController
Version: v1.0

Role:
- Orchestrate full physiological loop
- Glue layer between:
  Endocrine → Blood → Receptor → Reflex → Autonomic

STRICT RULES:
- No cognition
- No memory
- No persona logic
"""

import yaml
from datetime import datetime
from typing import Dict, Any, List

# --- Endocrine ---
from .logic.endocrine.EndocrineController import EndocrineController
from .logic.endocrine.HPARegulator import HPARegulator
from .logic.endocrine.CircadianController import CircadianController
from .logic.endocrine.glands import EndocrineGland

# --- Blood ---
from .logic.blood.BloodEngine import BloodEngine

# --- Receptor ---
from .logic.receptor.ReceptorEngine import ReceptorEngine

# --- Reflex ---
from .logic.reflex.FastReflexEngine import FastReflexEngine

# --- Autonomic ---
from .logic.autonomic.AutonomicResponseEngine import AutonomicResponseEngine


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


class PhysioController:
    """
    Full physiological pipeline controller
    """

    def __init__(
        self,
        endocrine_cfg_path: str,
        endocrine_reg_cfg_path: str,
        blood_cfg_path: str,
        receptor_cfg_path: str,
        reflex_cfg_path: str,
        autonomic_cfg_path: str,
        msp: Any = None,
    ):
        # --------------------------------------------------
        # Load configs
        # --------------------------------------------------
        self.endo_cfg = yaml.safe_load(open(endocrine_cfg_path))
        self.reg_cfg = yaml.safe_load(open(endocrine_reg_cfg_path))
        self.blood_cfg = yaml.safe_load(open(blood_cfg_path))
        self.receptor_cfg = yaml.safe_load(open(receptor_cfg_path))
        self.reflex_cfg_path = reflex_cfg_path
        self.autonomic_cfg = yaml.safe_load(open(autonomic_cfg_path))
        self.msp = msp

        # Streaming definitions (from contract)
        self.CORE_HORMONES = [
            "ESC_H01_ADRENALINE",
            "ESC_H02_CORTISOL",
            "ESC_N02_DOPAMINE",
            "ESC_N03_SEROTONIN",
            "ESC_H04_OXYTOCIN"
        ]

        # --------------------------------------------------
        # Build Endocrine
        # --------------------------------------------------
        glands = {
            h_id: EndocrineGland(h_id, spec)
            for h_id, spec in self.endo_cfg["glands"].items()
        }
        self.endocrine = EndocrineController(glands)

        self.hpa = HPARegulator(self.reg_cfg)
        self.circadian = CircadianController(self.reg_cfg)

        # --------------------------------------------------
        # Blood
        # --------------------------------------------------
        self.blood = BloodEngine(self.blood_cfg, msp=self.msp)

        # --------------------------------------------------
        # Receptor
        # --------------------------------------------------
        self.receptor = ReceptorEngine(self.receptor_cfg)

        # --------------------------------------------------
        # Reflex
        # --------------------------------------------------
        self.reflex = FastReflexEngine(self.reflex_cfg_path)

        # --------------------------------------------------
        # Autonomic
        # --------------------------------------------------
        self.autonomic = AutonomicResponseEngine(self.autonomic_cfg)

    def get_snapshot(self, **kwargs) -> Dict[str, Any]:
        """
        Return a snapshot of the current physiological state.
        Required by CIN (Context Injection Node).
        """
        return {
            "ans_state": self.autonomic.get_state(),
            "blood_levels": self.blood.get_concentrations(),
        }

    # ======================================================
    # Main tick
    # ======================================================

    def step(
        self,
        eva_stimuli: Dict[str, float],
        zeitgebers: Dict[str, float],
        dt: float,
        now: datetime | None = None,
    ) -> Dict[str, Any]:
        """
        Run one full physiological tick
        """

        if now is None:
            now = datetime.now()

        # --------------------------------------------------
        # 1) Regulation layer (HPA + Circadian)
        # --------------------------------------------------
        plasma_snapshot = self.blood.get_concentrations()

        hpa_mod = self.hpa.step(
            stress_inputs=eva_stimuli,
            plasma_snapshot=plasma_snapshot,
            dt=dt
        )

        circ_mod = self.circadian.step(
            zeitgeber_inputs=zeitgebers,
            now=now
        )

        # merge endocrine stimuli
        endocrine_stimuli = {}
        for k in set(hpa_mod) | set(circ_mod):
            endocrine_stimuli[k] = clamp(
                hpa_mod.get(k, 0.0) + circ_mod.get(k, 0.0),
                -1.0, 1.0
            )

        # --------------------------------------------------
        # 2) Endocrine production
        # --------------------------------------------------
        endo_out = self.endocrine.step(endocrine_stimuli, dt)

        for h_id, mass_pg in endo_out["released_pg"].items():
            self.blood.apply_hormone_influx(h_id, mass_pg)

        # --------------------------------------------------
        # 3) Blood transport / decay
        # --------------------------------------------------
        blood_levels = self.blood.step(dt)

        # --------------------------------------------------
        # 4) Fast reflex (IRE)
        # --------------------------------------------------
        gland_status = self.endocrine.get_status_report()
        reflex_surges = self.reflex.calculate_surges(
            stimuli=eva_stimuli,
            gland_status=gland_status,
            dt=dt
        )

        # --------------------------------------------------
        # 5) Receptor transduction
        # --------------------------------------------------
        receptor_out = self.receptor.step(
            blood_concentrations=blood_levels,
            dt=dt,
            nerve_surges=reflex_surges
        )

        # --------------------------------------------------
        # 6) Autonomic integration
        # --------------------------------------------------
        ans_state = self.autonomic.step(
            receptor_signals=receptor_out["signals"],
            reflex_surges=reflex_surges,
            dt=dt
        )

        # --------------------------------------------------
        # 7) Dashboard Streaming (MSP Integration)
        # --------------------------------------------------
        if self.msp:
            # Stream Hormones
            for h_id in self.CORE_HORMONES:
                val = blood_levels.get(h_id, 0.0)
                self.msp.register_dashboard_metric(
                    metric_id=h_id,
                    value=val,
                    category="physiological_stream"
                )
            
            # Stream Heart Rate (from autonomic state)
            hr = ans_state.get("heart_rate", 60.0)
            self.msp.register_dashboard_metric(
                metric_id="heart_rate",
                value=hr,
                category="physiological_stream"
            )

        # --------------------------------------------------
        # Output snapshot
        # --------------------------------------------------
        return {
            "blood": blood_levels,
            "receptors": receptor_out,
            "reflex": reflex_surges,
            "autonomic": ans_state,
            "endocrine_state": endo_out["gland_state"]
        }
