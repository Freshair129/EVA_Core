# Stimulus Vector Integration Notes

## Overview
`stimulus_vector` is a 20-dimensional affective state extracted by the LLM in Phase 1 of the Dual-Phase Orchestrator. It represents the emotional and physiological impact of user input.

## Current Structure
Based on `09_state/stimulus_vector_state.json`:
```json
{
  "vector": {
    "stress": 1.0,
    "warmth": 1.0,
    "threat": 1.0,
    "novelty": 0.8,
    "achievement": 0.5,
    "pain": 1.0,
    "hunger": 0.2,
    "thirst": 0.2,
    "satiety": 0.2,
    "anxiety": 1.0,
    "bonding": 1.0,
    "affection": 1.0,
    "intimacy": 0.4,
    "surprise": 0.3,
    "curiosity": 0.7,
    "success": 0.0,
    "mastery": 0.0,
    "fatigue": 0.0,
    "conflict": 0.5,
    "discomfort": 0.0
  },
  "ts": 1767090492.56
}
```

## Orchestrator Workflow

### Phase 1: Perception & Stimulus Extraction
1. **User Input** → CIN Phase 1 injection
2. **LLM Analysis** → Extracts stimulus_vector via function call
3. **Function**: `sync_biocognitive_state(stimulus_vector, tags)`
4. **Result**: stimulus_vector is generated

### Inter-Phase Gap: Biological Processing
- **Stimulus Application**: PhysioController receives stimulus_vector
- **Physiological Update**:
  - HPA Axis modulation (stress response)
  - Endocrine production (cortisol, adrenaline, oxytocin, etc.)
  - Blood transport & clearance
  - Receptor transduction
  - Autonomic nervous system update

### Chunking Relationship
**Question**: How many chunking rounds → how many stimulus sets?

**Answer** (from `dynamic_chunking_orchestrator.py`):
- **1 User Input** = **1 Turn**
- **1 Turn** = **1 or More Chunking Rounds** (adaptive)
- **Each Chunking Round** = **1 LLM Call** (Phase 1 + Phase 2 combined)
- **Each LLM Call (Phase 1)** = **1 Stimulus Vector Extraction**

**Therefore**:
- **N Chunking Rounds** = **N Stimulus Vectors**
- Stimulus vectors accumulate over the chunking cycle
- Each chunk of user input generates a NEW stimulus

### Example Scenario
```
User Input: "I'm really stressed about my deadline and my boss yelled at me"

Chunk 1: "I'm really stressed about my deadline"
  → stimulus_vector_1 = {stress: 0.8, anxiety: 0.7, ...}
  
Chunk 2: "my boss yelled at me"  
  → stimulus_vector_2 = {stress: 0.9, threat: 0.8, warmth: -0.5, ...}
  
Result: 2 chunking rounds = 2 stimulus vectors
Physio processes BOTH stimuli sequentially
```

## State Registry Integration
Now that `stimulus_vector` is added to `MSP_Write_Policy.yaml`:
- Orchestrator should call `msp.register_module_state("stimulus_vector", vector_data)` after each chunking round
- MSP will maintain:
  - Current state: Latest stimulus
  - Buffer: Last 20 stimuli (trend analysis)
  - History: Complete stimulus log (full archival)

## Implementation TODO
- [ ] Update orchestrator to register stimulus_vector after each chunk
- [ ] Verify buffer rotation works for multi-chunk scenarios
- [ ] Add dashboard visualization for stimulus trends
