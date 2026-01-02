# Specification Corrections - EVA 8.1.0

**Date:** 2025-12-31
**Status:** ✅ **CORRECTED**

---

## Issues Fixed

### 1. Memory Stream Count Mismatch ✅

**Issue:** CIN spec referenced "Penta-Stream" (5 streams) while Orchestrator spec and validated architecture use "Hept-Stream" (7 streams)

**Files affected:**
- `Context Injection Node Specifica 8.0.yaml`

**Changes made:**

**Line 45-46:** Updated RAG retrieval task
```yaml
# BEFORE
- task: "Penta-Stream RAG Retrieval (MSP)"
  description: "ค้นหาความจำผ่าน 5 สาย (Narrativa, Salience, Sensory, Intuition, Emotion) อิงตาม ANS State"

# AFTER
- task: "Hept-Stream RAG Retrieval (MSP)"
  description: "ค้นหาความจำผ่าน 7 สาย (Narrative, Salience, Sensory, Intuition, Emotion, Temporal, Reflection) อิงตาม ANS State"
```

**Line 70-71:** Updated Phase 2 template
```yaml
# BEFORE
- id: "Memory_Echoes"
  content: "## MSP_PENTA_STREAM_RECALL\n{memory_fragments_from_5_streams}"

# AFTER
- id: "Memory_Echoes"
  content: "## MSP_HEPT_STREAM_RECALL\n{memory_fragments_from_7_streams}"
```

**Line 125:** Updated invariant
```yaml
# BEFORE
- "MSP Primacy: การเรียกข้อมูลต้องผ่าน Penta-Stream Retrieval เสมอ"

# AFTER
- "MSP Primacy: การเรียกข้อมูลต้องผ่าน Hept-Stream Retrieval เสมอ"
```

---

### 2. Missing memory_cache Storage ✅

**Issue:** CIN spec didn't define storage mapping for `memory_cache` (context summaries)

**Files affected:**
- `Context Injection Node Specifica 8.0.yaml`

**Changes made:**

**Lines 93-98:** Added memory_cache to msp_storage_mapping
```yaml
# ADDED
memory_cache:
  collection: "turn_cache"
  data:
    - "summary (from LLM Phase 2 self-reflection)"
    - "tags (semantic markers for future retrieval)"
  purpose: "Fast context bootstrap for next turn's Phase 1"
```

**Rationale:**
- Orchestrator spec defines `memory_cache` with `summary` and `tags` fields (line 71-73)
- This cache is critical for Phase 1 rough retrieval (loads previous turn summary)
- Without this storage mapping, CIN wouldn't know where to persist/retrieve context summaries

---

### 3. Missing Response Weighting Rule ✅

**Issue:** CIN spec didn't document the Persona/Physio weighting rule

**Files affected:**
- `Context Injection Node Specifica 8.0.yaml`

**Changes made:**

**Lines 126-127:** Added two critical invariants
```yaml
# ADDED
- "Response Weighting: Persona 40% + Physio-State 60% (Physiology drives response more than identity)"
- "Two-Level Retrieval: Phase 1 rough/fast (keyword) + Phase 2 deep/accurate (emotion-congruent)"
```

**Rationale:**
- Orchestrator spec defines this weighting in `system_constraints` (line 78)
- This is fundamental to EVA's "Physiology first. Cognition later." principle
- CIN needs to enforce this during context injection

---

### 4. Context ID Format Inconsistency ✅

**Issue:** Different context_id formats between specs

**Files affected:**
- `Dual_Phase(One_Inference)_Orchestrator_spec.yaml`

**Changes made:**

**Lines 14-15:** Standardized to CIN's format
```yaml
# BEFORE
generation_rule: "UUID-v4 per User Interaction Turn"

# AFTER
generation_rule: "ctx_v8_{yymmdd}_{hhmmss}_{hash_short} per User Interaction Turn"
format_example: "ctx_v8_251231_183045_a1b2c3"
```

**Rationale:**
- CIN spec already defined detailed format: `ctx_v8_{timestamp}_{uuid_short}`
- ARCHITECTURE_FLOW_VALIDATED.md uses this format in examples
- More human-readable and traceable than raw UUID-v4
- Includes version marker (v8) for future compatibility

---

## Validation Status

| Aspect | Before | After | Status |
|:---|:---|:---|:---:|
| Memory Streams | 5 (Penta) | 7 (Hept) | ✅ Fixed |
| memory_cache Storage | Missing | Defined | ✅ Fixed |
| Response Weighting | Not documented | Persona 40% + Physio 60% | ✅ Fixed |
| Context ID Format | Inconsistent (UUID-v4 vs custom) | Standardized (ctx_v8_...) | ✅ Fixed |
| Phase 1 Template | Correct | Correct | ✅ OK |
| Phase 2 Template | Penta-Stream | Hept-Stream | ✅ Fixed |
| Function Specs | Correct | Correct | ✅ OK |
| Error Handling | Correct | Correct | ✅ OK |

---

## The 7 Memory Streams (Hept-Stream RAG)

For reference, the complete list of memory retrieval streams:

1. **Narrative Stream** - Sequential episode chains, storylines
2. **Salience Stream** - High-impact, unforgettable memories (RI-weighted)
3. **Sensory Stream** - Sensory-rich memories (qualia texture vectors)
4. **Intuition Stream** - Pattern recognition, semantic graph structures
5. **Emotion Stream** - Emotion-congruent memories (ANS State matching) **[KEY for affective recall]**
6. **Temporal Stream** - Time-based context (recent vs distant)
7. **Reflection Stream** - Meta-cognitive insights, self-understanding

---

## Next Steps

✅ **Specs are now consistent and validated**

**Ready for implementation:**
1. Create `orchestrator/cin.py` - Context Injection Node implementation
2. Create `orchestrator/chunking_orchestrator.py` - Main orchestrator
3. Create `services/hept_stream_rag.py` - 7-stream memory retrieval
4. Create `services/llm_bridge.py` - Gemini API wrapper with function calling

---

**Last Updated:** 2025-12-31
**Status:** ✅ ALL CORRECTIONS APPLIED
**Validation:** Specs align with ARCHITECTURE_FLOW_VALIDATED.md
