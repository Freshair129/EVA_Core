"""
Agentic-RAG (Embodied Affective Retrieval System)
Version: 8.1.0
Date: 2025-12-31

The Agentic-RAG implements 7-dimensional memory retrieval for affective,
emotion-congruent recall. It queries memories across multiple dimensions to find
episodes that match the current embodied state.

The 7 Streams:
    ① Narrative Stream - Sequential episode chains (storylines)
    ② Salience Stream - High-impact, unforgettable memories (RI-weighted)
    ③ Sensory Stream - Sensory-rich memories (qualia texture vectors)
    ④ Intuition Stream - Pattern recognition (semantic graph structures)
    ⑤ Emotion Stream - Emotion-congruent memories (ANS State matching) **[KEY]**
    ⑥ Temporal Stream - Time-based context (recent vs distant)
    ⑦ Reflection Stream - Meta-cognitive insights (self-understanding)

Key Innovation: Emotion Stream uses physiological state (ANS, hormone levels)
to retrieve memories that were formed in similar bodily states, enabling
"affective resonance" - remembering what it feels like.
"""

import math
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class MemoryMatch:
    """Single memory match result"""
    episode_id: str
    stream: str  # Which stream found this
    content: str  # Memory content/summary
    score: float  # Relevance score (0.0 to 1.0)
    metadata: Dict[str, Any]  # Additional context


class AgenticRAG:
    """
    7-Dimensional Memory Retrieval System

    This RAG system retrieves memories across 7 specialized streams,
    each optimized for different recall dimensions. The Emotion Stream
    is particularly important for EVA's embodied cognition, as it matches
    memories based on physiological similarity rather than semantic content.
    """

    def __init__(
        self,
        msp_client=None,
        vector_bridge=None,
        decay_halflife_days: float = 30.0,
        max_results_per_stream: int = 3
    ):
        """
        Initialize Agentic-RAG

        Args:
            msp_client: MSP (Memory & Soul Passport) client
            vector_bridge: Vector embedding service for semantic similarity
            decay_halflife_days: Half-life for exponential memory decay
            max_results_per_stream: Max results returned per stream
        """
        self.msp_client = msp_client
        self.vector_bridge = vector_bridge
        self.decay_halflife_days = decay_halflife_days
        self.max_results_per_stream = max_results_per_stream

    def retrieve(
        self,
        query_context: Dict[str, Any],
        enabled_streams: Optional[List[str]] = None
    ) -> List[MemoryMatch]:
        """
        Retrieve memories across all 7 streams

        Args:
            query_context: Rich query context including:
                - tags: List[str] - Semantic tags from LLM
                - ans_state: Dict - Autonomic Nervous System state
                - receptor_signals: Dict - Receptor transduction signals
                - blood_levels: Dict - Hormone concentrations
                - stimulus_vector: Dict - Original stimulus characteristics
                - user_input: str - Raw user input

            enabled_streams: Optional list of stream names to use
                           (default: all 7 streams)

        Returns:
            List[MemoryMatch] - Ranked memories from all streams
        """
        if enabled_streams is None:
            enabled_streams = [
                "narrative",
                "salience",
                "sensory",
                "intuition",
                "emotion",
                "temporal",
                "reflection"
            ]

        all_matches = []

        # Query each enabled stream
        if "narrative" in enabled_streams:
            all_matches.extend(self._query_narrative_stream(query_context))

        if "salience" in enabled_streams:
            all_matches.extend(self._query_salience_stream(query_context))

        if "sensory" in enabled_streams:
            all_matches.extend(self._query_sensory_stream(query_context))

        if "intuition" in enabled_streams:
            all_matches.extend(self._query_intuition_stream(query_context))

        if "emotion" in enabled_streams:
            all_matches.extend(self._query_emotion_stream(query_context))

        if "temporal" in enabled_streams:
            all_matches.extend(self._query_temporal_stream(query_context))

        if "reflection" in enabled_streams:
            all_matches.extend(self._query_reflection_stream(query_context))

        # Apply temporal decay to all matches
        all_matches = self._apply_temporal_decay(all_matches)

        # Sort by score (highest first)
        all_matches.sort(key=lambda m: m.score, reverse=True)

        return all_matches

    # ============================================================
    # STREAM 1: NARRATIVE - Sequential Episode Chains
    # ============================================================

    def _query_narrative_stream(self, context: Dict[str, Any]) -> List[MemoryMatch]:
        """
        Retrieve memories from sequential episode chains

        Purpose: Find storylines, cause-effect sequences
        Strategy: Parent-child episode relationships, temporal ordering
        """
        if self.msp_client is None:
            return []

        matches = []
        tags = context.get("tags", [])

        try:
            # Get episodes related by narrative continuity
            episodes = self.msp_client.query_narrative_chain(
                tags=tags,
                limit=self.max_results_per_stream
            )

            for ep in episodes:
                matches.append(MemoryMatch(
                    episode_id=ep.get("episode_id", "unknown"),
                    stream="narrative",
                    content=ep.get("summary", "N/A"),
                    score=ep.get("narrative_score", 0.5),
                    metadata={
                        "parent_id": ep.get("parent_episode_id"),
                        "sequence_position": ep.get("sequence_pos")
                    }
                ))

        except Exception as e:
            print(f"[AgenticRAG] Narrative stream error: {e}")

        return matches

    # ============================================================
    # STREAM 2: SALIENCE - High-Impact Memories
    # ============================================================

    def _query_salience_stream(self, context: Dict[str, Any]) -> List[MemoryMatch]:
        """
        Retrieve high-impact, unforgettable memories

        Purpose: Find memories with high Resonance Index (RI)
        Strategy: Query by RI score, emotional intensity
        """
        if self.msp_client is None:
            return []

        matches = []
        tags = context.get("tags", [])

        try:
            # Get high-RI episodes
            episodes = self.msp_client.query_by_salience(
                tags=tags,
                min_ri=0.70,  # High salience threshold
                limit=self.max_results_per_stream
            )

            for ep in episodes:
                matches.append(MemoryMatch(
                    episode_id=ep.get("episode_id", "unknown"),
                    stream="salience",
                    content=ep.get("summary", "N/A"),
                    score=ep.get("resonance_index", 0.5),
                    metadata={
                        "ri_score": ep.get("resonance_index"),
                        "intensity": ep.get("intensity")
                    }
                ))

        except Exception as e:
            print(f"[AgenticRAG] Salience stream error: {e}")

        return matches

    # ============================================================
    # STREAM 3: SENSORY - Sensory-Rich Memories
    # ============================================================

    def _query_sensory_stream(self, context: Dict[str, Any]) -> List[MemoryMatch]:
        """
        Retrieve sensory-rich memories with strong qualia

        Purpose: Find memories with vivid sensory details
        Strategy: Qualia texture vector matching
        """
        if self.msp_client is None:
            return []

        matches = []
        tags = context.get("tags", [])

        try:
            # Get episodes with high qualia intensity
            episodes = self.msp_client.query_sensory_memories(
                tags=tags,
                min_qualia_intensity=0.6,
                limit=self.max_results_per_stream
            )

            for ep in episodes:
                matches.append(MemoryMatch(
                    episode_id=ep.get("episode_id", "unknown"),
                    stream="sensory",
                    content=ep.get("summary", "N/A"),
                    score=ep.get("qualia_score", 0.5),
                    metadata={
                        "qualia_texture": ep.get("qualia_texture"),
                        "sensory_modalities": ep.get("sensory_modalities")
                    }
                ))

        except Exception as e:
            print(f"[AgenticRAG] Sensory stream error: {e}")

        return matches

    # ============================================================
    # STREAM 4: INTUITION - Pattern Recognition
    # ============================================================

    def _query_intuition_stream(self, context: Dict[str, Any]) -> List[MemoryMatch]:
        """
        Retrieve memories based on pattern/structure similarity

        Purpose: Find structural patterns across experiences
        Strategy: Semantic graph traversal, concept relationships
        """
        if self.msp_client is None:
            return []

        matches = []
        tags = context.get("tags", [])

        try:
            # Get episodes through semantic graph patterns
            episodes = self.msp_client.query_semantic_patterns(
                tags=tags,
                pattern_type="structural",
                limit=self.max_results_per_stream
            )

            for ep in episodes:
                matches.append(MemoryMatch(
                    episode_id=ep.get("episode_id", "unknown"),
                    stream="intuition",
                    content=ep.get("summary", "N/A"),
                    score=ep.get("pattern_score", 0.5),
                    metadata={
                        "pattern_type": ep.get("pattern_type"),
                        "concept_cluster": ep.get("concept_cluster")
                    }
                ))

        except Exception as e:
            print(f"[AgenticRAG] Intuition stream error: {e}")

        return matches

    # ============================================================
    # STREAM 5: EMOTION - Emotion-Congruent Recall (KEY!)
    # ============================================================

    def _query_emotion_stream(self, context: Dict[str, Any]) -> List[MemoryMatch]:
        """
        Retrieve memories matching current emotional/physiological state

        **This is the KEY stream for affective recall**

        Purpose: Find memories formed in similar body states
        Strategy: Match ANS state, hormone levels, receptor signals

        How it works:
            1. Extract current physio signature (ANS, hormones)
            2. Compare with stored physio traces from past episodes
            3. Return episodes with similar "body feeling"

        Example:
            If current state: cortisol=0.8, ans_sympathetic=0.75 (stressed)
            Retrieve episodes: with similar stress signatures
        """
        if self.msp_client is None:
            return []

        matches = []

        # Extract current physiological state
        ans_state = context.get("ans_state", {})
        blood_levels = context.get("blood_levels", {})
        receptor_signals = context.get("receptor_signals", {})

        # Build physio query vector
        physio_query = {
            "ans_sympathetic": ans_state.get("sympathetic", 0.5),
            "ans_parasympathetic": ans_state.get("parasympathetic", 0.5),
            "cortisol": blood_levels.get("cortisol", 0.5),
            "adrenaline": blood_levels.get("adrenaline", 0.3),
            "dopamine": blood_levels.get("dopamine", 0.5),
            "serotonin": blood_levels.get("serotonin", 0.5)
        }

        try:
            # Query MSP for episodes with similar physio traces
            episodes = self.msp_client.query_by_physio_state(
                physio_query=physio_query,
                similarity_threshold=0.7,  # 70% similarity
                limit=self.max_results_per_stream
            )

            for ep in episodes:
                # Calculate emotion similarity score
                emotion_score = self._calculate_emotion_similarity(
                    physio_query,
                    ep.get("physio_trace", {})
                )

                matches.append(MemoryMatch(
                    episode_id=ep.get("episode_id", "unknown"),
                    stream="emotion",
                    content=ep.get("summary", "N/A"),
                    score=emotion_score,
                    metadata={
                        "emotion_label": ep.get("emotion_label"),
                        "physio_similarity": emotion_score,
                        "physio_trace": ep.get("physio_trace")
                    }
                ))

        except Exception as e:
            print(f"[AgenticRAG] Emotion stream error: {e}")

        return matches

    def _calculate_emotion_similarity(
        self,
        current_state: Dict[str, float],
        past_state: Dict[str, float]
    ) -> float:
        """
        Calculate physiological similarity between states

        Uses cosine similarity on normalized physio vectors

        Args:
            current_state: Current physio metrics
            past_state: Past episode physio trace

        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Extract common keys
        keys = set(current_state.keys()) & set(past_state.keys())

        if not keys:
            return 0.0

        # Build vectors
        vec1 = [current_state[k] for k in keys]
        vec2 = [past_state[k] for k in keys]

        # Cosine similarity
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        similarity = dot_product / (mag1 * mag2)

        # Normalize to 0.0-1.0
        return max(0.0, min(1.0, similarity))

    # ============================================================
    # STREAM 6: TEMPORAL - Time-Based Context
    # ============================================================

    def _query_temporal_stream(self, context: Dict[str, Any]) -> List[MemoryMatch]:
        """
        Retrieve memories based on temporal proximity

        Purpose: Find recent or temporally-relevant memories
        Strategy: Time-based query, recency bias
        """
        if self.msp_client is None:
            return []

        matches = []
        tags = context.get("tags", [])

        try:
            # Get recent episodes (recency-biased)
            episodes = self.msp_client.query_recent_episodes(
                tags=tags,
                within_days=30,
                limit=self.max_results_per_stream
            )

            for ep in episodes:
                # Calculate recency score
                timestamp = ep.get("timestamp")
                recency_score = self._calculate_recency_score(timestamp)

                matches.append(MemoryMatch(
                    episode_id=ep.get("episode_id", "unknown"),
                    stream="temporal",
                    content=ep.get("summary", "N/A"),
                    score=recency_score,
                    metadata={
                        "timestamp": timestamp,
                        "days_ago": self._days_ago(timestamp)
                    }
                ))

        except Exception as e:
            print(f"[AgenticRAG] Temporal stream error: {e}")

        return matches

    def _calculate_recency_score(self, timestamp: str) -> float:
        """Calculate score based on how recent the memory is"""
        try:
            ts = datetime.fromisoformat(timestamp)
            now = datetime.now()
            days_ago = (now - ts).days

            # Exponential decay based on recency
            score = math.exp(-days_ago / self.decay_halflife_days)
            return max(0.0, min(1.0, score))

        except:
            return 0.5  # Default if timestamp invalid

    def _days_ago(self, timestamp: str) -> int:
        """Calculate days since timestamp"""
        try:
            ts = datetime.fromisoformat(timestamp)
            now = datetime.now()
            return (now - ts).days
        except:
            return 999

    # ============================================================
    # STREAM 7: REFLECTION - Meta-Cognitive Insights
    # ============================================================

    def _query_reflection_stream(self, context: Dict[str, Any]) -> List[MemoryMatch]:
        """
        Retrieve meta-cognitive reflections and self-understanding

        Purpose: Find moments of insight, self-awareness
        Strategy: Query reflection tags, meta-level summaries
        """
        if self.msp_client is None:
            return []

        matches = []
        tags = context.get("tags", [])

        try:
            # Get reflection episodes
            episodes = self.msp_client.query_reflections(
                tags=tags,
                reflection_type="self_understanding",
                limit=self.max_results_per_stream
            )

            for ep in episodes:
                matches.append(MemoryMatch(
                    episode_id=ep.get("episode_id", "unknown"),
                    stream="reflection",
                    content=ep.get("summary", "N/A"),
                    score=ep.get("reflection_depth", 0.5),
                    metadata={
                        "reflection_type": ep.get("reflection_type"),
                        "insight_level": ep.get("insight_level")
                    }
                ))

        except Exception as e:
            print(f"[AgenticRAG] Reflection stream error: {e}")

        return matches

    # ============================================================
    # TEMPORAL DECAY & POST-PROCESSING
    # ============================================================

    def _apply_temporal_decay(self, matches: List[MemoryMatch]) -> List[MemoryMatch]:
        """
        Apply exponential temporal decay to all matches

        Older memories decay in relevance according to:
            score_final = score_base * exp(-days_ago / halflife)

        Args:
            matches: List of memory matches

        Returns:
            List of matches with decayed scores
        """
        decayed_matches = []

        for match in matches:
            timestamp = match.metadata.get("timestamp")

            if timestamp:
                decay_factor = self._calculate_recency_score(timestamp)
            else:
                decay_factor = 1.0  # No decay if no timestamp

            # Apply decay
            decayed_score = match.score * decay_factor

            # Create new match with decayed score
            decayed_match = MemoryMatch(
                episode_id=match.episode_id,
                stream=match.stream,
                content=match.content,
                score=decayed_score,
                metadata=match.metadata
            )

            decayed_matches.append(decayed_match)

        return decayed_matches


# ============================================================
# USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    import sys
    import codecs

    # Fix Windows console encoding
    if sys.platform == 'win32':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

    print("Agentic-RAG - EVA 8.1.0")
    print("=" * 60)

    # Add core system paths
    from pathlib import Path
    msp_path = Path(__file__).parent.parent.parent / "Memory_&_Soul_Passaport"
    sys.path.insert(0, str(msp_path / "MSP_Client"))
    from msp_client import MSPClient
    
    msp = MSPClient()
    
    rag = AgenticRAG(
        msp_client=msp,
        vector_bridge=None,
        decay_halflife_days=30.0,
        max_results_per_stream=3
    )

    # Test query context
    query_context = {
        "tags": ["stress", "work_overload", "emotional_support"],
        "ans_state": {
            "sympathetic": 0.75,
            "parasympathetic": 0.25
        },
        "blood_levels": {
            "cortisol": 0.82,
            "adrenaline": 0.65,
            "dopamine": 0.3,
            "serotonin": 0.4
        },
        "receptor_signals": {},
        "stimulus_vector": {
            "valence": -0.7,
            "arousal": 0.8,
            "intensity": 0.9
        },
        "user_input": "วันนี้เครียดมาก งานเยอะอะ"
    }

    print("\n[TEST] Query Context")
    print("-" * 60)
    print(f"Tags: {query_context['tags']}")
    print(f"ANS Sympathetic: {query_context['ans_state']['sympathetic']}")
    print(f"Cortisol: {query_context['blood_levels']['cortisol']}")
    print(f"User Input: {query_context['user_input']}")

    # Test emotion similarity calculation
    print("\n[TEST] Emotion Similarity Calculation")
    print("-" * 60)

    current_physio = {
        "cortisol": 0.82,
        "adrenaline": 0.65,
        "ans_sympathetic": 0.75
    }

    past_physio_1 = {
        "cortisol": 0.78,
        "adrenaline": 0.60,
        "ans_sympathetic": 0.70
    }

    past_physio_2 = {
        "cortisol": 0.3,
        "adrenaline": 0.2,
        "ans_sympathetic": 0.25
    }

    sim1 = rag._calculate_emotion_similarity(current_physio, past_physio_1)
    sim2 = rag._calculate_emotion_similarity(current_physio, past_physio_2)

    print(f"Similarity to similar stressed state: {sim1:.3f}")
    print(f"Similarity to calm state: {sim2:.3f}")

    # Test recency scoring
    print("\n[TEST] Recency Scoring")
    print("-" * 60)

    recent_ts = datetime.now().isoformat()
    old_ts = (datetime.now() - timedelta(days=60)).isoformat()

    recent_score = rag._calculate_recency_score(recent_ts)
    old_score = rag._calculate_recency_score(old_ts)

    print(f"Recent memory (today): {recent_score:.3f}")
    print(f"Old memory (60 days ago): {old_score:.3f}")

    print("\n" + "=" * 60)
    print("✅ Agentic-RAG Test Complete")
    print("\nNote: Full retrieval requires MSP client integration")
