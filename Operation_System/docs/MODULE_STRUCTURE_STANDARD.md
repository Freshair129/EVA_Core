# EVA 8.1.0 Module Structure Standard (Official Reference)
**ID**: EVA-STD-001 | **Status**: CORE LAW | **Auth**: Core Team

> [!IMPORTANT]
> **STRICT ENFORCEMENT**: Deviations from this directory structure, naming convention, or contract pattern are forbidden.

## 1. Design Principles (Rule of Law)
1.  **Separation**: `configs/` (State), `contract/` (Agreements), `docs/` (Concepts). No mixing.
2.  **SSOT**: `configs/{Module}_[Input|Output]_Contract.yaml` is the SINGLE SOURCE OF TRUTH.
3.  **Flow**: Input sources must be in `contract/upstream_contract/`. Outputs in `downstream_contract/`.
4.  **Documentation**: `README.md` is MANDATORY describing Purpose, Structure, and Integration Flow.

## 2. Directory Structure (Master Template)
All modules must follow this schema. Use "Full" for complex modules, "Minimal" for utilities.

```text
{module_name}/                  # snake_case only
│
├── 📂 configs/                 # [SSOT] Configuration & Master Registries
│   ├── {Module}_Interface.yaml         # PUBLIC API Spec (Required)
│   ├── {Module}_Input_Contract.yaml    # Master Input Registry
│   ├── {Module}_Output_Contract.yaml   # Master Output Registry
│   └── {Module}_configs.yaml           # Runtime logic configs
│
├── 📂 contract/                # [Bilateral] Detailed Agreements
│   ├── 📂 upstream_contract/           # "Where data COMES FROM"
│   │   └── {Source}_Contract/          # One folder per source
│   │       └── Input_from_{Source}.yaml
│   │
│   └── 📂 downstream_contract/         # "Where data GOES TO"
│       └── {Dest}_Contract/            # One folder per destination
│           └── Output_to_{Dest}.yaml
│
├── 📂 docs/                    # [Human] Concepts & Guides
│   └── concept.md
│
├── 📂 schema/                  # [Validation] JSON Schemas (Optional)
├── 📂 validation/              # [Logic] Business Rules (Optional)
├── 📂 tests/                   # [QA] Unit & Integration Tests
│
├── 🐍 {module}.py              # Implementation (or {module}_engine.py)
├── 📄 README.md                # [Mandatory] Architecture & Usage
└── 📄 __init__.py
```

## 3. Naming Conventions

| Type | Pattern | Example |
| :--- | :--- | :--- |
| **Module Folder** | `snake_case` | `eva_matrix`, `physio_core` |
| **Interface** | `{Module}_Interface.yaml` | `EVA_Matrix_Interface.yaml` |
| **Master Contracts** | `{Module}_[Input/Output]_Contract.yaml` | `CIN_Input_Contract.yaml` |
| **Bilateral (Up)** | `Input_from_{Source}_Contract.yaml` | `Input_from_Physio_Contract.yaml` |
| **Bilateral (Down)**| `Output_to_{Dest}_Contract.yaml` | `Output_to_RMS_Contract.yaml` |
| **Contract Folders**| `{Source/Dest}_Contract` (PascalCase) | `PhysioController_Contract` |

## 4. Contract Templates (Copy Exact)

### A. Interface File (`configs/{Module}_Interface.yaml`)
```yaml
schema: EVA-{Module}-Interface-v1
version: 1.0
name: {Module Name}
role: {Brief Description}
position:
  upstream: [{Module A}]
  downstream: [{Module B}]
execution_order: [{Step 1}, {Step 2}]
```

### B. Master Input Contract (`configs/{Module}_Input_Contract.yaml`)
```yaml
schema: EVA-{Module}-Input-Contract-v1
module: {Module Name}
role: input_registry
sources:
  - module: {Source A}
    contract_path: contract/upstream_contract/{Source_A}_Contract/
    required_fields: [field_1, field_2]
validation:
  required_sources: [{Source A}]
```

### C. Master Output Contract (`configs/{Module}_Output_Contract.yaml`)
```yaml
schema: EVA-{Module}-Output-Contract-v1
module: {Module Name}
role: output_registry
destinations:
  - module: {Dest A}
    contract_path: contract/downstream_contract/{Dest_A}_Contract/
    output_fields: [field_1]
    # Options: orchestrator_mediated, direct_push, passive_pull
    delivery_mode: "orchestrator_mediated" 
```

### D. Bilateral Upstream (`contract/upstream_contract/...`)
```yaml
schema: EVA-Input-From-{Source}-Contract-v1
source: {module: {Source}, file: source.py}
destination: {module: {This}, component_id: ...}
data:
  fields:
    field_1: {type: float, required: true, desc: "..."}
delivery: {method: function_call}
```

## 5. Delivery Modes

| Mode | Description |
| :--- | :--- |
| **`orchestrator_mediated`** | (Default) Orchestrator requests data from this module and passes it to dest. |
| **`direct_push`** | Module calls destination API/Bridge directly (e.g., Database write). |
| **`passive_pull`** | Module exposes state; waits for query. |

## 6. Decision Tree (Tier Selection)
*   **Tier 1 (Full)**: Complex logic, Schema validation, >2 dependencies. (Use full tree above).
*   **Tier 2 (Standard)**: Most modules. `configs/`, `contract/`, `docs/`, `README`.
*   **Tier 3 (Minimal)**: Utilities. `configs/`, code, `README`. No `contract/` folder if no deps.
