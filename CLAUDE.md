# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EVA 8.1.0 is an embodied AI system implementing a **Dual-Phase One-Inference Orchestrator** with physiological simulation and affective memory retrieval. The system simulates human-like emotional processing by modeling biological signals (hormones, neural responses, autonomic states) and using them to drive both cognitive processing and memory recall.

**Core Innovation:** Single LLM inference with two internal phases connected by function calling, where the body state changes **during** inference ("The Gap"), enabling authentic embodied responses.

**Python Version:** 3.13.7

## Testing Components

### Test Individual Components

```powershell
# Test Context Injection Node (CIN)
python orchestrator/cin.py

# Test Hept-Stream RAG (7-dimensional memory retrieval)
python services/hept_stream_rag.py

# Test PhysioController (when integrated)
python physio_core/physio_controller.py
```

**Note:** Components include built-in tests in `if __name__ == "__main__":` blocks. Full integration tests require MSP (MongoDB/Neo4j) and LLM bridge implementation.

## Architecture: Dual-Phase One-Inference Pattern

### Critical Concept: NOT Two LLM Calls

**❌ WRONG:** Two separate LLM API calls (Phase 1 → Phase 2)
**✅ CORRECT:** ONE LLM call with function calling

```
Single LLM Inference:
  Phase 1 (Perception)
      ↓ LLM calls: sync_biocognitive_state(stimulus_vector, tags)
  [The Gap: PhysioController updates + Hept-Stream RAG retrieves]
      ↓ Function returns with deep context
  Phase 2 (Reasoning - same LLM thread continues)
```

**Benefits:**
- Persona continuity (LLM doesn't reset between phases)
- Cost efficiency (1 API call, not 2)
- Natural flow (LLM "pauses to feel and remember")

### The Flow

```
User Input
    ↓
┌─────────────────────────────────────────┐
│ PHASE 1: PERCEPTION (Deterministic)     │
│ • CIN injects rough context             │
│   - Physio baseline snapshot            │
│   - Recent history (5 turns)            │
│   - Quick keyword recall                │
│   - Persona identity                    │
│ • LLM analyzes intent & emotion         │
│ • LLM extracts stimulus_vector          │
│ • LLM calls sync_biocognitive_state()   │
└────────────┬────────────────────────────┘
             │
             ↓ [LLM paused]
             │
┌────────────▼────────────────────────────┐
│ THE GAP: Real-time Processing           │
│ • PhysioController.step()               │
│   - HPA Regulator modulates stimulus    │
│   - Endocrine produces hormones         │
│   - Blood Engine updates concentration  │
│   - Receptors transduce signals         │
│   - ANS integrates → new body state     │
│ • HeptStreamRAG.retrieve()              │
│   - Query 7 memory streams              │
│   - Emotion Stream: Match ANS state     │
│   - Return affective memories           │
│ • CIN builds deep context               │
└────────────┬────────────────────────────┘
             │
             ↓ [Function returns]
             │
┌────────────▼────────────────────────────┐
│ PHASE 2: REASONING (Same LLM)           │
│ • LLM receives:                         │
│   - Embodied sensation description      │
│   - Updated physio metrics              │
│   - Memory echoes (7 streams)           │
│ • LLM generates response                │
│   - Persona: 40% weight                 │
│   - Physio-State: 60% weight            │
│ • LLM creates context summary           │
└─────────────────────────────────────────┘
```

### Context ID Format

Every turn generates a unique context ID:
- Format: `ctx_v8_{yymmdd}_{hhmmss}_{hash_short}`
- Example: `ctx_v8_251231_183045_a1b2c3`
- Stays constant across both phases within one turn

## Core Components

### 1. Context Injection Node (CIN)

**Location:** `orchestrator/cin.py`
**Role:** Dual-phase context builder & state manager

**Key Methods:**
- `inject_phase_1(user_input)` → Rough context (fast, <100ms)
- `inject_phase_2(stimulus, tags, physio, memories)` → Deep context (accurate)
- `build_phase_1_prompt()` → LLM prompt for perception
- `build_phase_2_prompt()` → Function result for reasoning

**Design:**
- READ-ONLY access to memory (no writes)
- Auto-discovers Persona_01.md (searches 8.1.0 → 8.0)
- Graceful degradation (returns "disconnected" if PhysioController unavailable)

### 2. Hept-Stream RAG

**Location:** `services/hept_stream_rag.py`
**Role:** 7-dimensional affective memory retrieval

**The 7 Streams:**
1. **Narrative** - Sequential episode chains
2. **Salience** - High-impact memories (RI-weighted)
3. **Sensory** - Qualia-rich memories
4. **Intuition** - Pattern recognition via semantic graphs
5. **Emotion** - **Physio-congruent recall** (KEY for embodied cognition)
6. **Temporal** - Time-based context with recency bias
7. **Reflection** - Meta-cognitive insights

**Emotion Stream (Most Important):**
- Matches current ANS state + hormone levels with past episodes
- Uses cosine similarity on physio vectors
- Enables "remembering what it feels like"
- Threshold: 70% similarity for retrieval

**Temporal Decay:**
- Exponential: `score = base_score * exp(-days_ago / halflife)`
- Default halflife: 30 days

### 3. PhysioController

**Location:** `physio_core/physio_controller.py`
**Role:** Orchestrate full physiological pipeline

**Pipeline:**
```
Stimulus → HPA Regulator → Endocrine → Blood → Receptor → Autonomic
```

**Strict Rules:**
- No cognition
- No memory
- No persona logic
- Pure physiological simulation

**Sub-systems:**
- `EndocrineController` - Hormone secretion from glands
- `HPARegulator` - Stress modulation (HPA Axis)
- `CircadianController` - Circadian rhythm effects
- `BloodEngine` - Hormone transport & clearance
- `ReceptorEngine` - Signal transduction
- `FastReflexEngine` - Immediate reflex responses
- `AutonomicResponseEngine` - ANS integration

### 4. Memory & Soul Passport (MSP)

**Location:** `Memory_&_Soul_Passaport/MSP/`
**Role:** Unified memory persistence layer

**Three Memory Types:**
- **Episodic** (`episodic.py`) - Event sequences with temporal context
- **Semantic** (`semantic.py`) - Concept graphs and knowledge
- **Sensory** (`sensory.py`) - Raw sensory data sidecars

**Storage:**
- MongoDB: Episodes, concepts, sensory logs
- Neo4j: Semantic graph relationships
- Local JSON: State snapshots & backups

**Collections:**
- `episodes_v8` - Episodic memory documents
- `semantic_graph` - Concept relationships
- `sensory_log` - Emotion texture vectors
- `turn_cache` - Context summaries for Phase 1 bootstrap

### 5. EVA Matrix

**Location:** `eva_matrix/eva_matrix_engine.py`
**Role:** Convert neural signals → 9D psychological state

**9 Dimensions:** Stress, Warmth, Drive, Clarity, Joy, Alertness, Connection, Groundedness, Openness

**Output:** Safety Reflex directives (urgency, cognitive_drive, social_warmth, withdrawal)

### 6. Artifact Qualia

**Location:** `Artifact_Qualia/Artifact_Qualia.py`
**Role:** Phenomenological experience integrator

**Output Qualia:**
- `intensity` - How strong the experience feels
- `tone` - Quality (quiet/charged/settling/neutral)
- `coherence` - Internal consistency
- `depth` - Experiential immersion
- `texture` - 5D vector (emotional, relational, identity, ambient)

**Design:** Pure subjective experience representation (no decision-making, no memory admission)

### 7. Resonance Memory System (RMS)

**Location:** `Resonance_Memory_System/rms_v6.py`
**Role:** Encode psychological states into memory structures

**Encoding:**
- `core_color` - Hex color representing emotional state
- `resonance_textures` - 5D texture vector (roughness, smoothness, etc.)
- Trauma detection: threat > 0.85 → dimmed, fragmented memory

## Key Design Principles

### 1. Physiology First, Cognition Later

**Rule:** "Physio-State weighting 60% / Persona weighting 40%"

The body's physiological response drives the cognitive response more than persona identity. This is fundamental to embodied cognition.

### 2. Two-Level Retrieval

**Phase 1 (Rough/Fast):**
- Speed: <100ms
- Accuracy: Low (keyword matching)
- Purpose: Bootstrap LLM perception

**Phase 2 (Deep/Accurate):**
- Speed: ~500ms
- Accuracy: High (emotion-congruent)
- Purpose: Retrieve memories matching embodied state

### 3. One-Way Data Flow

```
Stimulus → Endocrine → Blood → Receptor → Matrix → Qualia → RMS → MSP
```

No backwards writes. Each component reads from previous, writes to next.

### 4. Separation of Concerns

**Stateful Components (Can write):**
- PhysioController - Body state
- MSP - Memory persistence
- EVA_Matrix - Psychological state
- Artifact_Qualia - Phenomenological state
- RMS - Memory encoding

**Stateless Components (Read-only):**
- CIN - Context building only
- HeptStreamRAG - Retrieval only
- All lib-* libraries - Pure computation

### 5. Graceful Degradation

Components work independently:
- CIN works without PhysioController (returns "disconnected")
- HeptRAG works without MSP (returns empty lists)
- Persona auto-discovery has fallback

## File Structure & Organization

```
EVA 8.1.0/
├── CLAUDE.md                 # This file (guide for Claude Code)
│
├── docs/                     # Documentation
│   ├── README.md
│   ├── ARCHITECTURE_FLOW_VALIDATED.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── MISSING_COMPONENTS.md
│   ├── SPEC_CORRECTIONS.md
│   ├── SPEC_UPDATE_2025-12-31.md
│   └── Dual-Phase one infer Orchestrator.md
│
├── specs/                    # YAML specifications
│   ├── README.md
│   ├── Context Injection Node Specifica 8.0.yaml
│   └── Dual_Phase(One_Inference)_Orchestrator_spec.yaml
│
├── examples/                 # Example payloads & templates
│   ├── README.md
│   └── example_cin_phase1_payload.txt
│
├── orchestrator/             # Orchestration layer
│   └── cin.py               # Context Injection Node
│
├── services/                 # Service layer
│   └── hept_stream_rag.py   # 7-stream memory retrieval
│
├── physio_core/             # Physiological simulation
│   ├── physio_controller.py  # Main orchestrator
│   ├── Endocrine System/     # Hormone production
│   ├── Circulation & Blood/  # Blood transport
│   ├── receptor/             # Signal transduction
│   ├── reflex/               # Fast reflexes
│   └── autonomic/            # ANS integration
│
├── Memory_&_Soul_Passaport/  # Memory persistence
│   ├── MSP/                  # Core MSP modules
│   │   ├── episodic.py
│   │   ├── semantic.py
│   │   └── sensory.py
│   └── Agentic_RaG.py        # Legacy RAG (being replaced)
│
├── eva_matrix/               # Psychological state
│   └── eva_matrix_engine.py
│
├── Artifact_Qualia/          # Phenomenology
│   └── Artifact_Qualia.py
│
├── Resonance_Memory_System/  # Memory encoding
│   └── rms_v6.py
│
├── resonance_index/          # RI calculation
├── resonance_impact/         # RIM calculation
│
├── Consciousness/            # State persistence
│   ├── 01_Episodic_memory/
│   ├── 02_Semantic_memory/
│   ├── 03_Sensory_memory/
│   └── 10_state/             # JSON state files
│
└── Operation_System/         # System specs
    └── (configuration files)
```

## Specifications & Documentation

**Critical Reading:**
1. `docs/ARCHITECTURE_FLOW_VALIDATED.md` - Complete validated flow (450 lines)
2. `specs/Dual_Phase(One_Inference)_Orchestrator_spec.yaml` - System orchestration
3. `specs/Context Injection Node Specifica 8.0.yaml` - CIN specification
4. `docs/IMPLEMENTATION_SUMMARY.md` - Implementation status (~60% complete)
5. `docs/SPEC_CORRECTIONS.md` - Recent fixes (Penta→Hept streams, etc.)
6. `docs/SPEC_UPDATE_2025-12-31.md` - Latest specification updates

**Documentation Structure:**
- `docs/` - All documentation and architecture guides
- `specs/` - YAML specification files
- `examples/` - Example payloads and templates

## What's Currently Missing (As of 2025-12-31)

### Critical (Needed for Full Functionality)

1. **LLM Bridge** (`services/llm_bridge.py`)
   - Gemini API integration
   - Function calling support for `sync_biocognitive_state()`
   - Bilingual response handling (Thai/English)

2. **Main Orchestrator** (`orchestrator/chunking_orchestrator.py`)
   - Connects all components
   - Manages dual-phase flow
   - Error handling & logging

3. **MSP Client** (`services/msp_client.py`)
   - MongoDB connection & CRUD
   - Neo4j graph operations
   - Query methods for HeptRAG streams

4. **PhysioController Integration**
   - Adapter/wrapper for EVA 8.1.0
   - State snapshot methods
   - Stimulus application interface

### Supporting Infrastructure

5. **Config System** (`config/`)
   - `default.yaml` - System defaults
   - `semantic_concepts.yaml` - Concept definitions
   - `prompts/` - LLM prompt templates

6. **CLI Interface** (`interfaces/eva_cli.py`)
   - Interactive chat
   - Session management
   - Rich console output with Thai support

## Important Constraints & Invariants

### System Invariants

1. **CIN Never Summarizes:** Summary must come from LLM Phase 2 only
2. **Context Continuity:** `context_id` stays constant across both phases in one turn
3. **MSP Primacy:** All memory retrieval must go through Hept-Stream RAG
4. **One Inference:** Never split into two separate LLM calls
5. **Response Weighting:** Always 40% Persona + 60% Physio-State

### Physiological Constraints

1. **Physiology First:** Body state updates BEFORE cognitive reasoning
2. **Deterministic Streaming:** PhysioController runs at 30Hz (deterministic)
3. **No Cognition in Physio:** PhysioController has no access to persona/memory/LLM
4. **One-Way Pipeline:** Stimulus → Endocrine → Blood → Receptor → ANS (no backwards flow)

### Memory Constraints

1. **Trauma Protection:** threat > 0.85 creates dimmed, fragmented memories
2. **Temporal Decay:** Older memories naturally fade (30-day halflife)
3. **Emotion Stream Priority:** For affective recall, Emotion Stream is most critical
4. **Parent-Child Links:** Narrative episodes must maintain sequential relationships

## Thai/English Bilingual Support

**Console Encoding Fix (Windows):**
```python
import sys
import codecs

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
```

**Language Detection:**
- System responds in same language as user input
- Persona can be Thai or English
- Docstrings in English for developer clarity
- User-facing text in Thai when appropriate

## Integration Pattern

**Typical Usage Flow:**
```python
# Initialize components
cin = ContextInjectionNode(
    physio_controller=physio_core,
    msp_client=msp,
    hept_stream_rag=rag
)

# Phase 1: Perception
phase_1_ctx = cin.inject_phase_1(user_input)
phase_1_prompt = cin.build_phase_1_prompt(phase_1_ctx)

# LLM Call with function calling
llm_response = llm.generate(
    prompt=phase_1_prompt,
    tools=[sync_biocognitive_state_tool]
)

# If LLM called function:
if llm_response.tool_calls:
    # The Gap: Update body & retrieve memories
    stimulus_vector = llm_response.tool_calls[0].args["stimulus_vector"]
    tags = llm_response.tool_calls[0].args["tags"]

    updated_physio = physio_controller.step(stimulus_vector)

    query_ctx = {
        "tags": tags,
        "ans_state": updated_physio["autonomic"],
        "blood_levels": updated_physio["blood"],
        ...
    }
    memory_matches = rag.retrieve(query_ctx)

    # Phase 2: Reasoning
    phase_2_ctx = cin.inject_phase_2(
        stimulus_vector, tags, updated_physio, memory_matches
    )
    function_result = cin.build_phase_2_prompt(phase_2_ctx)

    final_response = llm.continue_with_result(function_result)
```

## Common Pitfalls

1. **Don't bypass PhysioController:** Always use the full pipeline, never call Endocrine/Blood directly
2. **Don't write to episodic_log.jsonl directly:** Only MSP can write
3. **Don't modify EVA_Matrix state from other components:** Read-only access
4. **Don't split into two LLM calls:** Use function calling, not sequential calls
5. **Don't forget UTF-8 encoding:** Thai characters require proper console setup on Windows
6. **Don't skip The Gap:** Body state MUST update between Phase 1 and Phase 2

## Version History

- **8.1.0** (Current) - Dual-Phase One-Inference with Hept-Stream RAG
- **8.0.0** (Previous) - Two-Step Orchestrator (legacy)
- **7.x** (Legacy) - Earlier iterations

## Additional Context

This system is part of "The Human Algorithm" research project exploring embodied AI through biological metaphor. The goal is authentic emotional processing driven by simulated physiological states rather than rule-based sentiment analysis.

The architecture intentionally mimics human emotional processing: stimulus triggers hormonal response, hormones change body state, body state influences cognition and memory recall. This creates genuinely embodied, non-deterministic responses.
