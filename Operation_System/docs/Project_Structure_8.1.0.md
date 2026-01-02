# EVA 8.1.0 Project Structure Map
# Version: 1.1.0
# Date: 2026-01-02
# Description: Defines the target directory structure for the fully standardized EVA 8.1.0 system.

EVA 8.1.0/
├── 📂 Operation_System/                  # Core OS Definitions
│   ├── core_systems.yaml
│   ├── MODULE_STRUCTURE_STANDARD.md
│   └── permissions.yaml
│
├── 📂 docs/                              # Global Documentation
│   ├── Project_Structure_8.1.0.md
│   ├── Standard_Component_Structure.md
│   └── Full System Architecture Diagram.md
│
├── 📂 orchestrator/                      # [Tier 1] Executive Layer (Super-Module)
│   ├── main_orchestrator.py              # Execution Loop
│   ├── dual_phase_engine.py
│   │
│   ├── 📂 cin/                           # [Tier 2] Context Injection Node (Sub-System)
│   │   ├── configs/ (SSOT)
│   │   ├── contract/
│   │   └── cin.py
│   │
│   └── 📂 pmt/                           # [Tier 2] Prompt Rule Layer (Sub-System)
│       ├── configs/
│       ├── contract/
│       └── Identity/ (Persona & Soul)
│
├── 📂 eva_matrix/                        # [Tier 1] Psychological Core
│   ├── configs/
│   ├── contract/
│   └── ...
│
├── 📂 Memory_&_Soul_Passaport/           # [Tier 1] MSP Core
│   ├── configs/
│   ├── contract/
│   └── MSP/
│
├── 📂 Resonance_Memory_System/           # [Tier 1] RMS Core
│   ├── configs/
│   └── ...
│
├── 📂 physio_core/                       # [Tier 1] Biological Core
│   ├── configs/
│   └── ...
│
├── 📂 Artifact_Qualia/                   # [Tier 3] Phenomenology
│   └── ...
│
└── 📂 services/                          # External/Utility Services
    ├── hept_stream_rag/
    └── llm_bridge/
