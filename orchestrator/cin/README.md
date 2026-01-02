# CIN (Context Injection Node)
## Component ID: SYS-CIN-8.1

**Context Injection Node** is the orchestration brain responsible for building the "Prompt Context" for the LLM. It follows a Dual-Phase architecture to balance latency and depth.

### 📁 Directory Structure

- **`configs/`**: Defines **system behavior** & **Master Registries** (SSOT).
  - `CIN_Interface.yaml`: Public API.
  - `CIN_spec.yaml`: Internal Specification.
  - `CIN_Input_Contract.yaml`: **Master Input Registry**.
  - `CIN_Output_Contract.yaml`: **Master Output Registry**.

- **`contract/`**: Detailed Data Agreements.
  - **`upstream/`**:
    - `MSP_Contract/Input_from_MSP_Contract.yaml`: Memory & Matrix State.
    - `Physio_Contract/Input_from_PhysioController_Contract.yaml`: Biological State.
  - **`downstream/`**:
    - `Orchestrator_Contract/Output_to_Orchestrator_Contract.yaml`: Prompt Payloads.

- **`schema/`**: Data Models.
  - *(Empty - uses Global Schemas)*

- **`docs/`**: Documentation.
  - *(Pending)*

### 🔗 Integration Flow
1. **Perception (Phase 1)**: Pulls Physio Baseline + Recent Memory (MSP) → Prompt.
2. **Reasoning (Phase 2)**: Pulls Matrix State (via MSP) + Hept-Stream RAG (via MSP) → Prompt.
3. **Output**: Returns prompt strings to the Main Orchestrator.
