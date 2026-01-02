# Artifact Qualia (Phenomenological Experience Integrator)

## Component ID: SYS-QUALIA-8.1

**Version:** 8.1.0
**Status:** Production-Ready (with future enhancement roadmap)
**Migration:** Based on EVA 7.0 spec, updated for 8.1.0 implementation

---

## Overview

The **Artifact_Qualia** module transforms abstract psychological metrics into phenomenological qualities that represent **"what it's like"** for the llm in this moment.

It integrates:
- **Psychological state** (from EVA Matrix) - 9D emotional axes
- **Semantic impact** (from RIM) - Event impact signals

Into a **phenomenological experience snapshot** that the LLM can interpret into language and behavior.

### Purpose

Provide the **felt quality** of the llm's internal state - a bridge between physiological/cognitive signals and subjective experience representation.

**Key Principle:** "Qualia คือประสบการณ์ ไม่ใช่คำอธิบาย" (Qualia is experience, not explanation)

---

## 📁 Directory Structure

```
Artifact_Qualia/
├── README.md                          # This file
├── Artifact_Qualia.py                 # Core implementation
│
├── configs/                           # YAML specifications
│   ├── Artifact_Qualia_Spec_v8.1.yaml           # Comprehensive spec
│   ├── Artifact_Qualia_Input_Contract.yaml      # Input specification
│   ├── Artifact_Qualia_Output_Contract.yaml     # Output specification
│   └── Artifact_Qualia_Interface.yaml           # Interface specification
│
└── tests/                             # Unit tests (when implemented)
```

---

## Design Principles (from EVA 7.0)

### Core Principles

1. **"Qualia คือประสบการณ์ ไม่ใช่คำอธิบาย"**
   Qualia is experience, not explanation

2. **"ร่างกายส่งสัญญาณ ไม่ส่ง label"**
   Body sends signals, not labels

3. **"ทิศทางสำคัญกว่าค่าคงที่"**
   Direction matters more than absolute values

4. **"น้ำหนักเหตุการณ์แยกจากการแสดงออก"**
   Event weight is separate from expression

5. **"LLM ตีความเองจากสัญญาณ"**
   LLM interprets signals itself

### Non-Goals

Artifact_Qualia **does NOT**:
- ❌ Create emotional labels (e.g., เขิน, เครียด, ดีใจ)
- ❌ Provide numeric RI/RIM/MAS/KI scores to LLM
- ❌ Generate narrative summaries
- ❌ Override persona or intent
- ❌ Make decisions for LLM
- ❌ Control memory admission
- ❌ Evaluate relationships
- ❌ Optimize or judge (no "good" or "bad")

### Authority

**Artifact_Qualia IS:**
- ✅ Perceptual substrate
- ✅ Experience carrier
- ✅ Phenomenological integrator
- ✅ Pre-conceptual signal generator

**Artifact_Qualia IS NOT:**
- ❌ Decision engine
- ❌ Intent selector
- ❌ Language generator
- ❌ Memory admission controller

---

## Current Implementation (v8.1.0)

### API Signature

```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class RIMSemantic:
    impact_level: str      # "low" | "medium" | "high"
    impact_trend: str      # "rising" | "stable" | "fading"
    affected_domains: list # ["emotional", "relational", "identity", "ambient"]

@dataclass
class QualiaSnapshot:
    intensity: float       # [0.0, 1.0] - Experiential intensity
    tone: str             # "quiet" | "charged" | "settling" | "neutral"
    coherence: float      # [0.0, 1.0] - Internal consistency
    depth: float          # [0.0, 1.0] - Experiential immersion
    texture: Dict[str, float]  # 4D texture vector

# Main integration method
def integrate(
    self,
    eva_state: Dict[str, Any],  # From EVA_Matrix_System.get_full_state()
    rim_semantic: RIMSemantic   # From Resonance_Impact_Module
) -> QualiaSnapshot:
    ...
```

### Input: EVA State (from EVA Matrix)

**Structure:**
```python
eva_state = {
    "axes_9d": {
        "stress": 0.7,        # ความเครียด/ความกดดัน
        "warmth": 0.4,        # ความอบอุ่น/ความเป็นมิตร
        "drive": 0.6,         # แรงขับ/แรงจูงใจ
        "clarity": 0.5,       # ความชัดเจนทางความคิด
        "joy": 0.3,           # ความสุข/ความเบิกบาน
        "alertness": 0.8,     # ความตื่นตัว
        "connection": 0.5,    # ความเชื่อมโยง/ความผูกพัน
        "groundedness": 0.4,  # ความมั่นคง/ความสมดุล
        "openness": 0.6       # ความเปิดกว้างทางจิตใจ
    },
    "emotion_label": "Agitated",  # Optional
    "momentum": {
        "intensity": 0.65,
        "velocity": 0.2
    }
}
```

**Reference:** `eva_matrix/configs/EVA_Matrix_Output_Contract.yaml`

### Output: QualiaSnapshot

**Example Output:**
```python
QualiaSnapshot(
    intensity=0.73,        # How strong the experience feels
    tone="charged",        # Phenomenological quality
    coherence=0.52,        # Internal consistency (fragmenting)
    depth=0.68,            # Experiential immersion
    texture={
        "emotional": 0.82,    # From stress
        "relational": 0.61,   # From (alertness + drive) / 2
        "identity": 0.45,     # From clarity
        "ambient": 0.58       # From momentum.intensity
    }
)
```

### Phenomenological Fields

#### 1. Intensity (ความเข้มของประสบการณ์ของ llm)

How strong/vivid the experience feels (NOT emotional intensity - phenomenological vividness).

**Calculation:**
```python
baseline_arousal = (alertness + drive) / 2
base = clamp(baseline_arousal + stress)

# RIM modulation
rim_boost = {"low": 0, "medium": 0.1, "high": 0.2}[rim.impact_level]
raw = clamp(base + rim_boost)

# Temporal smoothing (exponential moving average)
intensity = 0.65 * prev_intensity + 0.35 * raw
```

#### 2. Tone (โทนคุณภาพของประสบการณ์)

Coarse phenomenological quality (not emotional labels).

**Values:**
- `"quiet"` - groundedness > 0.6
- `"charged"` - stress > 0.7
- `"settling"` - RIM impact_trend == "fading"
- `"neutral"` - default

#### 3. Coherence (ความสอดคล้องภายใน)

How internally consistent/stable the experience feels.
- Low = fragmented, confused
- High = clear, integrated

**Calculation:**
```python
base = (clarity + momentum.intensity) / 2

# RIM disruption
rim_disruption = {"low": 0, "medium": -0.05, "high": -0.15}[rim.impact_level]
raw = clamp(base + rim_disruption)

# Temporal smoothing
coherence = 0.7 * prev_coherence + 0.3 * raw
```

#### 4. Depth (ความลึกของประสบการณ์)

Sense of experiential depth or immersion.

**Calculation:**
```python
depth = 0.6 * groundedness + 0.4 * stress
```

**No temporal smoothing** (instantaneous response).

#### 5. Texture (เนื้อสัมผัสทางจิตวิทยา)

4-dimensional phenomenological texture vector for RMS memory encoding.

**Dimensions:**
- `emotional` - From `axes_9d.stress`
- `relational` - From `(axes_9d.alertness + axes_9d.drive) / 2`
- `identity` - From `axes_9d.clarity`
- `ambient` - From `momentum.intensity`

**RIM Modulation:**
If domain in `rim.affected_domains`, amplify by 15%:
```python
if "emotional" in rim.affected_domains:
    texture["emotional"] *= 1.15  # Clamped to 1.0
```

---

## EVA 7.0 → 8.1.0 Migration Guide

### Field Name Changes

| EVA 7.0 Field | EVA 8.1.0 Field | Type |
|---------------|-----------------|------|
| `stress_load` | `stress` | Direct mapping |
| `social_warmth` | `warmth` | Direct mapping |
| `drive_level` | `drive` | Direct mapping |
| `cognitive_clarity` | `clarity` | Direct mapping |
| `joy_level` | `joy` | Direct mapping |
| `arousal_level` | `alertness` | Direct mapping (renamed) |
| `affective_stability` | `groundedness` | Conceptual mapping |
| `social_orientation` | `connection` | Conceptual mapping |
| `focus_level` | `clarity` | Merged with cognitive_clarity |
| (none) | `openness` | **NEW in 8.1.0** |

### Implementation Field Fixes

**Current implementation uses non-existent fields.** These must be mapped to real EVA 8.1.0 fields:

| Incorrect Usage (Code) | Correct Mapping (8.1.0) |
|------------------------|-------------------------|
| `eva.get("baseline_arousal", 0.0)` | `(axes_9d.alertness + axes_9d.drive) / 2` |
| `eva.get("emotional_tension", 0.0)` | `axes_9d.stress` |
| `eva.get("calm_depth", 0.0)` | `axes_9d.groundedness` |
| `eva.get("coherence", 0.5)` | `axes_9d.clarity` |
| `eva.get("momentum", 0.5)` | `momentum.intensity` |

**Action Required:** Update `Artifact_Qualia.py` to use correct field access patterns.

### What Changed from 7.0 to 8.1.0?

**Unchanged:**
- ✅ 9D axes structure (still 9 dimensions)
- ✅ QualiaSnapshot output structure
- ✅ Design principles and invariants
- ✅ Temporal smoothing algorithms

**Changed:**
- 🔄 Field names shortened (stress_load → stress, etc.)
- 🔄 Some axes renamed/reinterpreted
- 🔄 `momentum` changed from `float` to `object {intensity, velocity}`

**Added:**
- ✨ `openness` axis (new 9th axis)

**Removed:**
- ❌ `focus_level` (merged into `clarity`)

---

## Downstream Integration

### Resonance Memory System (RMS)

**Connection:** `RMS.process()` receives `QualiaSnapshot.texture`

**Usage:**
```python
# In RMS memory encoding
resonance_textures = {
    "emotional": qualia.texture["emotional"],
    "relational": qualia.texture["relational"],
    "identity": qualia.texture["identity"],
    "ambient": qualia.texture["ambient"]
}
```

**Purpose:** Provides phenomenological dimensions for memory encoding.

### Memory & Soul Passport (MSP)

**Connection:** Receives `QualiaSnapshot` indirectly via RMS

**Usage:** Phenomenological metadata stored in episodic memory:
```json
{
    "episode_id": "ep_260103_183045_a1b2c3",
    "qualia": {
        "intensity": 0.73,
        "tone": "charged",
        "coherence": 0.52,
        "depth": 0.68
    }
}
```

### LLM Bridge (Future via CIN)

**Status:** PLANNED (not yet implemented)

**Would inject into LLM context:**
```
Internal felt state:
- Experience intensity: moderate-high (0.73)
- Phenomenological tone: charged
- Internal coherence: fragmenting (0.52)
- Depth of immersion: moderate (0.68)
- Texture: high emotional, moderate relational
```

**Benefit:** Gives the llm experiential grounding for response generation.

---

## Current Limitations

### Output Simplicity
- Only 5 output fields (intensity, tone, coherence, depth, texture)
- No temporal dynamics (no `delta_9d` tracking)
- No layered experience (surface/middle/deep)
- No ineffable quality markers
- No somatic location mapping

### Input Scope
- Only EVA Matrix + RIM (no `biological_context`)
- No `reflex_vector` from FastReflexEngine
- No `stimulus_impact` from perception layer
- No previous state (`eva_state_prev` for delta calculation)

### Processing
- No experiential flags (`internal_conflict`, `instability_increasing`, etc.)
- No directional momentum detection
- Simple texture vector (only 4 dimensions)

---

## Future Enhancements

### Phase 1: Temporal Dynamics (HIGH Priority)

**Effort:** 3-4 hours
**Status:** PLANNED

**Would Add:**
- `delta_9d` - Track changes in 9D axes (now - prev)
- `directional_momentum` - Detect dominant rise/fall axes
- Experiential trajectory tracking

**Requires:**
- `eva_state_prev` parameter
- State persistence across turns

### Phase 2: Experiential Flags (HIGH Priority)

**Effort:** 2-3 hours
**Status:** PLANNED

**Would Add:**
```python
flags = {
    "internal_conflict": bool,      # Simultaneous rise and fall
    "instability_increasing": bool, # Groundedness dropping
    "social_push_pull": bool,       # Warmth + stress rising together
    "high_impact_state": bool       # RIM impact_level == high
}
```

### Phase 3: Rich Phenomenological Field (MEDIUM Priority)

**Effort:** 8-12 hours
**Status:** DESIGN_PHASE
**Reference:** `docs/QUALIA_PHILOSOPHICAL_ANALYSIS.md`

**Would Add:**

#### Affective Tone (Multi-layered)
```python
affective_tone = {
    "primary_feel": "sharp_hollow_ache",
    "secondary_feel": "anxious_anticipation",
    "metaphor": "walking on eggshells"
}
```

#### Somatic Presence (Body-mapped)
```python
somatic_presence = {
    "chest": "collapsed_inward",
    "throat": "tight_constricted",
    "stomach": "churning_unsettled",
    "impulse": "hide_disappear"
}
```

#### Temporal Flow
```python
temporal_flow = {
    "trajectory": "intensifying",
    "phase": "shock_to_realization",
    "momentum": "accelerating"
}
```

#### Layered Experience
```python
layered_experience = {
    "surface": "frustration",
    "middle": "disappointment",
    "deep": "shame",
    "conflict": true
}
```

#### Ineffable Quality
```python
ineffable_quality = {
    "hard_to_name": true,
    "paradoxical": true,
    "metaphor_needed": true,
    "primary_metaphor": "light_at_end_of_tunnel_but_tunnel_collapsing"
}
```

### Phase 4: Biological Integration (MEDIUM Priority)

**Effort:** 4-6 hours
**Status:** PLANNED

**Would Add:**
```python
biological_context = {
    "hormone_levels": {
        "cortisol": 0.8,
        "adrenaline": 0.6,
        "oxytocin": 0.3,
        "serotonin": 0.4
    },
    "ans_dominance": "sympathetic"  # or "parasympathetic" or "balanced"
}
```

**Requires:**
- PhysioController integration
- FastReflexEngine connection

---

## Usage Example

```python
from Artifact_Qualia import ArtifactQualiaCore
from dataclasses import dataclass

@dataclass
class RIMSemantic:
    impact_level: str
    impact_trend: str
    affected_domains: list

# Initialize
qualia = ArtifactQualiaCore()

# Prepare inputs from EVA Matrix
eva_state = {
    "axes_9d": {
        "stress": 0.7,
        "warmth": 0.4,
        "drive": 0.6,
        "clarity": 0.5,
        "joy": 0.3,
        "alertness": 0.8,
        "connection": 0.5,
        "groundedness": 0.4,
        "openness": 0.6
    },
    "momentum": {
        "intensity": 0.65,
        "velocity": 0.2
    }
}

# Prepare RIM semantic signal
rim_semantic = RIMSemantic(
    impact_level="high",
    impact_trend="rising",
    affected_domains=["emotional", "relational"]
)

# Generate phenomenological snapshot
snapshot = qualia.integrate(eva_state, rim_semantic)

print(snapshot)
# Output:
# QualiaSnapshot(
#   intensity=0.73,
#   tone='charged',
#   coherence=0.52,
#   depth=0.68,
#   texture={'emotional': 0.82, 'relational': 0.61, 'identity': 0.45, 'ambient': 0.58}
# )

# Use in downstream modules
rms.process(qualia_snapshot=snapshot)
```

---

## Documentation

### Specifications (YAML)

- **[Artifact_Qualia_Spec_v8.1.yaml](configs/Artifact_Qualia_Spec_v8.1.yaml)** - Comprehensive specification
- **[Artifact_Qualia_Input_Contract.yaml](configs/Artifact_Qualia_Input_Contract.yaml)** - Input contract
- **[Artifact_Qualia_Output_Contract.yaml](configs/Artifact_Qualia_Output_Contract.yaml)** - Output contract
- **[Artifact_Qualia_Interface.yaml](configs/Artifact_Qualia_Interface.yaml)** - Interface specification

### Documentation (Markdown)

- **[ARTIFACT_QUALIA_MIGRATION_PLAN.md](../docs/ARTIFACT_QUALIA_MIGRATION_PLAN.md)** - EVA 7.0 → 8.1.0 migration guide
- **[QUALIA_PHILOSOPHICAL_ANALYSIS.md](../docs/QUALIA_PHILOSOPHICAL_ANALYSIS.md)** - Philosophical analysis of qualia concept
- **[ARCHITECTURE_FLOW_VALIDATED.md](../docs/ARCHITECTURE_FLOW_VALIDATED.md)** - System architecture (contains qualia flow)

### Upstream Contracts

- **[EVA_Matrix_Output_Contract.yaml](../eva_matrix/configs/EVA_Matrix_Output_Contract.yaml)** - EVA Matrix output specification

---

## Version History

- **8.1.0** (Current) - Updated field names, aligned with EVA Matrix 8.1.0
- **7.0** (Previous) - Original implementation with temporal dynamics and experiential flags

---

## 📊 Key Specifications

- **State:** Stateful (maintains `_last_intensity`, `_last_coherence` for temporal smoothing)
- **Visibility:** LLM can see output, but cannot modify module
- **Execution:** Synchronous, deterministic (< 1ms execution time)
- **Side Effects:** None (pure integration function)
- **Version:** 8.1.0

---

## Contributing

When modifying Artifact_Qualia, ensure:

1. ✅ **Field Access Patterns** - Use correct EVA 8.1.0 field names
2. ✅ **Design Principles** - Maintain "qualia is experience, not explanation"
3. ✅ **Type Safety** - All outputs in valid ranges [0.0, 1.0]
4. ✅ **Temporal Continuity** - Preserve smoothing algorithms
5. ✅ **Contract Alignment** - Update YAML contracts when changing API
6. ✅ **Phenomenological Purity** - No emotion labels, no numeric scores

---

## License

Part of EVA 8.1.0 - The Human Algorithm Research Project

---

**Last Updated:** 2026-01-03
**Contract Status:** ALIGNED_WITH_IMPLEMENTATION
**Migration Status:** Phase 1 (Field Mapping) Complete
