# Resonance Index (RI)
## Component ID: SYS-RI-8.1

The **Resonance Index** module is responsible for calculating the cognitive resonance score, representing how well the current experience aligns with stored memories and values.

### 📁 Directory Structure

- **`configs/`**: Configuration & Master Registries (SSOT).
  - `RI_Interface.yaml`: Public API specification.
  - `RI_Output_Contract.yaml`: Master Output Registry.
  - `ri_config.yaml`: Runtime parameters.

### 🔗 Integration Flow

1. **Input**: Receives cognitive state vectors from **EVA Matrix**.
2. **Process**: Compares current state with historical clusters provided by **RMS**.
3. **Output**: Sends `resonance_index` to **MSP** for memory encoding and **CIN** for prompt context adjustment.

### 📊 Key Specifications

- **Latency**: < 50ms
- **State**: Stateless (Calculates based on provided inputs)
- **Version**: 8.1.0
