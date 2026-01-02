# Artifact Qualia Migration Plan: EVA 7.0 → EVA 8.1.0

**Date:** 2026-01-03
**Status:** Analysis Complete
**Migration Type:** Spec Update + Implementation Fix

---

## Executive Summary

EVA 7.0 มี **Artifact_Qualia.yaml spec ที่ครบถ้วนและดีกว่า 8.1.0** มาก แต่ใช้ field names จาก EVA Matrix 9D เวอร์ชันเก่า

**แผนการ:**
1. ใช้ **structure/principles จาก EVA 7.0 spec** (ดีกว่า)
2. **อัพเดท field names** ให้ตรงกับ EVA 8.1.0
3. **แก้ implementation** ให้ใช้ field names ที่ถูกต้อง

---

## EVA Matrix 9D Field Mapping: 7.0 → 8.1.0

### EVA 7.0 (9 Axes)

```yaml
eva_matrix_9d:
  axes:
    - stress_load              # ความเครียด
    - social_warmth            # ความอบอุ่นทางสังคม
    - drive_level              # แรงขับ
    - cognitive_clarity        # ความชัดเจนทางความคิด
    - joy_level                # ความสุข
    - affective_stability      # เสถียรภาพทางอารมณ์
    - social_orientation       # การหันหน้าเข้าหาสังคม
    - focus_level              # ความตั้งใจ
    - arousal_level            # ความตื่นตัว
```

### EVA 8.1.0 (9 Axes)

```yaml
axes_9d:
  properties:
    - stress                   # ความเครียด/ความกดดัน
    - warmth                   # ความอบอุ่น/ความเป็นมิตร
    - drive                    # แรงขับ/แรงจูงใจ
    - clarity                  # ความชัดเจนทางความคิด
    - joy                      # ความสุข/ความเบิกบาน
    - alertness                # ความตื่นตัว
    - connection               # ความเชื่อมโยง/ความผูกพัน
    - groundedness             # ความมั่นคง/ความสมดุล
    - openness                 # ความเปิดกว้างทางจิตใจ
```

### Direct Mapping (1:1)

| EVA 7.0 | EVA 8.1.0 | Notes |
|---------|-----------|-------|
| `stress_load` | `stress` | ✅ Same concept |
| `social_warmth` | `warmth` | ✅ Same concept |
| `drive_level` | `drive` | ✅ Same concept |
| `cognitive_clarity` | `clarity` | ✅ Same concept |
| `joy_level` | `joy` | ✅ Same concept |
| `arousal_level` | `alertness` | ✅ Same concept (renamed) |

### Conceptual Mapping (needs interpretation)

| EVA 7.0 | EVA 8.1.0 | Mapping Logic |
|---------|-----------|---------------|
| `affective_stability` | `groundedness` | ⚠️ Stability ≈ Groundedness (emotional balance) |
| `social_orientation` | `connection` | ⚠️ Social orientation → interpersonal connection |
| `focus_level` | `clarity` | ⚠️ Focus is cognitive clarity in 8.1.0 |

### New in 8.1.0 (no 7.0 equivalent)

| EVA 8.1.0 Field | Description | 7.0 Equivalent |
|-----------------|-------------|----------------|
| `openness` | ความเปิดกว้างทางจิตใจ | ❌ No direct mapping |

---

## Implementation Field Names (Currently WRONG)

### Fields Used in Code (Both 7.0 and 8.1.0)

**ปัญหา:** Code ใช้ field names ที่**ไม่มีในทั้ง 7.0 และ 8.1.0**

```python
# ❌ These fields DON'T EXIST in either version:
eva.get("baseline_arousal", 0.0)      # Not in 7.0 or 8.1.0
eva.get("emotional_tension", 0.0)     # Not in 7.0 or 8.1.0
eva.get("calm_depth", 0.0)            # Not in 7.0 or 8.1.0
eva.get("coherence", 0.5)             # Not in 7.0 or 8.1.0
eva.get("momentum", 0.5)              # Wrong type (should be object)
```

### Proposed Field Mapping for Implementation

**Mapping non-existent fields → EVA 8.1.0 fields:**

| Code Field (WRONG) | Proposed Mapping | EVA 8.1.0 Source |
|--------------------|------------------|------------------|
| `baseline_arousal` | `(alertness + drive) / 2` | Composite of alertness + drive |
| `emotional_tension` | `stress` | Direct from axes_9d.stress |
| `calm_depth` | `groundedness` | Direct from axes_9d.groundedness |
| `coherence` | `clarity` | Direct from axes_9d.clarity |
| `momentum` (float) | `momentum.intensity` | From metadata.momentum.intensity |

---

## EVA 7.0 Spec Features (Worth Keeping)

### 1. Temporal Dynamics (Delta Calculation)

**EVA 7.0 มี - 8.1.0 ไม่มี:**
```yaml
derived:
  delta_9d:
    description: "การเปลี่ยนแปลงของแกน 9D (now - prev)"
    formula: "delta[k] = eva_matrix_9d[k] - eva_matrix_9d_prev[k]"
    clamp: [-1.0, 1.0]

directional_momentum:
  dominant_rise: "แกนที่พุ่งขึ้นแรงที่สุด"
  secondary_rise: "แกนที่พุ่งขึ้นรองลงมา"
  dominant_fall: "แกนที่ดิ่งลงแรงที่สุด"
  secondary_fall: "แกนที่ดิ่งลงรองลงมา"
```

**ควรเพิ่มใน 8.1.0:** ✅ YES - Temporal dynamics are valuable

---

### 2. Experiential Flags

**EVA 7.0 มี - 8.1.0 ไม่มี:**
```yaml
flags:
  internal_conflict: "มีแรงพุ่งและแรงดิ่งพร้อมกัน"
  instability_increasing: "เสถียรภาพลดลงอย่างมีนัย"
  social_push_pull: "แรงเข้าหาทางสังคม + ความตึงเพิ่มพร้อมกัน"
  high_impact_state: "เหตุการณ์มีน้ำหนักต่อประสบการณ์"
```

**ควรเพิ่มใน 8.1.0:** ✅ YES - Flags provide rich phenomenological context

---

### 3. Core Principles

**EVA 7.0 principles (ยอดเยี่ยม):**
```yaml
principles:
  - "Qualia คือประสบการณ์ ไม่ใช่คำอธิบาย"
  - "ร่างกายส่งสัญญาณ ไม่ส่ง label"
  - "ทิศทางสำคัญกว่าค่าคงที่"
  - "น้ำหนักเหตุการณ์แยกจากการแสดงออก"
  - "LLM ตีความเองจากสัญญาณ"
```

**ควรเพิ่มใน 8.1.0:** ✅ YES - Fundamental design principles

---

### 4. Detailed Input Sources

**EVA 7.0 ระบุชัดเจน:**
```yaml
inputs:
  reflex_vector:        # จาก IRE
  eva_matrix_9d:        # จาก EVA Matrix
  eva_matrix_9d_prev:   # ค่าเทิร์นก่อน
  persona_state:        # trust, familiarity, social_distance
  rim_signal:           # impact_level, impact_trend, affected_domains
  knowledge_impact_signal:  # gravity_level, integration_type
  memory_admission_signal:  # should_write, memory_route, priority
```

**8.1.0 Input Contract ปัจจุบัน:**
```yaml
# บางส่วนไม่ตรงกับ implementation
psychological_state: ✓ มี
biological_context: ⚠️ Contract มี แต่ implementation ไม่รับ
stimulus_impact: ⚠️ Contract มี แต่ implementation ไม่รับ
```

**ควรทำ:** ⚠️ Align contract with actual implementation

---

## Migration Strategy

### Phase 1: Quick Fix (Production Ready) ⭐ RECOMMENDED

**Goal:** Make Artifact_Qualia work with EVA 8.1.0 NOW

**Actions:**
1. ✅ Update `Artifact_Qualia.py` field mappings:
   - `baseline_arousal` → `(axes_9d.alertness + axes_9d.drive) / 2`
   - `emotional_tension` → `axes_9d.stress`
   - `calm_depth` → `axes_9d.groundedness`
   - `coherence` → `axes_9d.clarity`
   - `momentum` → `momentum.intensity`

2. ✅ Update Input Contract YAML to reflect actual implementation:
   ```yaml
   inputs:
     eva_state:
       type: "object"
       required: true
       description: "EVA Matrix output with axes_9d and momentum"
       ref: "EVA_Matrix_Output_Contract.yaml"

     rim_semantic:
       type: "object"
       required: true
       properties:
         impact_level: { type: "string", enum: [low, medium, high] }
         impact_trend: { type: "string", enum: [rising, stable, fading] }
         affected_domains: { type: "array", items: { type: "string" } }
   ```

3. ✅ Add EVA 7.0 principles to README

**Time:** ~1 hour
**Risk:** Low
**Result:** Working Artifact_Qualia with correct field access

---

### Phase 2: Enhanced Features (Future)

**Goal:** Add valuable features from EVA 7.0 spec

**Actions:**
1. ⏳ Implement delta_9d calculation (temporal dynamics)
2. ⏳ Add directional_momentum detection
3. ⏳ Implement experiential flags
4. ⏳ Add eva_matrix_9d_prev tracking

**Time:** ~3-4 hours
**Risk:** Medium (changes API)
**Result:** Rich phenomenological experience tracking

---

### Phase 3: Full Integration (Long-term)

**Goal:** Complete input integration as per original vision

**Actions:**
1. ⏳ Add biological_context from PhysioController
2. ⏳ Add stimulus_impact from perception layer
3. ⏳ Add reflex_vector from IRE/FastReflexEngine
4. ⏳ Add persona_state tracking
5. ⏳ Add knowledge_impact_signal routing
6. ⏳ Add memory_admission_signal routing

**Time:** ~8-12 hours (full system integration)
**Risk:** High (requires upstream systems)
**Result:** Complete phenomenological integration as originally designed

---

## Recommended Action Plan

### Immediate (Today) ✅

**Fix Critical Field Mapping Issues:**

```python
# File: Artifact_Qualia/Artifact_Qualia.py

def _compute_intensity(self, eva: Dict[str, float], rim: RIMSemantic) -> float:
    """Compute phenomenological intensity."""

    # Extract 8.1.0 fields correctly
    axes = eva.get("axes_9d", {})

    # Map old concepts to new fields
    baseline_arousal = (
        axes.get("alertness", 0.0) +
        axes.get("drive", 0.0)
    ) / 2
    emotional_tension = axes.get("stress", 0.0)

    base = clamp(baseline_arousal + emotional_tension)

    # ... rest of logic unchanged
```

**Same pattern for:**
- `_compute_coherence()` - use `axes.clarity` and `momentum.intensity`
- `_compute_depth()` - use `axes.groundedness` and `axes.stress`
- `_derive_tone()` - use `axes.groundedness` and `axes.stress`
- `_build_texture()` - use correct axes fields

---

### Short-term (This Week) ✅

**Update Documentation:**

1. Create `Artifact_Qualia_Spec_v8.1.yaml` based on EVA 7.0 structure:
   - Keep principles, non-goals, authority
   - Update field names to 8.1.0
   - Align inputs with actual implementation

2. Add EVA 7.0 → 8.1.0 field mapping table to README

3. Document future enhancements (delta_9d, flags, etc.)

---

### Medium-term (Next Sprint) ⏳

**Add Enhanced Features:**

1. Implement `delta_9d` calculation (track prev state)
2. Add directional momentum detection
3. Implement experiential flags

---

## File Changes Required

### Files to Update (Phase 1):

1. **`Artifact_Qualia/Artifact_Qualia.py`** - Fix field mappings
   - Lines 117-119 (_compute_intensity)
   - Lines 148-149 (_compute_coherence)
   - Lines 168-169 (_compute_depth)
   - Lines 186, 189 (_derive_tone)
   - Lines 209-212 (_build_texture)

2. **`Artifact_Qualia/configs/Artifact_Qualia_Input_Contract.yaml`** - Align with reality
   - Remove `biological_context`, `stimulus_impact` (not implemented yet)
   - Clarify `eva_state` structure
   - Document `rim_semantic` structure

3. **`Artifact_Qualia/configs/Artifact_Qualia_Interface.yaml`** - Update inputs
   - Remove non-existent upstream modules (K_Impact, MAS, IRE)
   - List actual inputs: EVA Matrix, RIM only

4. **`Artifact_Qualia/README.md`** - Add migration guide
   - Document 7.0 → 8.1.0 field mapping
   - Add EVA 7.0 principles
   - Explain future enhancements

### Files to Create:

5. **`Artifact_Qualia/configs/Artifact_Qualia_Spec_v8.1.yaml`** - New comprehensive spec
   - Based on EVA 7.0 structure
   - Updated to 8.1.0 field names
   - Current implementation scope

---

## Success Criteria

### Phase 1 (Immediate):
- ✅ Artifact_Qualia accesses real EVA Matrix data (not defaults)
- ✅ All `.get()` calls return actual values
- ✅ QualiaSnapshot contains accurate phenomenological data
- ✅ Contracts match implementation reality

### Phase 2 (Enhanced):
- ⏳ Delta tracking works
- ⏳ Directional momentum detected
- ⏳ Flags correctly computed

### Phase 3 (Full):
- ⏳ All 7.0 spec inputs integrated
- ⏳ Rich phenomenological experience packet
- ⏳ Complete upstream integration

---

## Conclusion

**EVA 7.0 spec เป็นแนวทางที่ดี** - ครบถ้วน มี principles ชัดเจน มี temporal dynamics

**แต่ต้องปรับให้เข้ากับ EVA 8.1.0:**
1. Field names เปลี่ยนไป
2. Upstream modules บางตัวยังไม่มี
3. Implementation ต้องแก้ให้ใช้ fields ที่ถูกต้อง

**Recommended: Phase 1 First** - ทำให้ระบบทำงานได้ก่อน แล้วค่อยเพิ่มฟีเจอร์ทีหลัง

---

**Migration Status:** Ready to Execute
**Priority:** 🔴 CRITICAL (Phase 1), 🟡 HIGH (Phase 2), 🟢 MEDIUM (Phase 3)
**Estimated Time:** 1 hour (Phase 1), 3-4 hours (Phase 2), 8-12 hours (Phase 3)
