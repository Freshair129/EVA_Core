# MSP Implementation Gap Analysis

**Generated:** 2026-01-01
**Comparison:** MSP_spec.yaml + MSP_Write_Policy.yaml vs Current Implementation

---

## ✅ Already Implemented

| Feature | Spec Location | Status |
|---------|--------------|--------|
| Episodic Memory (JSON files) | MSP_spec:18-22 | ✅ Implemented |
| Episodic Log (JSONL index) | MSP_Write_Policy:34-38 | ✅ Implemented |
| Semantic Memory (basic) | MSP_spec:24-27 | ✅ Basic implementation |
| Sensory Memory | MSP_spec:29-32 | ✅ Implemented |
| Schema V2 Structure | - | ✅ Just implemented |
| salience_anchor | MSP_Write_Policy:97 | ✅ Just added |

---

## ❌ Missing Implementation

### 1. Required Episode Fields

**Spec:** MSP_Write_Policy.yaml:77-85

```yaml
required_fields:
  - episode_id          # ✅ Have
  - timestamp           # ✅ Have
  - session_id          # ❌ MISSING
  - event_label         # ❌ MISSING
  - episode_tag         # ❌ MISSING (different from episode_type)
  - state_snapshot      # ✅ Have
  - turn_1              # ✅ Have
  - turn_2              # ✅ Have
```

**Current Implementation:**
- ❌ No `session_id` in episode structure
- ❌ No `event_label` (e.g., "gratitude_expressed", "question_asked")
- ❌ No `episode_tag` (e.g., "important", "trivial", "milestone")

**Impact:** Medium - These fields are required by spec but not critical for basic functionality

---

### 2. Index Fields for Search

**Spec:** MSP_Write_Policy.yaml:87-98

```yaml
index_fields:
  - episode_id          # ✅ Have
  - timestamp           # ✅ Have
  - resonance_index     # ✅ Have
  - emotion_label       # ✅ Have (in EVA_matrix)
  - event_label         # ❌ MISSING
  - episode_tag         # ❌ MISSING
  - tags                # ✅ Have (turn_1.semantic_frames)
  - summary_user        # ❌ MISSING (need extraction from turn_1)
  - summary_eva         # ❌ MISSING (need extraction from turn_2)
  - salience_anchor     # ✅ Have
  - speaker             # ✅ Have
```

**Current Implementation:**
- ✅ episodic_log.jsonl contains basic metadata
- ❌ No dedicated memory_index.json
- ❌ Missing summary_user/summary_eva in index

**Impact:** High - Affects RAG retrieval efficiency

---

### 3. Memory Index File

**Spec:** MSP_Write_Policy.yaml:40-43

```yaml
memory_index:
  description: "JSONL index for high-quality metadata querying"
  storage: "Consciousness/memory_index.json"
```

**Current Implementation:**
- ❌ No memory_index.json file
- ✅ Only episodic_log.jsonl exists

**Impact:** Medium - Current episodic_log.jsonl serves similar purpose, but not optimized

---

### 4. Context Storage

**Spec:** MSP_spec.yaml:39-43

```yaml
- id: CONTEXT_STORAGE
  path: "Consciousness/10_context_storage/"
  format: "JSON"
  purpose: "Real-time synchronization of context. Delivery by CIN"
```

**Current Implementation:**
- ❌ No 10_context_storage/ folder
- ❌ CIN doesn't persist context to disk
- ✅ Only turn_cache.json exists (in 10_state/)

**Impact:** Low - Context is ephemeral, but spec requires persistence

---

### 5. Consciousness State Storage

**Spec:** MSP_spec.yaml:34-37

```yaml
- id: CONSCIOUSNESS_STATE
  path: "Consciousness/09_state/"
  format: "JSON"
  purpose: "Real-time synchronization of body and physio_state"
```

**Current Implementation:**
- ❌ No 09_state/ folder
- ❌ No real-time state snapshots
- ✅ State is stored in episode state_snapshot only

**Impact:** Medium - Needed for continuous state tracking between episodes

---

### 6. Evidence Storage

**Spec:** MSP_Write_Policy.yaml:54-57

```yaml
Evidence:
  description: "บันทึกไฟล์ต่างๆเช่นภาพ วิดีโอ ไฟล์เสียง"
  storage: "Consciousness/03_Sensory_memory/Evidence/evidence_{sensory_id}.json"
```

**Current Implementation:**
- ❌ No Evidence/ subfolder
- ❌ No multimodal evidence handling

**Impact:** Low - Not currently needed (text-only system)

---

### 7. Write Strategy: Async Remote

**Spec:** MSP_spec.yaml:75-78

```yaml
persistence:
  write_strategy: "write-through (Local First -> Async Remote)"
  sync_on_episode_end: true
  auto_index_update: true
```

**Current Implementation:**
- ✅ Local write implemented
- ❌ No async remote write (MongoDB/Neo4j)
- ❌ No auto_index_update

**Impact:** High - Critical for production deployment

---

### 8. Database Bridges

**Spec:** MSP_spec.yaml:83-99

```yaml
bridges:
  mongo_bridge:
    db: "EVA_DATA"
    collections:
      episodes: "episodes_v8"
  neo4j_bridge:
    labels:
      episode: "Episode"
      concept: "Concept"
```

**Current Implementation:**
- ❌ No MongoDB connection
- ❌ No Neo4j connection
- ✅ Only local file storage

**Impact:** High - Required for semantic graph and deep archive

---

### 9. Retrieval Strategy Mismatch

**Spec:** MSP_spec.yaml:47-71 (Penta-Stream RAG)

```yaml
retrieval_strategies:
  - stream: narrativa
  - stream: salience
  - stream: sensory
  - stream: intuition
  - stream: emotion
```

**Current Implementation:**
- ✅ HeptStreamRAG (7 streams)
- ❌ Spec only defines 5 streams (Penta-Stream)

**Conflict:** Code has 7 streams, Spec has 5 streams

**Streams in code but not in spec:**
- Temporal stream
- Reflection stream

**Impact:** Low - Implementation is richer than spec (acceptable)

---

## 🔧 Recommended Implementation Priority

### Phase 1: Critical Missing Fields (High Priority)

1. ✅ **Add session_id to episodes**
   - Propagate from orchestrator
   - Required by spec

2. ✅ **Add event_label & episode_tag**
   - Auto-generate from emotion_signal
   - Required by spec

3. ✅ **Create memory_index.json**
   - Lightweight search index
   - Powers fast RAG

### Phase 2: Storage Structures (Medium Priority)

4. ⏳ **Create 09_state/ folder**
   - Real-time physio state snapshots
   - Update on every PhysioController.step()

5. ⏳ **Create 10_context_storage/ folder**
   - CIN context persistence
   - Write on every inject_phase_1()

### Phase 3: Database Integration (Low Priority - Future)

6. ⏳ **MongoDB Bridge**
   - Async write to episodes_v8
   - Deep archive

7. ⏳ **Neo4j Bridge**
   - Semantic graph relationships
   - Concept linking

---

## 📝 Notes

- **Spec Version:** MSP_spec.yaml v8.0.0, MSP_Write_Policy.yaml v7.2.5
- **Implementation Version:** EVA 8.1.0
- **Analysis Date:** 2026-01-01

The spec is authoritative but slightly outdated (refers to Penta-Stream when code uses Hept-Stream). Current implementation should:
1. Follow the spec for required fields
2. Keep the richer 7-stream RAG (superset of spec)
3. Add missing storage structures as needed
