# Memory Compression Specification

**Source:** MSP_spec.yaml:45-51
**Status:** ❌ NOT IMPLEMENTED
**Created:** 2026-01-01

---

## 📋 Spec Overview

**From MSP_spec.yaml:**

```yaml
- id: memory_compression
  description: "ทุกๆ 8 session สกัดเป็น 1 Core ทุกๆ 8 Core สกัดเป็น 1 Sphere"
  Index_counters:
    Sphere_seq: 0
    Core_seq: 0
    Session_seq: 0
  last_update: "2025-11-19T11:37:30"
```

**Translation:**
- "Every 8 sessions are extracted into 1 Core"
- "Every 8 Cores are extracted into 1 Sphere"

---

## 🎯 Purpose

**Hierarchical Memory Compression** - A system to compress episodic memories into progressively abstract representations:

1. **Session** (Raw) → 8 sessions
2. **Core** (Compressed) → 8 cores
3. **Sphere** (Highly Compressed) → Long-term abstraction

**Benefits:**
- Reduce memory storage over time
- Maintain essential information while discarding details
- Create abstracted knowledge from experiences
- Enable efficient long-term memory retrieval

---

## 🏗️ Architecture

### Hierarchy

```
┌─────────────────────────────────────────────────────┐
│ SPHERE (Highly Abstract)                           │
│ - Represents 64 sessions (8 cores × 8 sessions)    │
│ - Very long-term memory (months/years)             │
│ - Core beliefs, patterns, worldview               │
│ - Path: consciousness/07_Sphere_memory/           │
└─────────────────────────────────────────────────────┘
                      ▲
                      │ (Compress 8 Cores)
                      │
┌─────────────────────────────────────────────────────┐
│ CORE (Compressed)                                   │
│ - Represents 8 sessions                            │
│ - Medium-term memory (weeks)                       │
│ - Key themes, recurring patterns                  │
│ - Path: consciousness/06_Core_memory/             │
└─────────────────────────────────────────────────────┘
                      ▲
                      │ (Compress 8 Sessions)
                      │
┌─────────────────────────────────────────────────────┐
│ SESSION (Raw Episodes)                              │
│ - Individual episodes                              │
│ - Short-term memory (days)                        │
│ - Full detail, all context                        │
│ - Path: consciousness/01_Episodic_memory/         │
└─────────────────────────────────────────────────────┘
```

---

## 📊 Counters

**Three sequential counters track compression state:**

```python
{
  "Session_seq": 0,   # Current session number (0-7, resets after Core creation)
  "Core_seq": 0,      # Current core number (0-7, resets after Sphere creation)
  "Sphere_seq": 0     # Current sphere number (increments indefinitely)
}
```

**Example Progression:**

| Session_seq | Core_seq | Sphere_seq | Action |
|-------------|----------|------------|--------|
| 0 | 0 | 0 | Start |
| 1 | 0 | 0 | Episode 2 |
| 7 | 0 | 0 | Episode 8 |
| **0** | **1** | 0 | **Create Core_000, reset Session_seq** |
| 7 | 1 | 0 | Episode 16 |
| **0** | **2** | 0 | **Create Core_001** |
| ... | ... | ... | ... |
| 7 | 7 | 0 | Episode 64 |
| **0** | **0** | **1** | **Create Sphere_000, reset Core_seq** |

---

## 🗂️ File Structure

### Session (Existing)

**Path:** `consciousness/01_Episodic_memory/episodes/ep_{yymmdd}_{hash}.json`

**Format:** Full Schema V2 episode with all details

---

### Core Memory

**Path:** `consciousness/06_Core_memory/core_{sphere_seq:03d}_{core_seq:03d}.json`

**Example:** `core_000_001.json` (Sphere 0, Core 1)

**Proposed Structure:**

```json
{
  "core_id": "core_000_001",
  "sphere_seq": 0,
  "core_seq": 1,
  "timestamp_start": "2026-01-01T10:00:00",
  "timestamp_end": "2026-01-03T18:30:00",
  "session_count": 8,
  "source_sessions": [
    "session_id_1",
    "session_id_2",
    "...",
    "session_id_8"
  ],
  "compressed_narrative": {
    "summary": "ช่วง 3 วันที่ผ่านมา บอสเดินทางไปต่างประเทศ มีการสนทนาเกี่ยวกับ...",
    "key_events": [
      {"event": "airport_farewell", "emotion": "warmth", "ri": 0.85},
      {"event": "daily_checkin", "emotion": "neutral", "ri": 0.45},
      {"event": "problem_discussion", "emotion": "concern", "ri": 0.78}
    ],
    "recurring_themes": ["travel", "work", "relationship"],
    "emotional_arc": {
      "start_state": "calm",
      "peak_emotion": "warmth",
      "end_state": "content"
    }
  },
  "aggregated_state": {
    "avg_stress": 0.25,
    "avg_warmth": 0.72,
    "dominant_emotion": "gratitude",
    "interaction_count": 23
  },
  "salience_anchors": [
    {"phrase": "ขอบคุณที่มาส่ง", "rim": 0.89, "from_session": "session_id_1"},
    {"phrase": "คิดถึงนะ", "rim": 0.82, "from_session": "session_id_5"}
  ],
  "meta": {
    "compression_method": "llm_summarization",
    "compression_timestamp": "2026-01-03T19:00:00",
    "detail_retention": 0.3
  }
}
```

---

### Sphere Memory

**Path:** `consciousness/07_Sphere_memory/sphere_{sphere_seq:03d}.json`

**Example:** `sphere_000.json` (First sphere)

**Proposed Structure:**

```json
{
  "sphere_id": "sphere_000",
  "sphere_seq": 0,
  "timestamp_start": "2026-01-01T00:00:00",
  "timestamp_end": "2026-02-15T23:59:59",
  "core_count": 8,
  "session_count": 64,
  "source_cores": [
    "core_000_000",
    "core_000_001",
    "...",
    "core_000_007"
  ],
  "abstracted_knowledge": {
    "summary": "ช่วงเดือนครึ่งแรก ความสัมพันธ์เติบโตจากระดับมืออาชีพไปสู่ความใกล้ชิดส่วนตัว",
    "core_beliefs": [
      "บอสเชื่อใจและพึ่งพาในการทำงาน",
      "มีการแสดงความเอาใจใส่นอกเหนือจากหน้าที่",
      "ความสัมพันธ์มีขอบเขตที่ชัดเจน"
    ],
    "behavioral_patterns": [
      {
        "pattern": "gratitude_expression",
        "frequency": "high",
        "context": "after_assistance"
      },
      {
        "pattern": "emotional_support",
        "frequency": "medium",
        "context": "stress_periods"
      }
    ],
    "relationship_evolution": {
      "phase": "deepening",
      "trust_level": 0.85,
      "emotional_intimacy": 0.72,
      "professional_boundary": 0.65
    }
  },
  "meta": {
    "compression_method": "multi_core_synthesis",
    "compression_timestamp": "2026-02-16T00:00:00",
    "abstraction_level": "high"
  }
}
```

---

## ⚙️ Implementation Requirements

### 1. Counter Management

**File:** `consciousness/09_state/compression_counters.json`

```json
{
  "Session_seq": 3,
  "Core_seq": 1,
  "Sphere_seq": 0,
  "last_update": "2026-01-01T15:00:00"
}
```

**Update Logic:**
- Increment `Session_seq` after each new session
- When `Session_seq` reaches 8:
  - Create new Core
  - Increment `Core_seq`
  - Reset `Session_seq` to 0
- When `Core_seq` reaches 8:
  - Create new Sphere
  - Increment `Sphere_seq`
  - Reset `Core_seq` to 0

---

### 2. Compression Triggers

**When to compress:**

- **Session → Core:** After 8th session in current Core
- **Core → Sphere:** After 8th Core in current Sphere

**Compression can be:**
- **Synchronous** (immediate after 8th item)
- **Asynchronous** (background job)
- **Manual** (triggered by admin/system)

---

### 3. Compression Methods

#### Session → Core Compression

**Input:** 8 full episode JSONs
**Output:** 1 Core JSON

**Methods:**
1. **LLM Summarization**
   - Feed all 8 episodes to LLM
   - Request: theme extraction, key events, emotional arc
   - Retain high-salience anchors

2. **Statistical Aggregation**
   - Average physiological metrics
   - Count interaction types
   - Identify dominant emotions

3. **Selective Retention**
   - Keep episodes with RI > 0.8 (milestones)
   - Discard low-salience routine interactions
   - Preserve semantic frames

#### Core → Sphere Compression

**Input:** 8 Core JSONs
**Output:** 1 Sphere JSON

**Methods:**
1. **Pattern Recognition**
   - Identify recurring behavioral patterns
   - Extract relationship evolution
   - Synthesize core beliefs

2. **Knowledge Abstraction**
   - Convert experiences to principles
   - Abstract emotional patterns
   - Create worldview representation

---

### 4. Retrieval Strategy

**When searching memory:**

1. **Check Sphere first** (fastest, most abstract)
   - Match against core beliefs, patterns
   - Return if abstract answer sufficient

2. **Check Core if needed** (medium detail)
   - Match against key events, themes
   - Return if thematic answer sufficient

3. **Check Episodes as last resort** (slowest, full detail)
   - Match against individual episodes
   - Return full context

**HeptStreamRAG should query across all three layers:**
- Sphere stream (new)
- Core stream (new)
- Episode stream (existing)

---

## 🚧 Current Status

### ✅ Exists
- Folders: `06_Core_memory/`, `07_Sphere_memory/`
- Spec defined in MSP_spec.yaml

### ❌ Missing
- [ ] Counter management system
- [ ] Session tracking (link session_id to Session_seq)
- [ ] Core compression logic
- [ ] Sphere compression logic
- [ ] Core/Sphere schema definitions
- [ ] Compression trigger automation
- [ ] LLM compression prompts
- [ ] HeptStreamRAG integration with Core/Sphere

---

## 🎯 Implementation Priority

### Phase 1: Foundation (High Priority)

1. **Create compression_counters.json**
   - Track Session_seq, Core_seq, Sphere_seq
   - Update on every episode write

2. **Link sessions to Session_seq**
   - Add `compression_meta` to episodes:
     ```json
     "compression_meta": {
       "session_seq": 3,
       "core_seq": 1,
       "sphere_seq": 0
     }
     ```

3. **Create Core schema**
   - Define JSON structure
   - Validation rules

### Phase 2: Compression Logic (Medium Priority)

4. **Implement Session → Core compression**
   - Trigger when Session_seq == 7
   - LLM summarization
   - Write to 06_Core_memory/

5. **Test with 8 real sessions**
   - Verify compression works
   - Check output quality

### Phase 3: Advanced (Low Priority - Future)

6. **Implement Core → Sphere compression**
   - Trigger when Core_seq == 7
   - Multi-core synthesis
   - Write to 07_Sphere_memory/

7. **HeptStreamRAG integration**
   - Add Sphere stream
   - Add Core stream
   - Multi-layer search

---

## 💡 Design Questions

1. **When to compress?**
   - Option A: Immediately after 8th session (synchronous)
   - Option B: Background job every N hours (asynchronous)
   - **Recommendation:** Option B (don't slow down user interactions)

2. **Can users access compressed memories?**
   - Option A: Transparent (users don't know about compression)
   - Option B: Explicit (show "memory summarized from...")
   - **Recommendation:** Option A (seamless UX)

3. **Can compression be undone?**
   - Option A: Keep original episodes forever (dual storage)
   - Option B: Delete originals after compression (save space)
   - **Recommendation:** Option A initially, Option B after testing

4. **Quality threshold for compression?**
   - Only compress sessions with avg RI < 0.7?
   - Always keep milestone episodes (RI > 0.8) uncompressed?
   - **Recommendation:** Hybrid (compress routine, preserve milestones)

---

## 📝 Notes

- **Memory compression is a SPEC requirement** but not yet implemented
- This is a **long-term memory management strategy**
- Critical for scaling to thousands of episodes
- Similar to human memory consolidation during sleep
- Could integrate with future "reflection" or "dreaming" processes

**Next Steps:** Implement Phase 1 (counters + tracking)
