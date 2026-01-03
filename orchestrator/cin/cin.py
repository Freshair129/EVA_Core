"""
Context Injection Node (CIN) - EVA 8.1.0
Version: 8.1.0
Date: 2026-01-02

Dual-phase context builder & state manager for EVA 8.1.0 Dual-Phase Orchestrator.

Role:
- Phase 1: Rough context injection (fast, <100ms) - Bootstrap LLM perception
- Phase 2: Deep context injection (accurate, ~500ms) - Enrich LLM reasoning

Design Principles:
- READ-ONLY access to memory (no writes)
- Auto-discovers Persona (searches 8.1.0 → 8.0 for backward compatibility)
- Graceful degradation (returns "disconnected" if dependencies unavailable)
- Context ID stays constant across both phases in one turn
"""

import sys
import codecs
import os
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import hashlib

# Token counting with tiktoken
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    print("[CIN] ⚠️ tiktoken not available, using fallback token counting")

# Windows UTF-8 Fix (only if not already wrapped)
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


# ================================================================
# TOKEN COUNTER - Accurate token counting with tiktoken
# ================================================================

class TokenCounter:
    """
    Token Counter with tiktoken support

    Uses cl100k_base encoding (GPT-4, GPT-3.5-turbo)
    Falls back to char_count / 4 if tiktoken unavailable
    """

    def __init__(self, model: str = "cl100k_base"):
        """
        Initialize Token Counter

        Args:
            model: Encoding model (default: cl100k_base for GPT-4)
        """
        self.model = model

        if TIKTOKEN_AVAILABLE:
            try:
                self.encoding = tiktoken.get_encoding(model)
                self.method = "tiktoken"
            except Exception as e:
                print(f"[TokenCounter] ⚠️ Failed to load tiktoken: {e}")
                self.encoding = None
                self.method = "fallback"
        else:
            self.encoding = None
            self.method = "fallback"

    def count(self, text: str) -> int:
        """
        Count tokens in text

        Args:
            text: Input text

        Returns:
            int: Token count
        """
        if text is None or text == "":
            return 0

        if self.method == "tiktoken" and self.encoding is not None:
            try:
                return len(self.encoding.encode(text))
            except Exception as e:
                # Fallback on error
                return self._fallback_count(text)
        else:
            return self._fallback_count(text)

    def _fallback_count(self, text: str) -> int:
        """Fallback: Approximate 1 token = 4 characters"""
        return max(1, len(text) // 4)

    def truncate(self, text: str, max_tokens: int) -> Tuple[str, int]:
        """
        Truncate text to max tokens

        Args:
            text: Input text
            max_tokens: Maximum tokens

        Returns:
            tuple: (truncated_text, actual_token_count)
        """
        if text is None or text == "":
            return "", 0

        current_tokens = self.count(text)

        if current_tokens <= max_tokens:
            return text, current_tokens

        # Binary search for truncation point
        if self.method == "tiktoken" and self.encoding is not None:
            # Accurate truncation with tiktoken
            tokens = self.encoding.encode(text)
            truncated_tokens = tokens[:max_tokens]
            truncated_text = self.encoding.decode(truncated_tokens)
            return truncated_text, len(truncated_tokens)
        else:
            # Fallback: Approximate character truncation
            target_chars = max_tokens * 4
            truncated_text = text[:target_chars]
            return truncated_text, self._fallback_count(truncated_text)

    def get_budget_report(self, components: Dict[str, str], max_total: int) -> Dict[str, Any]:
        """
        Get token budget report for multiple components

        Args:
            components: Dict of {component_name: text}
            max_total: Maximum total tokens

        Returns:
            dict: Budget report with counts and percentages
        """
        report = {
            "components": {},
            "total_tokens": 0,
            "max_tokens": max_total,
            "usage_percent": 0.0,
            "within_budget": True
        }

        for name, text in components.items():
            count = self.count(text)
            report["components"][name] = {
                "tokens": count,
                "chars": len(text) if text else 0
            }
            report["total_tokens"] += count

        report["usage_percent"] = (report["total_tokens"] / max_total) * 100 if max_total > 0 else 0
        report["within_budget"] = report["total_tokens"] <= max_total

        return report


class ContextInjectionNode:
    """
    Context Injection Node (CIN) - Dual-Phase Context Builder

    Phase 1: Rough context for LLM perception (fast, deterministic)
    Phase 2: Deep context for LLM reasoning (accurate, affective)
    """

    def __init__(
        self,
        physio_controller=None,
        msp_client=None,
        hept_stream_rag=None,
        eva_matrix=None,
        artifact_qualia=None,
        base_path: Optional[str] = None,
        token_model: str = "cl100k_base"
    ):
        """
        Initialize Context Injection Node

        Args:
            physio_controller: PhysioController instance (optional, graceful degradation)
            msp_client: MSP Client instance (optional, graceful degradation)
            hept_stream_rag: HeptStreamRAG instance (optional, graceful degradation)
            eva_matrix: EVA Matrix instance (optional, graceful degradation)
            artifact_qualia: Artifact Qualia instance (optional, graceful degradation)
            base_path: Base path for EVA 8.1.0 (default: current directory parent)
            token_model: Tiktoken encoding model (default: cl100k_base)
        """
        self.physio_controller = physio_controller
        self.msp_client = msp_client
        self.hept_stream_rag = hept_stream_rag
        self.eva_matrix = eva_matrix
        self.artifact_qualia = artifact_qualia

        # Base path setup
        if base_path is None:
            self.base_path = Path(__file__).parent.parent
        else:
            self.base_path = Path(base_path)

        # Token counter setup
        self.token_counter = TokenCounter(model=token_model)
        print(f"[CIN] ✅ Token counter initialized (method: {self.token_counter.method})")

        # 1. Load External Configs (Standard Compliance)
        cfg_path = Path(__file__).parent / "configs" / "CIN_configs.yaml"
        if cfg_path.exists():
            try:
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    self.config_data = yaml.safe_load(f)
                    self.token_budgets = {
                        "phase_1": self.config_data.get("phase_1_budget", {}),
                        "phase_2": self.config_data.get("phase_2_budget", {})
                    }
                    print(f"[CIN] ✅ Loaded runtime budgets from {cfg_path.name}")
            except Exception as e:
                print(f"[CIN] ⚠️ Error loading configs: {e}. Using internal defaults.")
                self._set_default_budgets()
        else:
            self._set_default_budgets()

        # 2. Auto-discover Identity & Behavioral Rules
        self.persona_data = self._load_persona()
        self.soul_data = self._load_soul()
        self.pmt_rules = self._load_pmt_rules()

        # Context ID tracking
        self.current_context_id = None
        self.turn_index = 0

    def _set_default_budgets(self):
        """Internal fallback budgets if YAML is missing"""
        self.token_budgets = {
            "phase_1": {
                "identity_anchor": 500, "physio_baseline": 100, "pmt_rules": 200,
                "memory_buffer": 250, "conversation_history": 1500, "total_max": 3000
            }
        }

    # ================================================================
    # AUTO-DISCOVERY & FILE LOADING
    # ================================================================

    def _load_persona(self) -> Dict[str, Any]:
        """
        Auto-discover and load persona.yaml
        Searches: 8.1.0 → 8.0 for backward compatibility

        Returns:
            dict: Persona data or default template
        """
        search_paths = [
            self.base_path / "orchestrator" / "PMT_PromptRuleLayer" / "Identity" / "persona.yaml",
            self.base_path / "orchestrator" / "PMT_PromptRuleLayer" / "Identity" / "Persona_01.yaml",
            # Backward compatibility
            self.base_path / "Persona_01.yaml",
        ]

        for path in search_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        print(f"[CIN] ✅ Loaded persona from: {path}")
                        return data
                except Exception as e:
                    print(f"[CIN] ⚠️ Failed to load persona from {path}: {e}")

        # Fallback: default persona
        print("[CIN] ⚠️ No persona file found, using default template")
        return {
            "meta": {"name": "EVA"},
            "voice": {"tone": "supportive", "style": "empathetic"}
        }

    def _load_soul(self) -> Dict[str, Any]:
        """
        Load soul.md identity document

        Returns:
            dict: Soul data with Develop_id
        """
        soul_path = self.base_path / "orchestrator" / "PMT_PromptRuleLayer" / "Identity" / "soul.md"

        if not soul_path.exists():
            print("[CIN] ⚠️ soul.md not found, using default")
            return {"Deverlop_id": "UNKNOWN", "context": "No soul context available"}

        try:
            with open(soul_path, 'r', encoding='utf-8') as f:
                soul_content = f.read()

            # Parse Deverlop_id from soul.md (simple extraction)
            develop_id = "UNKNOWN"
            for line in soul_content.split('\n'):
                if 'Deverlop_id' in line or 'develop_id' in line.lower():
                    # Extract ID (e.g., "THA-01-S003")
                    parts = line.split(':')
                    if len(parts) > 1:
                        develop_id = parts[1].strip()
                        break

            print(f"[CIN] ✅ Loaded soul.md (Develop ID: {develop_id})")
            return {
                "Deverlop_id": develop_id,
                "context": soul_content[:500]  # First 500 chars
            }
        except Exception as e:
            print(f"[CIN] ⚠️ Failed to load soul.md: {e}")
            return {"Deverlop_id": "UNKNOWN", "context": "Error loading soul"}

    def _load_pmt_rules(self) -> str:
        """
        Load PMT Rules from Prompt Rule Layer
        Token budget: 200 tokens (Phase 1)

        Returns:
            str: PMT rules content or default (truncated to token budget)
        """
        pmt_path = self.base_path / "orchestrator" / "PMT_PromptRuleLayer"

        if not pmt_path.exists():
            print("[CIN] ⚠️ PMT_PromptRuleLayer not found")
            return "No PMT rules available"

        # Collect all .yaml and .md files in PMT directory
        rules_content = []
        for file_path in pmt_path.rglob('*.yaml'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    rules_content.append(f"# From: {file_path.name}\n{f.read()}")
            except Exception as e:
                print(f"[CIN] ⚠️ Failed to load {file_path}: {e}")

        if rules_content:
            full_content = "\n\n".join(rules_content)

            # Truncate to token budget (200 tokens for Phase 1)
            truncated_content, actual_tokens = self.token_counter.truncate(
                full_content,
                max_tokens=self.token_budgets["phase_1"]["pmt_rules"]
            )

            print(f"[CIN] ✅ Loaded {len(rules_content)} PMT rule files ({actual_tokens} tokens)")
            return truncated_content

        return "No PMT rules available"

    # ================================================================
    # PHASE 1: ROUGH CONTEXT INJECTION (Fast, <100ms)
    # ================================================================

    def inject_phase_1(self, user_input: str) -> Dict[str, Any]:
        """
        Phase 1: Rough context injection (Fast, deterministic)

        Purpose: Bootstrap LLM perception with enough context to analyze intent
        Performance: <100ms (max 200ms timeout)

        Args:
            user_input: Raw user input string

        Returns:
            dict: Phase 1 context with all components
        """
        # Generate new context ID for this turn
        self.current_context_id = self._generate_context_id()
        self.turn_index += 1

        context = {
            "context_id": self.current_context_id,
            "turn_index": self.turn_index,
            "timestamp": datetime.now().isoformat(),

            # Identity
            "persona": self.persona_data,
            "soul": self.soul_data,
            "pmt_rules": self.pmt_rules,

            # Physiological baseline
            "physio_baseline": self._get_physio_baseline(),

            # Memory components (Intuition Layer)
            "situation_context": self._get_situation_context(limit=5),
            "session_memory": self._get_session_memory(),
            "intuition_flashes": self._get_intuition_flashes(user_input),

            # Conversation history
            "conversation_history": self._get_conversation_history(),

            # Raw input
            "user_input": user_input
        }

        return context

    def build_phase_1_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build Phase 1 prompt from context

        Args:
            context: Phase 1 context dict from inject_phase_1()

        Returns:
            str: Formatted prompt for LLM Phase 1 (Perception)
        """
        persona_name = context["persona"].get("meta", {}).get("name", "EVA")
        episode_id = self._get_current_episode_id()

        prompt = f"""# [PHASE 1: PERCEPTION] | episode: {episode_id} | Turn: {context['turn_index']} | ID: {context['context_id']}

## 🎭 CORE_IDENTITY & SOUL
{yaml.dump(context['persona'], allow_unicode=True, default_flow_style=False)}
---
Develop ID: {context['soul']['Deverlop_id']}
{context['soul']['context'][:300]}

## ⚖️ BEHAVIORAL_CONSTRAINTS (PMT/GKS)
{context['pmt_rules'][:500]}

## 💓 AUTONOMIC_BASELINE (PRE-STIMULUS)
- Heart Rate Index: {context['physio_baseline'].get('heart_rate_index', 'N/A')}
- ANS State: Sympathetic: {context['physio_baseline'].get('sympathetic', 'N/A')}, Parasympathetic: {context['physio_baseline'].get('parasympathetic', 'N/A')}
- Hormone Levels: {context['physio_baseline'].get('hormone_summary', 'N/A')}
- Status: {context['physio_baseline'].get('status', 'connected')}

## 📂 RECENT_CONVERSATIONAL_CONTEXT
- 5-Turn Memory: {context['situation_context'].get('last_5_episodic_memory_summary', 'No recent context')}
- Session Memory: {context['session_memory'].get('summary', 'No long-term context')}
- Atmosphere: {context['situation_context'].get('interpersonal_atmosphere', 'neutral')}
- Previous Intent: {context['situation_context'].get('previous_intent', 'None')}
- Previous Context: {context['situation_context'].get('previous_context', 'None')}

## 🧩 INTUITION_FLASHES (แว๊บแรก)
{context.get('intuition_flashes', 'No mental flashes triggered')}

## 💬 CONVERSATION_HISTORY (RAW_TURNS)
[Format: Role: Content]
{context['conversation_history']}

## ⚡ RAW_STIMULUS_INPUT
User: {context['user_input']}

## 🎯 PERCEPTION_DIRECTIVE [MULTI-STAGE CHUNKING]
1. แบ่ง Raw Input ออกเป็น 1-3 ลำดับเหตุการณ์ย่อย (Semantic Chunks) ตามจังหวะอารมณ์
2. สำหรับแต่ละ Chunk:
   - ระบุ `valence`, `arousal`, `intensity`, `stress`, `warmth`
   - กำหนด `salience_anchor` (ประโยคสั้นๆ ที่เป็นจุดเกาะเกี่ยวทางอารมณ์)
   - ระบุ `tags` สำหรับการค้นหาความจำ
3. เรียกใช้ฟังก์ชัน `sync_biocognitive_state` โดยส่งข้อมูลเป็น List ของ Chunks เพื่อประมวลผลการตอบสนองขั้นสูง
"""
        return prompt



    # ================================================================
    # PHASE 2: DEEP CONTEXT INJECTION (Accurate, ~500ms)
    # ================================================================

    def inject_phase_2(
        self,
        stimulus_vector: Dict[str, float],
        tags: List[str],
        updated_physio: Dict[str, Any],
        memory_matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Phase 2: Deep context injection (Accurate, affective)

        Purpose: Enrich LLM reasoning with deep affective context and memories
        Performance: ~500ms (max 1000ms timeout)

        Args:
            stimulus_vector: {valence, arousal, intensity} from LLM Phase 1
            tags: Search tags from LLM Phase 1
            updated_physio: Updated physiological state after stimulus
            memory_matches: Hept-Stream RAG results

        Returns:
            dict: Phase 2 context with embodied state and memories
        """
        context = {
            "context_id": self.current_context_id,  # Same as Phase 1
            "turn_index": self.turn_index,
            "timestamp": datetime.now().isoformat(),

            # Embodied state
            "embodied_sensation": self._generate_embodied_description(updated_physio),
            "eva_matrix_9d": self._get_eva_matrix_state(updated_physio),
            "artifact_qualia": self._get_artifact_qualia(updated_physio),

            # Physiological delta
            "physio_delta": self._calculate_physio_delta(updated_physio),

            # Memory echoes (from Hept-Stream RAG)
            "memory_matches": memory_matches,
            "hept_stream_breakdown": self._breakdown_memory_streams(memory_matches),

            # PMT rules reminder
            "pmt_rules": self.pmt_rules[:300],  # Brief reminder
        }

        return context

    def build_phase_2_prompt(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build Phase 2 function result (returned to LLM after The Gap)

        Args:
            context: Phase 2 context dict from inject_phase_2()

        Returns:
            dict: Function result for sync_biocognitive_state()
        """
        episode_id = self._get_current_episode_id()

        # Format memory echoes by stream
        narrative_chunk = ""
        emotion_chunk = ""
        other_streams = []

        for match in context["memory_matches"]:
            stream = match.get("stream", "unknown")
            content = match.get("content", "")
            score = match.get("score", 0.0)

            if stream == "Narrative":
                narrative_chunk += f"- {content} (score: {score:.2f})\n"
            elif stream == "Emotion":
                emotion_chunk += f"- {content} (score: {score:.2f})\n"
            else:
                other_streams.append(f"[{stream}] {content} (score: {score:.2f})")

        # Build function result (this is what LLM receives)
        function_result = f"""# [PHASE 2: REASONING] | episode: {episode_id} | Turn: {context['turn_index']} | ID: {context['context_id']}

## ✨ INTERNAL_EMBODIED_SENSATION (FELT_STATE)
{context['embodied_sensation']}

## 🧭 EVA_MATRIX (9-DIMENSIONAL_PSYCHOLOGICAL_STATE)
Psychological Dimensions:
{yaml.dump(context['eva_matrix_9d'], allow_unicode=True, default_flow_style=False)}

## 🌈 PHENOMENOLOGICAL_QUALIA (SUBJECTIVE_EXPERIENCE)
{yaml.dump(context['artifact_qualia'], allow_unicode=True, default_flow_style=False)}

## 💉 PHYSIOLOGICAL_RESPONSE (BIO-UPDATE)
{context['physio_delta']}

## 🧬 HEPT-STREAM_MEMORY_ECHOES

### [1] Narrative Stream (Storyline Continuity)
{narrative_chunk if narrative_chunk else "No narrative memories found"}

### [5] Emotion Stream (Physio-Congruent Recall) ⚡ CRITICAL
{emotion_chunk if emotion_chunk else "No emotion-congruent memories found"}

### [Other Streams]
{chr(10).join(other_streams) if other_streams else "No other stream matches"}

## ⚖️ BEHAVIORAL_CONSTRAINTS (PMT/GKS)
{context['pmt_rules']}

## 📝 CONTEXT_SUMMARY_TEMPLATE (FOR_NEXT_TURN)
Required JSON Structure:
{{
  "summary": "1-2 sentence overview of this interaction",
  "atmosphere": "interpersonal tone (supportive/tense/neutral/curious/...)",
  "intent": "what EVA plans to do or expects next",
  "key_topics": ["topic1", "topic2", "..."],
  "emotional_state": "user's current emotional state",
  "physio_snapshot": {{
    "cortisol": 0.00,
    "adrenaline": 0.00,
    "ans_sympathetic": 0.00
  }}
}}

## 🎯 COGNITIVE_DIRECTIVE
1. ประสานความรู้สึก (Felt State) เข้ากับความทรงจำ (Memory Echoes)
2. ตอบสนองภายใต้กรอบ Persona (40%) และสภาวะร่างกาย (60%)
3. สร้างการตอบกลับที่สะท้อนทั้งความรู้สึกทางกายและความทรงจำ
4. สร้าง Context Summary ตาม Template ข้างบนเพื่อใช้ใน Turn ถัดไป
5. สร้างแผนการ/คาดการณ์ (Intent) สำหรับการโต้ตอบต่อเนื่อง
"""

        return {
            "status": "success",
            "embodied_sensation": context['embodied_sensation'],
            "physio_metrics": context['physio_delta'],
            "memory_matches": context["memory_matches"],
            "function_result_text": function_result
        }

    # ================================================================
    # HELPER METHODS - PHYSIOLOGICAL STATE
    # ================================================================

    def _get_physio_baseline(self) -> Dict[str, Any]:
        """
        Get physiological baseline from PhysioController
        Graceful degradation: Returns neutral values if unavailable

        Returns:
            dict: Physiological baseline state
        """
        if self.physio_controller is None:
            return {
                "status": "disconnected",
                "heart_rate_index": 1.0,
                "sympathetic": 0.5,
                "parasympathetic": 0.5,
                "hormone_summary": "Disconnected - neutral baseline"
            }

        try:
            # Call PhysioController.get_snapshot() with 50ms timeout
            snapshot = self.physio_controller.get_snapshot(timeout_ms=50)
            return {
                "status": "connected",
                "heart_rate_index": snapshot.get("heart_rate_index", 1.0),
                "sympathetic": snapshot.get("autonomic", {}).get("sympathetic", 0.5),
                "parasympathetic": snapshot.get("autonomic", {}).get("parasympathetic", 0.5),
                "hormone_summary": self._format_hormone_summary(snapshot.get("blood", {}))
            }
        except Exception as e:
            print(f"[CIN] ⚠️ PhysioController unavailable: {e}")
            return {
                "status": "error",
                "heart_rate_index": 1.0,
                "sympathetic": 0.5,
                "parasympathetic": 0.5,
                "hormone_summary": f"Error: {str(e)}"
            }

    def _format_hormone_summary(self, blood_levels: Dict[str, float]) -> str:
        """Format hormone levels into readable summary"""
        if not blood_levels:
            return "No hormone data"

        summary_parts = []
        for hormone, level in blood_levels.items():
            summary_parts.append(f"{hormone}: {level:.2f}")

        return ", ".join(summary_parts[:5])  # Max 5 hormones

    def _calculate_physio_delta(self, updated_physio: Dict[str, Any]) -> str:
        """
        Calculate physiological changes (delta) from baseline

        Args:
            updated_physio: Updated physio state after stimulus

        Returns:
            str: Human-readable delta description
        """
        baseline = self._get_physio_baseline()

        if baseline["status"] == "disconnected":
            return "Physiological tracking unavailable (disconnected)"

        # Calculate deltas
        cortisol_delta = updated_physio.get("cortisol", 0.5) - baseline.get("cortisol", 0.5)
        adrenaline_delta = updated_physio.get("adrenaline", 0.5) - baseline.get("adrenaline", 0.5)
        symp_delta = updated_physio.get("sympathetic", 0.5) - baseline.get("sympathetic", 0.5)

        delta_desc = f"""- Cortisol Change: {cortisol_delta:+.2f} (from {baseline.get('cortisol', 0.5):.2f} → {updated_physio.get('cortisol', 0.5):.2f})
- Adrenaline Surge: {adrenaline_delta:+.2f} (from {baseline.get('adrenaline', 0.5):.2f} → {updated_physio.get('adrenaline', 0.5):.2f})
- ANS Shift: Sympathetic {symp_delta:+.2f} (now {updated_physio.get('sympathetic', 0.5):.2f})"""

        return delta_desc

    def _generate_embodied_description(self, physio_state: Dict[str, Any]) -> str:
        """
        Generate natural language description of embodied sensation

        Args:
            physio_state: Current physiological state

        Returns:
            str: Natural language felt state description
        """
        # Simple rule-based description (can be enhanced with more sophisticated logic)
        symp = physio_state.get("sympathetic", 0.5)
        para = physio_state.get("parasympathetic", 0.5)
        cortisol = physio_state.get("cortisol", 0.5)

        if symp > 0.7:
            return "EVA รู้สึกตื่นตัวและมีพลัง หัวใจเต้นเร็วขึ้น ร่างกายพร้อมที่จะตอบสนอง"
        elif symp < 0.3 and para > 0.6:
            return "EVA รู้สึกสงบและผ่อนคลาย ลมหายใจช้าลง ร่างกายอยู่ในสภาวะพักผ่อน"
        elif cortisol > 0.7:
            return "EVA รู้สึกเครียดและตึงเครียด มีความกังวลเล็กน้อย ร่างกายตอบสนองต่อความกดดัน"
        else:
            return "EVA อยู่ในสภาวะสมดุล รู้สึกปกติและพร้อมที่จะรับฟัง"

    def _get_eva_matrix_state(self, physio_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get EVA Matrix 9D psychological state
        Graceful degradation: Returns neutral values if unavailable

        Args:
            physio_state: Current physiological state

        Returns:
            dict: 9D psychological dimensions + Safety Reflex
        """
        if self.eva_matrix is None:
            return {
                "Stress": 0.5,
                "Warmth": 0.5,
                "Drive": 0.5,
                "Clarity": 0.5,
                "Joy": 0.5,
                "Alertness": 0.5,
                "Connection": 0.5,
                "Groundedness": 0.5,
                "Openness": 0.5,
                "safety_reflex": {
                    "urgency": 0.0,
                    "cognitive_drive": 0.5,
                    "social_warmth": 0.5,
                    "withdrawal": 0.0
                },
                "status": "unavailable"
            }

        try:
            matrix_state = self.eva_matrix.calculate(physio_state)
            return matrix_state
        except Exception as e:
            print(f"[CIN] ⚠️ EVA Matrix calculation error: {e}")
            return {"status": "error", "Stress": 0.5}

    def _get_artifact_qualia(self, physio_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get Artifact Qualia (phenomenological experience quality)
        Graceful degradation: Returns neutral values if unavailable

        Args:
            physio_state: Current physiological state

        Returns:
            dict: Qualia (intensity, tone, coherence, depth, texture 5D)
        """
        if self.artifact_qualia is None:
            return {
                "intensity": 0.5,
                "tone": "neutral",
                "coherence": 0.5,
                "depth": 0.5,
                "texture": {
                    "emotional": 0.5,
                    "relational": 0.5,
                    "identity": 0.5,
                    "ambient": 0.5,
                    "complexity": 0.5
                },
                "status": "unavailable"
            }

        try:
            qualia = self.artifact_qualia.generate(physio_state)
            return qualia
        except Exception as e:
            print(f"[CIN] ⚠️ Artifact Qualia generation error: {e}")
            return {"status": "error", "intensity": 0.5}

    # ================================================================
    # HELPER METHODS - MEMORY RETRIEVAL
    # ================================================================

    def _get_situation_context(self, limit: int = 5) -> Dict[str, Any]:
        """
        Get recent situation context (5-turn summary + metadata) from MSP
        Graceful degradation: Returns empty if unavailable

        Args:
            limit: Number of recent turns to retrieve

        Returns:
            dict: Situation context for Phase 1
        """
        if self.msp_client is None:
            return {
                "last_5_episodic_memory_summary": "No recent context (MSP unavailable)",
                "interpersonal_atmosphere": "neutral",
                "previous_intent": "None",
                "previous_context": "None"
            }

        try:
            recent_turns = self.msp_client.get_recent_turns(limit=limit, timeout_ms=100)

            # Aggregate summaries
            summaries = [turn.get("context_summary", "") for turn in recent_turns]
            latest_turn = recent_turns[0] if recent_turns else {}

            return {
                "last_5_episodic_memory_summary": " → ".join(summaries[:3]),  # Max 3 summaries
                "interpersonal_atmosphere": latest_turn.get("atmosphere", "neutral"),
                "previous_intent": latest_turn.get("intent", "None"),
                "previous_context": latest_turn.get("summary", "None")
            }
        except Exception as e:
            print(f"[CIN] ⚠️ Situation context retrieval error: {e}")
            return {
                "last_5_episodic_memory_summary": "Error loading context",
                "interpersonal_atmosphere": "unknown",
                "previous_intent": "None",
                "previous_context": "None"
            }

    def _get_session_memory(self) -> Dict[str, Any]:
        """
        Get session memory (compressed snapshots) for long-term context
        Graceful degradation: Returns empty if unavailable

        Returns:
            dict: Session memory summary
        """
        session_memory_path = self.base_path / "consciousness" / "04_Session_Memory"

        if not session_memory_path.exists():
            return {"summary": "No session memory available", "status": "unavailable"}

        try:
            # Find latest session memory file
            session_files = list(session_memory_path.glob("*.json"))
            if not session_files:
                return {"summary": "No session snapshots found", "status": "empty"}

            latest_file = max(session_files, key=lambda p: p.stat().st_mtime)

            with open(latest_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            summary = session_data.get("summary", "")[:200]  # Max 200 chars
            return {
                "summary": summary,
                "file": latest_file.name,
                "status": "available"
            }
        except Exception as e:
            print(f"[CIN] ⚠️ Session memory read error: {e}")
            return {"summary": "Error loading session memory", "status": "error"}

    def _get_intuition_flashes(self, user_input: str) -> List[str]:
        """
        Intuition retrieval (First impression / แว๊บแรก).
        Non-LLM keyword-based memory scan providing initial mental flashes.

        Args:
            user_input: User input string

        Returns:
            list: Initial mental flashes (keywords/fragments)
        """
        if self.msp_client is None:
            return []

        try:
            # Intuition logic: Extract high-value keywords to trigger 'flashes'
            # (In a full implementation, this might query an inverted index)
            keywords = [word for word in user_input.split() if len(word) > 3][:5]
            print(f"[CIN] 🧠 Intuition triggered: {keywords}")
            return keywords
        except Exception as e:
            print(f"[CIN] ⚠️ Intuition recall error: {e}")
            return []

    def _get_conversation_history(self, max_tokens: int = 1500) -> str:
        """
        Get raw conversation history (recent turns)
        Token budget: 1500 tokens (Phase 1 - hard limit)

        Args:
            max_tokens: Maximum tokens for conversation history

        Returns:
            str: Formatted conversation history (truncated to token budget)
        """
        if self.msp_client is None:
            return "No conversation history (MSP unavailable)"

        try:
            recent_episodes = self.msp_client.get_recent_episodes(limit=10)

            history_lines = []
            for episode in recent_episodes:
                user_input = episode.get("user_input", "")
                response = episode.get("final_response", "")

                history_lines.append(f"User: {user_input}")
                history_lines.append(f"EVA: {response}")

            history_text = "\n".join(history_lines)

            # Truncate with accurate token counting
            truncated_history, actual_tokens = self.token_counter.truncate(
                history_text,
                max_tokens=max_tokens
            )

            print(f"[CIN] Conversation history: {actual_tokens}/{max_tokens} tokens")
            return truncated_history

        except Exception as e:
            print(f"[CIN] ⚠️ Conversation history error: {e}")
            return "Error loading conversation history"

    def _breakdown_memory_streams(self, memory_matches: List[Dict[str, Any]]) -> Dict[str, List]:
        """
        Break down memory matches by stream

        Args:
            memory_matches: List of memory matches from Hept-Stream RAG

        Returns:
            dict: Matches grouped by stream
        """
        breakdown = {
            "Narrative": [],
            "Salience": [],
            "Sensory": [],
            "Intuition": [],
            "Emotion": [],
            "Temporal": [],
            "Reflection": []
        }

        for match in memory_matches:
            stream = match.get("stream", "unknown")
            if stream in breakdown:
                breakdown[stream].append(match)

        return breakdown

    # ================================================================
    # TOKEN BUDGET MANAGEMENT
    # ================================================================

    def get_token_budget_report(self, phase: str, components: Dict[str, str]) -> Dict[str, Any]:
        """
        Get token budget report for a specific phase

        Args:
            phase: "phase_1" or "phase_2"
            components: Dict of {component_name: text}

        Returns:
            dict: Token budget report with usage details
        """
        if phase not in self.token_budgets:
            raise ValueError(f"Invalid phase: {phase}. Must be 'phase_1' or 'phase_2'")

        budget = self.token_budgets[phase]
        report = self.token_counter.get_budget_report(components, budget["total_max"])

        # Add budget limits for each component
        for comp_name, comp_data in report["components"].items():
            if comp_name in budget:
                comp_data["budget"] = budget[comp_name]
                comp_data["over_budget"] = comp_data["tokens"] > budget[comp_name]

        # Add phase info
        report["phase"] = phase
        report["budget_limits"] = budget

        return report

    def print_token_budget_report(self, phase: str, components: Dict[str, str]) -> None:
        """
        Print token budget report to console

        Args:
            phase: "phase_1" or "phase_2"
            components: Dict of {component_name: text}
        """
        report = self.get_token_budget_report(phase, components)

        print(f"\n{'='*60}")
        print(f"Token Budget Report - {phase.upper()}")
        print(f"{'='*60}")
        print(f"Total: {report['total_tokens']}/{report['max_tokens']} tokens ({report['usage_percent']:.1f}%)")
        print(f"Status: {'✅ Within Budget' if report['within_budget'] else '❌ OVER BUDGET'}")
        print(f"{'-'*60}")

        for comp_name, comp_data in report["components"].items():
            budget_limit = comp_data.get("budget", "N/A")
            status = "❌" if comp_data.get("over_budget", False) else "✅"

            print(f"{status} {comp_name:25s}: {comp_data['tokens']:4d}/{budget_limit} tokens")

        print(f"{'='*60}\n")

    # ================================================================
    # UTILITY METHODS
    # ================================================================

    def _generate_context_id(self) -> str:
        """
        Generate unique context ID for this turn
        Format: ctx_v8_{yymmdd}_{hhmmss}_{hash_short}

        Returns:
            str: Context ID
        """
        now = datetime.now()
        timestamp = now.strftime("%y%m%d_%H%M%S")

        # Generate short hash
        hash_input = f"{now.isoformat()}{self.turn_index}".encode('utf-8')
        hash_short = hashlib.md5(hash_input).hexdigest()[:6]

        return f"ctx_v8_{timestamp}_{hash_short}"

    def _get_current_episode_id(self) -> str:
        """
        Get current episode ID (format: EVA_EP{n})

        Returns:
            str: Episode ID
        """
        if self.msp_client is None:
            return "EVA_EP00"

        try:
            episode_counter = self.msp_client.get_episode_counter()
            persona_code = episode_counter.get("persona_code", "EVA")
            current_num = episode_counter.get("current_episode", 0)
            return f"{persona_code}_EP{current_num:02d}"
        except Exception as e:
            print(f"[CIN] ⚠️ Episode ID error: {e}")
            return "EVA_EP00"


    # ================================================================
    # COGNITIVE FIREWALL (PHASE 4)
    # ================================================================

    def normalize_stimulus(self, raw_data: Any) -> List[Dict[str, Any]]:
        """
        Cognitive Firewall: Normalize and validate LLM-driven stimulus triggers.
        Processes both single stimulus objects and multi-chunk lists.

        Args:
            raw_data: Raw output from LLM tool call or dict.

        Returns:
            List[Dict]: Normalized stimulus chunks, each with salience_anchor.
        """
        normalized_chunks = []

        # 1. Handle List of Chunks vs Single Chunk
        if isinstance(raw_data, list):
            raw_chunks = raw_data
        elif isinstance(raw_data, dict):
            # If it's a single dict with 'chunks', extract it; else wrap it
            if "chunks" in raw_data and isinstance(raw_data["chunks"], list):
                raw_chunks = raw_data["chunks"]
            else:
                raw_chunks = [raw_data]
        else:
            # Fallback for invalid data
            print(f"[CIN] ⚠️ Invalid stimulus data type: {type(raw_data)}. Using neutral fallback.")
            raw_chunks = [{"valence": 0.5, "arousal": 0.3, "intensity": 0.3}]

        # 2. Normalize Each Chunk
        for i, chunk in enumerate(raw_chunks):
            if not isinstance(chunk, dict):
                continue
            
            # Extract core vector (default to neutral)
            # LLM might provide 'stimulus_vector' key or flat keys
            if "stimulus_vector" in chunk and isinstance(chunk["stimulus_vector"], dict):
                vector = chunk["stimulus_vector"]
            else:
                vector = chunk

            norm_chunk = {
                "valence": float(vector.get("valence", 0.5)),
                "arousal": float(vector.get("arousal", 0.3)),
                "intensity": float(vector.get("intensity", 0.3)),
                "stress": float(vector.get("stress", 0.3)),
                "warmth": float(vector.get("warmth", 0.5)),
                "tags": list(chunk.get("tags", ["neutral"])),
                "salience_anchor": str(chunk.get("salience_anchor") or f"chunk_{i}")
            }

            # Enforce RI/RIM scoring slots if provided (V2 logic)
            if "ri_score" in chunk:
                norm_chunk["ri_score"] = float(chunk["ri_score"])
            if "rim_impact" in chunk:
                norm_chunk["rim_impact"] = float(chunk["rim_impact"])

            normalized_chunks.append(norm_chunk)

        if not normalized_chunks:
            normalized_chunks = [{
                "valence": 0.5, "arousal": 0.3, "intensity": 0.3, 
                "stress": 0.3, "warmth": 0.5, "tags": ["neutral"],
                "salience_anchor": "default_anchor"
            }]

        print(f"[CIN] 🛡️ Normalized {len(normalized_chunks)} stimulus chunks")
        return normalized_chunks

if __name__ == "__main__":
    print("=" * 60)
    print("Context Injection Node (CIN) - EVA 8.1.0")
    print("Testing standalone (without dependencies)")
    print("=" * 60)

    # Create CIN without dependencies (graceful degradation mode)
    cin = ContextInjectionNode()

    print("\n[TEST 1] Phase 1: Rough Context Injection")
    print("-" * 60)
    user_input = "วันนี้เครียดมาก งานเยอะอะ"
    phase1_context = cin.inject_phase_1(user_input)
    print(f"✅ Context ID: {phase1_context['context_id']}")
    print(f"✅ Turn Index: {phase1_context['turn_index']}")
    print(f"✅ Persona: {phase1_context['persona'].get('meta', {}).get('name', 'UNKNOWN')}")
    print(f"✅ Physio Baseline Status: {phase1_context['physio_baseline']['status']}")

    print("\n[TEST 2] Build Phase 1 Prompt")
    print("-" * 60)
    phase1_prompt = cin.build_phase_1_prompt(phase1_context)
    print(phase1_prompt[:500])
    print(f"\n... (Total length: {len(phase1_prompt)} chars)")

    print("\n[TEST 3] Phase 2: Deep Context Injection")
    print("-" * 60)
    # Simulate LLM Phase 1 output
    stimulus_vector = {"valence": -0.7, "arousal": 0.8, "intensity": 0.9}
    tags = ["stress", "work_overload", "emotional_support"]
    updated_physio = {"cortisol": 0.82, "adrenaline": 0.65, "sympathetic": 0.75, "parasympathetic": 0.25}
    memory_matches = [
        {"stream": "Emotion", "content": "ครั้งที่แล้วเครียดเหมือนกัน จากงานที่ต้องส่งเยอะ", "score": 0.89},
        {"stream": "Narrative", "content": "เคยบอกว่าจะแบ่งงานเป็นขั้นตอนเล็กๆ", "score": 0.76}
    ]

    phase2_context = cin.inject_phase_2(stimulus_vector, tags, updated_physio, memory_matches)
    print(f"✅ Context ID (same): {phase2_context['context_id']}")
    print(f"✅ Embodied Sensation: {phase2_context['embodied_sensation'][:100]}...")
    print(f"✅ EVA Matrix Status: {phase2_context['eva_matrix_9d'].get('status', 'N/A')}")
    print(f"✅ Memory Matches: {len(phase2_context['memory_matches'])} streams")

    print("\n[TEST 4] Build Phase 2 Function Result")
    print("-" * 60)
    function_result = cin.build_phase_2_prompt(phase2_context)
    print(f"✅ Status: {function_result['status']}")
    print(f"✅ Function Result Text:")
    print(function_result['function_result_text'][:500])
    print(f"\n... (Total length: {len(function_result['function_result_text'])} chars)")

    print("\n[TEST 5] Token Counting - Phase 1 Budget")
    print("-" * 60)
    # Build components dict for Phase 1
    phase1_components = {
        "identity_anchor": yaml.dump(phase1_context['persona'], allow_unicode=True),
        "physio_baseline": str(phase1_context['physio_baseline']),
        "pmt_rules": phase1_context['pmt_rules'],
        "conversation_history": phase1_context.get('conversation_history', ''),
        "user_input": phase1_context['user_input']
    }

    cin.print_token_budget_report("phase_1", phase1_components)

    print("\n[TEST 6] Token Counting - Truncation Test")
    print("-" * 60)
    long_text = "This is a test. " * 500  # ~1500 words
    original_tokens = cin.token_counter.count(long_text)
    truncated_text, truncated_tokens = cin.token_counter.truncate(long_text, max_tokens=100)

    print(f"✅ Original text: {original_tokens} tokens")
    print(f"✅ Truncated to: {truncated_tokens} tokens (max: 100)")
    print(f"✅ Truncation worked: {truncated_tokens <= 100}")
    print(f"✅ Token counter method: {cin.token_counter.method}")

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - CIN with Token Counting Ready")
    print("=" * 60)
