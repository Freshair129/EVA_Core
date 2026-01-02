# PMT (Prompt Rule Layer) Directory
## Component ID: SYS-PMT-8.1

**Prompt Rule Layer** manages the behavioral constraints, safety protocols, and core identity (Persona/Soul) of EVA. It ensures the AI adheres to character depth and safety guidelines, modulating its strictness based on physiological state.

### 📁 Directory Structure

- **`configs/`**: Defines **system behavior** & **Master Registries**.
  - `Identity/`: Contains `persona.yaml` and `soul.md` (Core Identity).
  - `PMT_configs.yaml`: Rule definitions and thresholds.
  - `PMT_Interface.yaml`: Public API.
  - `PMT_Input_Contract.yaml`: **Master Input Registry**.
  - `PMT_Output_Contract.yaml`: **Master Output Registry**.

- **`contract/`**: Detailed Data Agreements.
  - **`upstream/`**:
    - `Physio_Contract/Input_from_PhysioController_Contract.yaml`: State for modulation.
  - **`downstream/`**:
    - `CIN_Contract/Output_to_CIN_Contract.yaml`: Rule injection into prompt.

- **`pmt_engine.py`**: Core Logic.

### 🔗 Integration Flow
1. **Input**: Reads `Physio State` to determine Stress/Energy levels.
2. **Process**: Selects active rules from `PMT_configs.yaml` based on state (e.g., High Stress = stricter rules).
3. **Output**: Sends `Identity Block` and `Active Rules` to **CIN** for prompt construction.
