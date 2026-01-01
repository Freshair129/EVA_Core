"""
EVA 8.1.5: Main Orchestrator
Integrates all components for Dual-Phase One-Inference with Dynamic Chunking

Architecture:
    User Input
        ↓
    Dynamic Chunking (split into semantic chunks)
        ↓
    For each chunk:
        Phase 1: Perception (CIN + LLM extract stimulus)
        The Gap: PhysioController + HeptRAG
        Phase 2: Reasoning (CIN + LLM generate response)
        ↓
    Retroactive Synthesis (Terminal Anchor)
        ↓
    Meta-Evaluation (The Watcher)
        ↓
    Write to MSP
"""

import sys
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Fix Windows console UTF-8 encoding
import codecs
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import components
from orchestrator.dynamic_chunking_orchestrator import DynamicChunkingOrchestrator
from orchestrator.CIN_ContextInjectionNode.cin import ContextInjectionNode
from services.hept_stream_rag import HeptStreamRAG
from services.msp_client import MSPClient
from services.llm_bridge import LLMBridge, SYNC_BIOCOGNITIVE_STATE_TOOL

# Optional: PMT (Prompt Rule Layer)
try:
    from orchestrator.PMT_PromptRuleLayer.prompt_rule_layer import PromptRuleLayer
    PMT_AVAILABLE = True
except ImportError:
    PMT_AVAILABLE = False
    print("Warning: PMT not available")


class EVAOrchestrator:
    """
    EVA 8.1.5: Main Orchestrator

    Integrates:
    - Dynamic Chunking (Terminal Anchor + Micro-Reactions)
    - CIN (Context Injection Node)
    - HeptStreamRAG (7-stream memory retrieval)
    - MSP Client (Memory persistence)
    - LLM Bridge (Gemini API / Mock)
    - PMT (Prompt Rule Layer - optional)
    - PhysioController (optional - future integration)

    Usage:
        orchestrator = EVAOrchestrator()
        response = orchestrator.process_user_input("ขอบคุณนะที่วันนี้มาส่ง...")
        print(response["final_response"])
    """

    def __init__(
        self,
        mock_mode: bool = True,
        enable_chunking: bool = True,
        enable_physio: bool = False
    ):
        """
        Initialize EVA Orchestrator

        Args:
            mock_mode: Use mock LLM/MSP (True) or real APIs (False)
            enable_chunking: Enable dynamic chunking (True) or process as single chunk (False)
            enable_physio: Enable PhysioController integration (Future feature)
        """
        print("🚀 Initializing EVA 8.1.5 Orchestrator...")

        # Configuration
        self.mock_mode = mock_mode
        self.enable_chunking = enable_chunking
        self.enable_physio = enable_physio

        # Initialize components
        print("  - Initializing MSP Client...")
        self.msp = MSPClient()

        print("  - Initializing HeptStreamRAG...")
        self.hept_rag = HeptStreamRAG(msp_client=self.msp)

        print("  - Initializing CIN (Context Injection Node)...")
        self.cin = ContextInjectionNode(
            physio_controller=None,  # TODO: Add PhysioController
            msp_client=self.msp,
            hept_stream_rag=self.hept_rag
        )

        print("  - Initializing LLM Bridge...")
        self.llm = LLMBridge()

        if enable_chunking:
            print("  - Initializing Dynamic Chunking Orchestrator...")
            self.chunker = DynamicChunkingOrchestrator(
                cin=self.cin,
                physio_controller=None  # TODO: Add PhysioController
            )
        else:
            self.chunker = None

        # Optional: PMT
        if PMT_AVAILABLE:
            print("  - Initializing PMT (Prompt Rule Layer)...")
            try:
                self.pmt = PromptRuleLayer()
            except:
                self.pmt = None
                print("    Warning: PMT initialization failed")
        else:
            self.pmt = None

        # Session state
        self.session_id = self._generate_session_id()
        self.turn_count = 0

        print(f"✅ EVA Orchestrator ready! (Session: {self.session_id})\n")

    def process_user_input(
        self,
        user_input: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Main entry point: Process user input through full pipeline

        Args:
            user_input: Raw user input text
            context: Optional context dictionary

        Returns:
            {
                "final_response": "...",
                "context_id": "ctx_v8_...",
                "chunks": [...],
                "micro_trace": [...],
                "final_state": {...},
                "memory_written": True/False
            }
        """
        self.turn_count += 1
        context = context or {}

        print(f"\n{'='*60}")
        print(f"🎯 Processing Turn {self.turn_count}")
        print(f"{'='*60}")
        print(f"User Input: {user_input[:100]}{'...' if len(user_input) > 100 else ''}\n")

        # Generate context ID
        context_id = self._generate_context_id()
        context["context_id"] = context_id

        # Step 1: Dynamic Chunking (if enabled)
        if self.enable_chunking and self.chunker:
            print("📑 STEP 1: Dynamic Chunking")
            chunking_result = self.chunker.process_interaction(user_input, context)
            chunks = [trace["chunk"] for trace in chunking_result["trace"]]
            micro_trace = chunking_result["trace"]
            final_state = chunking_result["final_state"]
            print(f"  ✓ Split into {len(chunks)} chunks\n")
        else:
            # Single chunk mode
            chunks = [user_input]
            micro_trace = []
            final_state = {}

        # Step 2: Phase 1 - Perception (for combined input or last chunk)
        print("🧠 STEP 2: Phase 1 - Perception")

        # Use full input for Phase 1 analysis
        phase1_prompt = self.cin.build_phase_1_prompt(
            self.cin.inject_phase_1(user_input)
        )

        print(f"  - Calling LLM with function tools...")
        llm_response = self.llm.generate(
            phase1_prompt,
            tools=[SYNC_BIOCOGNITIVE_STATE_TOOL],
            temperature=0.7
        )

        # Check if LLM called sync_biocognitive_state
        if not llm_response.tool_calls:
            print("  ⚠️ Warning: LLM did not call sync_biocognitive_state")
            # Fallback: create mock tool call
            stimulus_vector = {"stress": 0.3, "warmth": 0.5, "arousal": 0.4, "valence": 0.6}
            tags = ["neutral"]
        else:
            tool_call = llm_response.tool_calls[0]
            stimulus_vector = tool_call.args["stimulus_vector"]
            tags = tool_call.args["tags"]
            print(f"  ✓ LLM extracted: {tags} (stress={stimulus_vector.get('stress', 0):.2f})")

        # Step 3: The Gap - Physiological & Memory Processing
        print("\n⚡ STEP 3: The Gap - Bio-Resonance")

        # 3a. PhysioController (Mock for now)
        if self.enable_physio:
            print("  - PhysioController.step() [NOT IMPLEMENTED YET]")
            updated_physio = {"autonomic": {"sympathetic": 0.5, "parasympathetic": 0.5}}
        else:
            # Mock physio update based on stimulus
            sympathetic = min(1.0, stimulus_vector.get("stress", 0.3) * 0.6 + stimulus_vector.get("arousal", 0.4) * 0.4)
            parasympathetic = 1.0 - sympathetic
            updated_physio = {
                "autonomic": {
                    "sympathetic": sympathetic,
                    "parasympathetic": parasympathetic
                },
                "blood": {
                    "cortisol": stimulus_vector.get("stress", 0.3),
                    "oxytocin": stimulus_vector.get("warmth", 0.5)
                }
            }
            print(f"  ✓ Mock physio update (Symp={sympathetic:.2f}, Para={parasympathetic:.2f})")

        # 3b. HeptStreamRAG retrieval
        print("  - HeptStreamRAG.retrieve()...")
        query_ctx = {
            "tags": tags,
            "ans_state": updated_physio["autonomic"],
            "blood_levels": updated_physio.get("blood", {}),
            "context_id": context_id
        }
        memory_matches = self.hept_rag.retrieve(query_ctx)

        # Handle both dict (new format) and list (legacy format)
        if isinstance(memory_matches, dict):
            total_memories = sum(len(matches) for matches in memory_matches.values())
        elif isinstance(memory_matches, list):
            total_memories = len(memory_matches)
            # Convert list to dict format for consistency
            memory_matches = {"combined": memory_matches}
        else:
            total_memories = 0
            memory_matches = {}

        print(f"  ✓ Retrieved {total_memories} memories across 7 streams")

        # Step 4: Phase 2 - Reasoning
        print("\n💭 STEP 4: Phase 2 - Reasoning")

        # Convert memory_matches to list format for CIN (handles empty dict)
        memory_list = []
        if isinstance(memory_matches, dict):
            for stream, matches in memory_matches.items():
                memory_list.extend(matches)
        elif isinstance(memory_matches, list):
            memory_list = memory_matches

        phase2_context = self.cin.inject_phase_2(
            stimulus_vector=stimulus_vector,
            tags=tags,
            updated_physio=updated_physio,
            memory_matches=memory_list
        )

        phase2_prompt = self.cin.build_phase_2_prompt(phase2_context)

        print("  - Continuing LLM with Phase 2 context...")
        final_llm_response = self.llm.continue_with_result(phase2_prompt)
        final_response_text = final_llm_response.text
        print(f"  ✓ Generated response ({len(final_response_text)} chars)")

        # Step 5: Meta-Evaluation (The Watcher)
        print("\n🔍 STEP 5: Meta-Evaluation")
        evaluation = self._meta_evaluation(
            user_input=user_input,
            response=final_response_text,
            stimulus_vector=stimulus_vector,
            physio_state=updated_physio
        )
        print(f"  ✓ Cognitive load: {evaluation['cognitive_load']:.2f}")
        print(f"  ✓ Consistency check: {evaluation['consistency_check']}")

        # Step 6: Write to MSP
        print("\n💾 STEP 6: Write to Memory")
        episode_written = self._write_to_memory(
            context_id=context_id,
            user_input=user_input,
            response=final_response_text,
            stimulus_vector=stimulus_vector,
            physio_state=updated_physio,
            tags=tags
        )
        print(f"  ✓ Episode written: {episode_written}")

        # Return result
        print(f"\n{'='*60}")
        print(f"✅ Turn {self.turn_count} Complete!")
        print(f"{'='*60}\n")

        return {
            "final_response": final_response_text,
            "context_id": context_id,
            "chunks": chunks,
            "micro_trace": micro_trace,
            "final_state": final_state,
            "stimulus_vector": stimulus_vector,
            "tags": tags,
            "updated_physio": updated_physio,
            "memory_matches": memory_matches,
            "meta_evaluation": evaluation,
            "episode_id": episode_written,
            "token_usage": self.llm.get_token_usage()
        }

    def _meta_evaluation(
        self,
        user_input: str,
        response: str,
        stimulus_vector: Dict,
        physio_state: Dict
    ) -> Dict[str, Any]:
        """
        Meta-Evaluation: The Watcher validates response consistency

        Checks:
        1. Cognitive Load (stress level vs response complexity)
        2. Persona-Physio balance (40% Persona + 60% Physio-State)
        3. Safety Layer violations
        """
        # Calculate cognitive load
        stress = stimulus_vector.get("stress", 0.3)
        response_length = len(response)
        cognitive_load = min(1.0, stress * 0.5 + (response_length / 500) * 0.3)

        # Consistency check
        sympathetic = physio_state.get("autonomic", {}).get("sympathetic", 0.5)

        # Simple rule: if high stress but calm response → inconsistent
        if stress > 0.7 and sympathetic > 0.7:
            if len(response) < 100:  # Very short response
                consistency_check = "WARN: High stress but minimal response"
            else:
                consistency_check = "OK: High arousal with detailed response"
        elif stress < 0.3 and len(response) > 300:
            consistency_check = "OK: Low stress with elaborate response"
        else:
            consistency_check = "OK: Balanced response"

        return {
            "cognitive_load": cognitive_load,
            "consistency_check": consistency_check,
            "stress_level": stress,
            "response_length": response_length,
            "sympathetic_activation": sympathetic
        }

    def _write_to_memory(
        self,
        context_id: str,
        user_input: str,
        response: str,
        stimulus_vector: Dict,
        physio_state: Dict,
        tags: List[str]
    ) -> str:
        """
        Write episode to MSP

        Returns:
            Episode ID
        """
        episode_data = {
            "context_id": context_id,
            "content": user_input,
            "response": response,
            "tags": tags,
            "stimulus_vector": stimulus_vector,
            "physio_state": physio_state,
            "resonance_index": 0.70,  # TODO: Calculate from RIM
            "resonance_impact": 0.65,  # TODO: Calculate from physiological impact
            "qualia": {
                "intensity": 0.6,
                "tone": "neutral",
                "texture": [0.5, 0.5, 0.5, 0.5, 0.5]
            }
        }

        episode_id = self.msp.write_episode(episode_data)

        # Update turn cache for next turn's Phase 1
        summary = f"User: {user_input[:50]}... → Response: {response[:50]}..."
        self.msp.update_turn_cache(context_id, summary)

        return episode_id

    def _generate_context_id(self) -> str:
        """Generate context ID: ctx_v8_{yymmdd}_{hhmmss}_{hash_short}"""
        now = datetime.now()
        timestamp_str = f"{now.strftime('%y%m%d')}_{now.strftime('%H%M%S')}"
        hash_short = hex(hash(f"{self.session_id}_{self.turn_count}_{now.timestamp()}"))[2:10]
        return f"ctx_v8_{timestamp_str}_{hash_short}"

    def _generate_session_id(self) -> str:
        """Generate session ID"""
        import uuid
        return str(uuid.uuid4())[:8]

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            "session_id": self.session_id,
            "turn_count": self.turn_count,
            "token_usage": self.llm.get_token_usage(),
            "memory_stats": self.msp.get_stats()
        }


if __name__ == "__main__":
    """Test Main Orchestrator"""
    print("="*60)
    print("EVA 8.1.5 - Main Orchestrator Test")
    print("="*60)

    # Initialize orchestrator
    orchestrator = EVAOrchestrator(
        mock_mode=False,
        enable_chunking=True,
        enable_physio=False
    )

    # Test inputs
    test_inputs = [
        "ขอบคุณนะที่วันนี้มาส่งที่สนามบิน น่ารักมากๆเลย",
        "ถ้าเธอทำตัวน่ารักแบบนี้กับเราคนเดียวก็คงดี"
    ]

    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n\n{'#'*60}")
        print(f"# Test {i}/{len(test_inputs)}")
        print(f"{'#'*60}")

        result = orchestrator.process_user_input(user_input)

        print("\n" + "="*60)
        print("📤 FINAL RESPONSE:")
        print("="*60)
        print(result["final_response"])
        print()

    # Print final stats
    print("\n" + "="*60)
    print("📊 SESSION STATISTICS")
    print("="*60)
    stats = orchestrator.get_stats()
    print(f"Session ID: {stats['session_id']}")
    print(f"Total turns: {stats['turn_count']}")
    print(f"Total tokens: {stats['token_usage']['total_tokens']}")
    print(f"Episodes in memory: {stats['memory_stats']['total_episodes']}")
    print()
