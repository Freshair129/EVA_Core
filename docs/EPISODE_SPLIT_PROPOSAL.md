# Episode Split Proposal: User vs LLM Storage

**Goal:** Optimize I/O by splitting episodes into user-focused and llm-focused files

**Benefits:**
- Faster RAG queries (load only user input + metadata)
- Reduce memory footprint
- Enable selective retrieval

---

## 🎯 Proposal A: Separate Folders (User/LLM)

### Structure

```
01_Episodic_memory/
├── episodes_user/
│   └── ep_260101_xxx_user.json          # User turn + metadata
├── episodes_llm/
│   └── ep_260101_xxx_llm.json           # LLM turn + full state
└── episodic_log.jsonl                   # Index (unchanged)
```

### User File (Small, Fast)

**Path:** `episodes_user/ep_260101_xxx_user.json`

```json
{
  "episode_id": "ep_260101_xxx",
  "timestamp": "2026-01-01T16:00:00",
  "session_id": "abc123",
  "event_label": "gratitude_expressed",
  "episode_tag": "routine",
  "compression_meta": {
    "session_seq": 3,
    "core_seq": 1,
    "sphere_seq": 0
  },
  "situation_context": {
    "context_id": "ctx_v8_xxx",
    "interaction_mode": "casual",
    "stakes_level": "low",
    "time_pressure": "low"
  },
  "turn_1": {
    "speaker": "user",
    "raw_text": "ขอบคุณมากนะคะ",
    "summary": "ขอบคุณมากนะคะ",
    "affective_inference": {
      "emotion_signal": "gratitude",
      "intensity": 0.8,
      "confidence": 0.9
    },
    "semantic_frames": ["gratitude"],
    "salience_anchor": {
      "phrase": "ขอบคุณมากนะคะ",
      "Resonance_impact": 0.85
    }
  },
  "state_snapshot": {
    "EVA_matrix": {
      "stress_load": 0.2,
      "social_warmth": 0.8,
      "emotion_label": "gratitude"
    },
    "Resonance_index": 0.75
  }
}
```

**Size:** ~500-800 bytes (compact)

### LLM File (Larger)

**Path:** `episodes_llm/ep_260101_xxx_llm.json`

```json
{
  "episode_id": "ep_260101_xxx",
  "turn_2": {
    "speaker": "eva",
    "text_excerpt": "ยินดีค่ะบอส ดีใจที่ได้ช่วยเหลือค่ะ...",
    "summary": "ยินดีค่ะบอส ดีใจที่ได้ช่วยเหลือค่ะ...",
    "epistemic_mode": "assert"
  },
  "state_snapshot": {
    "Endocrine": {
      "ESC_H01_ADRENALINE": 0.3,
      "ESC_H02_CORTISOL": 0.2,
      "ESC_H09_OXYTOCIN": 0.8,
      ...
    },
    "memory_encoding_level": "L2_standard",
    "memory_color": "#F0E68C",
    "qualia": {
      "intensity": 0.7
    },
    "reflex": {
      "threat_level": 0.2
    }
  }
}
```

**Size:** ~2-5 KB (detailed physio state)

### Retrieval Pattern

```python
# Fast query: User input only
user_file = f"episodes_user/{episode_id}_user.json"
user_data = json.load(open(user_file))
# → Get tags, salience, emotion WITHOUT loading LLM response

# Full episode: Load both when needed
llm_file = f"episodes_llm/{episode_id}_llm.json"
llm_data = json.load(open(llm_file))
full_episode = {**user_data, **llm_data}
```

---

## 🎯 Proposal B: Main + Sidecar Pattern

### Structure

```
01_Episodic_memory/
├── episodes/
│   └── ep_260101_xxx.json               # User + lightweight metadata
├── episodes_full/
│   └── ep_260101_xxx_full.json          # Complete episode with LLM
└── episodic_log.jsonl                   # Index
```

### Main File (Always loaded)

**Path:** `episodes/ep_260101_xxx.json`

```json
{
  "episode_id": "ep_260101_xxx",
  "timestamp": "2026-01-01T16:00:00",
  "session_id": "abc123",
  "event_label": "gratitude_expressed",
  "episode_tag": "routine",
  "compression_meta": {...},
  "situation_context": {...},
  "turn_1": {...},  // Full user turn
  "turn_2_ref": "episodes_full/ep_260101_xxx_full.json",  // Reference only
  "state_snapshot_lite": {
    "EVA_matrix": {
      "emotion_label": "gratitude",
      "stress_load": 0.2
    },
    "Resonance_index": 0.75
  }
}
```

### Sidecar File (Load on demand)

**Path:** `episodes_full/ep_260101_xxx_full.json`

```json
{
  "episode_id": "ep_260101_xxx",
  "turn_2": {...},  // Full LLM response
  "state_snapshot": {
    "Endocrine": {...},  // All 23 hormones
    "Hemodynamics": {...},
    "qualia": {...},
    "reflex": {...}
  }
}
```

---

## 📊 Comparison

| Feature | Proposal A (Separate Folders) | Proposal B (Sidecar) |
|---------|-------------------------------|----------------------|
| **Query Speed** | ⚡⚡⚡ Fastest (minimal data) | ⚡⚡ Fast (light main file) |
| **Storage** | 2 files per episode | 2 files per episode |
| **Complexity** | Low (clean separation) | Medium (need references) |
| **Backward Compat** | Breaking change | Breaking change |
| **RAG Integration** | Easy (just query user folder) | Easy (query main folder) |

---

## 🎯 Recommendation: **Proposal A** (Separate Folders)

**Reasons:**
1. ✅ **Cleaner separation** - User vs LLM is conceptually clear
2. ✅ **RAG optimized** - HeptStreamRAG only needs user folder
3. ✅ **Simpler logic** - No reference tracking needed
4. ✅ **Future-proof** - Easy to add more splits (e.g., `episodes_physio/`)

---

## 🚧 Implementation Plan

### Phase 1: Update MSP Client Write

```python
def write_episode(self, episode_data: Dict[str, Any]) -> str:
    episode_id = generate_episode_id()

    # Split data
    user_data = {
        "episode_id": episode_id,
        "timestamp": timestamp,
        "session_id": episode_data["session_id"],
        "event_label": episode_data["event_label"],
        "episode_tag": episode_data["episode_tag"],
        "compression_meta": {...},
        "situation_context": episode_data["situation_context"],
        "turn_1": episode_data["turn_1"],
        "state_snapshot": {
            "EVA_matrix": episode_data["state_snapshot"]["EVA_matrix"],
            "Resonance_index": episode_data["state_snapshot"]["Resonance_index"]
        }
    }

    llm_data = {
        "episode_id": episode_id,
        "turn_2": episode_data["turn_2"],
        "state_snapshot": {
            "Endocrine": episode_data["state_snapshot"]["Endocrine"],
            "memory_encoding_level": episode_data["state_snapshot"]["memory_encoding_level"],
            "memory_color": episode_data["state_snapshot"]["memory_color"],
            "qualia": episode_data["state_snapshot"]["qualia"],
            "reflex": episode_data["state_snapshot"]["reflex"]
        }
    }

    # Write to separate folders
    user_file = self.episodes_user_dir / f"{episode_id}_user.json"
    llm_file = self.episodes_llm_dir / f"{episode_id}_llm.json"

    write_json(user_file, user_data)
    write_json(llm_file, llm_data)

    return episode_id
```

### Phase 2: Update Query Methods

```python
def query_by_tags(self, tags: List[str]) -> List[Dict]:
    matches = []

    # Only scan user files (fast!)
    for user_file in self.episodes_user_dir.glob("*_user.json"):
        user_data = json.load(open(user_file))

        if match_tags(user_data["turn_1"]["semantic_frames"], tags):
            matches.append(user_data)

    return matches

def get_full_episode(self, episode_id: str) -> Dict:
    # Load both files when needed
    user_file = self.episodes_user_dir / f"{episode_id}_user.json"
    llm_file = self.episodes_llm_dir / f"{episode_id}_llm.json"

    user_data = json.load(open(user_file))
    llm_data = json.load(open(llm_file))

    # Merge
    return {**user_data, **llm_data}
```

### Phase 3: Migrate Existing Episodes

```python
def migrate_episodes_to_split():
    old_dir = Path("01_Episodic_memory/episodes")

    for old_file in old_dir.glob("ep_*.json"):
        episode = json.load(open(old_file))

        # Extract user data
        user_data = extract_user_data(episode)
        llm_data = extract_llm_data(episode)

        # Write to new structure
        write_user_file(user_data)
        write_llm_file(llm_data)

        # Archive old file
        old_file.rename(f"episodes_archive/{old_file.name}")
```

---

## 📝 Schema Updates

### Memory Index

**No change needed** - memory_index.json already contains user-focused data

### Episodic Log (JSONL)

**No change needed** - still contains full index metadata

### HeptStreamRAG

**Update:** Query from `episodes_user/` instead of `episodes/`

```python
# Old
episodes = glob("episodes/ep_*.json")

# New
user_episodes = glob("episodes_user/ep_*_user.json")
```

---

## ⚠️ Migration Considerations

1. **Backward Compatibility**
   - Keep old `episodes/` folder as archive
   - MSP Client can read both old and new formats
   - Gradual migration: new episodes use split, old episodes stay

2. **Storage Impact**
   - Minimal increase (metadata duplication)
   - User files: ~500 bytes each
   - LLM files: ~2-5 KB each
   - **Total: Similar to current single file**

3. **Performance Gain**
   - RAG queries: **3-5x faster** (smaller files)
   - Memory usage: **50-70% reduction** (load only what's needed)
   - Cache efficiency: Better (user data stays in cache)

---

## 🎯 Decision Point

**Choose:**
- [ ] Proposal A: Separate Folders (User/LLM)
- [ ] Proposal B: Main + Sidecar
- [ ] Alternative idea?

**If approved, next steps:**
1. Implement split write logic
2. Update query methods
3. Test with existing HeptStreamRAG
4. Migrate old episodes (optional)
