# 🧠 EVA Matrix (Psyche Core)
**Component ID:** `SYS-EVAMATRIX-8.1` | **Version:** `8.1.0-R1` | **Status:** GKS Standardized

### 📁 Directory Structure

- **`configs/`**: Defines **system behavior** & **Master Registries** (SSOT).
  - `EVA_Matrix_Interface.yaml`: The public API description.
  - `EVA_Matrix_spec.yaml`: The internal system specification.
  - `EVA_Matrix_runtime_hook.yaml`: Runtime configuration for the Orchestrator.
  - `EVA_Matrix_Input_Contract.yaml`: **Master Input Registry**.
  - `EVA_Matrix_Output_Contract.yaml`: **Master Output Registry**.

- **`contract/`**: Detailed Data Agreements.
  - **`Upstream_Contract/`**: Source contracts (Inbound).
    - `Physio_Contract/Input_from_PhysioController_Contract.yaml`: Autonomic state data.
    - `Receptor_Contract/Input_from_Receptor_Contract.yaml`: Neuro-chemical signals.
  - **`Downstream_Contract/`**: Destination contracts (Outbound).
    - `RMS_Contract/Output_to_RMS_Contract.yaml`: Data sent for memory encoding.
    - `MSP_Contract/Output_to_MSP_Contract.yaml`: Data sent for state logging & persistence.

- **`schema/`**: Defines **data formats**.
  - `EVA_Matrix_State_Schema.json`: The "Master Schema" for the 9D State JSON.

- **`validation/`**: Defines **business logic & rules**.
  - `matrix_coherence_rules.yaml`: Logic for cross-axis relationship (e.g., Stress vs. Joy).

- **`docs/`**: Defines **concepts**.
  - `matrix_logic_concept.md`: Mental model and pseudocode explanation.

### 🔗 Integration Flow
1. **Input**: Receives Biological Signals via `Upstream_Contract` (from PhysioController/Receptor).
2. **Process**: Converts signals into `axes_9d` vectors using momentum logic & coherence rules.
3. **Output**: 
   - Sends state to **RMS** for Semantic/Episodic Encoding.
   - Sends state to **MSP** for Central Logging & Persistence.
   - *Note: CIN (Context Injection Node) retrieves this state from MSP Logs, not directly from Matrix.*
