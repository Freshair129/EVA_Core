# Specifications

This folder contains YAML specification files for EVA 8.1.0 components.

## Core Specifications

### Context Injection Node Specifica 8.0.yaml

**Component:** Context Injection Node (CIN)
**Version:** 8.1.0
**File:** `orchestrator/cin.py`

**Sections:**
1. Architectural Position & ID Format
2. Dual-Phase Injection Logic
   - Phase 1: Perception (rough/fast, <100ms)
   - Phase 2: Reasoning (deep/accurate, ~500ms)
3. Context Structure (Prompt Templates)
4. MSP Integration & Storage Logic
5. Function I/O Specification (`sync_biocognitive_state`)
6. System Invariants & Error Handling
7. Implementation Notes
8. Integration Example
9. Windows UTF-8 Encoding Fix

**Key Features:**
- Performance targets for each phase
- Fallback behaviors (graceful degradation)
- Auto-discovery for Persona_01.md
- Hept-Stream RAG details
- Complete Python integration example

---

### Dual_Phase(One_Inference)_Orchestrator_spec.yaml

**Component:** Main Orchestrator
**Version:** 8.1.0
**Pattern:** Dual-Phase One-Inference

**Sections:**
1. Metadata & Core Innovation
2. Orchestration Flow
   - Context ID Management
   - Phase 1: Perception
   - Inter-Phase Gap (The Gap)
   - Phase 2: Reasoning
3. Data Structure (Context Document)
4. System Constraints
5. CIN Functional Roles
6. Performance Targets
7. Critical Clarifications
8. Implementation Checklist

**Key Highlights:**
- **ONE LLM inference** with function calling (NOT two separate calls)
- Detailed 7-stream RAG specification
- Emotion Stream priority (CRITICAL for embodied cognition)
- Performance breakdown: ~700ms total overhead
- Implementation status tracking

---

## Important Concepts

### The Dual-Phase Pattern

```
Single LLM Inference:
  Phase 1 (Perception)
      ↓ LLM calls: sync_biocognitive_state(stimulus_vector, tags)
  [LLM paused - waiting for function result]
      ↓ [The Gap: PhysioController + HeptRAG]
  Phase 2 (Reasoning - same LLM thread continues)
      ↓ Final response generation
```

### Performance Targets

- **Phase 1:** <100ms (rough retrieval)
- **The Gap:** ~500ms (physio update + deep RAG)
- **Phase 2:** ~100ms (prompt building)
- **Total Overhead:** ~700ms (excluding LLM inference time)

### Seven Memory Streams

1. **Narrative** - Sequential episode chains
2. **Salience** - High-impact memories (RI > 0.70)
3. **Sensory** - Qualia-rich memories
4. **Intuition** - Pattern recognition
5. **Emotion** - **Physio-congruent recall** (KEY!)
6. **Temporal** - Time-based with decay
7. **Reflection** - Meta-cognitive insights

### Response Weighting

```
Final Response = 40% Persona + 60% Physio-State
```

"Physiology first. Cognition later."

---

## Usage

These specifications are:
- **Normative** - Implementation MUST follow these specs
- **Production-ready** - Include latency targets and fallbacks
- **Example-driven** - Contain working code examples

When implementing:
1. Read the spec thoroughly
2. Follow the structure and method signatures
3. Meet the performance targets
4. Implement fallback behaviors
5. Test against the integration examples

---

## Version History

- **8.1.0** (2025-12-31) - Current version
  - Added performance targets
  - Added fallback behaviors
  - Added critical clarifications
  - Added implementation examples
- **8.0.0** (Previous) - Initial version
