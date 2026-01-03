# State Bus Architecture Analysis for EVA 8.1.0

**Date:** 2026-01-03
**Pattern:** State Bus (Centralized State Management)
**Status:** Re-evaluation - This is DIFFERENT from Message Bus

---

## ⚠️ Critical Clarification

**State Bus ≠ Message Bus**

| Pattern | Philosophy | Example |
|---------|-----------|---------|
| **Message Bus** | Event-driven, async pub/sub | RabbitMQ, Kafka |
| **State Bus** | Centralized state store | Redux, Vuex, MobX |

**Previous analysis was for Message Bus. Let's analyze State Bus properly.**

---

## What is State Bus?

### Concept: Single Source of Truth

```python
# Centralized State Store
class EVAStateStore:
    """
    Single source of truth for entire EVA system
    All components read/write from here
    """
    def __init__(self):
        self.state = {
            "physio": {
                "blood": {"cortisol": 0.0, "adrenaline": 0.0, ...},
                "autonomic": {"sympathetic": 0.0, "parasympathetic": 0.0},
                "glands": {...}
            },
            "eva_matrix": {
                "axes_9d": {"stress": 0.0, "warmth": 0.0, ...},
                "safety_reflex": {...}
            },
            "qualia": {
                "intensity": 0.0,
                "coherence": 0.0,
                ...
            },
            "memory": {
                "recent_episodes": [],
                "active_context": {}
            },
            "llm": {
                "phase": None,  # "phase_1" | "phase_2"
                "last_response": None,
                "function_call": None
            }
        }

        self.subscribers = {}  # Component callbacks
        self.history = []  # State history for time-travel

    def get_state(self, path: str):
        """
        Get nested state: store.get_state("physio.blood.cortisol")
        """
        keys = path.split(".")
        value = self.state
        for key in keys:
            value = value[key]
        return value

    def set_state(self, path: str, value: Any):
        """
        Update state and notify subscribers
        """
        # Update state
        keys = path.split(".")
        target = self.state
        for key in keys[:-1]:
            target = target[key]
        target[keys[-1]] = value

        # Save history (for time-travel debugging)
        self.history.append({
            "timestamp": time.time(),
            "path": path,
            "value": value,
            "state_snapshot": deepcopy(self.state)
        })

        # Notify subscribers
        self._notify_subscribers(path, value)

    def subscribe(self, path: str, callback: Callable):
        """
        Subscribe to state changes:
        store.subscribe("physio.blood", on_blood_change)
        """
        self.subscribers.setdefault(path, []).append(callback)


# Example: PhysioController uses State Bus
class PhysioController:
    def __init__(self, state_store: EVAStateStore):
        self.store = state_store

        # Subscribe to stimulus changes
        self.store.subscribe("inputs.stimulus", self.on_stimulus)

    def on_stimulus(self, stimulus: Dict):
        # React to stimulus
        self.step(stimulus)

    def step(self, stimulus: Dict):
        # Calculate new physio state
        new_blood = self.blood_engine.update(...)
        new_ans = self.ans.calculate(...)

        # Write to State Bus (everyone can read)
        self.store.set_state("physio.blood", new_blood)
        self.store.set_state("physio.autonomic", new_ans)


# Orchestrator just coordinates, state is in bus
class EVAOrchestrator:
    def __init__(self, state_store: EVAStateStore):
        self.store = state_store

    def process_user_input(self, user_input: str):
        # Write user input to state
        self.store.set_state("inputs.user_message", user_input)

        # Phase 1
        self.store.set_state("llm.phase", "phase_1")
        stimulus = self.llm_phase_1()  # LLM extracts stimulus

        # Write stimulus (triggers PhysioController via subscription)
        self.store.set_state("inputs.stimulus", stimulus)

        # Wait for physio to finish (read from state)
        while self.store.get_state("physio.status") != "ready":
            time.sleep(0.01)

        # Phase 2 (read updated state)
        physio_state = self.store.get_state("physio")
        eva_state = self.store.get_state("eva_matrix")

        self.store.set_state("llm.phase", "phase_2")
        response = self.llm_phase_2(physio_state, eva_state)

        return response
```

---

## State Bus vs Current Architecture

### Current: Pass-State-Around Pattern

```python
# State is passed as parameters
def process_user_input(self, user_input: str):
    # Phase 1
    ctx_p1 = self.cin.inject_phase_1(user_input)  # Creates context dict
    llm_p1 = self.llm_bridge.generate(ctx_p1)

    # The Gap - state passed between components
    physio_state = self.physio.step(stimulus)  # Returns dict
    eva_state = self.matrix.compute(physio_state)  # Receives dict
    qualia_state = self.qualia.integrate(eva_state, rim)  # Receives dict

    # Phase 2 - assemble all dicts
    ctx_p2 = self.cin.inject_phase_2(
        stimulus, tags, physio_state, eva_state, qualia_state, memories
    )
    llm_p2 = self.llm_bridge.continue_with_result(ctx_p2)
```

**Problem:**
- State scattered across return values
- Must pass state manually between components
- Hard to debug: "what was cortisol level when EVA Matrix computed stress?"
- Can't easily save/restore full system state

### State Bus: Centralized State Pattern

```python
# State lives in central store
def process_user_input(self, user_input: str):
    # Write input to state
    self.store.set_state("inputs.user_message", user_input)

    # Phase 1
    self.store.set_state("llm.phase", "phase_1")
    self.llm_phase_1()  # Writes stimulus to store

    # The Gap - components read/write from store
    self.physio.step()  # Reads stimulus from store, writes blood/ANS to store
    self.matrix.compute()  # Reads physio from store, writes eva_state to store
    self.qualia.integrate()  # Reads eva/rim from store, writes qualia to store

    # Phase 2 - everything is already in store
    self.store.set_state("llm.phase", "phase_2")
    self.llm_phase_2()  # Reads everything from store

    return self.store.get_state("llm.response")
```

**Benefits:**
- State in one place (easy to inspect)
- Components just read what they need
- Can save entire state snapshot easily
- Time-travel debugging possible

---

## Compatibility with Dual-Phase LLM ✅

**Critical Question:** Does State Bus break the dual-phase pattern?

**Answer: NO** ✅

```python
# Phase 1: LLM calls function
llm_response = llm_api.generate(
    prompt=ctx_p1,
    tools=[sync_biocognitive_state_tool]
)

if llm_response.function_call:
    # Extract function args
    stimulus = llm_response.function_call.args["stimulus_vector"]
    tags = llm_response.function_call.args["tags"]

    # Write to State Bus (triggers The Gap)
    self.store.set_state("inputs.stimulus", stimulus)
    self.store.set_state("inputs.tags", tags)

    # The Gap (components update state bus)
    self.run_the_gap()  # Components read/write from store

    # Read updated state from bus
    function_result = {
        "physio": self.store.get_state("physio"),
        "eva_matrix": self.store.get_state("eva_matrix"),
        "qualia": self.store.get_state("qualia"),
        "memories": self.store.get_state("memory.retrieved")
    }

    # Phase 2: Continue SAME LLM call
    llm_final = llm_api.continue_with_result(function_result)
```

**Verdict:** State Bus is **COMPATIBLE** with dual-phase LLM ✅
- Still one LLM API call
- Still pause & continue
- Just changes WHERE state is stored (central vs passed around)

---

## Advantages of State Bus for EVA

### 1. ✅ State Persistence & Recovery

**Current Problem:**
```python
# How to save full system state?
# Must manually collect from all components
state_snapshot = {
    "physio": self.physio.get_state(),
    "matrix": self.matrix.get_state(),
    "qualia": self.qualia.get_state(),
    "rms": self.rms.get_state(),
    # ... 10+ components
}
```

**State Bus Solution:**
```python
# One-line state snapshot
state_snapshot = self.store.get_full_state()

# One-line state restore
self.store.load_state(state_snapshot)
```

**Use Case:**
- Save state every turn → `Consciousness/10_state/turn_001.json`
- Crash recovery: restore from last saved state
- Debugging: load state from problematic turn

### 2. ✅ Time-Travel Debugging

**Scenario:** "Why did EVA respond angrily at turn 15?"

**Current:** Must re-run from turn 1 with logging

**State Bus:**
```python
# Load turn 15 state
store.load_state_from_file("turn_015.json")

# Replay events
for event in store.history:
    print(f"{event['timestamp']}: {event['path']} = {event['value']}")

# Output:
# 12:34:56.123: physio.blood.cortisol = 0.85
# 12:34:56.456: eva_matrix.axes_9d.stress = 0.92  ← Aha! High stress
# 12:34:56.789: qualia.tone = "charged"
```

### 3. ✅ Cross-Component State Access

**Current Problem:**
```python
# CIN needs to know current blood levels
# But PhysioController is not passed to CIN
# Solution: Pass physio_state as parameter (coupling)

ctx = self.cin.inject_phase_2(
    ...,
    physio_state=physio_state  # Manual passing
)
```

**State Bus Solution:**
```python
# CIN can directly read from state bus
class ContextInjectionNode:
    def __init__(self, store: EVAStateStore):
        self.store = store

    def inject_phase_2(self, ...):
        # Read directly from state bus (no coupling)
        blood_levels = self.store.get_state("physio.blood")
        ans_state = self.store.get_state("physio.autonomic")

        # Build context
        ...
```

**Benefit:** Loose coupling - CIN doesn't depend on PhysioController instance

### 4. ✅ State Validation

```python
class EVAStateStore:
    def set_state(self, path: str, value: Any):
        # Validate before setting
        if path == "physio.blood.cortisol":
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"Cortisol out of range: {value}")

        # Validate state transitions
        if path == "llm.phase":
            current_phase = self.state["llm"]["phase"]
            if current_phase == "phase_2" and value == "phase_1":
                raise StateTransitionError("Cannot go back to Phase 1")

        # Update state
        ...
```

**Benefit:** Centralized validation logic, catch bugs early

### 5. ✅ Observable State Changes

```python
# Subscribe to any state change for monitoring
def log_all_changes(path: str, value: Any):
    logger.info(f"State changed: {path} = {value}")

store.subscribe("*", log_all_changes)

# Subscribe to critical changes for alerts
def alert_high_cortisol(cortisol: float):
    if cortisol > 0.9:
        alert("⚠️ Cortisol critical: {cortisol}")

store.subscribe("physio.blood.cortisol", alert_high_cortisol)
```

### 6. ✅ Easier Testing

**Current:**
```python
# Must mock all components
mock_physio = MockPhysioController()
mock_matrix = MockEVAMatrix()
orch = EVAOrchestrator(physio=mock_physio, matrix=mock_matrix, ...)
```

**State Bus:**
```python
# Just pre-populate state
store = EVAStateStore()
store.set_state("physio.blood.cortisol", 0.85)  # Test high cortisol
store.set_state("eva_matrix.axes_9d.stress", 0.92)

orch = EVAOrchestrator(store)
response = orch.process_user_input("test")

# Verify state changes
assert store.get_state("qualia.tone") == "charged"
```

---

## Disadvantages of State Bus

### 1. ❌ Global Mutable State

**Problem:** Any component can modify any state

```python
# BAD: PhysioController accidentally overwrites EVA Matrix state
self.store.set_state("eva_matrix.axes_9d.stress", 0.5)  # Oops!
```

**Mitigation:**
- Access control: components can only write to their own namespace
- Immutable state (copy-on-write)

```python
class EVAStateStore:
    def set_state(self, path: str, value: Any, caller: str):
        # Validate caller can write to this path
        if not self._can_write(caller, path):
            raise PermissionError(f"{caller} cannot write to {path}")
```

### 2. ❌ Performance Overhead

**Concern:**
- Dict lookup: `store.get_state("physio.blood.cortisol")`
- Slower than direct attribute access: `self.blood.cortisol`

**Benchmark:**
```python
# Direct access
self.physio.blood["cortisol"]  # ~10 ns

# State bus access
store.get_state("physio.blood.cortisol")  # ~500 ns (50x slower)
```

**Mitigation:**
- Cache frequently accessed paths
- Use attribute proxy pattern

```python
class PhysioStateProxy:
    def __init__(self, store: EVAStateStore):
        self._store = store

    @property
    def cortisol(self) -> float:
        return self._store.get_state("physio.blood.cortisol")

# Usage
physio = PhysioStateProxy(store)
cortisol = physio.cortisol  # Looks like attribute access, uses store
```

### 3. ❌ Hidden Dependencies

**Problem:** Hard to see what state a component depends on

```python
class EVAMatrixSystem:
    def compute(self):
        # Where does it read from? Not obvious from signature
        physio = self.store.get_state("physio")  # Hidden dependency
        rim = self.store.get_state("resonance.ri")  # Another one
```

**Mitigation:** Document state dependencies

```python
class EVAMatrixSystem:
    """
    State Dependencies:
    - Reads: physio.*, resonance.ri
    - Writes: eva_matrix.*
    """
    READS = ["physio", "resonance.ri"]
    WRITES = ["eva_matrix"]
```

### 4. ❌ Memory Usage

**Concern:** Storing full state history for time-travel

```python
# After 1000 turns
store.history = [
    {...},  # Turn 1 snapshot (10 KB)
    {...},  # Turn 2 snapshot (10 KB)
    ...
    {...}   # Turn 1000 snapshot (10 KB)
]
# Total: 10 MB
```

**Mitigation:**
- Only store diffs, not full snapshots
- Compress old snapshots
- Limit history size (keep last 100 turns)

---

## Hybrid Approach: Selective State Bus

**Recommendation:** Don't put EVERYTHING in State Bus

### What SHOULD go in State Bus:

**✅ Physiological State (High Value)**
- Blood hormone levels
- ANS state (sympathetic/parasympathetic)
- Gland inventory
- Receptor activation

**Why:**
- Changes frequently
- Read by many components (EVA Matrix, Qualia, RMS, CIN)
- Critical for debugging ("what was cortisol when...")
- Benefits from time-travel

**✅ EVA Matrix State**
- 9D axes
- Safety reflex directives

**Why:**
- Central to EVA's psychology
- Read by Qualia, RMS, CIN
- Important to track over time

**✅ Qualia State**
- Phenomenological experience snapshot

**✅ Current Turn Context**
- LLM phase (phase_1 / phase_2)
- Function call args
- Retrieved memories
- Turn ID, timestamp

### What should STAY as direct references:

**❌ Memory (MSP)**
- Episodic memories are in JSONL files, not in-memory state
- Too large to keep in state bus
- Already has persistence layer

**❌ Configuration**
- Hormone specs, receptor configs
- Immutable during session
- Should be loaded once, not in dynamic state

**❌ LLM Bridge**
- API client state (session IDs, tokens)
- External system, not EVA's internal state

**❌ RAG Results**
- Too large (7 streams × N episodes)
- Already cached in MSP turn_cache

---

## Proposed Architecture: Hybrid State Bus

```python
class EVAStateStore:
    """
    Selective State Bus: Only critical, frequently-changing state
    """
    def __init__(self):
        self.state = {
            # ✅ In State Bus (dynamic, shared)
            "physio": {...},
            "eva_matrix": {...},
            "qualia": {...},
            "resonance": {
                "ri": {...},
                "rim": {...}
            },
            "turn": {
                "id": None,
                "phase": None,  # "phase_1" | "phase_2"
                "stimulus": None,
                "tags": []
            }
        }


class EVAOrchestrator:
    """
    Hybrid: State Bus for state, direct refs for services
    """
    def __init__(
        self,
        state_store: EVAStateStore,
        msp: MSPClient,  # Direct reference (not in state bus)
        rag: AgenticRAG,  # Direct reference
        llm_bridge: LLMBridge,  # Direct reference
        cin: ContextInjectionNode  # Direct reference
    ):
        self.store = state_store
        self.msp = msp
        self.rag = rag
        self.llm_bridge = llm_bridge
        self.cin = cin

        # Components that USE state bus
        self.physio = PhysioController(state_store)
        self.matrix = EVAMatrixSystem(state_store)
        self.qualia = ArtifactQualiaSystem(state_store)
        self.rms = RMSSystem(state_store, msp)


    def process_user_input(self, user_input: str):
        # Initialize turn state
        turn_id = self.msp.generate_turn_id()
        self.store.set_state("turn.id", turn_id)
        self.store.set_state("turn.phase", "phase_1")

        # Phase 1 (still using direct calls)
        ctx_p1 = self.cin.inject_phase_1(user_input)
        llm_p1 = self.llm_bridge.generate(ctx_p1)

        # Extract function call args → State Bus
        self.store.set_state("turn.stimulus", llm_p1.stimulus)
        self.store.set_state("turn.tags", llm_p1.tags)

        # The Gap - components read/write state bus
        self.store.set_state("turn.phase", "the_gap")

        self.physio.step()  # Reads turn.stimulus, writes physio.*
        self.matrix.compute()  # Reads physio.*, writes eva_matrix.*
        self.qualia.integrate()  # Reads eva_matrix.*, writes qualia.*

        # RAG still uses direct call (returns too much data for state bus)
        memories = self.rag.retrieve({
            "tags": self.store.get_state("turn.tags"),
            "physio": self.store.get_state("physio"),
        })

        # Phase 2 (read from state bus)
        self.store.set_state("turn.phase", "phase_2")

        ctx_p2 = self.cin.inject_phase_2(
            physio_state=self.store.get_state("physio"),
            eva_state=self.store.get_state("eva_matrix"),
            qualia_state=self.store.get_state("qualia"),
            memories=memories  # Not in state bus
        )

        llm_p2 = self.llm_bridge.continue_with_result(ctx_p2)

        # Persistence (read from state bus)
        self.rms.encode_memory()  # Reads from state bus
        self.msp.write_episode(...)

        # Save state snapshot
        self.msp.save_state_snapshot(
            turn_id=turn_id,
            state=self.store.get_full_state()
        )

        return llm_p2.response
```

---

## Implementation Plan

### Phase 1: Create State Store (2 days)

```python
# 1. Create EVAStateStore class
# 2. Define state schema
# 3. Add get/set methods
# 4. Add subscription mechanism
# 5. Add state validation
# 6. Add history tracking
```

### Phase 2: Migrate PhysioController (2 days)

```python
# Before
class PhysioController:
    def __init__(self, ...):
        self.blood = BloodEngine(...)
        self.ans = AutonomicEngine(...)

    def step(self, stimulus):
        self.blood.update(stimulus)
        self.ans.calculate(self.blood.get_state())
        return {
            "blood": self.blood.get_state(),
            "autonomic": self.ans.get_state()
        }

# After
class PhysioController:
    def __init__(self, state_store: EVAStateStore, ...):
        self.store = state_store
        self.blood = BloodEngine(...)
        self.ans = AutonomicEngine(...)

    def step(self):
        # Read stimulus from state bus
        stimulus = self.store.get_state("turn.stimulus")

        # Update
        blood_state = self.blood.update(stimulus)
        ans_state = self.ans.calculate(blood_state)

        # Write to state bus (no return value needed)
        self.store.set_state("physio.blood", blood_state)
        self.store.set_state("physio.autonomic", ans_state)
```

### Phase 3: Migrate EVA Matrix & Qualia (2 days)

### Phase 4: Update Orchestrator (1 day)

### Phase 5: Add State Persistence (1 day)

```python
# Save state every turn
def save_turn_state(self, turn_id: str):
    state_file = f"Consciousness/10_state/turn_{turn_id}.json"
    with open(state_file, 'w') as f:
        json.dump(self.store.get_full_state(), f, indent=2)

# Load state for debugging
def load_turn_state(self, turn_id: str):
    state_file = f"Consciousness/10_state/turn_{turn_id}.json"
    with open(state_file, 'r') as f:
        state = json.load(f)
    self.store.load_state(state)
```

### Phase 6: Testing & Validation (2 days)

**Total: ~10 days**

---

## Decision Matrix

| Aspect | Current | State Bus (Full) | State Bus (Hybrid) |
|--------|---------|------------------|-------------------|
| **Compatibility with Dual-Phase** | ✅ Perfect | ✅ Perfect | ✅ Perfect |
| **State Persistence** | ❌ Manual | ✅ Easy | ✅ Easy |
| **Time-Travel Debug** | ❌ Hard | ✅ Easy | ✅ Easy |
| **Cross-Component Access** | ⚠️ Manual passing | ✅ Direct access | ✅ Direct access |
| **Performance** | ✅ Fast | ⚠️ Slower | ✅ Good (selective) |
| **Memory Usage** | ✅ Low | ❌ High | ⚠️ Medium |
| **Testability** | ⚠️ Needs DI | ✅ Easy | ✅ Easy |
| **Code Complexity** | ✅ Simple | ⚠️ Medium | ⚠️ Medium |
| **Migration Cost** | - | ❌ High | ⚠️ Medium |
| **Type Safety** | ✅ Full | ❌ Lost | ⚠️ Partial |

---

## Recommendation

### ✅ **State Bus (Hybrid) is VALUABLE for EVA**

**Why it makes sense:**
1. **Physiological state is complex and shared** - perfect for centralized store
2. **State persistence is critical** - need to save/restore full body state
3. **Time-travel debugging** - invaluable for understanding EVA's responses
4. **Compatible with dual-phase** - doesn't break core architecture

**Why hybrid (not full):**
1. Keep MSP, RAG, LLM Bridge as direct references (they're services, not state)
2. Only put frequently-changing, shared state in bus
3. Better performance, lower memory usage

### Comparison to Previous Analysis

| Architecture | Event/Message Bus | State Bus (Hybrid) |
|--------------|-------------------|-------------------|
| **Verdict** | ❌ NOT Recommended | ✅ Recommended |
| **Reason** | Breaks dual-phase | Enhances dual-phase |
| **Migration** | Complete rewrite | Incremental |
| **Risk** | High | Medium |
| **Benefit** | Low | High |

---

## Final Answer

**State Bus เหมาะสมกับ EVA 8.1.0 ไหม?**

✅ **ใช่ - เหมาะสม** (แบบ Hybrid)

**ต่างจาก Message Bus ยังไง?**
- Message Bus = Event-driven (async) → ❌ ไม่เหมาะ
- State Bus = Centralized state (sync) → ✅ เหมาะสม

**ควรทำไหม?**
- ถ้าต้องการ state persistence + time-travel debugging → ✅ ทำเลย
- ถ้าแค่อยากให้ test ง่ายขึ้น → Dependency Injection ก็พอ
- ถ้ามีเวลา 10 วัน + เห็นคุณค่าของ debugging → ✅ Recommended

**Next Steps:**
1. สร้าง `EVAStateStore` prototype (1 day)
2. Migrate PhysioController เป็นตัวแรก (2 days)
3. ทดสอบ state save/load (1 day)
4. ถ้าได้ผล → migrate ส่วนอื่นต่อ

อยากให้ลองทำ prototype หรือยังคะ?
