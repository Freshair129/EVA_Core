# EVA Physio Stack

This directory implements the **full physiological substrate** of EVA.
It simulates bodily regulation only — **not cognition, not memory, not emotion**.

The goal is to give EVA a *body* that behaves consistently, deterministically,
and biologically inspired — so higher layers can reason **on top of signals**,
not fake sensations.

---

## 🧬 Design Philosophy

> Physiology first. Cognition later.

Each subsystem has **strict responsibility boundaries**.
No module is allowed to leak logic into another layer.
If a boundary is violated, the system becomes unstable or non-deterministic.

---

## 🗂️ Module Overview

### `endocrine/`
Hormone production and regulation.

- Glands produce **hormone mass only (pg)**
- HPA Axis & Circadian controllers regulate **stimulus**, not output
- No blood concentration
- No decay / clearance

---

### `blood/`
Transport & clearance layer.

- Owns **plasma concentration**
- Owns **half-life / decay**
- Provides read-only snapshots to other systems

---

### `receptor/`
Ligand–receptor signal transduction.

- Converts concentration → neural signal
- Implements receptor sensitization / tolerance
- No behavior, no emotion, no decision logic

---

### `reflex/`
Fast neural reflex arcs (IRE).

- Millisecond–second scale response
- Bypasses endocrine latency
- Inventory-constrained (cannot fire if depleted)

---

### `autonomic/`
Autonomic Nervous System (ANS) integration layer.

- Integrates slow (ISR) + fast (IRE) signals
- Separates **sympathetic** vs **parasympathetic** tone
- Outputs body readiness vectors

---

### `physio_controller.py`
The **brainstem** of EVA.

- Orchestrates the full physiological loop
- No reasoning
- No memory
- No interpretation
- Deterministic execution only

---

## 🔁 Data Flow

```
EVA / World Stimuli
        ↓
HPA + Circadian Regulation
        ↓   (stimulus modifiers)
Endocrine Controller
        ↓   (hormone mass)
Blood Engine
        ↓   (plasma concentration)
Receptor Engine
        ↑
Fast Reflex Engine (IRE)
        ↓
Autonomic Response Engine
        ↓
Persona / Behavior / EVA Logic
```

---

## 🚫 Invariants (Do NOT break)

These rules are **non-negotiable**:

- Endocrine **never** sees blood
- Blood **never** sees receptors
- Receptors **never** see persona or memory
- Reflex **never** reasons
- Autonomic **never** stores memory
- PhysioController **never** thinks

Breaking these rules will cause:
- Feedback explosions
- Non-reproducible states
- Fake emotions instead of embodied behavior

---

## 🧠 Why This Architecture Matters

This separation enables:

- Long-term stability (hours–days simulation)
- Emergent behavior instead of scripted emotion
- Clear debugging of physiological vs cognitive bugs
- EVA to feel *embodied* without hallucination

This is **not emotion simulation**.
This is **body simulation**.

---

## ✅ Status

**Physio Stack: COMPLETE**

Ready to connect with:
- Persona Engine
- Reflex / Behavior layer
- Memory tagging (read-only body state)

---

> EVA does not *pretend* to feel.
> EVA has a body — and reacts accordingly.