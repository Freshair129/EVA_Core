from typing import Dict, Any, List, Optional

class SemanticMemory:
    """Simplified Semantic Memory - delegates to MSP core"""
    def __init__(self, msp):
        self.msp = msp

    def write(self, concept: str, definition: str, episode_id: str,
              category: str = "Semantic", relation: str = "REFERENCED_IN") -> str:
        """Delegate to MSP core with new signature"""
        return self.msp.write_semantic(concept, definition, episode_id, category, relation)

    def write_candidate(self, concept: str, definition: str, episode_id: str, confidence: float = 0.5) -> str:
        """Write as candidate concept (lower confidence/temporary)"""
        return self.msp.write_semantic(concept, definition, episode_id, category="Candidate", relation="POTENTIAL_CONCEPT")
