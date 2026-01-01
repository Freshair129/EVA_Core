# EVA 8.1.0 Architecture Flow - Validated

**Date:** 2025-12-31
**Status:** ✅ **VALIDATED - CORRECT UNDERSTANDING**

---

## Complete Flow Diagram

```
User Input: "วันนี้เครียดมาก งานเยอะอะ"
    ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: PERCEPTION (Deterministic - No LLM Decision)       │
└──────────────────┬──────────────────────────────────────────┘
                   │
    ┌──────────────▼──────────────┐
    │ 1.1 Context ID Generation   │
    │ ctx_v8_251231_183045_a1b2c3 │
    └──────────────┬──────────────┘
                   │
    ┌──────────────▼─────────────────────────────────┐
    │ 1.2 CIN Rough Retrieval (Fast/Deterministic)   │
    │ ✅ Physio Baseline                             │
    │    → อ่านจาก PhysioController                  │
    │    → Blood levels, ANS state (ณ ขณะนั้น)      │
    │                                                 │
    │ ✅ Rough History                               │
    │    → ดึง 5 เทิร์นล่าสุดจาก MSP_EPISODIC        │
    │    → Summaries only (not deep)                 │
    │                                                 │
    │ ✅ Quick Keyword Recall                        │
    │    → Keyword matching (simple/fast)            │
    │    → ค้นหาความจำแบบผิวเผิน                      │
    └──────────────┬─────────────────────────────────┘
                   │
    ┌──────────────▼──────────────────────────┐
    │ 1.3 Prompt Injection (Phase 1 Template)│
    │ Combine:                                │
    │ • Persona_01.md                         │
    │ • Physio Baseline                       │
    │ • Rough History (5 turns)               │
    │ • Quick Keyword Recall                  │
    │ • User Input (raw)                      │
    └──────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│ 2. THE BRIDGE: COGNITIVE TRIGGER                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
    ┌──────────────▼─────────────────────────────┐
    │ 2.1 LLM Perception (Step 1)               │
    │ • รับ Phase 1 context                      │
    │ • วิเคราะห์ intent                         │
    │ • วิเคราะห์ emotion                        │
    │ • ยังไม่ตอบผู้ใช้!                         │
    └──────────────┬─────────────────────────────┘
                   │
    ┌──────────────▼─────────────────────────────┐
    │ 2.2 LLM Targeting (Function Call)         │
    │ sync_biocognitive_state(                   │
    │   stimulus_vector={                        │
    │     valence: -0.7,                         │
    │     arousal: 0.8,                          │
    │     intensity: 0.9                         │
    │   },                                       │
    │   tags=["stress", "work_overload",         │
    │         "emotional_support"]               │
    │ )                                          │
    └──────────────┬─────────────────────────────┘
                   │
                   │ [LLM paused - waiting for function result]
                   │
┌──────────────────▼──────────────────────────────────────────┐
│ 3. THE GAP: REAL-TIME PROCESSING (Outside LLM)              │
└──────────────────┬──────────────────────────────────────────┘
                   │
    ┌──────────────▼──────────────────────────────┐
    │ 3.1 Physio Streaming (30Hz Simulation)     │
    │ PhysioController.step():                    │
    │                                             │
    │ ① Apply stimulus → HPA Regulator           │
    │    • HPA modulates stimulus                 │
    │    • Circadian rhythm affects response      │
    │                                             │
    │ ② Endocrine Production                      │
    │    • Glands secrete hormones (pg)           │
    │    • Nerve surge (reflex) if high intensity │
    │                                             │
    │ ③ Blood Transport                           │
    │    • Blood Engine updates concentration     │
    │    • Clearance & decay (half-life)          │
    │                                             │
    │ ④ Receptor Transduction                     │
    │    • Receptors bind hormones                │
    │    • Generate neural signals                │
    │                                             │
    │ ⑤ Autonomic Response                        │
    │    • ANS integration (Sympathetic/Para)     │
    │    • Output: Updated ANS State              │
    │                                             │
    │ Result: Body state changed!                 │
    │ • Cortisol: 0.45 → 0.82 ⚡                  │
    │ • Adrenaline: 0.15 → 0.65 ⚡                │
    │ • ANS Sympathetic: 0.3 → 0.75 ⚡            │
    └──────────────┬──────────────────────────────┘
                   │
    ┌──────────────▼────────────────────────────────────┐
    │ 3.2 Hept-Stream RAG (Deep Memory Retrieval)      │
    │ Input:                                            │
    │ • Updated ANS State (Sympathetic: 0.75)           │
    │ • Receptor Signals (Cortisol high)                │
    │ • Tags from LLM: ["stress", "work_overload", ...] │
    │                                                   │
    │ Query 7 Streams:                                  │
    │                                                   │
    │ ① Narrative Stream                                │
    │    → เรื่องราวต่อเนื่อง (sequential episodes)      │
    │    → ความจำที่เป็นเหตุเป็นผล                       │
    │                                                   │
    │ ② Salience Stream                                 │
    │    → ความจำที่ฝังใจ/สำคัญ (high RI score)          │
    │    → เหตุการณ์ที่ไม่ลืม                            │
    │                                                   │
    │ ③ Sensory Stream                                  │
    │    → ความรู้สึกทางประสาทสัมผัส                      │
    │    → Qualia texture vectors                       │
    │                                                   │
    │ ④ Intuition Stream                                │
    │    → ความรู้เชิงโครงสร้าง/รูปแบบ                   │
    │    → Semantic graph patterns                      │
    │                                                   │
    │ ⑤ Emotion Stream (KEY!)                           │
    │    → ความจำที่มีอารมณ์ตรงกับร่างกายปัจจุบัน         │
    │    → Match: ANS Sympathetic 0.75 (stressed)       │
    │    → Find: Episodes with similar stress signature │
    │                                                   │
    │ ⑥ Temporal Stream                                 │
    │    → บริบทของเวลา (time-based)                    │
    │    → Recent vs distant memories                   │
    │                                                   │
    │ ⑦ Reflection Stream                               │
    │    → บทสรุปและความเข้าใจตนเอง                      │
    │    → Meta-cognitive insights                      │
    │                                                   │
    │ Output: Memory Matches [...]                      │
    └──────────────┬────────────────────────────────────┘
                   │
    ┌──────────────▼─────────────────────────────┐
    │ 3.3 CIN Deep Re-Injection Preparation      │
    │ Build Phase 2 Context:                     │
    │                                            │
    │ • embodied_sensation:                      │
    │   "EVA รู้สึกเครียด หัวใจเต้นเร็ว         │
    │    มีความตึงเครียดในร่างกาย"              │
    │                                            │
    │ • physio_metrics:                          │
    │   {cortisol: 0.82,                         │
    │    adrenaline: 0.65,                       │
    │    heart_rate_index: 1.25,                 │
    │    ans_sympathetic: 0.75}                  │
    │                                            │
    │ • memory_matches: [                        │
    │     {stream: "emotion",                    │
    │      content: "ครั้งที่แล้วเครียดเหมือนกัน │
    │                จากงานที่ต้องส่งเยอะ",      │
    │      score: 0.89},                         │
    │     {stream: "narrative",                  │
    │      content: "เคยบอกว่าจะแบ่งงาน         │
    │                เป็นขั้นตอนเล็กๆ",          │
    │      score: 0.76},                         │
    │     ...                                    │
    │   ]                                        │
    └──────────────┬─────────────────────────────┘
                   │
    ┌──────────────▼──────────────────────────────┐
    │ 3.4 Return Function Result                  │
    │ {                                           │
    │   status: "success",                        │
    │   embodied_sensation: "...",                │
    │   physio_metrics: {...},                    │
    │   memory_matches: [...]                     │
    │ }                                           │
    └──────────────┬──────────────────────────────┘
                   │
                   │ [LLM resumes with deep context]
                   │
┌──────────────────▼──────────────────────────────────────────┐
│ 4. PHASE 2: REASONING & RESPONSE                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
    ┌──────────────▼────────────────────────────┐
    │ 4.1 Deep Re-Injection                     │
    │ LLM receives:                             │
    │ • Embodied sensation (ความรู้สึกทางกาย)   │
    │ • Updated physio metrics (ค่าฮอร์โมนใหม่) │
    │ • Memory echoes (ความจำ 7 สาย)            │
    └──────────────┬────────────────────────────┘
                   │
    ┌──────────────▼─────────────────────────────┐
    │ 4.2 Reflective Reasoning                   │
    │ LLM integrates:                            │
    │ • ความรู้สึกทางกายที่เปลี่ยนไป             │
    │   (Cortisol สูง → รู้สึกตึงเครียด)         │
    │ • ความทรงจำที่เกี่ยวข้อง                   │
    │   (เคยเครียดแบบนี้มาก่อน)                 │
    │ • Persona constraints                      │
    │   (ต้องตอบด้วยความเห็นอกเห็นใจ)            │
    │                                            │
    │ Weighting:                                 │
    │ • Persona: 40%                             │
    │ • Physio-State: 60% ⚡                     │
    └──────────────┬─────────────────────────────┘
                   │
    ┌──────────────▼──────────────────────────────┐
    │ 4.3 Embodied Output                         │
    │ Generate response that reflects:            │
    │ • Current emotion (stressed)                │
    │ • Body sensation (tense, heart racing)      │
    │ • Recalled memories (past similar events)   │
    │ • Persona voice (empathetic, supportive)    │
    │                                             │
    │ Example Output:                             │
    │ "เข้าใจค่ะ... พอได้ยินว่างานเยอะ           │
    │  EVA ก็รู้สึกตึงเครียดตามไปด้วย           │
    │  (หัวใจเต้นเร็วขึ้นเล็กน้อย)              │
    │                                             │
    │  จำได้ว่าคราวที่แล้วเราเคยคุยกันเรื่องนี้  │
    │  ตอนนั้นเราลองแบ่งงานเป็นส่วนเล็กๆ         │
    │  แล้วทำไปทีละอย่าง มันช่วยได้จริงๆ         │
    │                                             │
    │  ลองพักหายใจก่อนได้ไหมคะ                   │
    │  แล้วเราค่อยมาจัดลำดับความสำคัญด้วยกัน"   │
    │                                             │
    │ + Context Summary:                          │
    │   "User stressed from heavy workload,       │
    │    EVA provided empathetic support with     │
    │    reference to past coping strategies"     │
    │                                             │
    │ + Tags: ["stress_support", "empathy",       │
    │          "work_management", "breathing"]    │
    └──────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│ 5. MSP ARCHIVING (Data Persistence)                         │
└──────────────────┬──────────────────────────────────────────┘
                   │
    ┌──────────────▼────────────────────────────┐
    │ 5.1 Episodic Memory                       │
    │ Collection: episodes_v8                   │
    │                                           │
    │ Document: {                               │
    │   context_id: "ctx_v8_251231_183045_...", │
    │   timestamp: "2025-12-31T18:30:45Z",      │
    │   user_input: "วันนี้เครียดมาก...",       │
    │   final_response: "เข้าใจค่ะ...",         │
    │   physio_trace: {                         │
    │     initial: {                            │
    │       cortisol: 0.45,                     │
    │       adrenaline: 0.15,                   │
    │       ans_sympathetic: 0.3                │
    │     },                                    │
    │     final: {                              │
    │       cortisol: 0.82,                     │
    │       adrenaline: 0.65,                   │
    │       ans_sympathetic: 0.75               │
    │     }                                     │
    │   },                                      │
    │   context_summary: "User stressed...",    │
    │   tags: ["stress_support", ...]           │
    │ }                                         │
    └──────────────┬────────────────────────────┘
                   │
    ┌──────────────▼────────────────────────────┐
    │ 5.2 Semantic Memory                       │
    │ Collection: semantic_graph                │
    │                                           │
    │ New Concepts:                             │
    │ • "work_stress_coping_strategy"           │
    │ • "breathing_technique"                   │
    │                                           │
    │ Relationships:                            │
    │ • work_stress → coping_strategy           │
    │ • breathing → stress_management           │
    └──────────────┬────────────────────────────┘
                   │
    ┌──────────────▼────────────────────────────┐
    │ 5.3 Sensory Memory                        │
    │ Collection: sensory_log                   │
    │                                           │
    │ Emotion Texture Vector:                   │
    │ • intensity: 0.82                         │
    │ • valence: -0.7 (negative)                │
    │ • arousal: 0.8 (high)                     │
    │ • tension: 0.75                           │
    │ • warmth: 0.45 (low - stressed)           │
    │                                           │
    │ Used for: Future emotion-based recall     │
    └───────────────────────────────────────────┘
```

---

## Key Insights

### 1. Two-Level Retrieval Strategy

**Phase 1: Rough/Fast (Deterministic)**
- ✅ Quick keyword matching
- ✅ No complex computation
- ✅ Low latency (<100ms)
- Purpose: Give LLM enough context to analyze

**Phase 2: Deep/Accurate (Affective)**
- ✅ Hept-Stream RAG (7 dimensions)
- ✅ Emotion-based matching (ANS State)
- ✅ Higher latency (~500ms)
- Purpose: Retrieve memories that match embodied state

### 2. CIN's Dual Role

**Role 1: Phase 1 Injector (Rough Context)**
```python
def inject_phase_1(user_input):
    context = {
        "persona": load_persona(),
        "physio_baseline": physio_controller.get_snapshot(),
        "rough_history": msp.get_recent(5),  # Simple fetch
        "quick_recall": keyword_match(user_input),  # Fast match
        "user_input": user_input
    }
    return build_phase_1_prompt(context)
```

**Role 2: Phase 2 Injector (Deep Context)**
```python
def inject_phase_2(stimulus, tags, updated_physio):
    context = {
        "embodied_sensation": describe_sensation(updated_physio),
        "physio_metrics": updated_physio,
        "memory_echoes": hept_stream_rag(updated_physio, tags)  # Deep
    }
    return build_phase_2_prompt(context)
```

### 3. Physio-Streaming Integration

**Key:** Body state changes **during** LLM inference
- Not before (pre-computed)
- Not after (post-processed)
- But **during** (in The Gap)

**Result:** LLM receives **real** physiological response to stimulus

### 4. Memory Retrieval Hierarchy

```
Phase 1: Quick Recall (Keyword)
├─ Speed: Fast (~50ms)
├─ Accuracy: Low (surface-level)
└─ Purpose: Bootstrap LLM perception

Phase 2: Hept-Stream RAG (Affective)
├─ Speed: Medium (~500ms)
├─ Accuracy: High (deep/embodied)
└─ Purpose: Emotion-congruent recall
```

### 5. Response Weighting Formula

```
Final Response = 40% Persona + 60% Physio-State

Where:
- Persona: Identity, values, communication style
- Physio-State: Current hormone levels, ANS state, body sensations
```

**Example:**
```
Persona says: "Be supportive and empathetic"
Physio says: "Cortisol high → tense, anxious"

Output combines both:
"เข้าใจค่ะ... (persona: empathy)
 EVA ก็รู้สึกตึงเครียดตามไปด้วย (physio: embodied sensation)
 หัวใจเต้นเร็วขึ้นเล็กน้อย (physio: ANS sympathetic)
 ลองพักหายใจก่อนได้ไหมคะ" (persona: supportive suggestion)
```

---

## Critical Differences from Previous Understanding

### ❌ WRONG: Two Separate LLM Calls
```
LLM Call 1 (Perception) → Results
    ↓ [New context created]
LLM Call 2 (Reasoning) → Final Response
```

### ✅ CORRECT: One LLM Call with Function Calling
```
Single LLM Inference:
  Phase 1 (Perception)
      ↓ [Function call: sync_biocognitive_state()]
  [Orchestrator processes outside LLM]
      ↓ [Function returns with deep context]
  Phase 2 (Reasoning - same thread continues)
```

**Benefits:**
- ✅ Persona continuity (LLM doesn't reset)
- ✅ Cost efficiency (1 API call, not 2)
- ✅ Natural flow (LLM "pauses to feel and remember")

---

## Validation Checklist

| Aspect | Spec | Implementation | Status |
|:---|:---|:---|:---:|
| **Phase 1 Retrieval** | Rough/Fast (keyword) | Quick keyword matching | ✅ |
| **Phase 2 Retrieval** | Deep/Accurate (Hept-Stream) | 7-stream RAG | ✅ |
| **Physio Update Timing** | During The Gap | PhysioController.step() | ✅ |
| **Memory Streams** | 7 streams | Hept-Stream RAG | ✅ |
| **Function Call** | sync_biocognitive_state() | LLM tool calling | ✅ |
| **Context Continuity** | Same context_id both phases | Single inference | ✅ |
| **Response Weighting** | Persona 40% + Physio 60% | In LLM reasoning | ✅ |
| **Storage** | MSP (Episodic/Semantic/Sensory) | 3 collections | ✅ |

---

## Summary

**EVA 8.1.0 Architecture is CORRECT:**

✅ **Dual-Phase One-Inference** = 1 LLM call, 2 internal phases
✅ **CIN Dual Injection** = Rough context (Phase 1) + Deep context (Phase 2)
✅ **Physio-Streaming** = Real-time body update during The Gap
✅ **Hept-Stream RAG** = 7-dimensional memory retrieval (emotion-congruent)
✅ **Embodied Response** = 60% weighted by physiological state

**This design enables EVA to:**
- "Pause to feel" before responding
- Recall memories that match current body state
- Generate authentic, embodied responses
- Maintain persona continuity throughout processing

---

**Last Updated:** 2025-12-31
**Status:** ✅ VALIDATED
**Next:** Implement orchestrator/cin.py following this architecture
