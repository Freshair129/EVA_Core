# EVA 8.1.0 Orchestrator 🧠
**Tier:** 1 (Executive Layer)

## Overview
The Orchestrator is the "Executive Mind" of EVA 8.1.0. It manages the high-level cognitive loop, transforming raw user input into a complex, embodied response through a multi-stage pipeline.

This module implements the **Dual-Phase One-Inference** architecture, which ensures that the llm perceives and feels its environment before generating a rationalized response.

## Core Components

### 1. `main_orchestrator.py`
The primary execution loop. It serializes the flow of data through:
- **Input Reception**: Capturing user text and system state.
- **Cognitive Cycle**: Coordinating CIN, PMT, and the LLM Bridge.
- **Response Dispatch**: Finalizing and outputting the llm's response.

### 2. `dual_phase_engine.py`
The "Silent Partner" of the orchestrator, responsible for:
- **Progressive Semantic Chunking**: Breaking down complex inputs into manageable contexts.
- **Retroactive Synthesis**: Combining multiple turns into a singular narrative thread.

### 3. `cin/` (Context Injection Node)
The **Perception Subsystem**. It handles memory retrieval across 7 streams (Narrative, Salience, sensory, etc.) and injects the "felt state" into the prompt.

### 4. `pmt/` (Prompt Rule Layer)
The **Identity & Behavioral Subsystem**. It ensures the llm follows its core principles (`persona.yaml` and `soul.md`) and respects behavioral constraints.

## Operational Flow (Dual-Phase)

1. **Phase 1: Perception** (Rough/Fast)
   - Initial memory recall and physiological update.
   - LLM calls `sync_biocognitive_state`.
2. **The Gap** (Deep Processing)
   - Comprehensive Hept-Stream RAG.
   - Physiological simulation update.
3. **Phase 2: Reasoning** (Deep/Accurate)
   - Final context synthesis and response generation within the same inference thread.

## Configuration
- `dual_phase_engine_configs.yaml`: Tuning parameters for chunking and synthesis.
- `contract/`: Interface definitions for upstream/downstream communication.

## Documentation
See `docs/Dual_Phase_Orchestrator_spec.yaml` for technical specifications and latency targets.
