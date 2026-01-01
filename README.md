# EVA 8.1.0 - Embodied Virtual Agent

**Version:** 8.1.0
**Architecture:** Dual-Phase One-Inference Orchestrator
**Status:** 🚧 In Development (~60% Complete)
**Date:** 2025-12-31

---

## Quick Start

### Testing Components

```powershell
# Test Context Injection Node
python orchestrator/cin.py

# Test Hept-Stream RAG
python services/hept_stream_rag.py
```

### Read First

1. **CLAUDE.md** - Complete guide for developers working in this repository
2. **docs/ARCHITECTURE_FLOW_VALIDATED.md** - Detailed architecture flow
3. **docs/IMPLEMENTATION_SUMMARY.md** - Current implementation status

---

## What is EVA 8.1.0?

EVA is an **embodied AI system** that simulates human-like emotional processing through biological metaphor. Unlike traditional sentiment analysis, EVA processes emotions through:

- **Physiological simulation** - Hormones, neural signals, autonomic responses
- **Affective memory** - Retrieves memories based on body state similarity
- **Embodied responses** - 60% driven by physiological state, 40% by persona

### Core Innovation

**Dual-Phase One-Inference Pattern**

```
Single LLM Call:
  Phase 1 (Perception)
      ↓ LLM calls: sync_biocognitive_state()
  [The Gap: Body updates + Memory retrieval]
      ↓ Function returns
  Phase 2 (Reasoning - same LLM continues)
```

**NOT** two separate API calls. This enables:
- ✅ Persona continuity (LLM context preserved)
- ✅ Cost efficiency (1 call, not 2)
- ✅ Natural flow (LLM "pauses to feel and remember")

---

## Project Structure

```
EVA 8.1.0/
├── CLAUDE.md                 # Guide for Claude Code
├── README.md                 # This file
│
├── docs/                     # 📚 Documentation
│   ├── ARCHITECTURE_FLOW_VALIDATED.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── ...
│
├── specs/                    # 📋 Specifications
│   ├── Context Injection Node Specifica 8.0.yaml
│   └── Dual_Phase(One_Inference)_Orchestrator_spec.yaml
│
├── examples/                 # 💡 Example templates
│   └── example_cin_phase1_payload.txt
│
├── orchestrator/             # 🎭 Orchestration
│   └── cin.py               # Context Injection Node ✅
│
├── services/                 # 🔧 Services
│   └── hept_stream_rag.py   # 7-stream memory retrieval ✅
│
├── physio_core/             # 🧬 Physiological simulation
│   ├── physio_controller.py
│   ├── Endocrine System/
│   ├── Circulation & Blood/
│   ├── receptor/
│   ├── reflex/
│   └── autonomic/
│
├── Memory_&_Soul_Passaport/ # 💾 Memory persistence (MSP)
├── eva_matrix/              # 📊 9D psychological state
├── Artifact_Qualia/         # 🎨 Phenomenological experience
├── Resonance_Memory_System/ # 🎵 Memory encoding (RMS)
└── Consciousness/           # 🧠 State persistence
```

---

## Implementation Status

### ✅ Implemented (~60%)

- **Context Injection Node (CIN)** - `orchestrator/cin.py`
  - Dual-phase context building
  - Persona auto-discovery
  - Graceful degradation

- **Hept-Stream RAG** - `services/hept_stream_rag.py`
  - 7-dimensional memory retrieval
  - Emotion-congruent recall
  - Temporal decay

- **PhysioController** - `physio_core/`
  - Full physiological pipeline
  - HPA Axis, Circadian, Endocrine, Blood, Receptor, Reflex, ANS

- **Architecture & Specs**
  - Complete validated flow
  - Production-ready specifications
  - Integration examples

### ⏳ Pending (~40%)

- **LLM Bridge** - `services/llm_bridge.py`
  - Gemini API integration
  - Function calling support

- **Main Orchestrator** - `orchestrator/chunking_orchestrator.py`
  - Connect all components
  - Dual-phase flow management

- **MSP Client** - `services/msp_client.py`
  - MongoDB/Neo4j integration
  - 7-stream query implementation

- **CLI Interface** - `interfaces/eva_cli.py`
  - Interactive chat
  - Session management

---

## Key Concepts

### 1. Dual-Phase Pattern

**Phase 1: Perception** (<100ms)
- Rough retrieval (keyword matching)
- Physio baseline snapshot
- Recent conversation history

**The Gap** (~500ms)
- PhysioController updates body state
- HeptStreamRAG retrieves emotion-congruent memories

**Phase 2: Reasoning** (~100ms)
- Deep context injection
- Embodied sensation description
- Response generation (40% Persona + 60% Physio)

### 2. Seven Memory Streams

1. **Narrative** - Sequential episodes
2. **Salience** - High-impact memories
3. **Sensory** - Qualia-rich experiences
4. **Intuition** - Pattern recognition
5. **Emotion** - **Physio-congruent** (KEY!)
6. **Temporal** - Time-based with decay
7. **Reflection** - Meta-cognitive insights

### 3. Emotion Stream (Most Critical)

Unlike semantic matching, Emotion Stream retrieves memories based on **physiological similarity**:

```
Current State: cortisol=0.82, ans_sympathetic=0.75 (stressed)
↓
Retrieve: Episodes with similar stress signatures
↓
Result: Memories that "feel the same" in the body
```

This enables **affective resonance** - remembering what it feels like.

### 4. Response Weighting

```
Final Response = 40% Persona + 60% Physio-State
```

The body's response drives cognition more than persona identity.

**"Physiology first. Cognition later."**

---

## Performance Targets

| Phase | Target | Purpose |
|:---|---:|:---|
| Phase 1 | <100ms | Rough retrieval |
| The Gap | ~500ms | Physio update + Deep RAG |
| Phase 2 | ~100ms | Prompt building |
| **Total** | **~700ms** | Overhead (excludes LLM time) |

---

## Technology Stack

- **Python:** 3.13.7
- **LLM:** Google Gemini 2.0 Flash (with function calling)
- **Databases:**
  - MongoDB - Episodic/Semantic/Sensory memory
  - Neo4j - Semantic graph relationships
- **Simulation:** 30Hz deterministic physiological streaming

---

## Documentation

### For Developers

- **CLAUDE.md** - Complete guide for working in this codebase
- **docs/README.md** - Documentation index
- **specs/README.md** - Specification overview

### Architecture

- **docs/ARCHITECTURE_FLOW_VALIDATED.md** - Complete validated flow (450 lines)
- **docs/Dual-Phase one infer Orchestrator.md** - Thai explanation

### Implementation

- **docs/IMPLEMENTATION_SUMMARY.md** - Status, what's done, what's pending
- **docs/SPEC_UPDATE_2025-12-31.md** - Latest updates

### Specifications

- **specs/Context Injection Node Specifica 8.0.yaml** - CIN specification
- **specs/Dual_Phase(One_Inference)_Orchestrator_spec.yaml** - Orchestrator spec

---

## Design Principles

1. **Physiology First** - Body state drives cognition (60/40 weighting)
2. **One Inference** - Single LLM call with function calling
3. **Graceful Degradation** - Works with missing dependencies
4. **Two-Level Retrieval** - Fast/rough Phase 1, deep/accurate Phase 2
5. **Emotion-Congruent Memory** - Retrieve by body state similarity
6. **Bilingual** - Thai/English support

---

## Common Pitfalls

❌ **Don't** split into two separate LLM calls
✅ **Do** use function calling within one inference

❌ **Don't** bypass PhysioController
✅ **Do** use the full pipeline (Endocrine → Blood → Receptor → ANS)

❌ **Don't** write to episodic memory directly
✅ **Do** let MSP handle all memory writes

❌ **Don't** forget UTF-8 encoding on Windows
✅ **Do** use `codecs.getwriter('utf-8')` for Thai support

---

## Contributing

When implementing:

1. Read **CLAUDE.md** first
2. Follow specifications in **specs/**
3. Meet performance targets
4. Implement fallback behaviors
5. Add tests to component files
6. Update **docs/IMPLEMENTATION_SUMMARY.md**

---

## License

Part of "The Human Algorithm" research project.

---

## Contact & Support

- See **CLAUDE.md** for implementation guidance
- See **docs/** for architecture details
- See **specs/** for component specifications

---

**Last Updated:** 2025-12-31
**Status:** 🚧 Active Development (60% Complete)
