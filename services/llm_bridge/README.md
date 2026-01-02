# LLM Bridge
## Component ID: SYS-LB-8.1

The **LLM Bridge** is the interface between EVA's internal cognitive systems and the Big Conscious (Gemini).

### 📁 Directory Structure

- **`configs/`**: Configuration & Master Registries.
  - `LLM_Bridge_Interface.yaml`: Public API specification.
  - `LLM_Bridge_Input_Contract.yaml`: Master Input Registry.
  - `LLM_Bridge_Output_Contract.yaml`: Master Output Registry.

- **`contract/`**: Detailed bilateral agreements.
  - `upstream/`: Sources for context (CIN).

### 🔗 Integration Flow

1. **Input**: Receives full prompt and context from **CIN**.
2. **Process**: Orchestrates calls to Gemini API, handles function calling and retries.
3. **Output**: Returns raw response and parsed function calls to **Main Orchestrator**.

### 📊 Key Specifications

- **Latency**: Variable (Network dependent)
- **State**: Stateless
- **Version**: 8.1.0
