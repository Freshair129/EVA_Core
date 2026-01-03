# CIN (Context Injection Node) - Architectural Concept

## 1. Role: The Cognitive Assembler
The **CIN (Context Injection Node)** is a specialized processing node within the **EVA 8.1.0** orchestration flow. Its primary mission is to act as the **Single Source of Truth (SSOT)** for context construction, ensuring the LLM (Large Language Model) has perfectly formatted cognitive frames for both perception and reasoning.

## 2. The "Intuition" (แว๊บแรก) Pattern
Unlike deep reasoning, human intuition is fast and fragmented. CIN implements this via Phase 1 injection:
- **Fast Path**: Bypasses heavy RAG (Retrieval-Augmented Generation) in Phase 1.
- **Intuition Flashes**: Performs a quick, non-LLM based "First Impression" scan of memories to provide the LLM with initial mental sparks.
- **Bootstrapping**: This lightweight context allows the LLM to efficiently process "intent" without token-heavy deep dives.

## 3. Dual-Phase Flow
CIN is the "Cognitive Bookend" to the "Gap" (Biological Processing):
1. **Phase 1 (Perception)**: CIN gathers Static Context (Soul/Persona) + Intuition context.
2. **The Gap**: Orchestrator runs PhysioController and Deep AgenticRAG.
3. **Phase 2 (Reasoning)**: CIN gathers the "Gap Results" and constructs the final Reasoning Frame (40% Persona / 60% Physio).

## 4. Design Invariants
- **Read-Only**: CIN observes all systems but never modifies state (Physiology or Memory).
- **Graceful Failure**: If a dependency (e.g., MSP) is offline, CIN provides "Disconnected" fallback frames to maintain conversational stability.
- **SSOT Positioning**: All prompt logic (Identity vs. Physicality weighting) is centered here.

---
**Standard**: EVA-STD-001 | **Version**: 8.1.0-R1
