import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# Try to import OllamaBridge for vector similarity
try:
    from services.ollama_bridge import OllamaBridge
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

class MSPClient:
    """
    Local MSP (Memory & Soul Passport) Client.
    Manages episodic memory using episodic_log.jsonl in the local filesystem.
    """
    def __init__(self, root_path: str = None):
        if root_path is None:
            # Default to EVA 8.1.0/Consciousness
            self.root_path = Path(__file__).parent.parent / "Consciousness"
        else:
            self.root_path = Path(root_path)
            
        self.episodic_path = self.root_path / "01_Episodic_memory" / "episodic_log.jsonl"
        self.semantic_path = self.root_path / "02_Semantic_memory" / "Semantic_memory.json"
        
        # Ensure directories exist
        self.episodic_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize Ollama if available
        self.ollama = OllamaBridge() if OLLAMA_AVAILABLE else None
        
        # In-memory session cache
        self.turn_cache = {}

    def _read_episodes(self) -> List[Dict[str, Any]]:
        """Read all episodes from logical log file."""
        episodes = []
        if not self.episodic_path.exists():
            return []
            
        with open(self.episodic_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        episodes.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return episodes

    def query_recent(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve most recent episodes."""
        episodes = self._read_episodes()
        return episodes[-limit:][::-1]

    def query_by_tags(self, tags: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """Filter episodes by matching any of the tags."""
        episodes = self._read_episodes()
        matches = []
        tags_set = {t.lower() for t in tags}
        
        for ep in episodes:
            ep_tags = {t.lower() for t in ep.get("tags", [])}
            if tags_set & ep_tags:
                matches.append(ep)
        
        return matches[-limit:][::-1]

    def query_by_physio_state(self, physio_query: Dict[str, float], similarity_threshold: float = 0.8, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Emotion Stream: Find episodes with similar physiological states.
        Uses simple distance/similarity on state_snapshot.
        """
        episodes = self._read_episodes()
        matches_with_scores = []
        
        for ep in episodes:
            snapshot = ep.get("state_snapshot", {})
            if not snapshot:
                continue
                
            # Calculate simple Euclidean similarity for keys present in both
            common_keys = set(physio_query.keys()) & set(snapshot.keys())
            if not common_keys:
                continue
                
            dist_sq = 0
            for k in common_keys:
                dist_sq += (physio_query[k] - snapshot[k])**2
            
            similarity = 1.0 / (1.0 + (dist_sq**0.5))
            
            if similarity >= similarity_threshold:
                matches_with_scores.append((ep, similarity))
        
        # Sort by similarity
        matches_with_scores.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in matches_with_scores[:limit]]

    def _scrub_data(self, obj: Any) -> Any:
        """Force convert anything to JSON-serializable types."""
        if isinstance(obj, dict):
            return {str(k): self._scrub_data(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._scrub_data(x) for x in obj]
        elif isinstance(obj, (int, float, bool, str)) or obj is None:
            return obj
        # Try to convert to dict if it's a protobuf/dataclass, else str
        if hasattr(obj, "to_dict"):
            try: return self._scrub_data(obj.to_dict())
            except: pass
        try:
            # Handle MapComposite/RepeatedComposite from protobuf
            if hasattr(obj, "items"):
                return {str(k): self._scrub_data(v) for k, v in obj.items()}
            if hasattr(obj, "__iter__"):
                return [self._scrub_data(x) for x in obj]
        except:
            pass
        return str(obj)

    def write_episode(self, episode_data: Dict[str, Any]) -> str:
        """Append a new episode to the local log file."""
        # Generate ID if not present
        if "episode_id" not in episode_data:
            timestamp = datetime.now().isoformat()
            episode_data["episode_id"] = f"ep_{hashlib.md5(timestamp.encode()).hexdigest()[:8]}"
        
        if "timestamp" not in episode_data:
            episode_data["timestamp"] = datetime.now().isoformat()
            
        # Ensure all data is JSON serializable
        clean_data = self._scrub_data(episode_data)
        
        try:
            with open(self.episodic_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(clean_data, ensure_ascii=False) + "\n")
            return episode_data["episode_id"]
        except Exception as e:
            print(f"[MSP] Write error: {e}")
            return f"Error: {e}"

    def update_turn_cache(self, context_id: str, summary: str):
        """Update temporal session cache."""
        self.turn_cache[context_id] = {
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }

    def get_stats(self) -> Dict[str, Any]:
        """Return local file stats."""
        episodes = self._read_episodes()
        return {
            "total_episodes": len(episodes),
            "file_size_bytes": os.path.getsize(self.episodic_path) if self.episodic_path.exists() else 0,
            "storage_mode": "local_filesystem"
        }

    def query_narrative_chain(self, tags: List[str], limit: int = 3) -> List[Dict[str, Any]]:
        """Narrative Stream: Find episodes related by context/tags in sequence."""
        # Simple implementation: filter by tags and return most recent
        return self.query_by_tags(tags, limit=limit)

    def query_by_salience(self, tags: List[str], min_ri: float = 0.7, limit: int = 3) -> List[Dict[str, Any]]:
        """Salience Stream: Find high-impact memories."""
        episodes = self._read_episodes()
        matches = []
        for ep in episodes:
            if ep.get("resonance_index", 0) >= min_ri:
                matches.append(ep)
        return matches[-limit:][::-1]

    def query_sensory_memories(self, tags: List[str], min_qualia_intensity: float = 0.6, limit: int = 3) -> List[Dict[str, Any]]:
        """Sensory Stream: Find memories with high sensory detail."""
        episodes = self._read_episodes()
        matches = []
        for ep in episodes:
            if ep.get("qualia", {}).get("intensity", 0) >= min_qualia_intensity:
                matches.append(ep)
        return matches[-limit:][::-1]

    def query_semantic_patterns(self, tags: List[str], pattern_type: str = "structural", limit: int = 3) -> List[Dict[str, Any]]:
        """Intuition Stream: Pattern recognition query."""
        # Stub for now: filter by tags
        return self.query_by_tags(tags, limit=limit)

    def query_recent_episodes(self, tags: List[str], within_days: int = 30, limit: int = 3) -> List[Dict[str, Any]]:
        """Temporal Stream: Find recent episodes within a timeframe."""
        episodes = self._read_episodes()
        cutoff = datetime.now() - timedelta(days=within_days)
        matches = []
        for ep in episodes:
            try:
                ts = datetime.fromisoformat(ep.get("timestamp"))
                if ts >= cutoff:
                    matches.append(ep)
            except:
                continue
        return matches[-limit:][::-1]

    def query_reflections(self, tags: List[str], reflection_type: str = "self_understanding", limit: int = 3) -> List[Dict[str, Any]]:
        """Reflection Stream: Meta-cognitive insights."""
        # Stub: filter by tags
        return self.query_by_tags(tags, limit=limit)

    def get_recent_episodes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Alias for CIN compatibility."""
        return self.query_recent(limit=limit)

    def keyword_search(self, keywords: List[str], limit: int = 3) -> List[Dict[str, Any]]:
        """Search episodes by keywords in user_input or summary."""
        episodes = self._read_episodes()
        matches = []
        kw_set = {k.lower() for k in keywords}
        
        for ep in episodes:
            text = (ep.get("user_input", "") + " " + ep.get("summary", "")).lower()
            if any(k in text for k in kw_set):
                matches.append(ep)
        
        return matches[-limit:][::-1]

    def get_concepts(self, keywords: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve semantic concepts from local semantic memory file."""
        if not self.semantic_path.exists():
            return []
            
        try:
            with open(self.semantic_path, "r", encoding="utf-8") as f:
                concepts_data = json.load(f)
                
            # Filter concepts that match keywords
            matches = []
            kw_set = {k.lower() for k in keywords}
            
            # Assuming concepts_data is a list of dicts with 'concept' field
            for c in concepts_data:
                if any(k in c.get("concept", "").lower() for k in kw_set):
                    matches.append(c)
            
            return matches[:limit]
        except:
            return []

if __name__ == "__main__":
    msp = MSPClient()
    stats = msp.get_stats()
    print(f"Stats: {stats}")
    
    recent = msp.query_recent(3)
    print(f"Read {len(recent)} recent episodes.")
    for ep in recent:
        print(f" - {ep.get('timestamp')}: {ep.get('user_input')[:30]}...")
        
    # Test Write
    test_id = msp.write_episode({
        "user_input": "Test Local RAG Write",
        "eva_response": "Recording to filesystem successfully.",
        "tags": ["test", "local"],
        "state_snapshot": {"stress": 0.1, "warmth": 0.5}
    })
    print(f"Wrote test episode with ID: {test_id}")
