from pathlib import Path
from typing import Dict, Any, List, Optional

class EpisodicMemory:
    """Simplified Episodic Memory - delegates to MSP core"""
    def __init__(self, msp):
        self.msp = msp

    def write(self, episode_data: Dict[str, Any], ri_level: str = "L3") -> str:
        """Delegate to MSP core"""
        return self.msp.write_episode(episode_data, ri_level)

    def write_texture(self, episode_id: str, texture_data: Dict[str, float]):
        """Store emotion texture in sensory sidecar"""
        return self.msp.sensory.write_texture(episode_id, texture_data)

    def write_embedding(self, episode_id: str, user_text: str, eva_text: str, model: str = "qwen3-embedding:0.6b"):
        """Placeholder - handled by MSP core now"""
        print(f"[EpisodicMemory] Embedding for {episode_id} (handled by MSP core)")

    def query_by_emotion(self, emotion_vec: Dict[str, float], threshold: float = 0.6, limit: int = 5):
        """Query episodes by emotion similarity via MongoBridge"""
        if self.msp.mongo_bridge:
            return self.msp.mongo_bridge.query_episodes_by_emotion_state(emotion_vec, limit)
        return []

    def query_by_tags(self, tags: List[str], limit: int = 5):
        """Query episodes by semantic tags via MongoBridge"""
        if self.msp.mongo_bridge:
            return self.msp.mongo_bridge.query_episodes_by_tags(tags, limit)
        return []
