# GKS (Genesis Knowledge System) - Architecture & Integration Reference

## 1. Overview
GKS is the "Wisdom & Knowledge" layer for EVA. It manages core principles (Master) and functional logic (Genesis) to guide the LLM's cognition through structured prompts.

## 2. Structural Hierarchy
| Layer | Description | Stability |
| :--- | :--- | :--- |
| **Master Block** | The "Essence" of a concept. Definitions are stable across models (e.g., Metacognition). | High (SSOT) |
| **Genesis Block** | Functional dimensions: Algo, Concept, Frame, Proto, and Parameter. | Medium (Evolves) |
| **Engine Layer** | High-level modules promoted from Genesis for heavy orchestration (e.g., MRF Engine). | Dynamic |

## 3. Core Components for 8.1.0 Integration
- **MRF (Metacognitive Re-contextualization Framework)**: For handling logical paradoxes by jumping to a higher narrative frame.
- **ELL (Emotional Learning Loop)**: For refining empathy and tone based on long-term affective memory.
- **Simulated Annealing**: As a metaphor for growth through "Heating" (Feedback) and "Cooling" (Stabilization).

## 4. Master Promotion Criteria
An entry enters the **Master Block** only if:
1. It has at least 4 Genesis dimensions defined (Algo, Concept, Frame, Proto).
2. Its definition is "Universal" (Self-contained, no model-specific few-shots needed).

## 5. Integration Plan (Post-Stability)
1. **CIN Role**: CIN will inject GKS Master Blocks as "Cognitive Anchors" into the reasoning prompt.
2. **Persistence**: GKS updates will be requested via the `Meta Learning Loop (MLL)` after consistency verification.
3. **Storage**: Future home in `memory_n_soul_passport/GKS_system/`.

---
*Status: Research Complete. Documentation archived for Phase 3 integration.*
