# Module State Registry Integration Guide

## Overview
MSP now serves as the **Central State Registry** for all EVA modules. Every component that maintains operational state MUST register its state with MSP using the unified State Registry API.

## Registration Pattern

### Python Example (EVA Matrix)
```python
from msp import MSP

# Initialize MSP
msp = MSP(use_local=True)

# Register module state
eva_matrix_state = {
    "axes_9d": {
        "stress_load": 0.02,
        "social_warmth": 0.02,
        "drive_level": 0.02,
        # ... other axes
    },
    "emotion_label": "Calm",
    "momentum": {}
}

msp.register_module_state(
    module_name="eva_matrix",
    state_data=eva_matrix_state,
    metadata={
        "update_frequency": "per-turn",
        "source": "EVA_Matrix_Engine",
        "dependencies": ["physio_core"]
    }
)
```

### Query Pattern
```python
# Get specific module state
current_matrix = msp.get_module_state("eva_matrix")
print(current_matrix["state_data"]["emotion_label"])  # "Calm"

# Get all system states (health check)
system_snapshot = msp.get_all_states()
for module, state in system_snapshot.items():
    print(f"{module}: {state['timestamp']}")
```

## Mandatory Modules
All modules listed in `MSP_Write_Policy.yaml` MUST register:
- `eva_matrix` (per-turn)
- `physio_core` (real-time)
- `rms` (per-turn)
- `artifact_qualia` (per-turn)
- `cin` (per-turn)
- `hept_stream_rag` (on-demand)

## File Structure
States are persisted to:
```
consciousness/09_state/
├── eva_matrix_state.json
├── physio_core_state.json
├── rms_state.json
├── artifact_qualia_state.json
├── cin_state.json
└── hept_stream_rag_state.json
```

## State Envelope Format
All states follow the standardized envelope defined in `Module_State_Schema.json`:
```json
{
  "module_name": "eva_matrix",
  "timestamp": "2026-01-02T19:00:00Z",
  "state_data": { /* module-specific state */ },
  "metadata": {
    "update_frequency": "per-turn",
    "source": "EVA_Matrix_Engine",
    "dependencies": ["physio_core"]
  }
}
```

## Benefits
1. **Single Source of Truth**: All modules query MSP for current state
2. **Health Monitoring**: `get_all_states()` provides system-wide snapshot
3. **Debugging**: Timestamped state history for replay/analysis
4. **Serialization**: Easy state export/import for persistence
