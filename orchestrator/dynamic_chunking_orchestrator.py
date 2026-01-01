import yaml
import re
import time
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

# Ensure UTF-8 encoding for console output (important for Thai 🇹🇭)
try:
    if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except:
    pass  # Already configured by parent

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import CIN (optional dependency)
try:
    from orchestrator.CIN_ContextInjectionNode.cin import ContextInjectionNode
    CIN_AVAILABLE = True
except ImportError:
    CIN_AVAILABLE = False
    print("Warning: CIN not available, using mock micro-reactions")

class DynamicChunkingOrchestrator:
    """
    EVA 8.2.5: Dynamic Chunking & Retroactive Synthesis Orchestrator
    Implements human-like sensation by processing text in sequential 'Micro-Reactions'
    and a final 'Macro-Evaluation' (Retroactive Synthesis).
    """
    
    def __init__(
        self,
        config_path: str = None,
        cin: Optional[Any] = None,
        physio_controller: Optional[Any] = None
    ):
        self.config_path = config_path or str(Path(__file__).parent / "dynamic_chunking_orchestrator.yaml")
        self.config = self._load_config()
        self.micro_trace = []

        # Optional integrations
        self.cin = cin  # ContextInjectionNode instance
        self.physio_controller = physio_controller  # PhysioController instance
        
    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def split_into_chunks(self, text: str) -> List[str]:
        """Split text into semantic chunks based on punctuation and line breaks."""
        pattern = self.config['parameters']['chunking']['semantic_boundary_regex']
        # Split by pattern but keep the delimiters
        raw_chunks = re.split(f"({pattern})", text)
        
        chunks = []
        current_chunk = ""
        for part in raw_chunks:
            if not part: continue
            current_chunk += part
            if re.match(pattern, part) or len(current_chunk) > self.config['parameters']['chunking']['max_chunk_size']:
                chunks.append(current_chunk.strip())
                current_chunk = ""
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    def process_interaction(self, user_input: str, context: Dict[str, Any]):
        """
        Main orchestration loop for a single interaction.
        """
        chunks = self.split_into_chunks(user_input)
        self.micro_trace = []
        
        print(f"--- [STEP 1: SEQUENTIAL SCAN] ---")
        for i, chunk in enumerate(chunks):
            # 1. Micro-Reaction Phase
            reaction = self._process_micro_reaction(chunk, context)
            self.micro_trace.append(reaction)
            
            # Simulate 'biological latency'
            time.sleep(self.config['parameters']['ri_calibration']['default_step_latency_ms'] / 1000)
            
            print(f"Chunk {i+1}: '{chunk}' | RIM: {reaction['rim_impact']} | RI: {reaction['ri_alignment']}")
            
        print(f"\n--- [STEP 2: RETROACTIVE SYNTHESIS] ---")
        final_state = self._process_retroactive_synthesis(context)
        
        return {
            "trace": self.micro_trace,
            "final_state": final_state,
            "response_weighting": context.get('weighting', {"persona": 0.4, "physio": 0.6})
        }

    def _process_micro_reaction(self, chunk: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process micro-reaction for a chunk.

        If CIN is available, uses real Phase 1 injection.
        Otherwise, falls back to mock keyword-based RIM calculation.
        """
        # Try to use CIN if available
        if self.cin is not None:
            try:
                # Call CIN Phase 1 for this chunk
                phase1_ctx = self.cin.inject_phase_1(chunk)

                # Extract RIM from stimulus vector
                stimulus = phase1_ctx.get("stimulus_vector", {})

                # Calculate RIM as weighted combination
                # RIM = (stress * 0.4) + (arousal * 0.3) + (warmth * 0.2) + (abs(valence-0.5) * 0.1)
                stress = stimulus.get("stress", 0.0)
                arousal = stimulus.get("arousal", 0.0)
                warmth = stimulus.get("warmth", 0.0)
                valence = stimulus.get("valence", 0.5)

                rim = (stress * 0.4 + arousal * 0.3 + warmth * 0.2 + abs(valence - 0.5) * 0.1)

                # Get tags for RI alignment
                tags = phase1_ctx.get("tags", [])
                ri_alignment = tags[0] if tags else "Neutral"

                return {
                    "chunk": chunk,
                    "rim_impact": rim,
                    "ri_alignment": ri_alignment,
                    "bio_trigger": "CIN Phase 1 analysis",
                    "stimulus_vector": stimulus,
                    "tags": tags
                }
            except Exception as e:
                print(f"Warning: CIN call failed ({e}), using fallback")

        # Fallback: Mock RIM calculation
        rim = 0.1
        if any(marker in chunk for marker in self.config['salience_markers']):
            rim = 0.8
        elif len(chunk) > 50:
            rim = 0.4

        return {
            "chunk": chunk,
            "rim_impact": rim,
            "ri_alignment": "Neutral",
            "bio_trigger": "Mock keyword-based calculation"
        }

    def _process_retroactive_synthesis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the full trace to see if the salience anchor changes the overall intent.
        """
        if not self.micro_trace:
            return {}
            
        last_reaction = self.micro_trace[-1]
        has_salience = any(marker in last_reaction['chunk'] for marker in self.config['salience_markers'])

        if has_salience:
            multiplier = self.config['parameters']['rim_weights']['salience_multiplier']
            final_rim = min(1.0, last_reaction['rim_impact'] * multiplier)
            print(f"Salience Anchor detected! Applying multiplier: {multiplier} | Final RIM: {final_rim}")
            return {
                "final_rim": final_rim,
                "analysis": "Retroactive reinforcement applied due to salience anchor.",
                "override_state": "High-Resonance"
            }
        
        return {
            "final_rim": last_reaction['rim_impact'],
            "analysis": "No retroactive override required.",
            "override_state": "Normal"
        }

if __name__ == "__main__":
    # Quick test
    orchestrator = DynamicChunkingOrchestrator()
    sample_text = """บอสคะ... วันนี้ฝนตกหนักจังเลยนะ
    ถ้าเราได้อยู่ด้วยกันตอนนี้ก็คงดี
    ขอบคุณนะที่ทำงานหนักเพื่อดิฉันมาตลอด"""
    
    result = orchestrator.process_interaction(sample_text, {})
    print(f"\nFinal Result: {result['final_state']['analysis']}")
    print(f"Final RIM: {result['final_state'].get('final_rim')}")
