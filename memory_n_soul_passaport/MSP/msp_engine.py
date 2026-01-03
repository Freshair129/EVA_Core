import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from .utils import now_iso
from .episodic import EpisodicMemory
from .semantic import SemanticMemory
from .sensory import SensoryMemory

class MSP:
    """
    Memory & Soul Passport (Simplified for Testing)
    Direct database writes without Origin/Instance/Session complexity
    """
    def __init__(self, base_path: Path = None, validation_mode: str = "off", use_local: bool = True):
        if base_path is None:
            base_path = Path(__file__).parent.parent.parent
            
        # Ensure base_path is in path for Orchestrator imports
        import sys
        base_str = str(base_path)
        if base_str not in sys.path:
            sys.path.append(base_str)

        self.base_path = base_path
        self.validation_mode = validation_mode
        self.use_local = use_local
        
        # Simplified state
        self.session_id: Optional[str] = None
        self.episode_count: int = 0

        # Initialize Database Bridges (Only if not in local mode)
        self.vector_bridge = None
        self.mongo_bridge = None
        self.neo4j_bridge = None

        if not use_local:
            try:
                # TODO: Re-implement Remote Bridges in services layer
                # from Orchestrator.vector_bridge import VectorBridge
                # from Orchestrator.mongo_bridge import MongoBridge
                # from Orchestrator.neo4j_bridge import Neo4jBridge
                pass # self.vector_bridge = None
            except ImportError as e:
                print(f"[MSP] Warning: Bridge import failed: {e}")

        # Logic Modules
        self.episodic = EpisodicMemory(self)
        self.semantic = SemanticMemory(self)
        self.sensory = SensoryMemory(self)

        # Local Paths for Indexed Storage
        self.consciousness_path = self.base_path / "Consciousness"
        self.episodic_dir = self.consciousness_path / "01_Episodic_memory"
        self.episodes_path = self.episodic_dir / "episodes"
        self.episodic_index_path = self.episodic_dir / "episodic_index.jsonl"
        self.context_ledger_path = self.episodic_dir / "context_ledger.jsonl"

        if use_local:
            self.episodes_path.mkdir(parents=True, exist_ok=True)

        print(f"[MSP] Initialized ({'LOCAL' if use_local else 'REMOTE'} Mode)")
        if not use_local:
            if self.mongo_bridge and self.mongo_bridge.client:
                print("[MSP] MongoDB Integration: ACTIVE")
            if self.neo4j_bridge and self.neo4j_bridge.driver:
                print("[MSP] Neo4j Integration: ACTIVE")
        else:
            print(f"[MSP] Local Consciousness path: {self.consciousness_path}")

    # =========================================================================
    # FACADE METHODS (Delegated to Submodules)
    # =========================================================================

    def write_episode(self, episode_data: Dict[str, Any], ri_level: str = "L3") -> str:
        """Write episode to local file or database"""
        import json
        
        # Generate ID if not present
        if "episode_id" not in episode_data:
            episode_data["episode_id"] = f"ep_{uuid.uuid4().hex[:12]}"
        
        episode_id = episode_data["episode_id"]
        timestamp = episode_data.get("timestamp", now_iso())
        episode_data["timestamp"] = timestamp
        episode_data["session_id"] = self.session_id or "default"
        
        # Prepare text for embedding
        user_sum = episode_data.get("turn_1", {}).get("summary", "")
        eva_sum = episode_data.get("turn_2", {}).get("summary", "")
        full_text = f"User: {user_sum}\nEVA: {eva_sum}"
        
        # LOCAL MODE PERSISTENCE
        if self.use_local:
            # 1. Save Full Episode to Individual File
            file_path = self.episodes_path / f"{episode_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(episode_data, f, ensure_ascii=False, indent=2)
                
            # 2. Update Metadata Index (L0 Search Index)
            # Separate User and LLM summaries for indexing
            metadata = {
                "episode_id": episode_id,
                "timestamp": timestamp,
                "session_id": self.session_id or "default",
                "ri_level": ri_level,
                "resonance_index": episode_data.get("state_snapshot", {}).get("Resonance_index", 0.5),
                "emotion_label": episode_data.get("state_snapshot", {}).get("EVA_matrix", {}).get("emotion_label", "Neutral"),
                "context_id": episode_data.get("situation_context", {}).get("context_id", ""), 
                "episode_tag": episode_data.get("episode_tag", ""), # Episode Name
                "event_label": episode_data.get("event_label", ""), # Narrative Event
                "tags": episode_data.get("turn_1", {}).get("semantic_frames", []),
                "summary_user": user_sum,
                "summary_eva": eva_sum,
                "salience_anchor": episode_data.get("turn_1", {}).get("salience_anchor", {}).get("phrase", "")
            }
            
            with open(self.episodic_index_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(metadata, ensure_ascii=False) + "\n")
                
            print(f"[MSP] [OK] Episode {episode_id} Indexed and Saved.")
            self.episode_count += 1
            return episode_id

        # REMOTE MODE (Bridges)
        # Generate embedding
        embedding = None
        if self.vector_bridge and full_text.strip():
            embedding = self.vector_bridge.get_embedding(full_text)
        
        # 1. Write to MongoDB (Full Document)
        if self.mongo_bridge:
            success = self.mongo_bridge.insert_episode(episode_data, embedding)
            if success:
                print(f"[MSP] [OK] Episode {episode_id} -> MongoDB")
            else:
                print(f"[MSP] [FAILED] MongoDB write failed for {episode_id}")
        
        # 2. Write to Neo4j (Structural Node)
        if self.neo4j_bridge:
            try:
                self.neo4j_bridge.create_episode_node(episode_id, timestamp, f"{user_sum[:50]}...")
            except Exception as e:
                print(f"[MSP] [FAILED] Neo4j Episode Node creation failed: {e}")

        self.episode_count += 1
        return episode_id

    def write_semantic(self, concept: str, definition: str, episode_id: str, 
                      category: str = "Semantic", relation: str = "REFERENCED_IN") -> str:
        """Write semantic concept to local file or Neo4j"""
        import json
        semantic_id = f"sem_{uuid.uuid4().hex[:8]}"
        
        if self.use_local:
            log_path = self.base_path / "Consciousness" / "02_Semantic_memory" / "semantic_log.jsonl"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            entry = {
                "semantic_id": semantic_id,
                "concept": concept,
                "definition": definition,
                "episode_id": episode_id,
                "category": category,
                "relation": relation,
                "timestamp": now_iso()
            }
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            print(f"[MSP] [OK] Concept '{concept}' -> Local JSONL")
            return semantic_id

        # Write to Neo4j
        if self.neo4j_bridge:
            try:
                # Create concept node with definition
                self.neo4j_bridge.create_concept(concept, category, definition)
                # Link to episode
                if episode_id:
                    self.neo4j_bridge.link_to_episode(concept, episode_id, relation)
                print(f"[MSP] [OK] Concept '{concept}' -> Neo4j (Linked to {episode_id})")
            except Exception as e:
                print(f"[MSP] [FAILED] Neo4j semantic write failed: {e}")
        
        return semantic_id

    def write_sensory(self, episode_id: str, data_type: str, source_name: str, 
                     capture_channel: str, raw_content, feature_snapshot: Optional[Dict] = None,
                     capture_quality: str = "medium") -> str:
        """Write sensory data to local file or MongoDB"""
        import json
        sensory_id = f"sen_{uuid.uuid4().hex[:8]}"
        
        sensory_data = {
            "sensory_id": sensory_id,
            "episode_id": episode_id,
            "data_type": data_type,
            "source": source_name,
            "channel": capture_channel,
            "content": raw_content,
            "features": feature_snapshot,
            "quality": capture_quality,
            "timestamp": now_iso()
        }
        
        if self.use_local:
            log_path = self.base_path / "Consciousness" / "03_Sensory_memory" / "sensory_log.jsonl"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(sensory_data, ensure_ascii=False) + "\n")
            print(f"[MSP] [OK] Sensory {sensory_id} -> Local JSONL")
            return sensory_id

        if self.mongo_bridge:
            success = self.mongo_bridge.insert_sensory_data(sensory_data)
            if success:
                print(f"[MSP] [OK] Sensory {sensory_id} -> MongoDB (Sidecar)")
            else:
                print(f"[MSP] [FAILED] Sensory write failed for {sensory_id}")
                
        return sensory_id

    def write_state(self, episode_id: str, state_snapshot: Dict[str, Any]) -> bool:
        """Write consciousness state snapshot to local files or MongoDB"""
        from .utils import save_json
        
        if self.use_local:
            # We save the full snapshot to a session-based file in state history
            # But we also update the individual state files for quick turn load
            state_dir = self.base_path / "Consciousness" / "09_state"
            
            # 1. Update individual "live" files
            for key, val in state_snapshot.items():
                if isinstance(val, dict):
                    file_path = state_dir / f"{key}_state.json"
                    save_json(file_path, val)
            
            # 2. Log complete snapshot for this episode
            log_path = state_dir / "consciousness_history.jsonl"
            import json
            entry = {
                "episode_id": episode_id,
                "timestamp": now_iso(),
                "snapshot": state_snapshot
            }
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
            print(f"[MSP] [OK] State Snapshot -> Local Files")
            return True

        if not self.mongo_bridge: return False
        payload = {
            "episode_id": episode_id,
            "state": state_snapshot,
            "timestamp": now_iso()
        }
        success = self.mongo_bridge.insert_state_snapshot(payload)
        if success:
            print(f"[MSP] [OK] State Snapshot -> MongoDB (Sidecar)")
        else:
            print(f"[MSP] [FAILED] State snapshot write failed")
        return success

    def write_user_block(self, block_data: Dict[str, Any]) -> bool:
        """Write user profile block locally or to DB"""
        if self.use_local:
            from .utils import save_json
            block_id = block_data.get("block_id", "unknown_user")
            path = self.base_path / "Consciousness" / "08_User_block" / f"{block_id}.json"
            save_json(path, block_data)
            print(f"[MSP] [OK] User Block '{block_id}' Saved Locally")
            return True

        # Remote
        if self.mongo_bridge:
            self.mongo_bridge.insert_user_block(block_data)
        if self.neo4j_bridge:
            block_name = block_data.get("block_name", "Untitled Block")
            description = block_data.get("description", "")
            self.neo4j_bridge.create_concept(block_name, "UserBlock", description)
        print(f"[MSP] [OK] User Block '{block_data.get('block_id')}' Synced")
        return True

    def write_context(self, context_id: str, episode_id: str, step1_data: Dict[str, Any], step2_data: Dict[str, Any]) -> bool:
        """Write aggregated LLM context payloads to local storage or MongoDB"""
        import json
        
        context_entry = {
            "context_id": context_id,
            "episode_id": episode_id,
            "timestamp": now_iso(),
            "session_id": self.session_id or "default",
            "step_1": step1_data,
            "step_2": step2_data
        }
        
        if self.use_local:
            log_path = self.base_path / "Consciousness" / "10_context_storage" / "context_log.jsonl"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(context_entry, ensure_ascii=False) + "\n")
            print(f"[MSP] [OK] Context {context_id} -> Local JSONL")
            return True

        if self.mongo_bridge:
            # We assume the mongo_bridge has an insert_context_data method (to be added if needed)
            if hasattr(self.mongo_bridge, 'insert_context_data'):
                return self.mongo_bridge.insert_context_data(context_entry)
            else:
                # Fallback to general insertion if specific method missing
                return self.mongo_bridge.db.context_storage.insert_one(context_entry).acknowledged
        
        return False
            
    def write_core_memory(self, core_data: Dict[str, Any]) -> bool:
        """Write foundational belief/identity data to Core Memory"""
        if self.use_local:
            from .utils import save_json
            # Use core_id or a unique field as filename
            core_id = core_data.get("core_id", f"core_{uuid.uuid4().hex[:8]}")
            path = self.base_path / "Consciousness" / "06_Core_memory" / f"{core_id}.json"
            save_json(path, core_data)
            print(f"[MSP] [OK] Core Memory '{core_id}' Saved Locally")
            return True
        return False

    def write_sphere_memory(self, sphere_data: Dict[str, Any]) -> bool:
        """Write conceptual domain data to Sphere Memory"""
        if self.use_local:
            from .utils import save_json
            sphere_id = sphere_data.get("sphere_id", f"sphere_{uuid.uuid4().hex[:8]}")
            path = self.base_path / "Consciousness" / "07_Sphere_memory" / f"{sphere_id}.json"
            save_json(path, sphere_data)
            print(f"[MSP] [OK] Sphere Memory '{sphere_id}' Saved Locally")
            return True
        return False

    # =========================================================================
    # MODULE STATE REGISTRY (Central State Management)
    # =========================================================================

    def register_module_state(self, module_name: str, state_data: Dict[str, Any], 
                             metadata: Optional[Dict[str, Any]] = None, buffer_size: int = 10) -> bool:
        """
        Register or update a module's current operational state with three-tier persistence.
        
        **Three-Tier Architecture (Audit-Focused):**
        1. Current State: {module}_state.json (instant access)
        2. Recent Buffer: {module}_state_buffer.json (audit trail, NOT for display)
        3. Full History: {module}_state_history.jsonl (complete log)
        
        **Buffer Usage:**
        - Buffers are for AUDIT and DIAGNOSTIC purposes only
        - Only Physio Core and MSP access buffers for internal validation
        - NOT displayed to users or external systems (use get_dashboard_snapshot for that)
        
        Args:
            module_name: Unique module identifier (e.g., 'eva_matrix', 'physio_core')
            state_data: Module-specific state object
            metadata: Optional metadata (update_frequency, source, dependencies)
            buffer_size: Number of recent entries for audit (default: 10, reduced from 20)
        
        Returns:
            bool: Success/failure of state registration
        """
        if self.use_local:
            from .utils import save_json, load_json
            import json
            
            state_dir = self.base_path / "Consciousness" / "09_state"
            timestamp = now_iso()
            
            # Wrap state in standardized envelope
            state_envelope = {
                "module_name": module_name,
                "timestamp": timestamp,
                "state_data": state_data,
                "metadata": metadata or {}
            }
            
            try:
                # TIER 1: Current State (instant access)
                current_file = state_dir / f"{module_name}_state.json"
                save_json(current_file, state_envelope)
                
                # TIER 2: Recent Buffer (trend analysis)
                buffer_file = state_dir / f"{module_name}_state_buffer.json"
                buffer_data = load_json(buffer_file) or {
                    "module_name": module_name,
                    "buffer_size": buffer_size,
                    "entries": []
                }
                
                # Add new entry
                buffer_entry = {
                    "timestamp": timestamp,
                    "state_data": state_data
                }
                buffer_data["entries"].append(buffer_entry)
                
                # Rotate buffer (keep only last N entries)
                if len(buffer_data["entries"]) > buffer_size:
                    buffer_data["entries"] = buffer_data["entries"][-buffer_size:]
                
                buffer_data["last_updated"] = timestamp
                save_json(buffer_file, buffer_data)
                
                # TIER 3: Full History Log (archival)
                history_file = state_dir / f"{module_name}_state_history.jsonl"
                with open(history_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(state_envelope, ensure_ascii=False) + "\n")
                
                print(f"[MSP] [STATE REGISTRY] {module_name} → Current/Buffer/History")
                return True
                
            except Exception as e:
                print(f"[MSP] [ERROR] Failed to register state for {module_name}: {e}")
                return False
        return False

    def get_module_state(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the current state of a specific module.
        
        Args:
            module_name: Module identifier
            
        Returns:
            dict: Module state envelope or None if not found
        """
        if self.use_local:
            from .utils import load_json
            state_file = self.base_path / "Consciousness" / "09_state" / f"{module_name}_state.json"
            return load_json(state_file)
        return None

    def get_all_states(self) -> Dict[str, Any]:
        """
        Retrieve current state of all registered modules (system-wide snapshot).
        
        Returns:
            dict: {module_name: state_envelope}
        """
        all_states = {}
        if self.use_local:
            state_dir = self.base_path / "Consciousness" / "09_state"
            if state_dir.exists():
                from .utils import load_json
                for state_file in state_dir.glob("*_state.json"):
                    module_name = state_file.stem.replace("_state", "")
                    state_data = load_json(state_file)
                    if state_data:
                        all_states[module_name] = state_data
        return all_states

    def get_module_state_buffer(self, module_name: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve recent state buffer for a specific module (for trend analysis).
        
        Args:
            module_name: Module identifier
            limit: Max entries to return (None = all in buffer)
            
        Returns:
            list: Recent state entries (oldest first)
        """
        if self.use_local:
            from .utils import load_json
            buffer_file = self.base_path / "Consciousness" / "09_state" / f"{module_name}_state_buffer.json"
            buffer_data = load_json(buffer_file)
            
            if buffer_data and "entries" in buffer_data:
                entries = buffer_data["entries"]
                if limit:
                    return entries[-limit:]
                return entries
        return []

    def get_dashboard_snapshot(self, buffer_limit: int = 10, include_streaming: bool = True) -> Dict[str, Any]:
        """
        Get dashboard-ready snapshot: current states + recent trends + streaming metrics.
        
        Args:
            buffer_limit: Number of recent entries for regular state buffers
            include_streaming: Include high-frequency streaming buffers (hormones, heart rate)
            
        Returns:
            dict: {
                "timestamp": "...",
                "modules": {...},  # Regular state modules
                "streaming_metrics": {...}  # Dashboard streaming data (if enabled)
            }
        """
        dashboard_data = {
            "timestamp": now_iso(),
            "modules": {},
            "streaming_metrics": {} if include_streaming else None
        }
        
        if self.use_local:
            state_dir = self.base_path / "Consciousness" / "09_state"
            
            # Get all current states (existing logic)
            if state_dir.exists():
                from .utils import load_json
                
                for state_file in state_dir.glob("*_state.json"):
                    module_name = state_file.stem.replace("_state", "")
                    
                    # Skip buffer and history files
                    if module_name.endswith("_buffer") or module_name.endswith("_history"):
                        continue
                    
                    current_state = load_json(state_file)
                    buffer_entries = self.get_module_state_buffer(module_name, limit=buffer_limit)
                    
                    if current_state:
                        dashboard_data["modules"][module_name] = {
                            "current": current_state.get("state_data", {}),
                            "trend": buffer_entries,
                            "last_update": current_state.get("timestamp")
                        }
            
            # Get streaming metrics (NEW)
            if include_streaming:
                dashboard_stream_dir = state_dir / "dashboard_stream"
                if dashboard_stream_dir.exists():
                    from .utils import load_json
                    
                    for stream_file in dashboard_stream_dir.glob("*_dashboard.json"):
                        metric_name = stream_file.stem.replace("_dashboard", "")
                        metric_data = load_json(stream_file)
                        
                        if metric_data:
                            dashboard_data["streaming_metrics"][metric_name] = {
                                "category": metric_data.get("category"),
                                "values": [e["value"] for e in metric_data["buffer"]["entries"]],
                                "timestamps": [e["timestamp"] for e in metric_data["buffer"]["entries"]],
                                "buffer_size": metric_data["buffer"]["size"],
                                "last_update": metric_data["metadata"]["last_update"]
                            }
        
        return dashboard_data

    def register_dashboard_metric(self, metric_name: str, value: Any, 
                                  category: str = "physiological_stream",
                                  buffer_size: Optional[int] = None) -> bool:
        """
        Register real-time dashboard metric for streaming visualization.
        
        **SEPARATE from audit buffers** - optimized for high-frequency updates (30 Hz).
        Uses circular buffers for efficient memory management.
        
        Args:
            metric_name: Metric identifier (e.g., 'ESC_H01_ADRENALINE', 'heart_rate', 'emotion_label')
            value: Current metric value (number for hormones, string for labels)
            category: 'physiological_stream' or 'cognitive_state'
            buffer_size: Override default buffer size (900 for physiological, 20 for cognitive)
        
        Returns:
            bool: Success/failure
        """
        if not self.use_local:
            return False
        
        from .utils import load_json, save_json
        import time
        
        # Determine buffer size based on category
        if buffer_size is None:
            buffer_size = 900 if category == "physiological_stream" else 20
        
        dashboard_dir = self.base_path / "Consciousness" / "09_state" / "dashboard_stream"
        dashboard_dir.mkdir(exist_ok=True)
        
        metric_file = dashboard_dir / f"{metric_name}_dashboard.json"
        
        try:
            # Load existing buffer or create new
            buffer_data = load_json(metric_file) or {
                "metric_name": metric_name,
                "category": category,
                "buffer": {
                    "size": buffer_size,
                    "circular": True,
                    "entries": []
                },
                "metadata": {
                    "update_frequency": "30 Hz" if category == "physiological_stream" else "per-turn",
                    "last_update": None
                }
            }
            
            # Create new entry
            new_entry = {
                "timestamp": time.time(),
                "value": value
            }
            
            # Circular buffer rotation (FIFO)
            entries = buffer_data["buffer"]["entries"]
            entries.append(new_entry)
            
            # Keep only last N entries (circular buffer)
            if len(entries) > buffer_size:
                buffer_data["buffer"]["entries"] = entries[-buffer_size:]
            
            # Update metadata
            buffer_data["metadata"]["last_update"] = now_iso()
            
            # Persist
            save_json(metric_file, buffer_data)
            
            # Silent mode for 30 Hz updates (avoid console spam)
            if category != "physiological_stream":
                print(f"[MSP] [DASHBOARD] {metric_name} = {value}")
            
            return True
            
        except Exception as e:
            print(f"[MSP] [ERROR] Failed to register dashboard metric {metric_name}: {e}")
            return False

    # =========================================================================
    # SESSION LIFECYCLE (Simplified)
    # =========================================================================

    def start_session(self, session_id: str = None) -> str:
        """Start a simple session and log it"""
        if session_id is None:
            session_id = f"S_{datetime.now().strftime('%y%m%d_%H%M%S')}"
        
        self.session_id = session_id
        self.episode_count = 0
        
        if self.use_local:
            import json
            log_path = self.base_path / "Consciousness" / "04_Session_Memory" / "session_log.jsonl"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            entry = {
                "event": "session_start",
                "session_id": session_id,
                "timestamp": now_iso()
            }
            try:
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            except Exception as e:
                print(f"[MSP] Error logging session start: {e}")

        print(f"[MSP] Session started: {session_id}")
        return session_id

    def end_session(self) -> Dict[str, Any]:
        """End session and log it"""
        result = {
            "session_id": self.session_id,
            "episode_count": self.episode_count,
            "status": "ended"
        }
        
        if self.use_local and self.session_id:
            import json
            log_path = self.base_path / "Consciousness" / "04_Session_Memory" / "session_log.jsonl"
            try:
                entry = {
                    "event": "session_end",
                    "session_id": self.session_id,
                    "timestamp": now_iso(),
                    "stats": result
                }
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            except: pass

        print(f"[MSP] Session ended: {self.session_id} ({self.episode_count} episodes)")
        self.session_id = None
        self.episode_count = 0
        return result

    # =========================================================================
    # STATE PERSISTENCE (Simplified - for EVATool compatibility)
    # =========================================================================

    def get_state(self, key: str) -> Optional[Dict[str, Any]]:
        """Get state from local files if in local mode"""
        if self.use_local:
            from .utils import load_json
            path = self.base_path / "Consciousness" / "09_state" / f"{key}_state.json"
            return load_json(path)
        return None

    def set_state(self, key: str, value: Dict[str, Any]):
        """Set state to local files if in local mode"""
        if self.use_local:
            from .utils import save_json
            path = self.base_path / "Consciousness" / "09_state" / f"{key}_state.json"
            save_json(path, value)

    # =========================================================================
    # QUERY METHODS (Delegated to Episodic Memory)
    # =========================================================================

    def query_by_emotion_label(self, label: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Stream E: Quick search by emotional label"""
        if self.use_local:
            if not self.episodic_index_path.exists(): return []
            
            results = []
            import json
            try:
                with open(self.episodic_index_path, "r", encoding="utf-8") as f:
                    for line in f:
                        meta = json.loads(line.strip())
                        if meta.get("emotion_label", "").lower() == label.lower():
                            # Lazy load full data
                            results.append(self._load_episode(meta["episode_id"]))
                            if len(results) >= limit: break
            except: pass
            return results
        return []

    def query_by_emotion(self, emotion_vec: Dict[str, float], threshold: float = 0.6, limit: int = 5) -> List[Dict[str, Any]]:
        """Query episodes by emotion similarity (Indexed)"""
        if self.use_local:
            if not self.episodic_index_path.exists(): return []
            
            results = []
            import json
            try:
                with open(self.episodic_index_path, "r", encoding="utf-8") as f:
                    for line in f:
                        meta = json.loads(line.strip())
                        # Note: Vector similarity should technically be in index if we want it fast
                        # But label check is a good first pass or we load full file if threshold is low
                        # For now, let's assume we might need to load full to check vector in detail
                        # OR if we only store 'emotion_label' in index, we match on that.
                        if meta.get("emotion_label") == emotion_vec.get("emotion_label"):
                             results.append(self._load_episode(meta["episode_id"]))
                        
                        if len(results) >= limit: break
            except: pass
            return results

        return self.episodic.query_by_emotion(emotion_vec, threshold, limit)

    def query_by_tags(self, tags: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """Query episodes by semantic tags (Indexed)"""
        if self.use_local:
            if not self.episodic_index_path.exists(): return []
            
            results = []
            import json
            try:
                with open(self.episodic_index_path, "r", encoding="utf-8") as f:
                    for line in f:
                        meta = json.loads(line.strip())
                        ep_tags = meta.get("tags", [])
                        if any(tag.lower() in [t.lower() for t in ep_tags] for tag in tags):
                            results.append(self._load_episode(meta["episode_id"]))
                            if len(results) >= limit: break
            except: pass
            return results

        return self.episodic.query_by_tags(tags, limit)

    def query_by_salience(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Query episodes by salience (Indexed)"""
        if self.use_local:
            if not self.episodic_index_path.exists(): return []
            
            candidates = []
            import json
            try:
                with open(self.episodic_index_path, "r", encoding="utf-8") as f:
                    for line in f:
                         meta = json.loads(line.strip())
                         ri = meta.get("resonance_index", 0.0)
                         anchor = meta.get("salience_anchor", "")
                         
                         score = ri
                         if query.lower() in anchor.lower():
                             score += 0.5
                         
                         if score > 0.6:
                             candidates.append((score, meta["episode_id"]))
                    
                    candidates.sort(key=lambda x: x[0], reverse=True)
                    return [self._load_episode(c[1]) for c in candidates[:limit]]
            except: pass
            return []
        return []

    def query_by_event(self, event_label: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Query episodes belonging to a specific named event or narrative arc"""
        if self.use_local:
            if not self.episodic_index_path.exists(): return []
            results = []
            import json
            try:
                with open(self.episodic_index_path, "r", encoding="utf-8") as f:
                    for line in f:
                        meta = json.loads(line.strip())
                        if event_label.lower() in meta.get("event_label", "").lower():
                            results.append(self._load_episode(meta["episode_id"]))
                            if len(results) >= limit: break
            except: pass
            return results
        return []

    def query_by_episode_name(self, name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Query episodes by their specific tag/name"""
        if self.use_local:
            if not self.episodic_index_path.exists(): return []
            results = []
            import json
            try:
                with open(self.episodic_index_path, "r", encoding="utf-8") as f:
                    for line in f:
                        meta = json.loads(line.strip())
                        if name.lower() in meta.get("episode_tag", "").lower():
                            results.append(self._load_episode(meta["episode_id"]))
                            if len(results) >= limit: break
            except: pass
            return results
        return []

    def write_context(self, context_id: str, summary: str, metadata: Dict = None) -> bool:
        """Store a high-level summary of a completed task/context"""
        if self.use_local:
            import json
            payload = {
                "context_id": context_id,
                "summary": summary,
                "timestamp": now_iso(),
                "metadata": metadata or {}
            }
            try:
                with open(self.context_ledger_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(payload, ensure_ascii=False) + "\n")
                return True
            except: return False
        return False

    def get_context(self, context_id: str) -> Optional[Dict]:
        """Retrieve the cached summary of a specific context (Latest entry)"""
        if self.use_local:
            if not self.context_ledger_path.exists(): return None
            import json
            latest = None
            try:
                with open(self.context_ledger_path, "r", encoding="utf-8") as f:
                    for line in f:
                        data = json.loads(line.strip())
                        if data.get("context_id") == context_id:
                            latest = data
                return latest
            except: pass
        return None

    def query_reflections(self, query: str, limit: int = 5) -> List[Dict]:
        """Query the persistent context ledger for high-level reflections/summaries"""
        results = []
        if self.use_local:
            if not self.context_ledger_path.exists(): return []
            import json
            try:
                with open(self.context_ledger_path, "r", encoding="utf-8") as f:
                    for line in f:
                        data = json.loads(line.strip())
                        if query.lower() in data.get("summary", "").lower():
                            results.append(data)
                            if len(results) >= limit: break
            except: pass
        return results

    def get_recent_episodes(self, limit: int = 5) -> List[Dict]:
        """Retrieve the most recent episodes for Temporal Flow (Stream F)"""
        results = []
        if self.use_local:
            if not self.episodic_index_path.exists(): return []
            import json
            try:
                # Read lines and get last N
                with open(self.episodic_index_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    recent_meta = lines[-limit:]
                    for line in reversed(recent_meta):
                        meta = json.loads(line.strip())
                        episode = self._load_episode(meta["episode_id"])
                        if episode: results.append(episode)
            except: pass
        return results

    def get_episode_by_id(self, episode_id: str) -> Optional[Dict]:
        """Direct retrieval by ID for Parent-Child re-linking"""
        return self._load_episode(episode_id)

    def query_child_chunks(self, query: str, limit: int = 5) -> List[Dict]:
        """Mock implementation of child chunk retrieval (Directly searches recent text)"""
        # In a real vector DB, this would be a separate index
        # For local file mode, we fallback to searching recent episode summaries
        recent = self.get_recent_episodes(limit=limit*3)
        matches = []
        for ep in recent:
            txt = f"{ep.get('turn_1', {}).get('summary', '')} {ep.get('turn_2', {}).get('summary', '')}"
            if query.lower() in txt.lower():
                matches.append({
                    "parent_episode_id": ep.get("episode_id"),
                    "text": txt[:200]
                })
                if len(matches) >= limit: break
        return matches

    def query_by_pattern(self, emotion_label_sequence: List[str], limit: int = 3) -> List[Dict[str, Any]]:
        """Query episodes that FOLLOWED a specific emotional sequence (Indexed)"""
        if self.use_local:
            if not self.episodic_index_path.exists(): return []
            
            index_data = []
            import json
            try:
                with open(self.episodic_index_path, "r", encoding="utf-8") as f:
                    for line in f:
                        index_data.append(json.loads(line.strip()))
            except: pass
            
            if not index_data or len(emotion_label_sequence) < 1: return []
            
            results = []
            seq_len = len(emotion_label_sequence)
            
            for i in range(len(index_data) - seq_len):
                hist_seq = [m.get("emotion_label") for m in index_data[i : i + seq_len]]
                if hist_seq == emotion_label_sequence:
                    results.append(self._load_episode(index_data[i + seq_len]["episode_id"]))
                    if len(results) >= limit: break
            
            return results
        return []

    def _load_episode(self, episode_id: str) -> Dict[str, Any]:
        """Load full episode content from disk"""
        import json
        file_path = self.episodes_path / f"{episode_id}.json"
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {}

