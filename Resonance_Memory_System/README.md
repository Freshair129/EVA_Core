# Resonance Memory System (RMS)
## Component ID: SYS-RMS-8.1

The **Resonance Memory System** manages the long-term memory clusters and provides semantic context for the resonance calculation.

### 📁 Directory Structure

- **`configs/`**: Configuration & Master Registries (SSOT).
  - `RMS_Interface.yaml`: Public API specification.
  - `RMS_Input_Contract.yaml`: Master Input Registry.
  - `RMS_Output_Contract.yaml`: Master Output Registry.

- **`contract/`**: Detailed Data Agreements.
  - `upstream/`: Input source contracts.
  - `downstream/`: Output destination contracts.

- **`docs/`**: Conceptual documentation.

### 🔗 Integration Flow

1. **Input**: Receives emotional vectors and resonance state from **EVA Matrix**.
2. **Process**: Clusters memories efficiently to find thematic resonance.
3. **Output**: Sends clustered semantic context to **RI Engine** and **MSP**.

### 📊 Key Specifications

- **Latency**: < 100ms (cluster query)
- **State**: Stateful (Manages memory clusters)
- **Version**: 8.1.0
