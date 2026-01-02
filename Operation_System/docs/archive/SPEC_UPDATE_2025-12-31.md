# Specification Update - 2025-12-31

**Status:** ✅ **COMPLETED**
**Files Updated:** 2 specification files

---

## Overview

อัพเดทไฟล์ spec ทั้ง CIN และ Dual-Phase Orchestrator ให้สอดคล้องกับ CLAUDE.md และเพิ่มรายละเอียดที่จำเป็นสำหรับการ implement

---

## Files Updated

### 1. Context Injection Node Specifica 8.0.yaml

**Major Additions:**

#### a) Performance Targets (Section 2)
```yaml
phases:
  phase_1_perception:
    performance_target:
      latency: "<100ms"
      accuracy: "Low (surface-level, keyword matching)"
      purpose: "Bootstrap LLM perception with enough context to analyze"

  phase_2_reasoning:
    performance_target:
      latency: "~500ms"
      accuracy: "High (deep, emotion-congruent)"
      purpose: "Retrieve memories matching embodied state"
```

#### b) Fallback Behaviors
เพิ่ม fallback สำหรับทุก task:
- **PhysioController:** `status='disconnected'` if unavailable
- **MSP Client:** Return empty lists if unavailable
- **Persona:** Use embedded default if file not found
- **LLM:** Cached response or generic acknowledgment on timeout

#### c) Auto-Discovery Details
```yaml
- task: "Persona Priming"
  auto_discovery: "Search EVA 8.1.0/User_profile/ → EVA 8.0/User_profile/"
  fallback: "Use embedded default persona if file not found"
```

#### d) Emotion Stream Details
```yaml
- task: "Hept-Stream RAG Retrieval (MSP)"
  key_stream: "Emotion Stream (ความจำที่มีอารมณ์ตรงกับร่างกายปัจจุบัน)"
  emotion_stream_strategy:
    method: "Cosine similarity on physiological vectors"
    threshold: "0.7 (70% similarity)"
    vectors: "ans_sympathetic, cortisol, adrenaline, dopamine, serotonin"
  max_results_per_stream: 3
  temporal_decay: "Exponential decay with 30-day halflife"
```

#### e) Implementation Section (New Section 7)
- Class name: `ContextInjectionNode`
- File location: `orchestrator/cin.py`
- Key methods with signatures and latency targets
- Dependencies (required vs optional)
- Design principles

#### f) Integration Example (New Section 8)
Complete Python code example showing:
- CIN initialization
- Phase 1 injection
- LLM function calling
- The Gap processing
- Phase 2 injection
- Final response

#### g) Windows UTF-8 Fix (New Section 9)
```python
import sys
import codecs

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
```

---

### 2. Dual_Phase(One_Inference)_Orchestrator_spec.yaml

**Major Additions:**

#### a) Core Innovation Clarification (Metadata)
```yaml
metadata:
  core_innovation: "Single LLM inference with function calling (NOT two separate API calls)"
  memory_engine: "Hept-Stream RAG (7-dimensional affective retrieval)"
```

#### b) Detailed Gap Description
```yaml
inter_phase_gap:
  description: "LLM is paused, waiting for function result. Body state updates in real-time."
```

#### c) Complete 7-Stream Specification
แต่ละ stream มี:
- Description
- Strategy
- Threshold (if applicable)
- Importance level

**Emotion Stream** (highlighted as CRITICAL):
```yaml
- stream: "Emotion"
  description: "Emotion-congruent recall (KEY for embodied cognition)"
  strategy: "Cosine similarity on physio vectors (ANS, hormones)"
  threshold: "0.7 (70% similarity)"
  importance: "CRITICAL - enables 'remembering what it feels like'"
```

#### d) Performance Targets (New Section)
```yaml
performance:
  phase_1_latency:
    target: "<100ms"
    components:
      - "Physio baseline read: ~10ms"
      - "Rough history retrieval: ~30ms"
      - "Quick keyword recall: ~20ms"
      - "Semantic concepts: ~30ms"
      - "Prompt building: ~10ms"

  inter_phase_gap_latency:
    target: "~500ms total"
    components:
      - "PhysioController.step(): ~200-300ms"
      - "HeptStreamRAG.retrieve(): ~200-300ms"
      - "CIN Phase 2 injection: ~50ms"

  total_overhead:
    target: "~700ms (Phase 1 + Gap + Phase 2 prep)"
    note: "Excludes LLM inference time"
```

#### e) Critical Clarifications (New Section)

**One Inference, Not Two:**
```yaml
critical_clarifications:
  one_inference_not_two:
    wrong: "Two separate LLM API calls"
    correct: "ONE LLM inference with function calling"
    benefits:
      - "Persona continuity (LLM context not reset)"
      - "Cost efficiency (1 API call, not 2)"
      - "Natural flow (LLM 'pauses to feel and remember')"
```

**The Gap Timing:**
```yaml
the_gap_timing:
  key: "Body state changes DURING LLM inference, not before or after"
  sequence:
    - "LLM receives Phase 1 context"
    - "LLM analyzes and calls function"
    - "LLM PAUSED (waiting for function return)"
    - "PhysioController updates body state"
    - "HeptRAG retrieves memories based on NEW body state"
    - "Function returns with deep context"
    - "LLM RESUMES with enriched context"
    - "LLM generates final response"
```

**Emotion Stream Priority:**
```yaml
emotion_stream_priority:
  description: "Emotion Stream is MOST CRITICAL for embodied cognition"
  why: |
    Unlike semantic matching (keyword/concept similarity),
    Emotion Stream matches physiological signatures:
    - Current: cortisol=0.82, ans_sympathetic=0.75 (stressed)
    - Retrieve: Episodes with similar stress signatures
    - Result: Memories that "feel the same" in the body

  this_enables: "Affective resonance - remembering what it feels like"
```

#### f) Implementation Checklist (New Section)
```yaml
implementation_checklist:
  required_components:
    - name: "ContextInjectionNode (CIN)"
      status: "✅ Implemented"

    - name: "HeptStreamRAG"
      status: "✅ Implemented"

    - name: "LLM Bridge (Gemini)"
      status: "⏳ Pending"

    - name: "Main Orchestrator"
      status: "⏳ Pending"

    - name: "MSP Client"
      status: "⏳ Pending"

    - name: "PhysioController Adapter"
      status: "⏳ Pending"
```

---

## Key Improvements

### 1. Production Readiness

**Before:** Specs were conceptual
**After:** Specs include:
- Concrete latency targets
- Fallback behaviors
- Error handling strategies
- Integration examples

### 2. Implementation Guidance

**Before:** High-level architecture only
**After:** Includes:
- Exact method signatures
- File locations
- Dependency requirements
- Code examples

### 3. Critical Clarifications

**Before:** Could be misinterpreted as 2 LLM calls
**After:** Explicitly clarifies:
- ONE inference with function calling
- Timing of "The Gap"
- Importance of Emotion Stream

### 4. Performance Baselines

**Before:** No performance guidance
**After:** Clear targets:
- Phase 1: <100ms
- The Gap: ~500ms
- Total overhead: ~700ms

---

## Alignment with CLAUDE.md

Both spec files now align perfectly with CLAUDE.md:

| Aspect | CIN Spec | Orchestrator Spec | CLAUDE.md |
|:---|:---:|:---:|:---:|
| One Inference Pattern | ✅ | ✅ | ✅ |
| Performance Targets | ✅ | ✅ | ✅ |
| Hept-Stream Details | ✅ | ✅ | ✅ |
| Emotion Stream Priority | ✅ | ✅ | ✅ |
| Graceful Degradation | ✅ | ✅ | ✅ |
| Auto-Discovery | ✅ | - | ✅ |
| UTF-8 Encoding | ✅ | - | ✅ |
| Integration Example | ✅ | - | ✅ |
| Implementation Status | - | ✅ | ✅ |

---

## Benefits for Developers

### 1. Clear Implementation Path
- Know exactly what to implement (method signatures, return types)
- Understand performance expectations
- Have working code examples

### 2. Reduced Ambiguity
- No confusion about "2 LLM calls" vs "1 inference"
- Clear understanding of when body state changes
- Explicit fallback behaviors

### 3. Easier Debugging
- Performance targets help identify bottlenecks
- Error handling strategies prevent crashes
- Fallback behaviors enable graceful degradation

### 4. Better Testing
- Know what latency to expect
- Understand edge cases (PhysioController down, MSP unavailable)
- Have reference examples for integration tests

---

## Next Steps

### Immediate

1. **Use these specs to implement:**
   - LLM Bridge (`services/llm_bridge.py`)
   - Main Orchestrator (`orchestrator/chunking_orchestrator.py`)
   - MSP Client (`services/msp_client.py`)

2. **Validate against specs:**
   - Performance benchmarking
   - Fallback behavior testing
   - Integration testing

### Future

1. **Add more examples:**
   - Error scenarios
   - Edge cases
   - Performance optimization tips

2. **Create visual diagrams:**
   - Flow diagrams from specs
   - Sequence diagrams for The Gap
   - Component interaction diagrams

---

## Summary

**What Changed:**
- Added 6 new sections to CIN spec
- Added 3 new sections to Orchestrator spec
- Expanded existing sections with details

**Why It Matters:**
- Specs now production-ready
- Clear implementation guidance
- No ambiguity about architecture
- Performance targets defined

**Result:**
- Developers can implement with confidence
- Architecture clearly documented
- Alignment across all documentation

---

**Updated By:** Claude Sonnet 4.5
**Date:** 2025-12-31
**Status:** ✅ Complete & Validated
