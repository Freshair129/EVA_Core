# EVA 8.1.0 System Architecture Map 🗺️

## 1. Conceptual Visualization
![EVA 8.1.0 Architecture Concept](/C:/Users/freshair/.gemini/antigravity/brain/2a29ec67-8f29-4451-ba8c-d20ac909550b/eva_810_architecture_concept_1767386047031.png)

---

## 2. Technical Architecture (Mermaid)

```mermaid
graph TD
    %% Base Layers
    subgraph User_Interface ["External World"]
        User((USER))
    end

    subgraph Executive_Mind ["Executive Mind (Tier 1)"]
        Orch[Main Orchestrator]
        CIN[Context Injection Node]
        PMT[Prompt Rule Layer]
        Bridge[LLM Bridge]
    end

    subgraph The_Gap ["The Gap (Biological & Phenomenological Processing)"]
        Physio[Physio Core - Soma]
        Matrix[EVA Matrix - Psyche]
        Qualia[Artifact Qualia - Experience]
        RI[Resonance Index - Scoring]
        RIM[Resonance Impact - Signal]
    end

    subgraph Memory_System ["Memory & Persistence (Root Anchor)"]
        MSP[Memory & Soul Passport]
        RMS[Resonance Memory System]
        RAG[Hept Stream RAG]
        Conscious[(Consciousness Store)]
    end

    %% Flow: Phase 1 (Perception)
    User -->|Stimulus| Orch
    Orch -->|Prompt Build| CIN
    CIN -->|Rules| PMT
    
    %% Flow: The Gap (Internal Sync)
    Orch -.->|Trigger| Physio
    Physio -->|Neural Signals| Matrix
    Matrix -->|9D State| Qualia
    
    %% Flow: Phase 2 (Reasoning)
    RAG -->|7D Context| CIN
    CIN -->|Final Prompt| Bridge
    RI -->|Weighting| RAG
    RIM -->|Semantic Impact| Qualia
    
    %% Flow: Persistence
    Bridge -->|Response| User
    Bridge -->|Episode Trace| MSP
    MSP -->|Encode| RMS
    RMS -->|Store| Conscious
    
    %% Connections
    Conscious -.->|Retrieval| RAG
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
