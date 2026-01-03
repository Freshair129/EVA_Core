import sys
import json
import re
import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone

# Add parent to path for MSP imports
base_path = Path(__file__).parent.parent
sys.path.append(str(base_path / "Memory_&_Soul_Passaport"))

class HeptStreamRAG:
    """
    EVA 8.0 Hept-Stream RAG Engine (Episodic-Resonance RAG)
    ระบบ RAG ขั้นสูงที่จำลองการระลึกถึงความจำมนุษย์ผ่าน 7 สายประสาน
    
    Streams:
    - Stream A (Narrative): Parent-Child Retrieval & Event Matching.
    - Stream B (Salience): High impact memories (Resonance Anchors).
    - Stream C (Sensory/Bio): Biological state matching (Emotion Texture).
    - Stream D (Intuitive): Temporal patterns & 9D Matrix Echoes.
    - Stream E (Emotion): Direct Affective Label matching.
    - Stream F (Temporal): Recency-based retrieval with Exponential Decay. [NEW]
    - Stream G (Reflection): Metacognitive summaries & Core beliefs. [NEW]
    """
    
    def __init__(self, msp=None):
        self.msp = msp
        self.base_path = Path(__file__).parent.parent
        self.decay_rate = 0.05 # สำหรับ Temporal Decay
        
    def set_msp(self, msp):
        self.msp = msp

    def search(self, user_input: str, current_state: Dict[str, Any], limit: int = 3) -> Dict[str, Any]:
        """
        Main Entry Point: 3-Step Cognitive Process
        1. Planning: ชั่งน้ำหนักความสำคัญของแต่ละ Stream ตามสภาวะอารมณ์
        2. Execution: ดึงข้อมูลจากทั้ง 7 Streams
        3. Synthesis: วิเคราะห์ความเชื่อมโยง ย่อสรุป และจัดลำดับด้วย Temporal Decay
        """
        if not self.msp:
            print("[RAG-Engine] Warning: MSP not connected. Returning empty results.")
            return {}

        # --- STEP 1: PLANNING ---
        plan = self._generate_search_plan(user_input, current_state)
        
        # --- STEP 2: RETRIEVAL (Hept-Stream) ---
        raw_results = self._execute_streams(user_input, current_state, plan, limit)
        
        # --- STEP 3: REASONING & SYNTHESIS ---
        synthesized = self._cross_stream_reasoning(raw_results, current_state, plan)
        
        # Merge results for Orchestrator/CPNBuilder compatibility
        final_output = {**raw_results, **synthesized}
        return final_output

    def _generate_search_plan(self, user_input: str, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """วิเคราะห์บริบทเพื่อกำหนดค่าน้ำหนักให้แต่ละ Stream (Planning Layer)"""
        weights = {
            "narrative": 1.0, "salience": 1.2, "sensory": 1.0, 
            "intuitive": 1.0, "emotion": 1.0, "temporal": 0.8, "reflection": 1.0
        }
        strategy = "Balanced"

        emotion_state = current_state.get("emotion_state", {})
        arousal = emotion_state.get("arousal", 0.5) if isinstance(emotion_state, dict) else 0.5
        
        # ถ้าอารมณ์พุ่งสูง (High Arousal) ให้เน้นความจำเชิงสัญชาตญาณและร่างกาย
        if arousal > 0.7:
            weights["sensory"] = 2.0
            weights["emotion"] = 1.8
            weights["temporal"] = 1.5 # ความจำสดๆ ร้อนๆ จะมีผลมาก
            weights["narrative"] = 0.6
            strategy = "Affective/Visceral Focus"
        
        # ถ้าผู้ใช้ถามหาเหตุผลหรือรูปแบบ (Pattern Seeking)
        if any(w in user_input.lower() for w in ["again", "always", "pattern", "why", "สรุป"]):
            weights["intuitive"] = 2.5
            weights["reflection"] = 2.0
            strategy = "Cognitive Synthesis"

        return {"weights": weights, "strategy": strategy}

    def _execute_streams(self, user_input: str, current_state: Dict[str, Any], plan: Dict, limit: int) -> Dict[str, List[Dict]]:
        """ประมวลผลทั้ง 7 Streams ตามค่าน้ำหนักที่วางแผนไว้"""
        results = {
            "narrative_match": [], "salience_match": [], "sensory_match": [],
            "intuitive_echo": [], "predictive_bio_pattern": [], "emotion_match": [],
            "temporal_flow": [], "reflection_nodes": []
        }
        w = plan["weights"]

        # ค้นหาตามลำดับความสำคัญ (ในอนาคตสามารถทำเป็น Parallel ได้)
        if w["narrative"] > 0.5: results["narrative_match"] = self._stream_a_narrative(user_input, limit)
        if w["salience"] > 0.5: results["salience_match"] = self._stream_b_salience(user_input, limit)
        if w["sensory"] > 0.5: results["sensory_match"] = self._stream_c_sensory(current_state, limit)
        if w["intuitive"] > 0.5: 
            e, p = self._stream_d_intuitive(current_state, limit)
            results["intuitive_echo"], results["predictive_bio_pattern"] = e, p
        
        if w["emotion"] > 0.5: results["emotion_match"] = self._stream_e_emotion(current_state, limit)
        if w["temporal"] > 0.5: results["temporal_flow"] = self._stream_f_temporal(limit)
        if w["reflection"] > 0.5: results["reflection_nodes"] = self._stream_g_reflection(user_input, limit)
        
        return results

    def _cross_stream_reasoning(self, raw_results: Dict, current_state: Dict, plan: Dict) -> Dict[str, Any]:
        """วิเคราะห์ความเชื่อมโยงข้ามสาย (Cross-stream Intersections) และใช้ Temporal Decay ในการจัดลำดับ"""
        trace = [f"Strategy: {plan['strategy']}"]
        memory_pool = {}
        cached_contexts = {}

        # รวมความจำจากทุกสายยกเว้นสายที่เน้นสถิติ (Patterns)
        streams_to_pool = ["narrative_match", "salience_match", "sensory_match", "emotion_match", "temporal_flow", "reflection_nodes"]
        
        for s_name in streams_to_pool:
            for mem in raw_results[s_name]:
                mid = mem.get("episode_id") or mem.get("id")
                if not mid: continue
                
                # 1. Base Score & Temporal Decay
                t_weight = self._calculate_temporal_weight(mem.get("timestamp", ""))
                score = (1.0 * mem.get("resonance_index", 0.5) * t_weight)
                
                # 2. Context Re-linking
                cid = mem.get("situation_context", {}).get("context_id") or mem.get("context_id")
                if cid and cid not in cached_contexts and hasattr(self.msp, 'get_context'):
                    ctx = self.msp.get_context(cid)
                    if ctx:
                        cached_contexts[cid] = ctx.get("summary")
                        trace.append(f"Context '{cid}' re-linked.")
                        score *= 1.3 # Boost memories in a known work context
                
                if mid not in memory_pool:
                    mem["reasoning_score"] = score
                    mem["found_in"] = [s_name]
                    memory_pool[mid] = mem
                else:
                    # Resonance Effect: ถ้าถูกดึงซ้ำจากหลายสาย ให้คะแนนเพิ่ม
                    memory_pool[mid]["reasoning_score"] += (score * 0.5)
                    memory_pool[mid]["found_in"].append(s_name)

        # จัดลำดับตามคะแนนรวมสุทธิ
        final_candidates = sorted(memory_pool.values(), key=lambda x: x.get("reasoning_score", 0), reverse=True)
        
        return {
            "top_memories": final_candidates[:3],
            "reasoning_trace": trace,
            "cached_contexts": cached_contexts
        }

    def _calculate_temporal_weight(self, entry_timestamp: str) -> float:
        """คำนวณค่าน้ำหนักความสดใหม่ (Exponential Decay)"""
        if not entry_timestamp: return 0.5
        try:
            target_date = datetime.fromisoformat(entry_timestamp.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            days_passed = (now - target_date).days
            days_passed = max(0, days_passed)
            return math.exp(-self.decay_rate * days_passed)
        except: return 0.5

    # --- STREAM IMPLEMENTATIONS ---

    def _stream_a_narrative(self, query: str, limit: int) -> List[Dict]:
        """Stream A: Narrative (Parent-Child & Event Search)"""
        results = []
        # ค้นหาตามชื่อเหตุการณ์/ตอนก่อน
        if hasattr(self.msp, 'query_by_event'):
            results.extend(self.msp.query_by_event(query, limit=limit))
        
        # ถ้าไม่พอ ใช้ข้อความสั้นๆ (Child Chunks) - ถ้า MSP รองรับ
        if len(results) < limit and hasattr(self.msp, 'query_child_chunks'):
            child_matches = self.msp.query_child_chunks(query, limit=limit)
            for c in child_matches:
                p_id = c.get("parent_episode_id")
                if p_id and hasattr(self.msp, 'get_episode_by_id'):
                    parent = self.msp.get_episode_by_id(p_id)
                    if parent: results.append(parent)
        
        # Fallback to tags
        if len(results) < limit and hasattr(self.msp, 'query_by_tags'):
            tags = self._extract_tags(query)
            results.extend(self.msp.query_by_tags(tags, limit=limit - len(results)))
        return results

    def _stream_b_salience(self, query: str, limit: int) -> List[Dict]:
        """Stream B: Salience (High RI)"""
        if hasattr(self.msp, 'query_by_salience'):
             return self.msp.query_by_salience(query, limit=limit)
        return []

    def _stream_c_sensory(self, current_state: Dict[str, Any], limit: int) -> List[Dict]:
        """Stream C: Sensory (Biological State)"""
        emotion_vec = current_state.get("emotion_state", {})
        if not emotion_vec: return []
        if hasattr(self.msp, 'query_by_emotion'):
            return self.msp.query_by_emotion(emotion_vec, threshold=0.7, limit=limit)
        return []

    def _stream_d_intuitive(self, current_state: Dict[str, Any], limit: int) -> Tuple[List, List]:
        """Stream D: Intuitive Echo & Patterns"""
        echoes, patterns = [], []
        matrix_9d = current_state.get("emotion_state", {}) or current_state.get("matrix_state", {})
        
        if matrix_9d and hasattr(self.msp, 'query_by_emotion'):
             echoes = self.msp.query_by_emotion(matrix_9d, threshold=0.8, limit=limit)
             
        history = current_state.get("session_history", [])
        if len(history) >= 2 and hasattr(self.msp, 'query_by_pattern'):
             # Extract labels: [..., p-1, current]
             p_labels = [ep.get("state_snapshot", {}).get("EVA_matrix", {}).get("emotion_label") for ep in history[-3:]]
             p_labels = [p for p in p_labels if p]
             if len(p_labels) >= 2:
                  patterns = self.msp.query_by_pattern(p_labels, limit=limit)
        return echoes, patterns

    def _stream_e_emotion(self, current_state: Dict[str, Any], limit: int) -> List[Dict]:
        """Stream E: Emotion (Label Match)"""
        emotion_state = current_state.get("emotion_state", {})
        if not emotion_state: return []
        label = emotion_state.get("emotion_label")
        if label and hasattr(self.msp, 'query_by_emotion_label'):
             return self.msp.query_by_emotion_label(label, limit=limit)
        if hasattr(self.msp, 'query_by_emotion'):
            return self.msp.query_by_emotion(emotion_state, threshold=0.85, limit=limit)
        return []

    def _stream_f_temporal(self, limit: int) -> List[Dict]:
        """Stream F: Temporal (Recency)"""
        if hasattr(self.msp, 'get_recent_episodes'):
            return self.msp.get_recent_episodes(limit=limit)
        return []

    def _stream_g_reflection(self, query: str, limit: int) -> List[Dict]:
        """Stream G: Reflection (Core Beliefs & Summaries)"""
        if hasattr(self.msp, 'query_reflections'):
            return self.msp.query_reflections(query, limit=limit)
        return []

    def _extract_tags(self, text: str) -> List[str]:
        words = re.sub(r'[^\w\s]', '', text.lower()).split()
        return [w for w in words if len(w) > 3]

# Initialization
if __name__ == "__main__":
    rag = HeptStreamRAG()
    print("EVA 8.0 Hept-Stream RAG Engine Initialized.")