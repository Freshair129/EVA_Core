# MSP Data Persistence Request (CIN Phase 1 Requirement)
**Version:** 8.1.0-R1
**Requester:** CIN (Context Injection Node)
**Target:** MSP (Memory & Soul Passport)
**Date:** 2026-01-03

status: pending 

## 1. Objective
To enhance the "Intuition" (แว๊บแรก) capabilities of CIN by ensuring critical context metadata is persisted by MSP at the end of every turn and available for immediate retrieval in Phase 1 of the next turn.

## 2. Missing Data Identification
Currently, `Episodic_Memory_Schema_v2.json` and MSP's indexing logic (`write_episode`) lack the following fields required for high-fidelity perception bootstrapping:

| Required Field | Importance for CIN Phase 1 | Current Status in MSP |
| :--- | :--- | :--- |
| `last_turn_physio_state`| Provides baseline for Phase 1 intuition (e.g., comparing current HR with last turn's end state). | **Partially Available** (In Snapshot) |
| `current_physio_state` | Real-time biological context for rapid perception. | **Injected at runtime** |
| `user_profile` | Pulls user persona/preferences from `08_User_block` for personalized intuition. | **Inconsistent** |
| `interpersonal_atmosphere` | Establishes the "vibe" (e.g., tense, playful, serious) immediately for the intuition layer. | **Missing** |
| `previous_intent` | Informs CIN about what the user was trying to achieve in the last turn. | **Missing** |

## 3. Context Lifecycle & Storage (3-Stage Accumulation)
CIN takes ownership of the `context_id` and requires MSP to support a "Buffered Persistence" model. Every interaction context must be accumulated in 3 stages before final archival into `10_context_storage`:

1.  **Stage 1 (Phase 1 Perception)**: Bootstrap data (Raw history + Physio + User Profile).
2.  **Stage 2 (Phase 2 Reasoning)**: Processed context (Atmosphere + Intent + RAG).
3.  **Stage 3 (Final Output)**: The LLM response + Final state update.

**Request:** MSP must provide a method to `append_to_buffer(context_id, stage_data)` and a final `commit_context(context_id)` that writes the complete lifecycle to `10_context_storage`.

## 3. Impact Analysis
Without these fields, CIN Phase 1 is forced to rely on:
1.  **Raw Text History**: Requires more tokens and more "reasoning" from the LLM to re-identify the atmosphere.
2.  **Redundant Analysis**: The system must re-extract the "tone" and "intent" in every turn instead of building upon the conclusion of the previous turn.

## 4. Proposed Modifications (for future implementation)
1.  **Schema Update**: Add `interpersonal_atmosphere` and `active_intent` to `Episodic_Memory_Schema_v2.json` under `situation_context`.
2.  **Indexing Update**: Update `MSPClient.write_episode` to index these fields in `episodic_index.jsonl` for fast < 50ms retrieval.
3.  **Bootstrap Expansion**: Update `MSPClient.get_recent_history` to return these rich metadata fields alongside the raw text.

## 5. Summary for MSP Consideration
CIN requests that MSP provides a "Persistent Mental State" block that lives across turns, rather than just storing historical "Episodes". CIN Phase 1 needs to know *where we were* psychologically to intuitively know *where we are going*.
