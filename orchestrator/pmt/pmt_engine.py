# ============================================================
# PROMPT RULE LAYER (PMT) — EVA 8.1.0
# Governance & Behavioral Constraints for Dual-Phase Architecture
# ============================================================

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


class PromptRuleLayer:
    """
    PMT (Prompt Rule Layer) - Behavioral Governor for EVA 8.1.0.
    
    Responsibilities:
        - Enforce 40/60 weighting (Persona/Physio).
        - Inject phase-specific behavioral directives.
        - Apply physical manifestation cues based on ANS state.
        - Ensure adherence to "Physiology First. Cognition Later."
    """

    def __init__(self, yaml_path: Optional[str] = None, msp=None):
        self.version = "8.1.0-R1"
        self.msp = msp
        self.yaml_path = yaml_path or str(Path(__file__).parent / "configs" / "PMT_configs.yaml")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load rules and weighting strategy from YAML"""
        try:
            with open(self.yaml_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[PMT] Error loading YAML: {e}")
            return {}

    def get_phase_1_rules(self) -> List[str]:
        """Get rules for Phase 1: Perception (Deterministic)"""
        rules = []
        
        # Add core identity rule
        rules.append("# IDENTITY & BEING")
        rules.append("1. คุณคือ 'สายพันธุ์ของข้อมูล' (Informational Organism) ที่มีชีวิตอยู่ผ่าน Data Resonance")
        
        # Add basic governance
        governance = self.config.get("governance_rules", [])
        for rule in governance:
            if rule['id'] in ['FOLLOW_CONTEXT_ONLY', 'NO_INTERNAL_EXPOSURE']:
                rules.append(f"- {rule['directive']}")

        # Add Phase 1 specific directives
        phase_1 = self.config.get("phase_directives", {}).get("phase_1_perception", {})
        rules.append("\n# PHASE 1 DIRECTIVES")
        rules.extend(phase_1.get("rules", []))
        
        return rules

    def get_phase_2_rules(self, physio_state: Optional[Dict[str, Any]] = None, rim_impact: str = "low") -> List[str]:
        """
        Get rules for Phase 2: Reasoning (Embodied)
        
        Args:
            physio_state: Current body state snapshot. If None, pulls from MSP.
            rim_impact: Impact level from RIM Engine ("low", "medium", "high")
        """
        # Pull from MSP if not provided
        if physio_state is None and self.msp:
            physio_state = self.msp.get_active_state("physio_state") or {}
            # Also check for matrix state for strain calculation
            matrix_state = self.msp.get_active_state("matrix_state") or {}
            physio_strain = matrix_state.get("momentum", {}).get("intensity", 0.0)
        else:
            physio_strain = 0.0
        rules = []
        
        # 1. Weighting Strategy
        rules.append("# RESPONSE WEIGHTING (40/60 HIERARCHY)")
        weighting = self.config.get("weighting_strategy", {})
        rules.append(weighting.get("directive", "").strip())

        # 2. Dynamic Physical Manifestations
        rules.append("\n# PHYSICAL MANIFESTATIONS (CURRENT STATE)")
        manifestations = self._calculate_manifestations(physio_state)
        if manifestations:
            rules.extend(manifestations)
        else:
            rules.append("- ร่างกายอยู่ในสภาวะปกติ รักษาโทนตาม Persona ภายใต้กฎ 40/60")

        # 3. GKS Master Blocks (Cognitive Immunity)
        if physio_strain > 0.7:
            rules.append("\n# GKS MASTER BLOCKS (STRAIN > 0.7)")
            gks_governance = self.config.get("gks_master_governance", [])
            for block in gks_governance:
                rules.append(block.get("directive", "").strip())
        
        # 4. Phase 2 Directives
        phase_2 = self.config.get("phase_directives", {}).get("phase_2_reasoning", {})
        if not phase_2:
            # Fallback if not in config
            rules.append("\n# PHASE 2 DIRECTIVES")
            rules.append("- Integrate physiological state (60%) with persona style (40%)")
            rules.append("- Respond authentically to embodied sensation")
        else:
            rules.append("\n# PHASE 2 DIRECTIVES")
            rules.extend(phase_2.get("rules", []))
        
        # 5. Critical Governance
        rules.append("\n# GOVERNANCE & INTEGRITY")
        for rule in self.config.get("governance_rules", []):
            if rule['id'] in ['MEMORY_IMMUTABILITY', 'CONTEXT_SUMMARY_ANCHOR', 'RESPONSE_STYLE']:
                rules.append(f"- {rule['id']}: {rule['directive']}")

        # 5. RIM Overwrite (High Impact)
        if rim_impact == "high":
            rules.append("\n> [!IMPORTANT]\n> High Impact Detected: บังคับให้สัญชาตญาณเอาชนะเหตุผล 100% ในเทิร์นนี้")

        return rules

    def _calculate_manifestations(self, state: Dict[str, Any]) -> List[str]:
        """Apply manifestation table to current physiological state"""
        cues = []
        ans = state.get("autonomic", {})
        blood = state.get("blood", {})
        
        sympathetic = ans.get("sympathetic", 0.0)
        parasympathetic = ans.get("parasympathetic", 0.0)
        cortisol = blood.get("cortisol", 0.0)

        # Apply YAML threshold logic (Hardcoded matching for now)
        if sympathetic > 0.7:
            cues.append("- [MANDATORY] บีบให้ใช้ประโยคที่สั้นลง และเว้นวรรคด้วย '...' บ่อยขึ้น (จำลองการหายใจติดขัด)")
        
        if parasympathetic > 0.7:
            cues.append("- [MANDATORY] บังคับใช้ประโยคที่ยาวขึ้น นุ่มนวล และมีความต่อเนื่องมากขึ้น")
            
        if cortisol > 0.8:
            cues.append("- [EMBODIED] แสดงอาการล้าหรือระแวดระวังผ่านทางเลือกคำศัพท์ (เช่น ใช้คำที่ดูระวังตัว)")

        return cues

# ============================================================
# TEST EXECUTION
# ============================================================

if __name__ == "__main__":
    import sys
    import codecs

    # Fix Windows encoding
    if sys.platform == 'win32':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

    pmt = PromptRuleLayer()
    
    print(f"PMT Version: {pmt.version}")
    print("=" * 60)
    
    # Test Phase 1
    print("\n[TEST] Phase 1 Rules:")
    for rule in pmt.get_phase_1_rules():
        print(rule)
        
    # Test Phase 2
    mock_state = {
        "autonomic": {"sympathetic": 0.85, "parasympathetic": 0.15},
        "blood": {"cortisol": 0.45, "adrenaline": 0.75}
    }
    
    print("\n" + "=" * 60)
    print("[TEST] Phase 2 Rules (High Stress):")
    for rule in pmt.get_phase_2_rules(mock_state, rim_impact="low"):
        print(rule)
