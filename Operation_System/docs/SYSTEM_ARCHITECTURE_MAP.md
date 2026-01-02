# EVA 8.1.0 System Architecture Map 🗺️

## 1. Conceptual Visualization
![EVA 8.1.0 Architecture Concept](/C:/Users/freshair/.gemini/antigravity/brain/2a29ec67-8f29-4451-ba8c-d20ac909550b/eva_810_architecture_concept_1767386047031.png)

---

## 2. Technical Architecture (Mermaid)

## 2. Technical Architecture (Detailed Mermaid)

```mermaid
graph TB
    %% User Layer
    UserIn(["User Input"])
    UserOut(["Final Response"])

    %% Orchestration Layer
    Orch["Main Orchestrator"]
    CIN["Context Injection Node - CIN"]
    LLMBridge["LLM Bridge - Gemini API"]

    %% Dual-Phase Loop
    P1["Phase 1: Perception<br/>LLM Analyzes Intent/Emotion"]
    FnCall{{"sync_biocognitive_state()<br/>(Function Call)"}}
    P2["Phase 2: Reasoning<br/>40% Persona + 60% Physio"]

    %% The Gap - Physiological Pipeline
    subgraph Gap ["THE GAP: Real-time Processing (Outside LLM)"]
        direction TB

        subgraph PhysioPipeline ["Physiological System - 30Hz Streaming"]
            HPA["HPA Axis Regulator<br/>Stress Modulation"]
            Circ["Circadian Controller<br/>Time-based Effects"]
            Endo["Endocrine System<br/>Hormone Production"]
            Blood["Blood Engine<br/>Transport & Clearance"]
            Receptor["Receptor Engine<br/>Signal Transduction"]
            ANS["Autonomic Nervous System<br/>Sympathetic/Parasympathetic"]

            HPA --> Circ
            Circ --> Endo
            Endo --> Blood
            Blood --> Receptor
            Receptor --> ANS
        end

        subgraph Embodiment ["Embodiment Pipeline"]
            EVAMatrix["EVA Matrix<br/>9D Psychological State"]
            ArtQualia["Artifact Qualia<br/>Phenomenological Experience"]

            Receptor --> EVAMatrix
            EVAMatrix --> ArtQualia
        end

        subgraph MemRetrieval ["Memory Retrieval"]
            HeptRAG["Hept-Stream RAG<br/>7-Dimensional Retrieval"]

            Stream1["① Narrative Stream"]
            Stream2["② Salience Stream"]
            Stream3["③ Sensory Stream"]
            Stream4["④ Intuition Stream"]
            Stream5["⑤ Emotion Stream<br/>Physio-Congruent"]
            Stream6["⑥ Temporal Stream"]
            Stream7["⑦ Reflection Stream"]

            HeptRAG --> Stream1
            HeptRAG --> Stream2
            HeptRAG --> Stream3
            HeptRAG --> Stream4
            HeptRAG --> Stream5
            HeptRAG --> Stream6
            HeptRAG --> Stream7
        end

        CINPhase2["CIN Phase 2<br/>Deep Context Building"]
    end

    %% Memory Storage Layer
    subgraph MemoryStorage ["Memory & Soul Passport - MSP"]
        RMS["Resonance Memory System<br/>Emotional Texture Encoding"]
        MSP_Auth["MSP Authority<br/>Persistence Layer"]

        subgraph EpisodicMem ["Episodic Memory v8.1.0"]
            EpUser["episodes_user/<br/>EVA_EP01_user.json"]
            EpLLM["episodes_llm/<br/>EVA_EP01_llm.json"]
            EpIndex["episodic_log.jsonl<br/>Search Index"]
        end

        subgraph SessionMem ["Session Memory - Compressed"]
            SesMem["THA-01-S003_SP1C2_SS2.json<br/>Compressed Snapshots"]
        end

        subgraph SemanticMem ["Semantic Memory"]
            SemGraph["Concept Graph<br/>Neo4j/Local"]
        end
    end

    %% Identity Layer
    subgraph IdentityLayer ["Soul & Persona - Identity Constraints"]
        PMTRule["Prompt Rule Layer<br/>PMT Framework"]
        Soul["soul.md<br/>Develop ID: THA-01-S003"]
        Persona["persona.yaml<br/>Name: llm"]
    end

    %% Main Flow
    UserIn --> Orch
    Orch --> CIN

    %% Phase 1 Flow
    CIN -->|Phase 1: Rough Context| P1
    PMTRule -.->|Identity Rules| CIN
    Soul -.->|Soul Context| CIN
    Persona -.->|Persona Voice| CIN

    P1 --> LLMBridge
    LLMBridge --> FnCall

    %% The Gap Trigger
    FnCall -->|"stimulus_vector + tags"| HPA
    FnCall -->|"Query Context"| HeptRAG

    %% The Gap Processing
    ANS -->|Updated Physio State| CINPhase2
    ArtQualia -->|Embodied Sensation| CINPhase2
    Stream5 -.->|Memory Matches| CINPhase2
    HeptRAG -.->|All 7 Streams| CINPhase2

    %% Phase 2 Flow
    CINPhase2 -->|Deep Context| LLMBridge
    LLMBridge --> P2

    %% Output Flow
    P2 --> UserOut

    %% Persistence Flow
    P2 -->|"Response + Context Summary"| RMS
    RMS -->|Encoded Memory| MSP_Auth
    MSP_Auth --> EpUser
    MSP_Auth --> EpLLM
    MSP_Auth --> EpIndex
    MSP_Auth --> SesMem
    MSP_Auth --> SemGraph

    %% Memory Read Flow (Dotted - Read Operations)
    EpUser -.->|RAG Queries| HeptRAG
    SesMem -.->|Long-term Recall| HeptRAG
    SemGraph -.->|Concept Relations| HeptRAG

    %% Styling
    classDef phaseClass fill:#e1f5ff,stroke:#0066cc,stroke-width:3px
    classDef gapClass fill:#fff3e0,stroke:#ff9800,stroke-width:3px
    classDef memClass fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    classDef identityClass fill:#e8f5e9,stroke:#4caf50,stroke-width:2px

    class P1,P2 phaseClass
    class Gap,PhysioPipeline,Embodiment,MemRetrieval gapClass
    class MemoryStorage,RMS,MSP_Auth memClass
    class IdentityLayer identityClass
```

---

## 3. Layer Definitions

### 🟦 Executive Mind (Tier 1)
- **Main Orchestrator**: The central loop director.
- **CIN (Context Injection Node)**: The dynamic prompt assembler.
- **LLM Bridge**: The cognitive bridge to Gemini/Ollama.

### 🟨 The Gap (Inter-Inference Processing)
- **Physio Core**: Simulates autonomic nervous system and hormones.
- **EVA Matrix**: Map of 9D psychological axes (Stress, Warmth, etc.).
- **Artifact Qualia**: Translates numeric states into descriptive "feelings" for the LLM.
- **RI/RIM**: Evaluates semantic alignment and determines biological impact.

### 🟥 Memory System (Persistence)
- **MSP (Memory & Soul Passport)**: The gatekeeper for episode persistence.
- **Hept Stream RAG**: Ultra-high-fidelity 7-dimensional memory retrieval.
- **Consciousness Store**: Standardized Episodic/Semantic memory storage.

---

## 4. Key Standards
- **Standard**: [MODULE_STRUCTURE_STANDARD.md](file:///E:/The%20Human%20Algorithm/T2/EVA%208.1.0/Operation_System/docs/MODULE_STRUCTURE_STANDARD.md)
- **Compliance**: All 10 core modules are 100% compliant with the 3-Tier standard.
- **Subject**: References to "EVA" now conceptually refer to the **llm** as the subject of experience.
