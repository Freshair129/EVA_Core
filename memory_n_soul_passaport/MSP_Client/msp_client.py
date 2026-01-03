"""
EVA 8.1.0: MSP Client with Local Filesystem Persistence
Manages episodic memory using JSONL format + individual JSON files

Storage Structure:
    Consciousness/
    ├── 01_Episodic_memory/
    │   ├── episodic_log.jsonl       # Append-only log (fast retrieval)
    │   ├── episodic_index.jsonl     # Index with metadata
    │   └── episodes/
    │       ├── ep_260101_abc123.json
    │       └── ep_260101_def456.json
    │
    ├── 02_Semantic_memory/
    │   └── semantic_concepts.json
    │
    └── 10_state/
        └── turn_cache.json

Advantages:
    - ✅ Persistent (survives program restart)
    - ✅ Fast (JSONL + in-memory cache)
    - ✅ Simple (no database required)
    - ✅ Human-readable (JSON format)
    - ✅ Upgradeable to MongoDB later
"""

import json
import hashlib
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import math
import re


class MSPClient:
    """
    MSP (Memory & Soul Passport) Client with Local Filesystem Persistence

    Provides persistent storage and retrieval for:
    - Episodic Memory (episodes, events, conversations)
    - Semantic Memory (concepts, relationships)
    - Turn Cache (recent conversation summaries)

    Storage Format:
    - episodic_log.jsonl: Append-only log (one episode per line)
    - episodes/*.json: Individual episode files (detailed storage)
    - In-memory cache: Recent episodes for fast access
    """

    def __init__(
        self,
        root_path: Optional[str] = None,
        cache_size: int = 50
    ):
        """
        Initialize MSP Client

        Args:
            root_path: Root path for Consciousness directory
            cache_size: Number of recent episodes to keep in memory
        """
        # Setup paths
        if root_path is None:
            # Default to EVA 8.1.0/Consciousness (at project root)
            self.root_path = Path(__file__).parent.parent.parent / "Consciousness"
        else:
            self.root_path = Path(root_path)

        # Episodic Memory paths
        self.episodic_dir = self.root_path / "01_Episodic_memory"
        self.episodic_log = self.episodic_dir / "episodic_log.jsonl"
        self.episodic_index = self.episodic_dir / "episodic_index.jsonl"

        # Split storage: User vs LLM
        self.episodes_user_dir = self.episodic_dir / "episodes_user"
        self.episodes_llm_dir = self.episodic_dir / "episodes_llm"

        # Legacy folder (for backward compatibility)
        self.episodes_dir = self.episodic_dir / "episodes"

        # Semantic Memory paths
        self.semantic_dir = self.root_path / "02_Semantic_memory"
        self.semantic_concepts_file = self.semantic_dir / "semantic_concepts.json"

        # State paths
        self.state_dir_10 = self.root_path / "10_state"
        self.turn_cache_file = self.state_dir_10 / "turn_cache.json"

        self.state_dir_09 = self.root_path / "09_state"
        self.compression_counters_file = self.state_dir_09 / "compression_counters.json"
        self.episode_counter_file = self.state_dir_09 / "episode_counter.json"
        self.developer_config_file = self.state_dir_09 / "developer_config.json"

        # Session Memory (compression snapshots)
        self.session_memory_dir = self.root_path / "04_Session_memory"

        # Persona config (for episode_id generation)
        self.persona_file = self.root_path.parent / "orchestrator" / "PMT_PromptRuleLayer" / "Identity" / "persona.yaml"

        # Memory Index (lightweight search index)
        self.memory_index_file = self.root_path / "memory_index.json"

        # Create directories
        self.episodic_dir.mkdir(parents=True, exist_ok=True)
        self.episodes_user_dir.mkdir(parents=True, exist_ok=True)
        self.episodes_llm_dir.mkdir(parents=True, exist_ok=True)
        self.episodes_dir.mkdir(parents=True, exist_ok=True)  # Legacy
        self.semantic_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir_10.mkdir(parents=True, exist_ok=True)
        self.state_dir_09.mkdir(parents=True, exist_ok=True)
        self.session_memory_dir.mkdir(parents=True, exist_ok=True)

        # In-memory cache
        self.cache_size = cache_size
        self._episode_cache: List[Dict] = []
        self._cache_loaded = False

        # Semantic concepts
        self._semantic_concepts: Dict = {}
        self._load_semantic_concepts()

        # Turn cache (session-specific)
        self.turn_cache: Dict = {}

        # Compression counters
        self.compression_counters: Dict = self._load_compression_counters()

        # Episode counter (for human-readable episode IDs)
        self.episode_counter: Dict = self._load_episode_counter()

        # Developer config (for session memory file naming)
        self.developer_config: Dict = self._load_developer_config()

        self._load_turn_cache()

        print(f"[MSP] Initialized with root: {self.root_path}")
        print(f"[MSP] Episodic log: {self.episodic_log}")
        print(f"[MSP] Episodes directory: {self.episodes_dir}")

    # ============================================================
    # EPISODIC MEMORY - READ OPERATIONS
    # ============================================================

    def _load_cache(self):
        """Load recent episodes into memory cache"""
        if self._cache_loaded:
            return

        episodes = self._read_all_episodes_from_log()
        self._episode_cache = episodes[-self.cache_size:]
        self._cache_loaded = True
        print(f"[MSP] Loaded {len(self._episode_cache)} episodes into cache")

    def _read_all_episodes_from_log(self) -> List[Dict]:
        """Read all episodes from JSONL log file"""
        if not self.episodic_log.exists():
            return []

        episodes = []
        with open(self.episodic_log, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        episodes.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"[MSP] Warning: Failed to parse episode: {e}")
                        continue
        return episodes

    def _read_episode_file(self, episode_id: str) -> Optional[Dict]:
        """Read individual episode file (redirects to get_full_episode)"""
        # Use new split storage
        return self.get_full_episode(episode_id)

    def _read_user_episodes(self) -> List[Dict]:
        """
        Read all user episodes (lightweight, fast)
        Use this for RAG queries that don't need LLM responses
        """
        user_episodes = []
        for user_file in self.episodes_user_dir.glob("*_user.json"):
            try:
                with open(user_file, 'r', encoding='utf-8') as f:
                    user_episodes.append(json.load(f))
            except Exception as e:
                print(f"[MSP] Warning: Failed to parse user episode {user_file}: {e}")
        return user_episodes

    def query_by_tags(
        self,
        tags: List[str],
        max_results: int = 5,
        min_ri: float = 0.0
    ) -> List[Dict]:
        """
        Query episodes by semantic tags

        Args:
            tags: List of tags to search for
            max_results: Maximum number of results
            min_ri: Minimum Resonance Index threshold

        Returns:
            List of matching episodes
        """
        self._load_cache()

        # Search in cache first (fast)
        matches = []
        tags_lower = [t.lower() for t in tags]

        for ep in self._episode_cache:
            # Schema V2: tags are in turn_1.semantic_frames
            # Legacy: tags are at root level
            if "turn_1" in ep:
                ep_tags = [t.lower() for t in ep.get("turn_1", {}).get("semantic_frames", [])]
            else:
                ep_tags = [t.lower() for t in ep.get("tags", [])]

            if any(tag in ep_tags for tag in tags_lower):
                # Schema V2: RI in state_snapshot.Resonance_index
                # Legacy: resonance_index at root
                if "state_snapshot" in ep:
                    ri = ep.get("state_snapshot", {}).get("Resonance_index", 0)
                else:
                    ri = ep.get("resonance_index", 0)

                if ri >= min_ri:
                    matches.append(ep)

        # If not enough matches, search user episodes (fast, no LLM data)
        if len(matches) < max_results:
            user_episodes = self._read_user_episodes()
            for ep in user_episodes:
                if ep in matches:
                    continue

                # Schema V2: tags in turn_1.semantic_frames
                ep_tags = [t.lower() for t in ep.get("turn_1", {}).get("semantic_frames", [])]

                if any(tag in ep_tags for tag in tags_lower):
                    # Schema V2: RI in state_snapshot.Resonance_index
                    ri = ep.get("state_snapshot", {}).get("Resonance_index", 0)

                    if ri >= min_ri:
                        matches.append(ep)

        # Sort by RI (descending)
        def get_ri(ep):
            if "state_snapshot" in ep:
                return ep.get("state_snapshot", {}).get("Resonance_index", 0)
            return ep.get("resonance_index", 0)

        matches.sort(key=get_ri, reverse=True)
        return matches[:max_results]

    def query_by_physio_state(
        self,
        physio_query: Dict[str, float],
        similarity_threshold: float = 0.7,
        max_results: int = 3
    ) -> List[Dict]:
        """
        Query episodes by physiological similarity (Emotion Stream)

        Args:
            physio_query: Current physiological state
            similarity_threshold: Minimum cosine similarity (0.0-1.0)
            max_results: Maximum number of results

        Returns:
            List of matching episodes sorted by similarity
        """
        self._load_cache()
        all_episodes = self._read_all_episodes_from_log()

        matches = []
        for ep in all_episodes:
            # Schema V2: physio state in state_snapshot.Endocrine
            # Legacy: physio_state at root
            if "state_snapshot" in ep:
                physio_state = ep.get("state_snapshot", {}).get("Endocrine", {})
            else:
                physio_state = ep.get("physio_state", {})

            if not physio_state:
                continue

            similarity = self._cosine_similarity(physio_query, physio_state)

            if similarity >= similarity_threshold:
                ep_copy = ep.copy()
                ep_copy["physio_similarity"] = similarity
                matches.append(ep_copy)

        # Sort by similarity (descending)
        matches.sort(key=lambda x: x["physio_similarity"], reverse=True)
        return matches[:max_results]

    def query_by_ri(
        self,
        min_ri: float = 0.70,
        max_results: int = 3
    ) -> List[Dict]:
        """
        Query high-salience episodes (Salience Stream)

        Args:
            min_ri: Minimum Resonance Index
            max_results: Maximum results

        Returns:
            High-impact episodes
        """
        self._load_cache()
        all_episodes = self._read_all_episodes_from_log()

        # Schema V2 or Legacy format
        def get_ri(ep):
            if "state_snapshot" in ep:
                return ep.get("state_snapshot", {}).get("Resonance_index", 0)
            return ep.get("resonance_index", 0)

        matches = [ep for ep in all_episodes if get_ri(ep) >= min_ri]
        matches.sort(key=get_ri, reverse=True)
        return matches[:max_results]

    def query_by_qualia(
        self,
        min_intensity: float = 0.6,
        max_results: int = 3
    ) -> List[Dict]:
        """
        Query sensory-rich episodes (Sensory Stream)

        Args:
            min_intensity: Minimum qualia intensity
            max_results: Maximum results

        Returns:
            Sensory-rich episodes
        """
        self._load_cache()
        all_episodes = self._read_all_episodes_from_log()

        # Schema V2 or Legacy format
        def get_qualia_intensity(ep):
            if "state_snapshot" in ep:
                return ep.get("state_snapshot", {}).get("qualia", {}).get("intensity", 0)
            return ep.get("qualia", {}).get("intensity", 0)

        matches = [
            ep for ep in all_episodes
            if get_qualia_intensity(ep) >= min_intensity
        ]
        matches.sort(key=get_qualia_intensity, reverse=True)
        return matches[:max_results]

    def query_recent(
        self,
        max_results: int = 5,
        max_age_days: int = 30
    ) -> List[Dict]:
        """
        Query recent episodes (Temporal Stream)

        Args:
            max_results: Maximum results
            max_age_days: Maximum age in days

        Returns:
            Recent episodes with recency scores
        """
        self._load_cache()
        all_episodes = self._read_all_episodes_from_log()

        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        matches = []

        for ep in all_episodes:
            timestamp_str = ep.get("timestamp", "")
            if not timestamp_str:
                continue

            try:
                ep_date = datetime.fromisoformat(timestamp_str)
                if ep_date >= cutoff_date:
                    days_ago = (datetime.now() - ep_date).days
                    recency_score = self._exponential_decay(days_ago, halflife=30)

                    ep_copy = ep.copy()
                    ep_copy["recency_score"] = recency_score
                    matches.append(ep_copy)
            except:
                continue

        # Sort by recency
        matches.sort(key=lambda x: x.get("recency_score", 0), reverse=True)
        return matches[:max_results]

    # ============================================================
    # EPISODIC MEMORY - WRITE OPERATIONS
    # ============================================================

    def write_episode(
        self,
        episode_data: Dict[str, Any]
    ) -> str:
        """
        Write new episode to persistent storage

        Writes to:
        1. episodic_log.jsonl (append-only log)
        2. episodes/{episode_id}.json (individual file)
        3. In-memory cache (for fast access)

        Args:
            episode_data: Episode data

        Returns:
            Episode ID
        """
        # Generate episode ID and timestamp
        timestamp = datetime.now().isoformat()
        episode_id = self._generate_episode_id()  # Format: EVA_EP01, EVA_EP79, etc.

        # Add compression metadata (BEFORE incrementing)
        compression_meta = {
            "session_seq": self.compression_counters.get("Session_seq", 0),
            "core_seq": self.compression_counters.get("Core_seq", 0),
            "sphere_seq": self.compression_counters.get("Sphere_seq", 0)
        }

        # Split episode data: User vs LLM
        # User file: Lightweight (turn_1, tags, emotion, basic state)
        user_episode = {
            "episode_id": episode_id,
            "timestamp": timestamp,
            "session_id": episode_data.get("session_id"),
            "event_label": episode_data.get("event_label"),
            "episode_tag": episode_data.get("episode_tag"),
            "episode_type": episode_data.get("episode_type"),
            "compression_meta": compression_meta,
            "situation_context": episode_data.get("situation_context"),
            "turn_1": episode_data.get("turn_1"),
        }

        # Add lightweight state snapshot
        if "state_snapshot" in episode_data:
            user_episode["state_snapshot"] = {
                "EVA_matrix": episode_data["state_snapshot"].get("EVA_matrix"),
                "Resonance_index": episode_data["state_snapshot"].get("Resonance_index")
            }

        # LLM file: Detailed (turn_2, full physio state)
        llm_episode = {
            "episode_id": episode_id,
            "turn_2": episode_data.get("turn_2"),
        }

        # Add detailed state snapshot
        if "state_snapshot" in episode_data:
            llm_episode["state_snapshot"] = {
                "Endocrine": episode_data["state_snapshot"].get("Endocrine"),
                "memory_encoding_level": episode_data["state_snapshot"].get("memory_encoding_level"),
                "memory_color": episode_data["state_snapshot"].get("memory_color"),
                "qualia": episode_data["state_snapshot"].get("qualia"),
                "reflex": episode_data["state_snapshot"].get("reflex")
            }

        # 1. Write user episode file (lightweight, fast queries)
        try:
            user_file = self.episodes_user_dir / f"{episode_id}_user.json"
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(user_episode, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[MSP] Error writing user episode: {e}")

        # 2. Write LLM episode file (detailed state)
        try:
            llm_file = self.episodes_llm_dir / f"{episode_id}_llm.json"
            with open(llm_file, 'w', encoding='utf-8') as f:
                json.dump(llm_episode, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[MSP] Error writing llm episode: {e}")

        # 3. Append to JSONL log (index - full episode for backward compat)
        full_episode = {**user_episode, **llm_episode}
        try:
            with open(self.episodic_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(full_episode, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"[MSP] Error writing to episodic_log: {e}")

        # 4. Update cache (use full episode for backward compat)
        self._episode_cache.append(full_episode)
        if len(self._episode_cache) > self.cache_size:
            self._episode_cache.pop(0)

        # 5. Update memory_index.json (lightweight search index)
        self._update_memory_index(full_episode)

        # 6. Write sensory memory sidecar if qualia exists
        if "state_snapshot" in episode_data:
            qualia = episode_data.get("state_snapshot", {}).get("qualia")
            if qualia:
                self.write_sensory_log(episode_id, qualia)
        elif "qualia" in episode_data:
            # Legacy format
            self.write_sensory_log(episode_id, episode_data["qualia"])

        # 7. Increment compression counters (AFTER writing episode)
        new_counters = self._increment_compression_counters()
        print(f"[MSP] ✓ Written episode: {episode_id} (User: {len(json.dumps(user_episode))}B, LLM: {len(json.dumps(llm_episode))}B)")
        print(f"[MSP]   Session {new_counters['session_seq']}/8, Core {new_counters['core_seq']}/8")

        return episode_id

    def get_full_episode(self, episode_id: str) -> Optional[Dict]:
        """
        Get full episode by merging user + llm files

        Args:
            episode_id: Episode ID

        Returns:
            Full episode dict or None if not found
        """
        user_file = self.episodes_user_dir / f"{episode_id}_user.json"
        llm_file = self.episodes_llm_dir / f"{episode_id}_llm.json"

        if not user_file.exists():
            print(f"[MSP] Warning: User file not found for {episode_id}")
            return None

        try:
            # Load user data (always needed)
            with open(user_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)

            # Load LLM data (if exists)
            if llm_file.exists():
                with open(llm_file, 'r', encoding='utf-8') as f:
                    llm_data = json.load(f)

                # Merge state_snapshot
                if "state_snapshot" in llm_data:
                    if "state_snapshot" not in user_data:
                        user_data["state_snapshot"] = {}
                    user_data["state_snapshot"].update(llm_data["state_snapshot"])

                # Add turn_2
                user_data["turn_2"] = llm_data.get("turn_2")

            return user_data

        except Exception as e:
            print(f"[MSP] Error loading full episode {episode_id}: {e}")
            return None

    # ============================================================
    # SEMANTIC MEMORY OPERATIONS
    # ============================================================

    def _load_semantic_concepts(self):
        """Load semantic concepts from file"""
        if not self.semantic_concepts_file.exists():
            self._semantic_concepts = {
                "gratitude": {"related": ["appreciation", "thanks", "acknowledgment"]},
                "longing": {"related": ["desire", "yearning", "missing"]},
                "stress": {"related": ["pressure", "overwhelm", "tension"]},
                "joy": {"related": ["happiness", "delight", "pleasure"]},
                "sadness": {"related": ["sorrow", "melancholy", "grief"]}
            }
            self._save_semantic_concepts()
            return

        try:
            with open(self.semantic_concepts_file, 'r', encoding='utf-8') as f:
                self._semantic_concepts = json.load(f)
        except Exception as e:
            print(f"[MSP] Error loading semantic concepts: {e}")
            self._semantic_concepts = {}

    def _save_semantic_concepts(self):
        """Save semantic concepts to file"""
        try:
            with open(self.semantic_concepts_file, 'w', encoding='utf-8') as f:
                json.dump(self._semantic_concepts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[MSP] Error saving semantic concepts: {e}")

    def get_semantic_concepts(
        self,
        tags: List[str]
    ) -> Dict[str, Any]:
        """
        Get related semantic concepts

        Args:
            tags: Input tags

        Returns:
            Related concepts
        """
        related = {}
        for tag in tags:
            if tag in self._semantic_concepts:
                related[tag] = self._semantic_concepts[tag]
        return related

    # ============================================================
    # COMPRESSION COUNTER OPERATIONS
    # ============================================================

    def _load_compression_counters(self) -> Dict[str, int]:
        """Load compression counters from 09_state/compression_counters.json"""
        if not self.compression_counters_file.exists():
            # Create default counters
            default_counters = {
                "Session_seq": 0,
                "Core_seq": 0,
                "Sphere_seq": 0,
                "last_update": datetime.now().isoformat()
            }
            self._save_compression_counters(default_counters)
            return default_counters

        try:
            with open(self.compression_counters_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[MSP] Error loading compression counters: {e}")
            return {
                "Session_seq": 0,
                "Core_seq": 0,
                "Sphere_seq": 0,
                "last_update": datetime.now().isoformat()
            }

    def _save_compression_counters(self, counters: Dict[str, Any] = None):
        """Save compression counters to file"""
        if counters is None:
            counters = self.compression_counters

        try:
            with open(self.compression_counters_file, 'w', encoding='utf-8') as f:
                json.dump(counters, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[MSP] Error saving compression counters: {e}")

    def _increment_compression_counters(self):
        """
        Increment compression counters according to hierarchy:
        - Increment Session_seq
        - If Session_seq reaches 8:
            - Create Core (TODO)
            - Increment Core_seq
            - Reset Session_seq to 0
        - If Core_seq reaches 8:
            - Create Sphere (TODO)
            - Increment Sphere_seq
            - Reset Core_seq to 0
        """
        session_seq = self.compression_counters.get("Session_seq", 0)
        core_seq = self.compression_counters.get("Core_seq", 0)
        sphere_seq = self.compression_counters.get("Sphere_seq", 0)
        total_sessions = self.compression_counters.get("Total_sessions", 0)

        # Increment session & total
        session_seq += 1
        total_sessions += 1

        # Check if we need to create a Core
        if session_seq >= 8:
            print(f"[MSP] Compression trigger: 8 sessions completed → Creating Core {core_seq}")
            # TODO: Implement Core compression
            # self._compress_to_core(session_seq, core_seq, sphere_seq)

            core_seq += 1
            session_seq = 0

            # Check if we need to create a Sphere
            if core_seq >= 8:
                print(f"[MSP] Compression trigger: 8 cores completed → Creating Sphere {sphere_seq}")
                # TODO: Implement Sphere compression
                # self._compress_to_sphere(core_seq, sphere_seq)

                sphere_seq += 1
                core_seq = 0

        # Update counters
        self.compression_counters["Session_seq"] = session_seq
        self.compression_counters["Core_seq"] = core_seq
        self.compression_counters["Sphere_seq"] = sphere_seq
        self.compression_counters["Total_sessions"] = total_sessions
        self.compression_counters["last_update"] = datetime.now().isoformat()

        # Save to file
        self._save_compression_counters()

        return {
            "session_seq": session_seq,
            "core_seq": core_seq,
            "sphere_seq": sphere_seq
        }

    # ============================================================
    # EPISODE COUNTER & ID GENERATION
    # ============================================================

    def _load_episode_counter(self) -> Dict[str, Any]:
        """Load episode counter from 09_state/episode_counter.json"""
        if not self.episode_counter_file.exists():
            # Load persona name
            persona_code = self._get_persona_code()

            # Create default counter
            default_counter = {
                "current_episode": 0,
                "last_update": datetime.now().isoformat(),
                "persona_code": persona_code,
                "meta": {
                    "description": "Episode counter for human-readable episode IDs",
                    "format": "{persona_code}_EP{number}",
                    "example": f"{persona_code}_EP01, {persona_code}_EP79",
                    "persona_code_max_length": 4,
                    "auto_increment": True
                }
            }
            self._save_episode_counter(default_counter)
            return default_counter

        try:
            with open(self.episode_counter_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[MSP] Error loading episode counter: {e}")
            return {
                "current_episode": 0,
                "last_update": datetime.now().isoformat(),
                "persona_code": "EVA"
            }

    def _save_episode_counter(self, counter: Dict[str, Any] = None):
        """Save episode counter to file"""
        if counter is None:
            counter = self.episode_counter

        try:
            with open(self.episode_counter_file, 'w', encoding='utf-8') as f:
                json.dump(counter, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[MSP] Error saving episode counter: {e}")

    def _increment_episode_counter(self) -> int:
        """
        Increment episode counter and return new episode number

        Returns:
            New episode number
        """
        current = self.episode_counter.get("current_episode", 0)
        current += 1

        self.episode_counter["current_episode"] = current
        self.episode_counter["last_update"] = datetime.now().isoformat()

        self._save_episode_counter()

        return current

    def _get_persona_code(self) -> str:
        """
        Get persona code from persona.yaml
        If name > 4 chars, abbreviate like airport codes

        Returns:
            Persona code (max 4 chars, uppercase)
        """
        try:
            if self.persona_file.exists():
                with open(self.persona_file, 'r', encoding='utf-8') as f:
                    persona_data = yaml.safe_load(f)
                    persona_name = persona_data.get('meta', {}).get('name', 'EVA')
            else:
                persona_name = 'EVA'
        except Exception as e:
            print(f"[MSP] Error loading persona: {e}, using default 'EVA'")
            persona_name = 'EVA'

        # Abbreviate if needed
        return self._abbreviate_persona_name(persona_name)

    def _abbreviate_persona_name(self, name: str) -> str:
        """
        Abbreviate persona name to max 4 characters (like airport codes)

        Rules:
        - If <= 4 chars: Use as-is
        - If > 4 chars: Take first 4 consonants/letters
        - Examples:
            EVA → EVA
            Alexander → ALEX
            Christopher → CHRS
            สมหญิง → สมหญ

        Args:
            name: Persona name

        Returns:
            Abbreviated code (max 4 chars, uppercase for English)
        """
        name = name.strip()

        # If already <= 4, use as-is
        if len(name) <= 4:
            return name.upper()

        # For English names: Extract consonants + vowels, prioritize first letters
        # Simple approach: Take first 4 characters and remove vowels if needed
        if re.match(r'^[A-Za-z]+$', name):
            # Remove vowels, keep consonants
            consonants = re.sub(r'[aeiouAEIOU]', '', name)
            if len(consonants) >= 4:
                return consonants[:4].upper()
            else:
                # Not enough consonants, use first 4 letters
                return name[:4].upper()
        else:
            # For Thai or other scripts: Just take first 4 characters
            return name[:4]

    def _generate_episode_id(self) -> str:
        """
        Generate human-readable episode ID

        Format: {PERSONA}_EP{number}
        Examples: EVA_EP01, EVA_EP79, ALEX_EP123

        Returns:
            Episode ID
        """
        persona_code = self.episode_counter.get("persona_code", "EVA")
        episode_num = self._increment_episode_counter()

        # Format with zero-padding (2 digits minimum)
        episode_id = f"{persona_code}_EP{episode_num:02d}"

        return episode_id

    # ============================================================
    # SESSION MEMORY & DEVELOPER CONFIG
    # ============================================================

    def _load_developer_config(self) -> Dict[str, Any]:
        """Load developer config from 09_state/developer_config.json"""
        if not self.developer_config_file.exists():
            # Try to load from soul.md first
            develop_id = self._get_develop_id_from_soul()

            # Create default config
            default_config = {
                "develop_id": develop_id,
                "description": "Development ID + Subject ID for EVA instance",
                "components": {
                    "project_id": develop_id.split('-S')[0] if '-S' in develop_id else develop_id,
                    "subject_id": f"S{develop_id.split('-S')[1]}" if '-S' in develop_id else "S001"
                },
                "format": "{country_code}-{project_seq}-{subject_id}",
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat()
            }
            try:
                with open(self.developer_config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[MSP] Error creating developer config: {e}")
            return default_config

        try:
            with open(self.developer_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[MSP] Error loading developer config: {e}")
            return {"develop_id": "THA-01-S003"}

    def _get_develop_id_from_soul(self) -> str:
        """
        Get develop_id from soul.md file

        Returns:
            Develop ID (e.g., "THA-01-S003")
        """
        soul_file = self.root_path.parent / "orchestrator" / "PMT_PromptRuleLayer" / "Identity" / "soul.md"

        try:
            if soul_file.exists():
                with open(soul_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if 'Deverlop_id' in line or 'develop_id' in line:
                            # Parse: Deverlop_id : "THA-01-S003"
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                value = parts[1].strip().strip('"').strip("'")
                                if value:
                                    return value
        except Exception as e:
            print(f"[MSP] Error reading soul.md: {e}")

        # Default fallback
        return "THA-01-S003"

    def _generate_session_memory_filename(self) -> str:
        """
        Generate session memory filename based on compression hierarchy

        Format: {develop_id}_SP{sphere}C{core}_SS{session}.json
        Examples:
            - Session 1 (Sphere 1, Core 1): THA-01-S003_SP1C1_SS1.json
            - Session 6 (Sphere 1, Core 1): THA-01-S003_SP1C1_SS6.json
            - Session 9 (Sphere 1, Core 2): THA-01-S003_SP1C2_SS1.json

        Where:
            - THA-01 = Development project ID
            - S003 = Subject 003 (clone instance)
            - SP1C1 = Sphere 1, Core 1
            - SS6 = Session 6 in current Core

        Returns:
            Session memory filename
        """
        develop_id = self.developer_config.get("develop_id", "THA-01-S003")

        # Get counters (note: these are 0-indexed, so add 1 for display)
        sphere_seq = self.compression_counters.get("Sphere_seq", 0) + 1  # Display as 1-indexed
        core_seq = self.compression_counters.get("Core_seq", 0) + 1      # Display as 1-indexed
        session_seq = self.compression_counters.get("Session_seq", 0)    # This is position in Core

        # Format: {develop_id}_SP{sphere}C{core}_SS{session}.json
        filename = f"{develop_id}_SP{sphere_seq}C{core_seq}_SS{session_seq}.json"

        return filename

    def _generate_session_memory_id(self) -> str:
        """
        Generate session memory ID (without .json extension)

        Format: {develop_id}_SP{sphere}C{core}_SS{session}
        Examples: THA-01-S003_SP1C1_SS1, THA-01-S003_SP1C1_SS6

        Returns:
            Session memory ID
        """
        filename = self._generate_session_memory_filename()
        return filename.replace('.json', '')

    def write_session_memory(self, session_data: Dict[str, Any]) -> str:
        """
        Write compressed session memory (snapshot) to persistent storage
        This is triggered at Core/Sphere compression boundaries.

        Args:
            session_data: The compressed memory snapshot data

        Returns:
            Session ID (filename without extension)
        """
        # Ensure session memory directory exists
        self.session_memory_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique ID and filename
        session_id = self._generate_session_memory_id()
        filename = f"{session_id}.json"
        storage_path = self.session_memory_dir / filename

        # Add metadata if not present
        if "session_id" not in session_data:
            session_data["session_id"] = session_id
        
        if "timestamp" not in session_data:
            session_data["timestamp"] = datetime.now().isoformat()
        
        # Add current counters for traceability
        session_data["compression_counters"] = self.compression_counters.copy()

        # Write to local file
        try:
            with open(storage_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            print(f"[MSP] ✓ Written session memory: {session_id}")
            return session_id
        except Exception as e:
            print(f"[MSP] Error writing session memory: {e}")
            raise e

    # ============================================================
    # TURN CACHE OPERATIONS
    # ============================================================

    def _load_turn_cache(self):
        """Load turn cache from file"""
        if not self.turn_cache_file.exists():
            self.turn_cache = {}
            return

        try:
            with open(self.turn_cache_file, 'r', encoding='utf-8') as f:
                self.turn_cache = json.load(f)
        except Exception as e:
            print(f"[MSP] Error loading turn cache: {e}")
            self.turn_cache = {}

    def _save_turn_cache(self):
        """Save turn cache to file"""
        try:
            with open(self.turn_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.turn_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[MSP] Error saving turn cache: {e}")

    def update_turn_cache(
        self,
        context_id: str,
        summary: str
    ):
        """
        Update turn cache for Phase 1 bootstrap

        Args:
            context_id: Context ID
            summary: Turn summary
        """
        self.turn_cache[context_id] = {
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        self._save_turn_cache()

    def get_recent_history(
        self,
        max_turns: int = 5
    ) -> List[Dict]:
        """
        Get recent conversation history

        Args:
            max_turns: Maximum number of turns

        Returns:
            Recent turn summaries
        """
        # Sort by timestamp
        turns = sorted(
            self.turn_cache.items(),
            key=lambda x: x[1]["timestamp"],
            reverse=True
        )
        return [{"context_id": k, **v} for k, v in turns[:max_turns]]

    def get_recent_turns(
        self,
        limit: int = 5,
        timeout_ms: int = 100
    ) -> List[Dict]:
        """
        Get recent turn summaries from turn cache (for CIN Phase 1 bootstrap)

        Args:
            limit: Maximum number of turns to retrieve
            timeout_ms: Timeout in milliseconds (not used for filesystem - always fast)

        Returns:
            List of recent turn summaries
        """
        # Note: timeout_ms is ignored for filesystem-based implementation
        # Filesystem reads are always fast (<10ms typically)
        return self.get_recent_history(max_turns=limit)

    def get_recent_episodes(
        self,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent episodes for conversation history (for CIN Phase 1)

        Args:
            limit: Maximum number of episodes to retrieve

        Returns:
            List of recent episodes (user-only data for speed)
        """
        # Use user episodes for speed (no LLM response data)
        user_episodes = self._read_user_episodes()

        # Sort by timestamp (descending - most recent first)
        user_episodes.sort(
            key=lambda ep: ep.get("timestamp", ""),
            reverse=True
        )

        # Return last N episodes
        return user_episodes[:limit]

    def get_episode_counter(self) -> Dict[str, Any]:
        """
        Get current episode counter data (for CIN episode ID generation)

        Returns:
            Episode counter dict with persona_code and current_episode
        """
        return self.episode_counter.copy()

    # ============================================================
    # SENSORY MEMORY OPERATIONS
    # ============================================================

    def write_sensory_log(
        self,
        episode_id: str,
        qualia_data: Dict[str, Any]
    ) -> str:
        """
        Write sensory memory sidecar for an episode

        Args:
            episode_id: Associated episode ID
            qualia_data: Qualia/phenomenological data

        Returns:
            Sensory log ID
        """
        # Sensory memory path
        sensory_file = self.root_path / "03_Sensory_memory" / "Sensory_memory.json"

        # Load existing entries
        if sensory_file.exists():
            try:
                with open(sensory_file, 'r', encoding='utf-8') as f:
                    sensory_data = json.load(f)
            except:
                sensory_data = {"entries": []}
        else:
            sensory_data = {"entries": []}

        # Create sensory entry
        sensory_entry = {
            "sensory_id": f"sen_{datetime.now().strftime('%y%m%d')}_{self._hash_short(episode_id)}",
            "episode_id": episode_id,
            "timestamp": datetime.now().isoformat(),
            "qualia": qualia_data
        }

        # Append to entries
        sensory_data["entries"].append(sensory_entry)

        # Write back
        try:
            with open(sensory_file, 'w', encoding='utf-8') as f:
                json.dump(sensory_data, f, ensure_ascii=False, indent=2)
            print(f"[MSP] ✓ Written sensory log: {sensory_entry['sensory_id']}")
        except Exception as e:
            print(f"[MSP] Error writing sensory log: {e}")

        return sensory_entry["sensory_id"]

    def query_sensory_logs(
        self,
        episode_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Query sensory memory logs

        Args:
            episode_id: Optional filter by episode

        Returns:
            List of sensory logs
        """
        sensory_file = self.root_path / "03_Sensory_memory" / "Sensory_memory.json"

        if not sensory_file.exists():
            return []

        try:
            with open(sensory_file, 'r', encoding='utf-8') as f:
                sensory_data = json.load(f)
        except:
            return []

        entries = sensory_data.get("entries", [])

        if episode_id:
            return [e for e in entries if e.get("episode_id") == episode_id]

        return entries

    # ============================================================
    # UTILITY METHODS
    # ============================================================

    def _cosine_similarity(
        self,
        vec1: Dict[str, float],
        vec2: Dict[str, float]
    ) -> float:
        """
        Calculate cosine similarity between two physio state vectors

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score (0.0-1.0)
        """
        # Get common keys
        common_keys = set(vec1.keys()) & set(vec2.keys())
        if not common_keys:
            return 0.0

        # Calculate dot product and magnitudes
        dot_product = sum(vec1[k] * vec2[k] for k in common_keys)
        mag1 = sum(vec1[k] ** 2 for k in common_keys) ** 0.5
        mag2 = sum(vec2[k] ** 2 for k in common_keys) ** 0.5

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)

    def _exponential_decay(
        self,
        days_ago: int,
        halflife: int = 30
    ) -> float:
        """
        Calculate exponential decay score

        Args:
            days_ago: Number of days ago
            halflife: Halflife in days

        Returns:
            Decay score (0.0-1.0)
        """
        return math.exp(-days_ago / halflife)

    def _update_memory_index(self, episode: Dict[str, Any]):
        """
        Update memory_index.json with lightweight episode metadata

        Args:
            episode: Full episode document
        """
        # Extract index fields according to MSP_Write_Policy.yaml:87-98
        index_entry = {
            "episode_id": episode.get("episode_id"),
            "timestamp": episode.get("timestamp"),
            "session_id": episode.get("session_id"),
            "event_label": episode.get("event_label"),
            "episode_tag": episode.get("episode_tag"),
        }

        # Schema V2 fields
        if "turn_1" in episode:
            turn_1 = episode.get("turn_1", {})
            index_entry["summary_user"] = turn_1.get("summary")
            index_entry["tags"] = turn_1.get("semantic_frames", [])
            index_entry["salience_anchor"] = turn_1.get("salience_anchor")
            index_entry["speaker_1"] = turn_1.get("speaker")

        if "turn_2" in episode:
            turn_2 = episode.get("turn_2", {})
            index_entry["summary_eva"] = turn_2.get("summary")
            index_entry["speaker_2"] = turn_2.get("speaker")

        if "state_snapshot" in episode:
            state = episode.get("state_snapshot", {})
            index_entry["resonance_index"] = state.get("Resonance_index")
            eva_matrix = state.get("EVA_matrix", {})
            index_entry["emotion_label"] = eva_matrix.get("emotion_label")

        # Load existing index
        if self.memory_index_file.exists():
            try:
                with open(self.memory_index_file, 'r', encoding='utf-8') as f:
                    memory_index = json.load(f)
            except:
                memory_index = {"episodes": []}
        else:
            memory_index = {"episodes": []}

        # Append new entry
        memory_index["episodes"].append(index_entry)

        # Keep only last 1000 entries (prevent bloat)
        if len(memory_index["episodes"]) > 1000:
            memory_index["episodes"] = memory_index["episodes"][-1000:]

        # Write back
        try:
            with open(self.memory_index_file, 'w', encoding='utf-8') as f:
                json.dump(memory_index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[MSP] Error updating memory_index: {e}")

    def _hash_short(self, text: str) -> str:
        """Generate short hash (8 chars)"""
        return hashlib.md5(text.encode()).hexdigest()[:8]

    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        total_episodes = len(list(self.episodes_dir.glob("ep_*.json")))

        # Count lines in JSONL
        jsonl_count = 0
        if self.episodic_log.exists():
            with open(self.episodic_log, 'r', encoding='utf-8') as f:
                jsonl_count = sum(1 for line in f if line.strip())

        return {
            "total_episodes": total_episodes,
            "jsonl_episodes": jsonl_count,
            "cached_episodes": len(self._episode_cache),
            "semantic_concepts": len(self._semantic_concepts),
            "cached_turns": len(self.turn_cache),
            "storage_path": str(self.root_path)
        }

    def clear_cache(self):
        """Clear in-memory cache"""
        self._episode_cache = []
        self._cache_loaded = False
        print("[MSP] Cache cleared")

    def reload(self):
        """Reload all data from disk"""
        self.clear_cache()
        self._load_semantic_concepts()
        self._load_turn_cache()
        self._load_cache()
        print("[MSP] Reloaded from disk")


if __name__ == "__main__":
    """Test MSP Client with Filesystem Persistence"""
    # Fix Windows console UTF-8 encoding
    import sys
    import codecs
    if sys.platform == 'win32':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

    print("="*60)
    print("Testing MSP Client with Filesystem Persistence")
    print("="*60)

    # Initialize
    msp = MSPClient()

    # Test 1: Write new episode
    print("\n--- Test 1: Write New Episode ---")
    episode_data = {
        "content": "ขอบคุณนะที่วันนี้มาส่งที่สนามบิน",
        "response": "ยินดีค่ะ บอส",
        "tags": ["gratitude", "airport"],
        "stimulus_vector": {
            "stress": 0.3,
            "warmth": 0.8,
            "arousal": 0.4,
            "valence": 0.9
        },
        "physio_state": {
            "cortisol": 0.3,
            "dopamine": 0.7,
            "oxytocin": 0.8,
            "ans_sympathetic": 0.3,
            "ans_parasympathetic": 0.7
        },
        "resonance_index": 0.75,
        "resonance_impact": 0.65,
        "qualia": {
            "intensity": 0.7,
            "tone": "warm",
            "texture": [0.8, 0.6, 0.5, 0.7, 0.4]
        }
    }
    episode_id = msp.write_episode(episode_data)
    print(f"Created episode: {episode_id}")

    # Test 2: Query by tags
    print("\n--- Test 2: Query by Tags ---")
    results = msp.query_by_tags(["gratitude"], max_results=3)
    print(f"Found {len(results)} episodes with tag 'gratitude'")
    for ep in results:
        content = ep.get("content", "")[:50]
        print(f"  - {ep['episode_id']}: {content}... (RI: {ep.get('resonance_index', 0)})")

    # Test 3: Query by physio similarity
    print("\n--- Test 3: Query by Physio Similarity ---")
    current_state = {
        "cortisol": 0.5,
        "dopamine": 0.6,
        "oxytocin": 0.7,
        "ans_sympathetic": 0.4
    }
    results = msp.query_by_physio_state(current_state, similarity_threshold=0.7)
    print(f"Found {len(results)} episodes with similar physio state")
    for ep in results:
        content = ep.get("content", "")[:50]
        similarity = ep.get("physio_similarity", 0)
        print(f"  - {ep['episode_id']}: {content}... (Similarity: {similarity:.2f})")

    # Test 4: Query recent
    print("\n--- Test 4: Query Recent Episodes ---")
    results = msp.query_recent(max_results=5)
    print(f"Found {len(results)} recent episodes")
    for ep in results:
        content = ep.get("content", "")[:50]
        recency = ep.get("recency_score", 0)
        print(f"  - {ep['episode_id']}: {content}... (Recency: {recency:.2f})")

    # Test 5: Turn cache
    print("\n--- Test 5: Turn Cache ---")
    msp.update_turn_cache("ctx_v8_260101_120000_abc123", "User thanked for airport ride")
    history = msp.get_recent_history(max_turns=3)
    print(f"Recent history: {len(history)} turns")
    for turn in history:
        print(f"  - {turn['context_id']}: {turn['summary']}")

    # Print stats
    print("\n--- Storage Statistics ---")
    stats = msp.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")

    print("\n✅ All tests completed!")
    print(f"\nData stored in: {msp.root_path}")
