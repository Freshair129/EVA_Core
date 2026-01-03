# MSP (Memory & Soul Passport)
## Component ID: SYS-MSP-8.1

**Memory & Soul Passport (MSP)** is the Unified Memory Operating System of EVA. It handles the lifelong persistence of Episodic, Semantic, and Sensory data, ensuring every memory is encoded with the current Psychological and Physiological context.

### 📁 Directory Structure

- **`configs/`**: Master Registries & Policies.
  - `MSP_Interface.yaml`: Public API.
  - `MSP_Input_Contract.yaml`: **Master Input Registry**.
  - `MSP_Output_Contract.yaml`: **Master Output Registry**.
  - `MSP_spec.yaml`: Internal System Definition.
  - `MSP_Write_Policy.yaml`: Rules for memory admission.

- **`contract/`**: Detailed Data Agreements.
  - **`upstream/`**:
    - `EVA_Matrix_Contract/`: Psychological State Input.
    - `RMS_Contract/`: Encoding Data Input.
    - `LLM_Proposal_Contract/`: Memory Proposals.
  - **`downstream/`**:
    - `CIN_Contract/`: Data provided to Context Injection.

- **`msp_engine.py`**: Core Logic (formerly `core.py`).
- **`episodic.py`, `semantic.py`, `sensory.py`**: Sub-system logic.

## Standardized Structure

MSP follows the [Standard Component Structure](../docs/Standard_Component_Structure.md):
- `configs/`: Configuration files and master I/O contracts
- `contract/`: Upstream and downstream contract specifications
- `schema/`: JSON schemas for validation
- `validation/`: Validation rules
- `docs/`: Component-specific documentation

## Central State Registry

**New in v8.1.1**: MSP now serves as the **Central State Registry** for all EVA modules.

### Registration Pattern
```python
msp.register_module_state("eva_matrix", state_data, metadata)
```

### Query Pattern
```python
current_state = msp.get_module_state("eva_matrix")
system_snapshot = msp.get_all_states()
```

**Benefits:**
- Single source of truth for system-wide state
- Health monitoring via `get_all_states()`
- Timestamped state history for debugging
- Easy state serialization/persistence

See [`docs/State_Registry_Integration.md`](docs/State_Registry_Integration.md) for integration guide.

### 🔗 Integration Flow
1. **Ingest**: Receives Memory Proposal (LLM) + Matrix State (EVA Matrix) + Encoding (RMS).
2. **Validate**: Checks against `MSP_Write_Policy.yaml`.
3. **Persist**: Writes standardized JSON files to **`e:\The Human Algorithm\T2\EVA 8.1.0\consciousness`** (The "Reasoning" Storage).
   - `01_Episodic_memory/` (Schema: `Episodic_Memory_Schema_v2.json`)
   - `02_Semantic_memory/` (Schema: `Semantic_Memory_Schema_v2.json`)
   - `03_Sensory_memory/` (Schema: `Sensory_Memory_Schema_v2.json`)
4. **Serve**: Provides retrieved context to CIN.
