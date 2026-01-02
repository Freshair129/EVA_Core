# EVA 8.1.0 Project Structure Map
# Version: 1.2.0
# Date: 2026-01-02
# Description: Final standardized directory structure for EVA 8.1.0 (Post-Restructuring).

EVA 8.1.0/
├── 📂 Operation_System/                  # [Core] System Definitions & Documentation
│   ├── core_systems.yaml                 # System Registry
│   ├── glossary.yaml                     # Terminology SSOT
│   ├── permissions.yaml                  # Access Control
│   └── 📂 docs/                          # Global Blueprints
│       ├── Project_Structure_8.1.0.md    # [THIS FILE]
│       ├── MODULE_STRUCTURE_STANDARD.md  # 3-Tier Standard
│       ├── Standard_Component_Structure.md
│       ├── Full System Architecture Diagram.md
│       └── 📂 archive/                   # Historical Dev Logs & Specs
│
├── 📂 Consciousness/                     # [Data] Root Anchor (Mind Storage)
│   ├── 01_Episodic_memory/
│   ├── 02_Semantic_memory/
│   └── 09_state/
│
├── 📂 orchestrator/                      # [Tier 1] Executive Layer
│   ├── main_orchestrator.py              # Main Loop
│   ├── dual_phase_engine.py              # Chunking & Synthesis
│   ├── 📂 cin/                           # [Tier 2] Context Injection Node
│   └── 📂 pmt/                           # [Tier 2] Prompt Rule Layer
│
├── 📂 eva_matrix/                        # [Tier 1] Psychological Core (Psyche)
├── 📂 Memory_&_Soul_Passaport/           # [Tier 1] Memory Orchestration (MSP)
│   ├── 📂 MSP/                           # MSP Engine
│   └── 📂 MSP_Client/                    # Persistence Client
│
├── 📂 Resonance_Memory_System/           # [Tier 1] Long-term Persistence (RMS)
├── 📂 physio_core/                       # [Tier 1] Biological Core (Soma)
│   ├── 📂 logic/                         # Subsystems (Blood, Endocrine, etc.)
│   └── 📂 contract/                      # Interface Definitions
│
├── 📂 resonance_index/                   # [Tier 2] RI Calculation
├── 📂 resonance_impact/                  # [Tier 2] RIM Analysis
├── 📂 Artifact_Qualia/                   # [Tier 3] Sensory Sidecars
│
├── 📂 services/                          # [Support] External Bridges
│   ├── 📂 llm_bridge/                    # Gemini/Ollama Integration
│   └── 📂 hept_stream_rag/               # 7-Dimensional Retrieval
│
├── 📂 tests/                             # [Verification] Quality Assurance
│   ├── 📂 v8.1.0_compliance/              # Restructuring Verifications
│   └── TEST_HISTORY.md                   # Versioned Test Ledger
│
├── README.md                             # Project Entry Point
├── CLAUDE.md                             # Agent Instructions
└── .gitignore                            # Exclusion Rules
