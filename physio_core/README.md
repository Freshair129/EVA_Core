# PhysioCore Module

## Component ID: `CORE-PHYSIO-01`
## Tier: **Full**

### Overview
PhysioCore is the autonomous physiological engine for EVA. It simulates biological subsystems including Endocrine, Cardiovascular (Blood), Receptor Transduction, Reflex Arcs, and Autonomic Nervous System responses.

### Directory Structure
- `configs/`: YAML configurations for each subsystem.
- `contract/`: Upstream (Stimuli) and Downstream (State) contracts.
- `logic/`: Functional implementation of all physiological loops.
- `schema/`: Data definitions for Hormones and Hemodynamics.
- `docs/`: Detailed architectural and physiological overview.

### Integration Flow
1. **Upstream**: Receives stimuli from `CIN` or `Orchestrator`.
2. **Processing**: Runs the biological loop (Endocrine → Blood → Receptor → Reflex → Autonomic).
3. **Downstream**: Outputs the updated physiological state to `MSP` and `CIN`.

### Key Specifications
- **No Cognition**: Purely biological/stateless simulation of state over time.
- **Deterministic**: Given the same stimuli and dt, output is consistent.
- **High Fidelity**: PG-level mass tracking for hormones.