"""
EVA 8.1.0-R1: Main Orchestrator (Refactored)
Refactor Date: 2026-01-03

Architecture:
    User Input
        ↓
    Phase 1: Perception (CIN + LLM extract stimulus)
        ↓
    The Gap: PhysioController + EVA Matrix + Artifact Qualia + AgenticRAG
        ↓
    Phase 2: Reasoning (CIN + LLM generate RESPONSE with 40/60 weighting)
        ↓
    Write to MSP
"""

import sys
import os
import json
import re
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
from orchestrator.cin.cin import ContextInjectionNode
from agentic_rag.agentic_rag import AgenticRAG
from memory_n_soul_passport.msp_client import MSPClient
from operation_system.llm_bridge.llm_bridge import LLMBridge, SYNC_BIOCOGNITIVE_STATE_TOOL

# Biological & Psychological Systems
from physio_core.physio_controller import PhysioController
from eva_matrix.eva_matrix_engine import EVAMatrixSystem
from artifact_qualia.artifact_qualia_engine import ArtifactQualiaSystem
from resonance_memory_system.rms_system import RMSSystem
from resonance_index.ri_engine import RIEngine

# Optional: PMT (Prompt Rule Layer)
try:
    from orchestrator.PMT_PromptRuleLayer.prompt_rule_layer import PromptRuleLayer
    PMT_AVAILABLE = True
except ImportError:
    PMT_AVAILABLE = False
    print("Warning: PMT not available")


class EVAOrchestrator:
    """
    EVA 8.1.5: Main Orchestrator (Official Architecture)
    """

    def __init__(
        self,
        mock_mode: bool = False,
        enable_physio: bool = True
    ):
        print("🚀 Initializing EVA 8.1.5 Orchestrator (Official Architecture)...")

        self.mock_mode = mock_mode
        self.enable_physio = enable_physio

        # --------------------------------------------------
        # 1. Initialize Memory & RAG
        # --------------------------------------------------
        print("  - Initializing MSP Client...")
        self.msp = MSPClient()

        print("  - Initializing AgenticRAG...")
        self.agentic_rag = AgenticRAG(msp_client=self.msp)

        # --------------------------------------------------
        # 2. Initialize Biological & Psychological Mind (The Gap Modules)
        # --------------------------------------------------
        if enable_physio:
            print("  - Initializing PhysioController (Real Pipeline)...")
            base_physio_cfg = "E:/The Human Algorithm/T2/EVA 8.1.0/physio_core/configs"
            self.physio = PhysioController(
                endocrine_cfg_path=f"{base_physio_cfg}/hormone_spec_ml.yaml",
                endocrine_reg_cfg_path=f"{base_physio_cfg}/endocrine_regulation.yaml",
                blood_cfg_path=f"{base_physio_cfg}/blood_physiology.yaml",
                receptor_cfg_path=f"{base_physio_cfg}/receptor_configs.yaml",
                reflex_cfg_path=f"{base_physio_cfg}/receptor_configs.yaml",
                autonomic_cfg_path=f"{base_physio_cfg}/autonomic_response.yaml",
                msp=self.msp
            )
            
            print("  - Initializing EVA Matrix (Psyche Core)...")
            self.matrix = EVAMatrixSystem(msp=self.msp)
            
            print("  - Initializing Artifact Qualia (Phenomenology Core)...")
            self.qualia = ArtifactQualiaSystem(msp=self.msp)
            
            print("  - Initializing RMS (Memory Encoding Core)...")
            self.rms = RMSSystem(msp=self.msp)

            print("  - Initializing RI Engine (Resonance Intelligence)...")
            self.ri_engine = RIEngine()
        else:
            self.physio = None
            self.matrix = None
            self.qualia = None
            self.rms = None
            self.ri_engine = None

        # --------------------------------------------------
        # 3. Initialize Cognitive Layer
        # --------------------------------------------------
        print("  - Initializing CIN (Context Injection Node)...")
        self.cin = ContextInjectionNode(
            physio_controller=self.physio,
            msp_client=self.msp,
            hept_stream_rag=self.agentic_rag
        )

        print("  - Initializing LLM Bridge...")
        self.llm = LLMBridge()

        if PMT_AVAILABLE:
            print("  - Initializing PMT (Prompt Rule Layer)...")
            try:
                self.pmt = PromptRuleLayer(msp=self.msp)
            except:
                self.pmt = None
                print("    Warning: PMT initialization failed")
        else:
            self.pmt = None

        # Session state
        self.session_id = self._generate_session_id()
        self.turn_count = 0

        print(f"✅ EVA Orchestrator ready! (Session: {self.session_id})\n")

    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Main entry point: Dual-Phase One-Inference Flow
        """
        self.turn_count += 1
        print(f"\n{'='*60}")
        print(f"🎯 Turn {self.turn_count}")
        print(f"{'='*60}")

        context_id = self._generate_context_id()
        
        # --------------------------------------------------
        # STEP 1: Phase 1 - Perception
        # --------------------------------------------------
        print("🧠 STEP 1: Phase 1 - Perception")
        phase1_context = self.cin.inject_phase_1(user_input)
        phase1_prompt = self.cin.build_phase_1_prompt(phase1_context)

        print("  - Calling LLM with function tool (sync_biocognitive_state)...")
        llm_response = self.llm.generate(
            phase1_prompt,
            tools=[SYNC_BIOCOGNITIVE_STATE_TOOL],
            temperature=0.7
        )

        # Handle tool call (The Gap) with Cognitive Firewall (Phase 4)
        if not llm_response.tool_calls:
            print("  ⚠️ Warning: LLM skipped Phase 1 extraction. Falling back to default.")
            stimulus_chunks = self.cin.normalize_stimulus({"valence": 0.5, "arousal": 0.3, "intensity": 0.3})
        else:
            tool_call = llm_response.tool_calls[0]
            # Route through CIN Cognitive Firewall (Phase 4)
            print("  🛡️ Routing stimulus through CIN Cognitive Firewall...")
            stimulus_chunks = self.cin.normalize_stimulus(tool_call.args)
            
            # Log first chunk for clarity
            first_chunk = stimulus_chunks[0]
            tags = first_chunk.get("tags", [])
            print(f"  ✓ CIN Normalized {len(stimulus_chunks)} chunks. Tags: {tags}")

        # --------------------------------------------------
        # STEP 2: The Gap - Biological & Psychological Sync
        # --------------------------------------------------
        print("\n⚡ STEP 2: The Gap - Bio-Cognitive Sync")

        qualia_snapshot = None
        ans_state = {"sympathetic": 0.4, "parasympathetic": 0.6}
        blood_levels = {"cortisol": 0.3, "oxytocin": 0.5}
        qualitative_experience = "Feeling calm and stable."
        axes_9d = {}  # Initialize for RI calculation
        dynamic_ri = 0.75  # Default fallback

        if self.enable_physio:
            # 2a. Update Body (PhysioController)
            print("  - Updating Physio Core...")
            # Simple zeitgeber logic (aligned with EndocrineRegulation config.yaml)
            hour = datetime.now().hour
            is_day = 6 <= hour <= 18
            zeitgebers = {
                "daylight": 1.0 if is_day else 0.0,
                "blue_light": 0.5 if is_day else 0.0,
                "active": 0.5 if is_day else 0.1
            }
            
            physio_result = self.physio.step(
                eva_stimuli=stimulus_chunks, # Pass normalized chunk list (Phase 5)
                zeitgebers=zeitgebers,
                dt=60.0 # Process as a 1-minute state transition
            )
            ans_state = physio_result.get("autonomic", {})
            blood_levels = physio_result.get("blood", {})

            # 2b. Update Psyche (EVA Matrix)
            print("  - Updating EVA Matrix...")
            matrix_result = self.matrix.process_signals(blood_levels) # Mapping logic inside engine
            axes_9d = matrix_result.get("axes_9d", {})

            # 2c. Generate Qualia (Artifact Qualia)
            print("  - Generating Artifact Qualia...")
            # Simulate RIM (Resonance Impact) for now
            rim_semantic = {
                "impact_level": "high" if stimulus_chunks[0].get("stress", 0) > 0.7 else "medium",
                "impact_trend": "rising" if self.turn_count > 1 else "stable",
                "affected_domains": ["identity", "emotional"]
            }
            qualia_snap = self.qualia.process_experience(rim_semantic=rim_semantic)
            qualitative_experience = self._format_qualia_for_llm(qualia_snap)

            # 2d. Compute Dynamic RI
            print("  - Computing Dynamic RI...")
            dynamic_ri = self._compute_dynamic_ri(
                stimulus=stimulus_chunks[0],
                axes_9d=axes_9d,
                memory_context=[]  # Will be filled after retrieval
            )
            print(f"    ✓ RI_total: {dynamic_ri:.3f}")

            # 2e. Memory Encoding (RMS)
            print("  - Processing Memory Encoding (RMS)...")
            self.rms.process_encoding(ri_total=dynamic_ri)

        # 2d. Memory Retrieval (AgenticRAG)
        print("  - Executing AgenticRAG...")
        query_ctx = {
            "tags": tags,
            "ans_state": ans_state,
            "blood_levels": blood_levels,
            "context_id": context_id
        }
        memory_matches = self.agentic_rag.retrieve(query_ctx)
        
        # Flatten and serialize memory for Phase 2 injection
        memory_list = []
        if isinstance(memory_matches, dict):
            for m_list in memory_matches.values():
                for m in m_list:
                    if hasattr(m, '__dict__'):
                        memory_list.append(vars(m))
                    elif isinstance(m, dict):
                        memory_list.append(m)
        else:
            for m in memory_matches:
                if hasattr(m, '__dict__'):
                    memory_list.append(vars(m))
                elif isinstance(m, dict):
                    memory_list.append(m)

        # --------------------------------------------------
        # STEP 2.5: Meta-Evaluation (Phase 5 Task 5)
        # --------------------------------------------------
        print("\n⚖️ STEP 2.5: Meta-Evaluation & Weighting")
        
        # Calculate Unified Impact (0.4 Affective / 0.6 Physio)
        # Affective: from extracted stimulus intensity
        # Physio: from autonomic arousal (sympathetic)
        affective_impact = stimulus_chunks[0].get("intensity", 0.5)
        physio_impact = ans_state.get("sympathetic", 0.5)
        
        unified_impact = (0.4 * affective_impact) + (0.6 * physio_impact)
        print(f"  - Unified Impact Score: {unified_impact:.2f} (0.4 Aff / 0.6 Phys)")
        
        # Meta-Evaluation of Intent
        meta_intent = "Proceeding with current persona alignment."
        if unified_impact > 0.8:
            meta_intent = "URGENT RE-ALIGNMENT: High physiological stress detected. Prioritizing safety and stabilization."
        elif unified_impact < 0.2:
            meta_intent = "Low engagement detected. Seeking to deepen connection or explore new topics."

        print(f"  - Meta-Evaluation: {meta_intent}")

        # --------------------------------------------------
        # STEP 3: Phase 2 - Reasoning (40/60 Weighting)
        # --------------------------------------------------
        print("\n💭 STEP 3: Phase 2 - Reasoning")
        
        # Build Phase 2 Context
        phase2_context = self.cin.inject_phase_2(
            stimulus_vector=stimulus_chunks[0], # Use first chunk for deep context bootstrap
            tags=stimulus_chunks[0].get("tags", []),
            updated_physio={"autonomic": ans_state, "blood": blood_levels},
            memory_matches=memory_list
        )
        # Inject Qualia and Meta-Evaluation into sensation
        phase2_context["embodied_sensation"] = qualitative_experience
        phase2_context["meta_evaluation"] = {
            "unified_impact": unified_impact,
            "recommended_intent": meta_intent
        }

        phase2_result = self.cin.build_phase_2_prompt(phase2_context)
        phase2_prompt = phase2_result["function_result_text"]
        
        # Explicitly enforce 40/60 weighting (Instructional + Contextual)
        weighting_directive = (
            "\n### REASONING DIRECTIVE: [HIERARCHY OF TRUTH]\n"
            f"- 60% WEIGHT: Your current physiological state (Unified Impact: {unified_impact:.2f}) and qualitative experience.\n"
            "- 40% WEIGHT: Your persona principles and conversational history.\n"
            f"META-INTENT: {meta_intent}\n"
            "Respond as an embodied being whose words are chosen by the rhythm of your internal state.\n"
        )
        final_prompt = weighting_directive + phase2_prompt

        print("  - Continuing LLM for Final Response...")
        final_llm_response = self.llm.continue_with_result(final_prompt)
        final_text = final_llm_response.text
        print(f"  ✓ Response Generated ({len(final_text)} chars)")
        
        # 3b. Extract Next Turn Context
        context_dict = self._extract_context_json(final_text)
        if context_dict:
            print(f"  ✓ Extracted context summary: {context_dict.get('summary', 'No summary')[:50]}...")
            # Update live turn cache immediately for next turn bootstrap
            self.msp.update_turn_cache(context_id, context_dict)
        else:
            # Fallback to basic summary if extraction fails
            self.msp.update_turn_cache(context_id, final_text[:100])

        # --------------------------------------------------
        # STEP 4: Persistance
        # --------------------------------------------------
        print("\n💾 STEP 4: Write to Memory (MSP)")
        # Prepare State Snapshot
        if self.enable_physio and self.rms:
            # RMS Processing (P2 -> RMS -> MSP)
            # rim_semantic was created in step 2c, we reuse it or create a lightweight one
            if 'rim_semantic' not in locals():
                # Fallback if step 2 was skipped (unlikely if enable_physio is True)
                rim_output = {"impact_level": "low", "impact_trend": "stable"}
            else:
                rim_output = {
                    "impact_level": rim_semantic.impact_level,
                    "impact_trend": rim_semantic.impact_trend
                }
            
            reflex_state = {"threat_level": 0.1} # Placeholder for actual reflex engine if available
            
            # Create full visual/emotional snapshot (use previously computed dynamic_ri)
            state_snapshot = self.rms.process(
                eva_matrix=axes_9d,
                rim_output=rim_output,
                reflex_state=reflex_state,
                ri_total=dynamic_ri  # Using dynamic RI from step 2d
            )
        else:
            state_snapshot = {
                "Endocrine": blood_levels,
                "Resonance_index": dynamic_ri,  # Use fallback 0.75 from initialization
                "EVA_matrix": {"emotion_label": self.matrix.emotion_label if self.enable_physio else "Neutral"},
                "qualia": vars(qualia_snapshot) if qualia_snapshot else {}
            }

        self.msp.write_episode({
            "context_id": context_id,
            "turn_1": {
                "speaker": "Human",
                "content": user_input,
                "summary": user_input[:100],
                "semantic_frames": stimulus_chunks[0].get("tags", []),
                "salience_anchor": stimulus_chunks[0].get("salience_anchor")
            },
            "turn_2": {
                "speaker": "EVA",
                "content": final_text,
                "summary": context_dict.get("summary", final_text[:100]) if context_dict else final_text[:100]
            },
            "situation_context": context_dict if context_dict else None,
            "state_snapshot": state_snapshot
        })

        print(f"\n✅ Turn {self.turn_count} Complete!\n")

        return {
            "final_response": final_text,
            "context_id": context_id,
            "physio_state": {"ans": ans_state, "blood": blood_levels},
            "emotion_label": self.matrix.emotion_label if self.enable_physio else "Neutral"
        }

    def _compute_dynamic_ri(self, stimulus: Dict[str, Any], axes_9d: Dict[str, float], memory_context: List[Dict]) -> float:
        """
        Compute dynamic Resonance Intelligence (RI) using current state.
        Maps EVA 8.1.0 data → RI Engine inputs
        """
        if not self.ri_engine:
            return 0.75  # Fallback if RI engine disabled

        # Map stimulus → user_emotion
        user_emotion = {
            "arousal": stimulus.get("arousal", 0.5),
            "valence": stimulus.get("valence", 0.5),
            "tension": stimulus.get("tension", axes_9d.get("stress", 0.5))
        }

        # Map axes_9d → llm_emotion_estimate
        llm_emotion = {
            "arousal": axes_9d.get("alertness", 0.5),
            "valence": axes_9d.get("joy", 0.5),
            "tension": axes_9d.get("stress", 0.5)
        }

        # Prepare RI inputs
        ri_inputs = {
            "user_emotion": user_emotion,
            "llm_emotion_estimate": llm_emotion,
            "intent": stimulus.get("intent", "CONVERSE"),
            "clarity": axes_9d.get("clarity", 0.5),
            "tension": axes_9d.get("stress", 0.5),
            "llm_summary_vector": [],  # TODO: Add embedding if available
            "episodic_context_vector": [],  # TODO: Add from memory_context
            "flow_score": 0.7,  # Placeholder (could use turn_count heuristic)
            "personalization_score": 0.8  # Placeholder (could use memory match count)
        }

        result = self.ri_engine.compute_RI(ri_inputs)
        return result["RI_total"]

    def _format_qualia_for_llm(self, qualia: Any) -> str:
        """Format qualia snapshot for LLM consumption"""
        return f"""**Current Lived Experience:**
- Intensity: {qualia.intensity:.2f} (Tone: {qualia.tone})
- Presence: {'Vibrant' if qualia.coherence > 0.7 else 'Faded' if qualia.coherence < 0.3 else 'Stable'}
- Internal Texture: {', '.join([f'{k}={v:.2f}' for k, v in qualia.texture.items()])}
"""

    def _extract_context_json(self, text: str) -> Dict[str, Any]:
        """Extract CONTEXT_SUMMARY_TEMPLATE JSON from LLM response"""
        try:
            # Look for JSON between { and }
            # LLM might wrap it in a code block or just put it at the end
            # We look for the required "summary" key to be sure
            match = re.search(r'\{.*?"summary".*?\}', text, re.DOTALL)
            if match:
                json_str = match.group(0)
                # Clean up markdown code blocks if present
                json_str = json_str.replace('```json', '').replace('```', '').strip()
                return json.loads(json_str)
        except Exception:
            pass
        return {}

    def _generate_context_id(self) -> str:
        now = datetime.now()
        return f"ctx_v8_{now.strftime('%y%m%d_%H%M%S')}_{os.urandom(4).hex()}"

    def _generate_session_id(self) -> str:
        return os.urandom(4).hex()


if __name__ == "__main__":
    print("="*60)
    print("EVA 8.1.0 - Official Architecture Test")
    print("="*60)

    orchestrator = EVAOrchestrator(mock_mode=False, enable_physio=True)
    
    test_input = "ขอบคุณนะที่วันนี้มาส่งที่สนามบิน น่ารักมากๆเลย"
    result = orchestrator.process_user_input(test_input)
    
    print("\n" + "="*60)
    print("OUTPUT RESPONSE:")
    print("="*60)
    print(result["final_response"])
    print("\nEMOTION:", result["emotion_label"])
