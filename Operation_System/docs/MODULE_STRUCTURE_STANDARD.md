# EVA 8.1.0 - Module Structure Standard 📐
**Document ID**: EVA-STD-001
**Version**: 1.0
**Date**: 2026-01-02
**Status**: ✅ Official Standard
**Authority**: EVA 8.1.0 Core Team

---

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Design Principles](#design-principles)
3. [Standard Structure (3 Tiers)](#standard-structure-3-tiers)
4. [Folder Definitions](#folder-definitions)
5. [Naming Conventions](#naming-conventions)
6. [File Type Specifications](#file-type-specifications)
7. [Decision Tree](#decision-tree)
8. [Examples](#examples)
9. [Migration Guide](#migration-guide)
10. [Validation Checklist](#validation-checklist)

---

## Introduction

### Purpose (วัตถุประสงค์)

This document establishes the **official standard** for file and folder structure across all modules in EVA 8.1.0. The standard ensures:

- ✅ **Consistency** - ทุกโมดูลมีโครงสร้างเดียวกัน
- ✅ **Clarity** - หาไฟล์ที่ต้องการได้ง่าย
- ✅ **Scalability** - รองรับการขยายระบบ
- ✅ **Maintainability** - ง่ายต่อการดูแลระบบ
- ✅ **Onboarding** - นักพัฒนาใหม่เข้าใจเร็ว

### Scope (ขอบเขต)

This standard applies to:
- ✅ All new modules (โมดูลใหม่ทั้งหมด)
- ✅ Major refactors (การปรับโครงสร้างใหญ่)
- ⚠️ Existing modules (โมดูลเดิม - แนะนำให้ปรับตาม)

### Reference Implementation (ต้นแบบอ้างอิง)

The **EVA Matrix** (`eva_matrix/`) serves as the reference implementation for this standard.

---

## Design Principles

### Core Principles (หลักการหลัก)

#### 1. **Separation of Concerns** (แยกหน้าที่ชัดเจน)
```
Each folder has ONE clear responsibility.
แต่ละโฟลเดอร์มีหน้าที่เดียวที่ชัดเจน
```

**Good Example**:
```
configs/      → Configuration files only
contract/     → Data agreements only
docs/         → Documentation only
```

**Bad Example**:
```
module/
├── config.yaml
├── input_contract.yaml
├── README.md
├── implementation.py
└── schema.json
```
❌ Everything mixed together

---

#### 2. **SSOT Pattern** (Single Source of Truth)
```
Master → Detailed → Implementation
มีแหล่งข้อมูลเดียวที่เป็นความจริง
```

**Hierarchy**:
```
configs/
  ├── {Module}_Input_Contract.yaml    ← MASTER (Summary)

contract/
  └── upstream/
      ├── SourceA_Contract.yaml       ← DETAILED (Specific)
      └── SourceB_Contract.yaml       ← DETAILED (Specific)
```

---

#### 3. **Upstream/Downstream Clarity** (ชัดเจนทิศทางข้อมูล)
```
Always separate input sources from output destinations.
แยกแหล่งข้อมูลเข้ากับปลายทางข้อมูลออก
```

**Structure**:
```
contract/
  ├── upstream/     → "Where does data COME FROM?"
  └── downstream/   → "Where does data GO TO?"
```

---

#### 4. **Documentation First** (เอกสารก่อนโค้ด)
```
README.md is MANDATORY for every module.
ทุกโมดูลต้องมี README.md
```

**Required Content**:
- Module purpose
- Directory structure explanation
- Integration flow (Input → Process → Output)

---

#### 5. **Contract-Driven Development** (พัฒนาตาม Contract)
```
Define contracts BEFORE implementation.
กำหนด contract ก่อนเขียนโค้ด
```

**Workflow**:
```
1. Write Interface.yaml
2. Write Input/Output Contracts
3. Write Implementation
4. Validate against contracts
```

---

## Standard Structure (3 Tiers)

### Overview (ภาพรวม)

| Tier | Use Case | Complexity | Folders | Files |
|------|----------|------------|---------|-------|
| **Full** | Large, complex modules | High | 7+ | 10+ |
| **Standard** | Most modules | Medium | 5 | 6-8 |
| **Minimal** | Small, simple modules | Low | 3 | 4-5 |

---

### Tier 1: Full Structure (โครงสร้างเต็ม)

**Use When**:
- Module has multiple upstream/downstream dependencies
- Complex business logic requiring validation
- Needs JSON schema validation
- Multiple integration points

**Structure**:
```
{module_name}/
│
├── 📂 configs/                              # Configuration & Master Registries
│   ├── {Module}_Interface.yaml              # ⭐ Public API specification
│   ├── {Module}_spec.yaml                   # Internal system specification
│   ├── {Module}_runtime_hook.yaml           # Runtime configuration (for Orchestrator)
│   ├── {Module}_Input_Contract.yaml         # 🔴 MASTER Input Registry (SSOT)
│   ├── {Module}_Output_Contract.yaml        # 🔴 MASTER Output Registry (SSOT)
│   └── {Module}_configs.yaml                # General runtime configs
│
├── 📂 contract/                             # Detailed Data Agreements
│   │
│   ├── 📂 upstream/                         # Inbound contracts (Sources)
│   │   ├── 📂 {Source_A}_Contract/
│   │   │   └── Input_from_{Source_A}_Contract.yaml
│   │   └── 📂 {Source_B}_Contract/
│   │       └── Input_from_{Source_B}_Contract.yaml
│   │
│   └── 📂 downstream/                       # Outbound contracts (Destinations)
│       ├── 📂 {Dest_A}_Contract/
│       │   └── Output_to_{Dest_A}_Contract.yaml
│       └── 📂 {Dest_B}_Contract/
│           └── Output_to_{Dest_B}_Contract.yaml
│
├── 📂 docs/                                 # Conceptual Documentation
│   ├── concept.md                           # Mental model & design rationale
│   ├── integration_guide.md                 # How to integrate with this module
│   └── examples.md                          # Usage examples
│
├── 📂 schema/                               # Data Format Definitions
│   ├── {Module}_State_Schema.json           # JSON Schema for state
│   └── {Module}_Message_Schema.json         # JSON Schema for messages
│
├── 📂 validation/                           # Business Logic & Rules
│   ├── {module}_rules.yaml                  # Validation rules
│   └── {module}_invariants.yaml             # System invariants
│
├── 📂 tests/                                # Unit tests (optional but recommended)
│   ├── test_{module}_unit.py
│   └── test_{module}_integration.py
│
├── 🐍 {module}_engine.py                    # Main implementation
├── 🐍 {module}_utils.py                     # Helper functions (if needed)
├── 📄 README.md                             # ⭐⭐⭐ MANDATORY - Directory guide
├── 📄 __init__.py                           # Python package init
└── 📂 __pycache__/                          # Python cache (gitignored)
```

**Examples**: `eva_matrix/`, `physio_core/` (if refactored)

---

### Tier 2: Standard Structure (โครงสร้างมาตรฐาน)

**Use When** (ใช้เมื่อ):
- Most general-purpose modules
- Has upstream/downstream dependencies
- Moderate complexity
- Standard integration points

**Structure**:
```
{module_name}/
│
├── 📂 configs/                              # Configuration & Contracts
│   ├── {Module}_Interface.yaml              # ⭐ Public API
│   ├── {Module}_Input_Contract.yaml         # 🔴 Input Registry
│   ├── {Module}_Output_Contract.yaml        # 🔴 Output Registry
│   └── {Module}_configs.yaml                # Runtime configs
│
├── 📂 contract/                             # Bilateral Agreements
│   ├── 📂 upstream/                         # Input sources
│   │   └── {Source}_Contract.yaml
│   └── 📂 downstream/                       # Output destinations
│       └── {Dest}_Contract.yaml
│
├── 📂 docs/                                 # Documentation
│   └── concept.md                           # Design & integration guide
│
├── 🐍 {module}.py                           # Implementation
├── 📄 README.md                             # ⭐ MANDATORY
└── 📄 __init__.py
```

**Examples**: `services/hept_stream_rag/` (if refactored), `Resonance_Memory_System/` (if refactored)

---

### Tier 3: Minimal Structure (โครงสร้างย่อ)

**Use When** (ใช้เมื่อ):
- Small, simple modules
- Few or no external dependencies
- Utility modules
- Simple services

**Structure**:
```
{module_name}/
│
├── 📂 configs/                              # Contracts only
│   ├── {Module}_Interface.yaml              # ⭐ Public API
│   ├── {Module}_Input_Contract.yaml         # Input (if applicable)
│   └── {Module}_Output_Contract.yaml        # Output (if applicable)
│
├── 🐍 {module}.py                           # Implementation
└── 📄 README.md                             # ⭐ MANDATORY
```

**Examples**: Small utility modules, simple helpers

---

## Folder Definitions

### 1. `configs/` - Configuration & Master Registries

**Purpose**: Contains **master configuration files** and **authoritative contracts** (SSOT).

**Required Files**:
```yaml
{Module}_Interface.yaml         # ⭐ MANDATORY
{Module}_Input_Contract.yaml    # MANDATORY (if module has inputs)
{Module}_Output_Contract.yaml   # MANDATORY (if module has outputs)
```

**Optional Files**:
```yaml
{Module}_spec.yaml              # Internal specification
{Module}_runtime_hook.yaml      # Runtime configuration
{Module}_configs.yaml           # General configs
```

**Characteristics**:
- ✅ Single Source of Truth (SSOT)
- ✅ High-level summaries
- ✅ Read by orchestrator and other modules

---

### 2. `contract/` - Detailed Bilateral Agreements

**Purpose**: Contains **detailed, bilateral contracts** between this module and specific upstream/downstream modules.

**Structure**:
```
contract/
├── upstream/        # "Where does data COME FROM?"
│   ├── {Source_A}_Contract/
│   │   └── Input_from_{Source_A}_Contract.yaml
│   └── {Source_B}_Contract/
│       └── Input_from_{Source_B}_Contract.yaml
│
└── downstream/      # "Where does data GO TO?"
    ├── {Dest_A}_Contract/
    │   └── Output_to_{Dest_A}_Contract.yaml
    └── {Dest_B}_Contract/
        └── Output_to_{Dest_B}_Contract.yaml
```

**Naming Convention**:
- Upstream: `Input_from_{SourceModule}_Contract.yaml`
- Downstream: `Output_to_{DestModule}_Contract.yaml`

**Relationship to Master Contracts**:
```
configs/{Module}_Input_Contract.yaml    (MASTER - Summary)
    ↓ references
contract/upstream/{Source}_Contract/    (DETAILED - Specific)
```

---

### 3. `docs/` - Conceptual Documentation

**Purpose**: Contains **human-readable documentation** for understanding the module.

**Recommended Files**:
```markdown
concept.md              # Mental model, design rationale
integration_guide.md    # How to integrate with this module
examples.md             # Usage examples
```

**Characteristics**:
- ✅ Written for humans, not machines
- ✅ Explains "why" not "what"
- ✅ Includes diagrams, examples, tutorials

---

### 4. `schema/` - Data Format Definitions

**Purpose**: Contains **JSON Schema** files for data validation.

**Use Cases**:
- State validation
- Message format validation
- API request/response validation

**Example**:
```json
// schema/EVA_Matrix_State_Schema.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "stress_load": {"type": "number", "minimum": 0, "maximum": 1},
    "social_warmth": {"type": "number", "minimum": 0, "maximum": 1}
  }
}
```

---

### 5. `validation/` - Business Logic & Rules

**Purpose**: Contains **business rules and invariants** in YAML format.

**Use Cases**:
- Cross-field validation rules
- System invariants
- Coherence rules

**Example**:
```yaml
# validation/matrix_coherence_rules.yaml
rules:
  - name: stress_joy_inverse
    description: High stress should reduce joy
    logic: "if stress > 0.7 then joy < 0.5"
```

---

### 6. `tests/` - Unit & Integration Tests

**Purpose**: Contains **automated tests** for the module.

**Structure**:
```
tests/
├── test_{module}_unit.py          # Unit tests
├── test_{module}_integration.py   # Integration tests
└── fixtures/                      # Test data
```

**Optional but Recommended** for production-ready modules.

---

### 7. `README.md` - Directory Guide

**Purpose**: ⭐⭐⭐ **MANDATORY** - Explains the module's purpose and structure.

**Required Sections**:
```markdown
# {Module Name}
## Component ID: SYS-{MODULE}-8.1

### Purpose
{Brief description}

### Directory Structure
- configs/: {Description}
- contract/: {Description}
- docs/: {Description}

### Integration Flow
Input → Process → Output
```

**Template**: See [README Template](#readme-template)

---

## Naming Conventions

### File Naming (ตั้งชื่อไฟล์)

#### 1. **Interfaces & Specs**
```
{Module}_Interface.yaml         # Public API
{Module}_spec.yaml              # Internal specification
```

**Examples**:
- `EVA_Matrix_Interface.yaml`
- `Hept_Stream_RAG_Interface.yaml`
- `LLM_Bridge_Interface.yaml`

---

#### 2. **Master Contracts** (SSOT)
```
{Module}_Input_Contract.yaml    # Master Input Registry
{Module}_Output_Contract.yaml   # Master Output Registry
```

**Examples**:
- `EVA_Matrix_Input_Contract.yaml`
- `CIN_Output_Contract.yaml`

---

#### 3. **Detailed Contracts** (Bilateral)
```
Input_from_{SourceModule}_Contract.yaml     # Upstream
Output_to_{DestModule}_Contract.yaml        # Downstream
```

**Examples**:
- `Input_from_PhysioController_Contract.yaml`
- `Output_to_RMS_Contract.yaml`

---

#### 4. **Implementation Files**
```
{module}_engine.py              # Main engine
{module}_controller.py          # Controller
{module}_utils.py               # Utilities
{module}_adapter.py             # Adapter
```

**Examples**:
- `eva_matrix_engine.py`
- `physio_controller.py`
- `hept_stream_rag.py`

---

#### 5. **Configuration Files**
```
{Module}_configs.yaml           # General configs
{Module}_runtime_hook.yaml      # Runtime configuration
```

---

#### 6. **Schema Files**
```
{Module}_{Type}_Schema.json     # JSON Schema

Examples:
- EVA_Matrix_State_Schema.json
- CIN_Context_Schema.json
```

---

### Folder Naming (ตั้งชื่อโฟลเดอร์)

#### 1. **Module Folders**
```
{module_name}/                  # Lowercase with underscores

Examples:
- eva_matrix/
- hept_stream_rag/
- llm_bridge/
```

❌ **Avoid**:
- CamelCase folders (`EvaMatrix/`)
- Spaces (`EVA Matrix/`)
- Hyphens (`eva-matrix/`)

---

#### 2. **Standard Subfolders**
```
configs/        # Configuration & Master Registries
contract/       # Bilateral agreements
docs/           # Documentation
schema/         # JSON Schemas
validation/     # Business rules
tests/          # Unit & integration tests
```

**All lowercase, no plurals for standard folders** (except `tests/`)

---

#### 3. **Contract Subfolders**
```
upstream/       # Input sources
downstream/     # Output destinations

{Module}_Contract/    # PascalCase for module-specific folders
```

**Examples**:
```
contract/
├── upstream/
│   ├── PhysioController_Contract/
│   └── Receptor_Contract/
└── downstream/
    ├── RMS_Contract/
    └── MSP_Contract/
```

---

## File Type Specifications

### Interface File (Interface.yaml)

**Purpose**: Public API specification - "What does this module do?"

**Required Sections**:
```yaml
schema: EVA-{Module}-Interface-v1
version: 1.0
updated: YYYY-MM-DD

name: {Module Name}
role: {Brief role description}

description: >
  {Detailed description}

# Position in system
position:
  upstream:
    - {Module A}
    - {Module B}
  downstream:
    - {Module C}

# Execution order
execution_order:
  - {Step 1}
  - {Step 2}

# Input contract reference
inputs:
  input_1:
    source: {Source module}
    type: {Data type}
    required_fields:
      - field_1
      - field_2

# Output contract reference
outputs:
  output_1:
    type: {Data type}
    fields:
      - field_1
      - field_2

# Constraints
constraints:
  forbidden_actions:
    - {Action 1}
  performance:
    - latency: {Target}

# Invariants
invariants:
  - {Invariant 1}
  - {Invariant 2}
```

**Example**: See `eva_matrix/configs/EVA_Matrix_Interface.yaml`

---

### Input Contract (Input_Contract.yaml)

**Purpose**: Master registry of all inputs - "What does this module need?"

**Required Sections**:
```yaml
schema: EVA-{Module}-Input-Contract-v1
version: 1.0
updated: YYYY-MM-DD

module: {Module Name}
role: input_registry

# Sources (upstream modules)
sources:
  - module: {Source Module A}
    contract_path: contract/upstream/{Source_A}_Contract/
    required_fields:
      - field_1
      - field_2

  - module: {Source Module B}
    contract_path: contract/upstream/{Source_B}_Contract/
    required_fields:
      - field_3

# Validation rules
validation:
  required_sources:
    - {Source A}
  optional_sources:
    - {Source B}

# Format requirements
format:
  encoding: utf-8
  structure: {json|yaml|custom}
```

**Example**: See `eva_matrix/configs/EVA_Matrix_Input_Contract.yaml`

---

### Output Contract (Output_Contract.yaml)

**Purpose**: Master registry of all outputs - "What does this module produce?"

**Required Sections**:
```yaml
schema: EVA-{Module}-Output-Contract-v1
version: 1.0
updated: YYYY-MM-DD

module: {Module Name}
role: output_registry

# Destinations (downstream modules)
destinations:
  - module: {Dest Module A}
    contract_path: contract/downstream/{Dest_A}_Contract/
    output_fields:
      - field_1
      - field_2

  - module: {Dest Module B}
    contract_path: contract/downstream/{Dest_B}_Contract/
    output_fields:
      - field_3

# Output guarantees
guarantees:
  - {Guarantee 1}
  - {Guarantee 2}

# Forbidden actions
forbidden:
  description: "Fields that LLM/other modules MUST NOT modify"
  fields:
    - field_1
    - field_2
```

**Example**: See `eva_matrix/configs/EVA_Matrix_Output_Contract.yaml`

---

### Bilateral Contract (Upstream/Downstream)

**Purpose**: Detailed agreement between two specific modules.

**Upstream Contract Template**:
```yaml
schema: EVA-Input-From-{Source}-Contract-v1
version: 1.0
updated: YYYY-MM-DD

# Source information
source:
  module: {Source Module Name}
  component_id: SYS-{SOURCE}-8.1
  file: {source_module_file.py}

# Destination information
destination:
  module: {This Module Name}
  component_id: SYS-{MODULE}-8.1

# Data specification
data:
  format: {json|yaml|binary}
  encoding: utf-8

  fields:
    field_1:
      type: {type}
      range: [min, max]
      required: true
      description: {Description}

    field_2:
      type: {type}
      required: false
      description: {Description}

# Delivery mechanism
delivery:
  method: {function_call|message_queue|file}
  frequency: {on_demand|continuous|batch}

# Validation rules
validation:
  required_fields:
    - field_1
  optional_fields:
    - field_2
```

**Downstream Contract Template**:
```yaml
schema: EVA-Output-To-{Dest}-Contract-v1
version: 1.0
updated: YYYY-MM-DD

# Source information
source:
  module: {This Module Name}
  component_id: SYS-{MODULE}-8.1

# Destination information
destination:
  module: {Dest Module Name}
  component_id: SYS-{DEST}-8.1
  file: {dest_module_file.py}

# Data specification
data:
  format: {json|yaml|binary}

  fields:
    output_field_1:
      type: {type}
      description: {Description}

    output_field_2:
      type: {type}
      description: {Description}

# Delivery guarantee
guarantee:
  delivery: {at_least_once|exactly_once|at_most_once}
  ordering: {ordered|unordered}
```

---

## Decision Tree

### Which Tier Should I Use? (ควรใช้ Tier ไหน?)

```
START
  │
  ├─ Module has complex validation rules?
  │     YES → [Full Structure]
  │     NO  ↓
  │
  ├─ Module has 3+ upstream OR downstream dependencies?
  │     YES → [Full Structure]
  │     NO  ↓
  │
  ├─ Module needs JSON schema validation?
  │     YES → [Full Structure]
  │     NO  ↓
  │
  ├─ Module has upstream AND downstream contracts?
  │     YES → [Standard Structure]
  │     NO  ↓
  │
  ├─ Module is a core system component?
  │     YES → [Standard Structure]
  │     NO  ↓
  │
  ├─ Module is a simple utility or helper?
  │     YES → [Minimal Structure]
  │     NO  → [Standard Structure] (default)
```

### Examples by Tier

| Module | Tier | Reason |
|--------|------|--------|
| eva_matrix/ | Full | Complex, 4 contracts, validation rules |
| hept_stream_rag/ | Standard | 2 upstream, 1 downstream, moderate complexity |
| llm_bridge/ | Standard | Core component, 2 contracts |
| Token Counter | Minimal | Simple utility, no dependencies |

---

## Examples

### Example 1: Full Structure (eva_matrix)

**Current State**: ✅ Already following standard

```
eva_matrix/
├── configs/
│   ├── EVA_Matrix_Interface.yaml
│   ├── EVA_Matrix_spec.yaml
│   ├── EVA_Matrix_runtime_hook.yaml
│   ├── EVA_Matrix_Input_Contract.yaml
│   ├── EVA_Matrix_Output_Contract.yaml
│   └── EVA_Matrix_configs.yaml
├── contract/
│   ├── upstream/
│   │   ├── PhysioController_Contract/
│   │   └── Receptor_Contract/
│   └── downstream/
│       ├── RMS_Contract/
│       └── MSP_Contract/
├── docs/
│   └── matrix_logic_concept.md
├── schema/
│   └── EVA_Matrix_State_Schema_01.json
├── validation/
│   └── matrix_coherence_rules.yaml
├── eva_matrix_engine.py
└── README.md
```

**Status**: ✅ **Perfect Example**

---

### Example 2: Standard Structure (hept_stream_rag - Proposed)

**Current State** (Flat):
```
services/
├── hept_stream_rag.py
├── Hept_Stream_RAG_Interface.yaml
├── Hept_Stream_RAG_Input_Contract.yaml
└── Hept_Stream_RAG_Output_Contract.yaml
```

**Proposed** (Standard Structure):
```
services/hept_stream_rag/
├── configs/
│   ├── Hept_Stream_RAG_Interface.yaml
│   ├── Hept_Stream_RAG_Input_Contract.yaml
│   ├── Hept_Stream_RAG_Output_Contract.yaml
│   └── Hept_Stream_RAG_configs.yaml
├── contract/
│   ├── upstream/
│   │   ├── CIN_Contract/
│   │   │   └── Input_from_CIN_Contract.yaml
│   │   └── MSP_Contract/
│   │       └── Input_from_MSP_Contract.yaml
│   └── downstream/
│       └── CIN_Contract/
│           └── Output_to_CIN_Contract.yaml
├── docs/
│   └── seven_streams_concept.md
├── hept_stream_rag.py
└── README.md
```

---

### Example 3: Minimal Structure (token_counter)

**Use Case**: Simple utility module with no dependencies

```
token_counter/
├── configs/
│   ├── TokenCounter_Interface.yaml
│   └── TokenCounter_Output_Contract.yaml
├── token_counter.py
└── README.md
```

---

## Migration Guide

### Step-by-Step Migration (การย้ายโมดูลเดิม)

#### Phase 1: Assessment (ประเมินสถานะ)

1. **Identify Current Structure**
   ```bash
   ls -la {module}/
   ```

2. **Determine Target Tier**
   - Use [Decision Tree](#decision-tree)
   - Consider complexity, dependencies

3. **List Required Changes**
   - Create checklist of files to move/create
   - Identify missing contracts

---

#### Phase 2: Create New Structure (สร้างโครงสร้างใหม่)

1. **Create Folders**
   ```bash
   cd {module}/
   mkdir -p configs contract/{upstream,downstream} docs
   ```

2. **Move Existing Files**
   ```bash
   mv {Module}_Interface.yaml configs/
   mv {Module}_Input_Contract.yaml configs/
   mv {Module}_Output_Contract.yaml configs/
   ```

3. **Create Missing Files**
   - [ ] README.md
   - [ ] configs/{Module}_Interface.yaml
   - [ ] configs/{Module}_Input_Contract.yaml
   - [ ] configs/{Module}_Output_Contract.yaml

---

#### Phase 3: Update References (อัพเดทการอ้างอิง)

1. **Update Import Paths** (in Python files)
   ```python
   # Old
   from services.hept_stream_rag import HeptStreamRAG

   # New
   from services.hept_stream_rag.hept_stream_rag import HeptStreamRAG
   ```

2. **Update Config Paths** (in YAML files)
   ```yaml
   # Old
   contract_path: Hept_Stream_RAG_Interface.yaml

   # New
   contract_path: configs/Hept_Stream_RAG_Interface.yaml
   ```

3. **Update Documentation Links**

---

#### Phase 4: Validation (ตรวจสอบ)

1. **Run Tests**
   ```bash
   pytest tests/test_{module}.py
   ```

2. **Check Imports**
   ```bash
   python -c "from {module} import *"
   ```

3. **Validate Checklist**
   - Use [Validation Checklist](#validation-checklist)

---

### Migration Priority (ลำดับความสำคัญ)

| Priority | Module | Current | Target | Effort |
|----------|--------|---------|--------|--------|
| 🔴 HIGH | services/ (all) | Flat | Standard | Medium |
| 🟡 MEDIUM | Resonance_Memory_System/ | Flat | Standard | Low |
| 🟡 MEDIUM | Artifact_Qualia/ | Flat | Standard | Low |
| 🟢 LOW | physio_core/ sub-systems | Mixed | Full | High |

---

## Validation Checklist

### Module Structure Checklist

Use this checklist when creating or migrating a module:

#### Essential (ต้องมี)

- [ ] **README.md** exists and contains:
  - [ ] Module purpose
  - [ ] Directory structure explanation
  - [ ] Integration flow

- [ ] **configs/ folder** exists with:
  - [ ] {Module}_Interface.yaml
  - [ ] {Module}_Input_Contract.yaml (if module has inputs)
  - [ ] {Module}_Output_Contract.yaml (if module has outputs)

- [ ] **Implementation file** exists:
  - [ ] {module}.py or {module}_engine.py

- [ ] **Naming conventions** followed:
  - [ ] Module folder is lowercase with underscores
  - [ ] Contract files follow naming pattern
  - [ ] No spaces in file/folder names

#### Standard Tier Requirements

- [ ] **contract/ folder** exists with:
  - [ ] upstream/ subfolder (if applicable)
  - [ ] downstream/ subfolder (if applicable)
  - [ ] Bilateral contracts for each dependency

- [ ] **docs/ folder** exists with:
  - [ ] concept.md or integration_guide.md

#### Full Tier Requirements

- [ ] **schema/ folder** exists with:
  - [ ] JSON Schema files for validation

- [ ] **validation/ folder** exists with:
  - [ ] Business rules YAML files

- [ ] **tests/ folder** exists with:
  - [ ] Unit tests
  - [ ] Integration tests

---

### Contract Validation Checklist

For each contract file:

- [ ] **Schema field** present and correct
- [ ] **Version field** present (1.0, 1.1, etc.)
- [ ] **Updated date** is current
- [ ] **Module/source/destination** clearly identified
- [ ] **Required fields** documented
- [ ] **Optional fields** documented
- [ ] **Data types** specified
- [ ] **Validation rules** defined (if applicable)

---

### README.md Validation Checklist

- [ ] **Component ID** present (SYS-{MODULE}-8.1)
- [ ] **Purpose section** describes what the module does
- [ ] **Directory Structure section** explains each folder
- [ ] **Integration Flow section** shows Input → Process → Output
- [ ] **No broken links** to other files
- [ ] **Code examples** (if applicable)

---

## README Template

### Basic README Template

```markdown
# {Module Name}
## Component ID: SYS-{MODULE}-8.1

The **{Module Name}** is responsible for {brief description}.

### 📁 Directory Structure

- **`configs/`**: Configuration & Master Registries (SSOT).
  - `{Module}_Interface.yaml`: Public API specification.
  - `{Module}_Input_Contract.yaml`: Master Input Registry.
  - `{Module}_Output_Contract.yaml`: Master Output Registry.

- **`contract/`**: Detailed Data Agreements.
  - **`upstream/`**: Input source contracts.
    - `{Source}_Contract/`: {Description}
  - **`downstream/`**: Output destination contracts.
    - `{Dest}_Contract/`: {Description}

- **`docs/`**: Conceptual documentation.
  - `concept.md`: {Description}

### 🔗 Integration Flow

1. **Input**: Receives {data type} from {source modules}.
2. **Process**: {Processing description}.
3. **Output**:
   - Sends {data type} to **{Dest A}** for {purpose}.
   - Sends {data type} to **{Dest B}** for {purpose}.

### 📊 Key Specifications

- **Latency**: < {target}ms
- **State**: {Stateful/Stateless}
- **Version**: 8.1.0

### 🚀 Usage

```python
from {module} import {Class}

# Initialize
instance = {Class}(config)

# Process
result = instance.process(input_data)
```

### 🔗 Dependencies

**Upstream**:
- {Source Module A}
- {Source Module B}

**Downstream**:
- {Dest Module A}
- {Dest Module B}
```

---

## Appendix

### A. Glossary (คำศัพท์)

| Term | Definition |
|------|------------|
| **SSOT** | Single Source of Truth - แหล่งข้อมูลเดียวที่เป็นความจริง |
| **Master Contract** | High-level summary contract (in configs/) |
| **Bilateral Contract** | Detailed agreement between two modules (in contract/) |
| **Upstream** | Input sources - modules that send data TO this module |
| **Downstream** | Output destinations - modules that receive data FROM this module |
| **Interface** | Public API specification - what the module does |
| **Contract** | Data agreement - what data is exchanged |
| **Schema** | JSON Schema - data format validation |

---

### B. Anti-Patterns (สิ่งที่ควรหลีกเลี่ยง)

#### ❌ Anti-Pattern 1: Flat Structure for Complex Modules
```
module/
├── module.py
├── interface.yaml
├── input_contract.yaml
├── output_contract.yaml
├── config.yaml
├── schema.json
└── README.md
```

**Problem**: Hard to navigate, unclear organization

**Fix**: Use Standard or Full tier structure

---

#### ❌ Anti-Pattern 2: Missing README.md
```
module/
├── configs/
│   └── ...
├── contract/
│   └── ...
└── module.py
```

**Problem**: New developers can't understand module structure

**Fix**: Always include README.md

---

#### ❌ Anti-Pattern 3: Inconsistent Naming
```
module/
├── configs/
│   ├── ModuleInterface.yaml        ❌ PascalCase
│   ├── module-input-contract.yaml  ❌ Kebab-case
│   └── MODULE_OUTPUT_CONTRACT.yaml ❌ SCREAMING_SNAKE_CASE
```

**Fix**: Use consistent {Module}_{Type}.yaml format

---

#### ❌ Anti-Pattern 4: No Master Contract (SSOT)
```
contract/
├── upstream/
│   ├── SourceA_Contract.yaml
│   └── SourceB_Contract.yaml
└── downstream/
    └── DestA_Contract.yaml
```

**Problem**: No single place to see all inputs/outputs

**Fix**: Create Master Input/Output Contracts in configs/

---

#### ❌ Anti-Pattern 5: Mixed Upstream/Downstream
```
contract/
├── PhysioController_Contract.yaml
├── RMS_Contract.yaml
└── MSP_Contract.yaml
```

**Problem**: Unclear which are inputs vs. outputs

**Fix**: Separate into upstream/ and downstream/

---

### C. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-02 | Initial release - based on eva_matrix structure |

---

### D. References

- **EVA 8.1.0 Architecture**: `docs/ARCHITECTURE_FLOW_VALIDATED.md`
- **Reference Implementation**: `eva_matrix/`
- **Module Interfaces Report**: `docs/MISSING_INTERFACES_REPORT.md`

---

## Enforcement & Compliance

### Compliance Levels

| Level | Description | Enforcement |
|-------|-------------|-------------|
| **MANDATORY** | Must comply for production | ✅ CI/CD validation |
| **RECOMMENDED** | Should comply unless exception | ⚠️ PR review |
| **OPTIONAL** | Nice to have | 💡 Suggestion |

### Mandatory Requirements

- ✅ README.md present
- ✅ configs/ folder with Interface.yaml
- ✅ Input/Output Contracts (if applicable)
- ✅ Naming conventions followed

### Recommended Requirements

- ⚠️ Upstream/downstream contract separation
- ⚠️ docs/ folder with concept.md
- ⚠️ Bilateral contracts for each dependency

### Optional Requirements

- 💡 schema/ folder with JSON Schema
- 💡 validation/ folder with rules
- 💡 tests/ folder with unit/integration tests

---

## Support & Questions

### FAQ

**Q: Do I need to refactor existing modules immediately?**
A: No. Apply this standard to:
- All new modules (mandatory)
- Major refactors (recommended)
- Gradual migration for existing (optional)

**Q: What if my module is very simple?**
A: Use **Minimal Structure** (Tier 3). At minimum: configs/, implementation, README.md

**Q: Can I add custom folders?**
A: Yes, but document them in README.md and ensure they have clear, single responsibility.

**Q: What about legacy modules?**
A: No need to refactor unless:
- Major changes required
- Module becomes complex
- Integration issues arise

---

## Approval & Authority

**Approved By**: EVA 8.1.0 Core Team
**Effective Date**: 2026-01-02
**Review Cycle**: Quarterly
**Next Review**: 2026-04-02

---

**Document Status**: ✅ **OFFICIAL STANDARD**
**Compliance**: MANDATORY for new modules, RECOMMENDED for existing
**Version**: 1.0

---

**End of Standard Document**
