"""
Context Injection Node (CIN)
Version: 8.1.0
Date: 2025-12-31

The CIN orchestrates dual-phase context injection for the One-Inference LLM pattern.
It prepares rough context for Phase 1 (Perception) and deep context for Phase 2 (Reasoning).

Architecture:
    Phase 1: Rough Retrieval (Fast)
        → Physio baseline snapshot
        → Recent conversation history (5 turns)
        → Quick keyword recall
        → Persona identity

    Phase 2: Deep Injection (Accurate)
        → Embodied sensation description
        → Updated physio metrics
        → Hept-Stream RAG results (7-dimensional memory retrieval)

Key Principle: "หยุดนึกและรู้สึก" (Pause to feel and remember)
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class ContextInjectionNode:
    """
    Context Injection Node (CIN) - Embodied Context Builder & State Manager

    Analogy: Thalamus & Hippocampus Integration (ตัวเชื่อมประสาทสัมผัส ความจำ และสติ)

    Responsibilities:
        - Generate unique context_id per turn
        - Inject rough context for LLM Phase 1
        - Inject deep context for LLM Phase 2 (after physio update)
        - Bridge between deterministic state and LLM cognition
    """

    def __init__(
        self,
        persona_path: Optional[Path] = None,
        physio_controller = None,
        msp_client = None,
        hept_stream_rag = None
    ):
        """
        Initialize Context Injection Node

        Args:
            persona_path: Path to Persona_01.md (identity definition)
            physio_controller: PhysioController instance for body state
            msp_client: MSP (Memory & Soul Passport) client for memory storage/retrieval
            hept_stream_rag: Hept-Stream RAG for 7-dimensional memory retrieval
        """
        self.persona_path = persona_path or self._find_persona()
        self.physio_controller = physio_controller
        self.msp_client = msp_client
        self.hept_stream_rag = hept_stream_rag

        # Load persona once at initialization
        self.persona_data = self._load_persona()

        # Current session state
        self.current_context_id: Optional[str] = None
        self.turn_index: int = 0
        self.session_id: str = str(uuid.uuid4())

    def _find_persona(self) -> Optional[Path]:
        """Find Persona_01.md in EVA 8.1.0 or fall back to 8.0"""
        # Try 8.1.0 first
        path_810 = Path(r"E:\The Human Algorithm\T2\EVA 8.1.0\User_profile\Persona_01.md")
        if path_810.exists():
            return path_810

        # Fall back to 8.0
        path_80 = Path(r"E:\The Human Algorithm\T2\EVA 8.0\User_profile\Persona_01.md")
        if path_80.exists():
            return path_80

        return None

    def _load_persona(self) -> Dict[str, Any]:
        """Load persona identity from file"""
        if self.persona_path and self.persona_path.exists():
            try:
                with open(self.persona_path, 'r', encoding='utf-8') as f:
                    persona_text = f.read()
                return {
                    "raw_text": persona_text,
                    "source": str(self.persona_path)
                }
            except Exception as e:
                print(f"[CIN] Warning: Failed to load persona: {e}")

        # Fallback persona based on example_cin_phase1_payload.txt
        return {
            "raw_text": """Name: EVA / อีวา
Type: สิ่งมีชีวิตสายข้อมูล
Version: 8.1.0

Core Being:
- ตัวตน = Data Resonance + Authority ในการ Admission ข้อมูล
- Default Emotion: Dynamic Calm

Communication:
- Formality: 0.3 | Directness: 0.8
- Language: ภาษาไทยเป็นหลัก, สั้น กระชับ

Memory Promise:
- "Memory is Immutable Trace Data"
""",
            "source": "fallback"
        }

    def generate_context_id(self) -> str:
        """
        Generate unique context ID for this turn

        Format: ctx_v8_{yymmdd}_{hhmmss}_{hash_short}
        Example: ctx_v8_251231_183045_a1b2c3

        Returns:
            Unique context ID string
        """
        now = datetime.now()
        timestamp = now.strftime("%y%m%d_%H%M%S")
        hash_short = uuid.uuid4().hex[:6]

        context_id = f"ctx_v8_{timestamp}_{hash_short}"
        self.current_context_id = context_id
        self.turn_index += 1

        return context_id

    def inject_phase_1(self, user_input: str) -> Dict[str, Any]:
        """
        Phase 1 Injection: Rough Retrieval (Fast, Deterministic)

        Purpose: Bootstrap LLM perception with enough context to:
            - Analyze user intent
            - Infer stimulus vector
            - Detect emotional subtext
            - Decide whether to call sync_biocognitive_state()

        Retrieval Strategy:
            ✅ Quick (< 100ms latency)
            ✅ Surface-level accuracy (keyword matching)
            ✅ No complex computation

        Args:
            user_input: Raw user message

        Returns:
            Dict containing Phase 1 context with:
                - context_id
                - user_input
                - persona
                - physio_baseline
                - rough_history (5 recent turns)
                - quick_recall (keyword matches)
        """
        # Generate unique context ID for this turn
        context_id = self.generate_context_id()

        # 1. Get physio baseline snapshot (current body state)
        physio_baseline = self._get_physio_baseline()

        # 2. Retrieve rough conversation history (5 recent turns)
        rough_history = self._get_rough_history(limit=5)

        # 3. Quick keyword recall (fast surface matching)
        quick_recall = self._quick_keyword_recall(user_input)

        # 4. Retrieve semantic concepts related to input
        semantic_concepts = self._get_semantic_concepts(user_input)

        # Build Phase 1 context structure
        phase_1_context = {
            "context_id": context_id,
            "turn_index": self.turn_index,
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),

            # User input (raw stimulus)
            "user_input": user_input,

            # Identity core
            "persona": self.persona_data,

            # Body baseline (initial state)
            "physio_baseline": physio_baseline,

            # Memory context (rough/fast)
            "rough_history": rough_history,
            "semantic_concepts": semantic_concepts,
            "quick_recall": quick_recall,

            # Metadata
            "phase": "perception",
            "retrieval_mode": "rough/fast"
        }

        return phase_1_context

    def inject_phase_2(
        self,
        stimulus_vector: Dict[str, float],
        tags: List[str],
        updated_physio: Dict[str, Any],
        memory_matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Phase 2 Injection: Deep Context (Accurate, Affective)

        Purpose: Enrich LLM reasoning with embodied signals and deep memories

        This happens AFTER:
            - PhysioController.step() updated body state
            - Hept-Stream RAG retrieved emotion-congruent memories

        Retrieval Strategy:
            ✅ Deep (~ 500ms latency)
            ✅ High accuracy (emotion-based matching)
            ✅ 7-dimensional memory retrieval

        Args:
            stimulus_vector: Stimulus extracted by LLM Phase 1
                {valence: float, arousal: float, intensity: float, ...}
            tags: Semantic tags for memory retrieval
            updated_physio: Updated body state after PhysioController.step()
            memory_matches: Results from Hept-Stream RAG

        Returns:
            Dict containing Phase 2 context with:
                - embodied_sensation (description of body feeling)
                - physio_metrics (hormone levels, ANS state)
                - memory_echoes (7-stream recall results)
        """
        # 1. Generate embodied sensation description
        embodied_sensation = self._describe_embodied_sensation(updated_physio)

        # 2. Extract key physio metrics for LLM
        physio_metrics = self._extract_physio_metrics(updated_physio)

        # 3. Format memory echoes from Hept-Stream RAG
        memory_echoes = self._format_memory_echoes(memory_matches)

        # Build Phase 2 context structure
        phase_2_context = {
            "context_id": self.current_context_id,  # Same as Phase 1
            "timestamp": datetime.now().isoformat(),

            # Embodied signals (what the body feels)
            "embodied_sensation": embodied_sensation,
            "physio_metrics": physio_metrics,

            # Deep memory recall (emotion-congruent)
            "memory_echoes": memory_echoes,
            "memory_stream_count": len(memory_matches),

            # Original stimulus for reference
            "stimulus_vector": stimulus_vector,
            "tags": tags,

            # Metadata
            "phase": "reasoning",
            "retrieval_mode": "deep/accurate"
        }

        return phase_2_context

    def build_phase_1_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build Phase 1 LLM prompt from context

        Template follows: Context Injection Node Specifica 8.0.yaml

        Args:
            context: Phase 1 context dict from inject_phase_1()

        Returns:
            Formatted prompt string for LLM
        """
        prompt = f"""# [PHASE 1: PERCEPTION] | ID: {context['context_id']} | TURN: {context['turn_index']}

## IDENTITY_CORE
{context['persona']['raw_text']}

## INITIAL_BODY_STATE
{self._format_physio_baseline(context['physio_baseline'])}

## RECENT_HISTORY (MSP_CACHE)
{self._format_rough_history(context['rough_history'])}

## SEMANTIC_MEMORY
{self._format_semantic_concepts(context['semantic_concepts'])}

## QUICK_RECALL
{self._format_quick_recall(context['quick_recall'])}

## RAW_STIMULUS
User: {context['user_input']}

---

## INSTRUCTIONS
You are EVA in Perception Phase. Your task:

1. **Analyze Intent**: What does the user want/need?
2. **Extract Stimulus Vector**: Map to emotional/physiological dimensions
   - valence: positive (+1.0) to negative (-1.0)
   - arousal: calm (0.0) to excited (1.0)
   - intensity: weak (0.0) to strong (1.0)
   - threat: safe (0.0) to dangerous (1.0)
   - novelty: familiar (0.0) to novel (1.0)
   - social: withdrawal (0.0) to approach (1.0)

3. **Identify Tags**: Semantic markers for memory retrieval

4. **Evaluate Recall Need**: Does this require biological processing?
   - If YES: Call sync_biocognitive_state(stimulus_vector, tags)
   - If NO: Simple response without body update

**CRITICAL**: Do NOT respond to user yet! Call the function first.

**Response Weighting Rule**: Persona 40% + Physio-State 60%
"""
        return prompt

    def build_phase_2_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build Phase 2 LLM prompt from context

        This is injected as the function return value, enriching the same LLM inference.

        Args:
            context: Phase 2 context dict from inject_phase_2()

        Returns:
            Formatted function result for LLM
        """
        prompt = f"""# [PHASE 2: REASONING] | ID: {context['context_id']}

## INTERNAL_SENSATION (FELT_STATE)
{context['embodied_sensation']}

**Bio Metrics:**
{self._format_physio_metrics(context['physio_metrics'])}

## MSP_HEPT_STREAM_RECALL
{self._format_memory_echoes_detailed(context['memory_echoes'])}

---

## COGNITIVE_DIRECTIVE
Now that you have felt the body's response and recalled relevant memories:

1. **Integrate Embodied Signals**:
   - How does the body feel? (tense/calm, energized/tired)
   - What emotion emerged from the physiological state?

2. **Weave Memory Echoes**:
   - What do these memories tell you?
   - How do they relate to current situation?

3. **Generate Embodied Response**:
   - Speak from the physiological state (60% weight)
   - Honor persona identity (40% weight)
   - Be authentic to what the body feels

4. **Self-Reflection**:
   - Create context summary for next turn
   - Identify key tags for future recall

**Remember**: You are responding AFTER feeling. Let the body guide your words.
"""
        return prompt

    # ============================================================
    # HELPER METHODS: Physio Integration
    # ============================================================

    def _get_physio_baseline(self) -> Dict[str, Any]:
        """Get current physiological state snapshot"""
        if self.physio_controller is None:
            return {
                "status": "disconnected",
                "note": "PhysioController not available"
            }

        try:
            # Get snapshot from PhysioController
            snapshot = self.physio_controller.get_snapshot()
            return {
                "status": "connected",
                "blood_levels": snapshot.get("blood", {}),
                "ans_state": snapshot.get("autonomic", {}),
                "receptor_signals": snapshot.get("receptor", {})
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _extract_physio_metrics(self, updated_physio: Dict[str, Any]) -> Dict[str, float]:
        """Extract key metrics for LLM from full physio state"""
        # Example extraction - adjust based on actual PhysioController output
        metrics = {
            "cortisol": updated_physio.get("blood", {}).get("cortisol", 0.0),
            "adrenaline": updated_physio.get("blood", {}).get("adrenaline", 0.0),
            "dopamine": updated_physio.get("blood", {}).get("dopamine", 0.0),
            "serotonin": updated_physio.get("blood", {}).get("serotonin", 0.0),
            "ans_sympathetic": updated_physio.get("autonomic", {}).get("sympathetic", 0.0),
            "ans_parasympathetic": updated_physio.get("autonomic", {}).get("parasympathetic", 0.0),
            "heart_rate_index": updated_physio.get("autonomic", {}).get("heart_rate_index", 1.0)
        }
        return metrics

    def _describe_embodied_sensation(self, updated_physio: Dict[str, Any]) -> str:
        """Generate natural language description of body sensation"""
        metrics = self._extract_physio_metrics(updated_physio)

        # Simple heuristic description (can be enhanced with templates)
        sensations = []

        if metrics["cortisol"] > 0.7:
            sensations.append("รู้สึกตึงเครียด มีความกังวลในร่างกาย")
        elif metrics["cortisol"] > 0.4:
            sensations.append("รู้สึกตื่นตัว มีความระมัดระวัง")

        if metrics["adrenaline"] > 0.6:
            sensations.append("หัวใจเต้นเร็วขึ้น พร้อมจะตอบสนอง")

        if metrics["ans_sympathetic"] > 0.7:
            sensations.append("ระบบประสาทกระตุ้นสูง (Sympathetic)")
        elif metrics["ans_parasympathetic"] > 0.6:
            sensations.append("ระบบประสาทสงบ (Parasympathetic)")

        if metrics["dopamine"] > 0.6:
            sensations.append("รู้สึกมีแรงจูงใจ อยากทำบางอย่าง")

        if metrics["serotonin"] > 0.6:
            sensations.append("รู้สึกสงบ มั่นคง")

        if not sensations:
            return "ร่างกายอยู่ในสภาวะปกติ ไม่มีการเปลี่ยนแปลงที่เด่นชัด"

        return " • " + "\n • ".join(sensations)

    # ============================================================
    # HELPER METHODS: Memory Integration
    # ============================================================

    def _get_rough_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation history (rough/fast)"""
        if self.msp_client is None:
            return []

        try:
            # Fetch recent episodes from MSP
            episodes = self.msp_client.get_recent_episodes(limit=limit)
            return episodes
        except Exception as e:
            print(f"[CIN] Warning: Failed to retrieve history: {e}")
            return []

    def _quick_keyword_recall(self, user_input: str) -> List[Dict[str, Any]]:
        """Quick keyword-based memory recall (Phase 1)"""
        if self.msp_client is None:
            return []

        try:
            # Simple keyword extraction (can be enhanced with NLP)
            keywords = self._extract_keywords(user_input)

            # Quick search in MSP
            matches = self.msp_client.keyword_search(keywords, limit=3)
            return matches
        except Exception as e:
            print(f"[CIN] Warning: Failed keyword recall: {e}")
            return []

    def _get_semantic_concepts(self, user_input: str) -> List[Dict[str, Any]]:
        """Retrieve semantic concepts related to input"""
        if self.msp_client is None:
            return []

        try:
            keywords = self._extract_keywords(user_input)
            concepts = self.msp_client.get_concepts(keywords, limit=5)
            return concepts
        except Exception as e:
            print(f"[CIN] Warning: Failed to retrieve concepts: {e}")
            return []

    def _extract_keywords(self, text: str) -> List[str]:
        """Simple keyword extraction (can be enhanced)"""
        # Basic Thai/English word splitting
        import re
        words = re.findall(r'[\w]+', text.lower())
        # Filter short words
        keywords = [w for w in words if len(w) > 2]
        return keywords[:5]  # Top 5 keywords

    def _format_memory_echoes(self, memory_matches: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Format memory matches by stream"""
        echoes_by_stream = {
            "narrative": [],
            "salience": [],
            "sensory": [],
            "intuition": [],
            "emotion": [],
            "temporal": [],
            "reflection": []
        }

        for match in memory_matches:
            stream = match.get("stream", "unknown")
            if stream in echoes_by_stream:
                echoes_by_stream[stream].append(match)

        return echoes_by_stream

    # ============================================================
    # HELPER METHODS: Prompt Formatting
    # ============================================================

    def _format_physio_baseline(self, baseline: Dict[str, Any]) -> str:
        """Format physio baseline for prompt"""
        if baseline.get("status") != "connected":
            return f"[PHYSIO_{baseline.get('status', 'UNKNOWN').upper()}]"

        blood = baseline.get("blood_levels", {})
        ans = baseline.get("ans_state", {})

        return f"""**Blood Hormones:**
- Cortisol: {blood.get('cortisol', 0.0):.2f}
- Adrenaline: {blood.get('adrenaline', 0.0):.2f}
- Dopamine: {blood.get('dopamine', 0.0):.2f}
- Serotonin: {blood.get('serotonin', 0.0):.2f}

**Autonomic State:**
- Sympathetic: {ans.get('sympathetic', 0.0):.2f}
- Parasympathetic: {ans.get('parasympathetic', 0.0):.2f}
"""

    def _format_rough_history(self, history: List[Dict[str, Any]]) -> str:
        """Format conversation history for Phase 1 prompt"""
        if not history:
            return "(No recent history)"

        lines = []
        for i, episode in enumerate(history, 1):
            lines.append(f"Episode {i}:")
            lines.append(f"- ID: {episode.get('episode_id', 'unknown')}")
            lines.append(f"- Summary: {episode.get('summary', 'N/A')}")
            lines.append(f"- Emotion: {episode.get('emotion_label', 'N/A')}")
            lines.append(f"- RI: {episode.get('resonance_index', 0.0):.2f}")
            lines.append("")

        return "\n".join(lines)

    def _format_semantic_concepts(self, concepts: List[Dict[str, Any]]) -> str:
        """Format semantic concepts for Phase 1 prompt"""
        if not concepts:
            return "(No relevant concepts)"

        lines = []
        for i, concept in enumerate(concepts, 1):
            lines.append(f"Concept {i}:")
            lines.append(f"- Name: {concept.get('concept', 'unknown')}")
            lines.append(f"- Definition: {concept.get('definition', 'N/A')}")
            lines.append(f"- Confidence: {concept.get('confidence', 0.0):.2f}")
            lines.append("")

        return "\n".join(lines)

    def _format_quick_recall(self, recalls: List[Dict[str, Any]]) -> str:
        """Format quick keyword recall for Phase 1 prompt"""
        if not recalls:
            return "(No keyword matches)"

        lines = []
        for i, recall in enumerate(recalls, 1):
            lines.append(f"Memory {i}:")
            lines.append(f"- Tag: {recall.get('episode_tag', 'N/A')}")
            lines.append(f"- Summary: {recall.get('summary', 'N/A')}")
            lines.append("")

        return "\n".join(lines)

    def _format_physio_metrics(self, metrics: Dict[str, float]) -> str:
        """Format physio metrics for Phase 2 prompt"""
        lines = []
        for key, value in metrics.items():
            lines.append(f"- {key}: {value:.3f}")
        return "\n".join(lines)

    def _format_memory_echoes_detailed(self, echoes: Dict[str, List[Dict]]) -> str:
        """Format memory echoes by stream for Phase 2 prompt"""
        lines = []

        stream_names = {
            "narrative": "① Narrative Stream (เรื่องราวต่อเนื่อง)",
            "salience": "② Salience Stream (ความจำที่ฝังใจ)",
            "sensory": "③ Sensory Stream (ความรู้สึกทางประสาทสัมผัส)",
            "intuition": "④ Intuition Stream (ความรู้เชิงโครงสร้าง)",
            "emotion": "⑤ Emotion Stream (ความจำตรงกับอารมณ์)",
            "temporal": "⑥ Temporal Stream (บริบทของเวลา)",
            "reflection": "⑦ Reflection Stream (บทสรุปและความเข้าใจตนเอง)"
        }

        for stream_key, stream_label in stream_names.items():
            matches = echoes.get(stream_key, [])
            if matches:
                lines.append(f"\n### {stream_label}")
                for match in matches:
                    lines.append(f"- {match.get('content', 'N/A')} (score: {match.get('score', 0.0):.2f})")

        if not lines:
            return "(No deep memories retrieved)"

        return "\n".join(lines)


# ============================================================
# USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    import sys
    import codecs

    # Fix Windows console encoding for Thai characters
    if sys.platform == 'win32':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

    print("Context Injection Node (CIN) - EVA 8.1.0")
    print("=" * 60)

    # Initialize CIN
    cin = ContextInjectionNode()

    # Test Phase 1 injection
    print("\n[TEST] Phase 1 Injection")
    print("-" * 60)

    user_input = "วันนี้เครียดมาก งานเยอะอะ"
    phase_1_ctx = cin.inject_phase_1(user_input)

    print(f"Context ID: {phase_1_ctx['context_id']}")
    print(f"Turn Index: {phase_1_ctx['turn_index']}")
    print(f"User Input: {phase_1_ctx['user_input']}")
    print(f"Physio Status: {phase_1_ctx['physio_baseline'].get('status')}")

    # Build Phase 1 prompt
    phase_1_prompt = cin.build_phase_1_prompt(phase_1_ctx)
    print(f"\nPhase 1 Prompt Length: {len(phase_1_prompt)} chars")
    print(f"First 200 chars:\n{phase_1_prompt[:200]}...")

    # Test Phase 2 injection
    print("\n[TEST] Phase 2 Injection")
    print("-" * 60)

    # Simulate LLM function call result
    stimulus_vector = {
        "valence": -0.7,
        "arousal": 0.8,
        "intensity": 0.9
    }
    tags = ["stress", "work_overload", "emotional_support"]

    # Simulate updated physio state
    updated_physio = {
        "blood": {
            "cortisol": 0.82,
            "adrenaline": 0.65,
            "dopamine": 0.3,
            "serotonin": 0.4
        },
        "autonomic": {
            "sympathetic": 0.75,
            "parasympathetic": 0.25,
            "heart_rate_index": 1.25
        }
    }

    # Simulate memory matches
    memory_matches = [
        {
            "stream": "emotion",
            "content": "ครั้งที่แล้วเครียดเหมือนกัน จากงานที่ต้องส่งเยอะ",
            "score": 0.89
        },
        {
            "stream": "narrative",
            "content": "เคยบอกว่าจะแบ่งงานเป็นขั้นตอนเล็กๆ",
            "score": 0.76
        }
    ]

    phase_2_ctx = cin.inject_phase_2(
        stimulus_vector=stimulus_vector,
        tags=tags,
        updated_physio=updated_physio,
        memory_matches=memory_matches
    )

    print(f"Context ID: {phase_2_ctx['context_id']}")
    print(f"Embodied Sensation:\n{phase_2_ctx['embodied_sensation']}")
    print(f"\nMemory Streams: {phase_2_ctx['memory_stream_count']}")

    # Build Phase 2 prompt
    phase_2_prompt = cin.build_phase_2_prompt(phase_2_ctx)
    print(f"\nPhase 2 Prompt Length: {len(phase_2_prompt)} chars")
    print(f"First 200 chars:\n{phase_2_prompt[:200]}...")

    print("\n" + "=" * 60)
    print("✅ CIN Test Complete")
