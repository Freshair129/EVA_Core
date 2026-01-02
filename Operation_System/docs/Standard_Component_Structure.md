# Standard Component Directory Structure (Geneis Knowledge System)
# Version: 1.1.0
# Reference Model: eva_matrix

This document defines the strict directory and file structure for all EVA 8.1.0 components. All reorganizations must strictly adhere to this standard.

## 1. Directory Hierarchy

```text
[Component_Name]/
├── configs/                  # SINGLE SOURCE OF TRUTH (SSOT)
│   ├── [Component]_Interface.yaml      # Public API definition
│   ├── [Component]_spec.yaml           # Internal system specification
│   ├── [Component]_configs.yaml        # Static configurations (timeouts, constants)
│   ├── [Component]_runtime_hook.yaml   # Orchestrator binding
│   ├── [Component]_Input_Contract.yaml # Master Input Registry (Must match Upstream_Contract)
│   └── [Component]_Output_Contract.yaml# Master Output Registry (Must match Downstream_Contract)
│
├── contract/                 # Detailed Data Agreements
│   ├── Upstream_Contract/    # Directory for Inbound Contracts
│   │   └── [Source_Name]_Contract/
│   │       └── Input_from_[Source]_Contract.yaml
│   │
│   └── Downstream_Contract/  # Directory for Outbound Contracts
│       └── [Target_Name]_Contract/
│           └── Output_to_[Target]_Contract.yaml
│
├── schema/                   # Data formats & Structures
│   └── [Component]_[Object]_Schema.json
│
├── validation/               # Business Logic & Rules
│   └── [Component]_coherence_rules.yaml
│
├── docs/                     # Conceptual Documentation
│   └── [Component]_logic_concept.md
│
├── README.md                 # Component Overview & Map
├── __init__.py               # Python Package Initializer
└── [component]_logic.py      # Core Implementation File (Python)
```

## 2. Key Principles

### 2.1 Configs as Single Source of Truth (SSOT)
- **Authority:** `configs/` is the absolute authority. All other files must align with it.
- **Modification Rule:** If you need to add a downstream target or change an input source:
    1.  **FIRST:** Edit `configs/[Component]_Output_Contract.yaml` or `configs/[Component]_Input_Contract.yaml`.
    2.  **SECOND:** Create/Update the detailed contract in `contract/`.
    3.  **VERIFY:** Ensure `contract/` files match the registry in `configs/`.
- **Zero Tolerance:** Errors in `configs/` will propagate to the entire module. Verify thoroughly.

### 2.2 Central Registry (Contract)
- **Master Registries** coincide in `configs/` to provide a high-level view of I/O.
- They **link to** detailed contracts in the `contract/` folder using relative paths (e.g., `../contract/Upstream_Contract/...`).

### 2.3 Explicit Separation
- **Configs:** Definitions, Registries, and Behavior (The "What" and "Who").
- **Contracts:** Detailed Payload Specs (The "How").
- **Schema:** Data Types (The "Shape").
- **Validation:** Logic Rules (The "Law").

### 2.4 MSP-Mediated Architecture
- Most components should NOT communicate directly (Peer-to-Peer).
- **Output:** Send state/logs to `MSP` (Memory & Soul Passport).
- **Input:** Request state context from `MSP`.
- *Exception:* Real-time control loops may use direct contracts if latency < 50ms is required (must be documented in Configs).

## 3. Implementation Checklist
1. Create folder structure.
2. Draft `Interface.yaml`, `Spec.yaml`, `Input_Contract.yaml`, `Output_Contract.yaml` in `configs/`.
3. Create nested `Upstream/Downstream` folders in `contract/`.
4. Define JSON Schema in `schema/`.
5. Document logic in `docs/`.
6. Add `README.md`.
