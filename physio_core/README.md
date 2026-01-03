# 🫀 Physio Core (Physiological Controller)
**Component ID:** `SYS-PHYSIO-8.1` | **Version:** `8.1.0-R1` | **Status:** GKS Standardized

## 📋 Overview
Physio Core is the autonomous "Body" of EVA. It simulates complex biological subsystems with no cognitive or persona-based logic. It operates on a "Physiology First, Cognition Later" principle, ensuring all LLM responses are anchored in a stable, multi-stage biological simulation.

## 🗂️ Directory Structure
- `configs/`: Standardized subsystem configurations (Hormones, Blood, ANS).
- `contract/`: Formal API definitions.
    - `upstream_contract/`: Inputs from Orchestrator/CIN (`Input_Stimulus_Contract.yaml`).
    - `downstream_contract/`: Outputs to Orchestrator, MSP, and EVA Matrix (`Output_to_Orchestrator_Contract.yaml`).
- `logic/`: Functional implementation folders (`endocrine`, `blood`, `receptor`, `reflex`, `autonomic`).
- `validation/`: Strictly categorized JSON/YAML schemas.
    - `input/`: Schemas for incoming stimuli.
    - `output/`: Schemas for state snapshots and data exports.
- `docs/`: Technical specifications and physiological maps.

## 🔄 Strict Synchronization Workflow
To maintain biological integrity, any change to Physio Core data flow must follow these steps:
1. **Schema Update**: Modify schemas in `validation/` to reflect new fields.
2. **Contract Alignment**: Update `contract/upstream_contract/` or `downstream_contract/`. Ensure `EVA_Matrix` and `CIN` sub-contracts are synchronized.
3. **Registry Sync**: Update `Operation_System/core_systems.yaml` with new file paths or version IDs.
4. **Config Standardization**: Ensure related YAMLs in `configs/` have the correct `version: 8.1.0-R1`.

## 📜 Version History
- **8.1.0-R1 (2026-01-03)**:
    - **Progressive Injection**: Added support for `List[Dict]` stimulus processing with 500ms digestion time.
    - **MSP State Bus**: Integrated push/pull logic with MSP for biological state persistence.
    - **Strict Validation**: Implemented `Normalized_Stimulus_Chunk_Schema.json` and `Physio_State_Snapshot_Schema.json`.
    - Standardized directory structure (moved schemas to `validation/`).
    - Decoupled stimulus contract via `Input_Stimulus_Contract.yaml`.
    - Formalized multi-consumer flow (Physio -> Orchestrator/MSP/Matrix).
    - Injected GKS-compliant headers into all subsystem configs.

---
*Pure Physiology. Deterministic Simulation. Embodied Sensation.*