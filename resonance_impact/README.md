# Resonance Impact (RIM)
## Component ID: SYS-RIM-8.1

The **Resonance Impact** module translates the abstract Resonance Index into actionable physiological and cognitive multipliers.

### 📁 Directory Structure

- **`configs/`**: Configuration & Master Registries (SSOT).
  - `RIM_Interface.yaml`: Public API specification.
  - `RIM_Output_Contract.yaml`: Master Output Registry.
  - `rim_config.yaml`: Impact curve parameters.

### 🔗 Integration Flow

1. **Input**: Receives `resonance_index` from **RI Engine**.
2. **Process**: Appraises the impact of resonance depth using psychological impact curves.
3. **Output**: sends multipliers to **PhysioController** (affecting hormone release) and **Receptor** (affecting sensitivity).

### 📊 Key Specifications

- **Latency**: < 30ms
- **State**: Stateless
- **Version**: 8.1.0
