# EVA 8.1.0 - Production Roadmap
**Version**: 8.1.0
**Date**: 2026-01-02
**Current Status**: ~65% Complete (Core Components Ready)

---

## 🎯 Vision: Production-Ready Dual-Phase Orchestrator

**Goal**: Fully functional EVA 8.1.0 with Dual-Phase One-Inference pattern that can:
- Process user input through physiological simulation
- Retrieve affective memories via Hept-Stream RAG
- Generate embodied responses (40% Persona + 60% Physio-State)
- Persist memories to MSP with split storage

---

## ✅ What's Already Complete (65%)

### Core Infrastructure ✅
1. **CIN (Context Injection Node)** - `orchestrator/cin.py` (1110 lines)
   - ✅ Dual-phase context building
   - ✅ Token counting & budget enforcement
   - ✅ Auto-discovery (Persona, Soul, PMT)
   - ✅ Graceful degradation
   - ✅ Production-ready with tests

2. **HeptStreamRAG** - `services/hept_stream_rag.py`
   - ✅ 7-stream memory retrieval
   - ✅ Emotion Stream (physio-congruent)
   - ✅ Stream weighting (Emotion: 0.35)
   - ✅ Temporal decay support

3. **MSP Client v8.1.0** - `services/msp_client.py`
   - ✅ Episode split storage (user/llm)
   - ✅ Human-readable IDs (EVA_EP01)
   - ✅ Session memory naming
   - ✅ Compression counters
   - ✅ CIN integration methods (FIXED 2026-01-02):
     - `get_recent_turns(limit, timeout_ms)`
     - `get_recent_episodes(limit)`
     - `get_episode_counter()`
   - ✅ All tests passing

4. **EVA Matrix** - `eva_matrix/eva_matrix_engine.py`
   - ✅ 9D psychological state conversion
   - ✅ Safety Reflex directives

5. **Artifact Qualia** - `Artifact_Qualia/Artifact_Qualia.py`
   - ✅ Phenomenological experience (5D texture)

6. **RMS v6** - `Resonance_Memory_System/rms_v6.py`
   - ✅ Emotional texture encoding
   - ✅ Core color generation
   - ✅ Trauma detection

7. **PhysioController** - `physio_core/physio_controller.py`
   - ✅ Full physiological pipeline
   - ⚠️ Needs adapter for v8.1.0

### Supporting Systems ✅
- ✅ Identity Layer (Persona, Soul, PMT)
- ✅ Architecture Documentation
- ✅ Specifications (CIN, Dual-Phase, MSP)
- ✅ Test Coverage (~60%)

---

## ❌ What's Missing (Critical for Production - 35%)

### Priority 1: Core Integration (CRITICAL)

#### 1. **LLM Bridge** 🔴 **HIGHEST PRIORITY**
**File**: `services/llm_bridge.py`
**Status**: ❌ Not Implemented

**Requirements**:
- Gemini API integration (google.generativeai)
- Function calling support for `sync_biocognitive_state()`
- Bilingual response handling (Thai/English)
- Error handling & retries
- Token usage tracking

**Implementation Tasks**:
```python
class LLMBridge:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        # Initialize Gemini API

    def generate_with_function_calling(
        self,
        prompt: str,
        tools: List[Dict],
        max_tokens: int = 2000
    ) -> Dict:
        # Phase 1: LLM Perception
        # Wait for function call
        # Return function call args

    def continue_with_function_result(
        self,
        function_result: Dict
    ) -> Dict:
        # Phase 2: LLM Reasoning
        # Return final response + context summary
```

**Dependencies**: None (standalone)
**Estimated Complexity**: Medium
**Why Critical**: ระบบไม่สามารถทำงานได้เลยถ้าไม่มี LLM

---

#### 2. **Main Orchestrator** 🔴 **HIGHEST PRIORITY**
**File**: `orchestrator/main_orchestrator.py`
**Status**: ❌ Not Implemented (มี `orchestrator/dynamic_chunking_orchestrator.py` แต่ไม่ใช่ที่ต้องการ)

**Requirements**:
- Connect all components (CIN, PhysioController, HeptRAG, LLMBridge, MSP, RMS)
- Manage dual-phase flow
- Error handling & logging
- Context ID management
- Episode persistence

**Implementation Tasks**:
```python
class DualPhaseOrchestrator:
    def __init__(
        self,
        cin: ContextInjectionNode,
        physio_controller: PhysioController,
        hept_rag: HeptStreamRAG,
        llm_bridge: LLMBridge,
        msp_client: MSPClient,
        rms: ResonanceMemorySystem,
        eva_matrix: EVAMatrixEngine,
        artifact_qualia: ArtifactQualia
    ):
        # Initialize all components

    def process_turn(self, user_input: str) -> Dict:
        # Phase 1: Perception
        phase1_context = self.cin.inject_phase_1(user_input)
        phase1_prompt = self.cin.build_phase_1_prompt(phase1_context)

        # LLM Phase 1
        llm_response = self.llm_bridge.generate_with_function_calling(
            phase1_prompt,
            tools=[sync_biocognitive_state_tool]
        )

        # The Gap: Process stimulus
        stimulus_vector = llm_response['tool_calls'][0]['args']['stimulus_vector']
        tags = llm_response['tool_calls'][0]['args']['tags']

        updated_physio = self.physio_controller.step(stimulus_vector)
        memory_matches = self.hept_rag.retrieve(query_context)

        # Phase 2: Reasoning
        phase2_context = self.cin.inject_phase_2(
            stimulus_vector, tags, updated_physio, memory_matches
        )
        function_result = self.cin.build_phase_2_prompt(phase2_context)

        # LLM Phase 2
        final_response = self.llm_bridge.continue_with_function_result(
            function_result
        )

        # Persist to MSP
        self._persist_episode(final_response)

        return final_response
```

**Dependencies**: CIN ✅, LLMBridge ❌, PhysioController ⚠️, HeptRAG ✅, MSP ✅, RMS ✅
**Estimated Complexity**: High
**Why Critical**: หัวใจของระบบ - เชื่อมทุก component เข้าด้วยกัน

---

#### 3. **PhysioController Adapter** 🟡 **HIGH PRIORITY**
**File**: `physio_core/physio_adapter_v8.py`
**Status**: ⚠️ PhysioController มีแล้ว แต่ต้อง adapt

**Requirements**:
- Adapter/wrapper สำหรับ EVA 8.1.0
- `step(stimulus_vector)` method
- `get_snapshot()` method
- State serialization for CIN

**Implementation Tasks**:
```python
class PhysioAdapterV8:
    def __init__(self, physio_controller):
        self.controller = physio_controller

    def step(self, stimulus_vector: Dict[str, float]) -> Dict[str, Any]:
        # Apply stimulus to physiological system
        # Return updated state (hormones, ANS, etc.)

    def get_snapshot(self, timeout_ms: int = 50) -> Dict[str, Any]:
        # Quick snapshot for CIN Phase 1
        # Return: {blood, autonomic, heart_rate_index}
```

**Dependencies**: PhysioController ✅
**Estimated Complexity**: Low-Medium
**Why Critical**: CIN ต้องการ physio baseline และ updated state

---

### Priority 2: Integration Testing (IMPORTANT)

#### 4. **Integration Test Suite** 🟡 **HIGH PRIORITY**
**File**: `tests/test_integration_dual_phase.py`
**Status**: ❌ Not Implemented

**Requirements**:
- End-to-end test (User Input → Final Response)
- Mock Gemini API (หรือใช้จริงด้วย test API key)
- Verify context ID continuity
- Verify token budgets
- Verify memory persistence

**Test Scenarios**:
1. Simple greeting
2. Emotional input (stress)
3. Multi-turn conversation
4. Memory recall
5. Error handling (PhysioController down)

**Dependencies**: All core components
**Estimated Complexity**: Medium
**Why Important**: Ensure ระบบทำงานร่วมกันได้จริง

---

#### 5. **CLI Interface** 🟢 **MEDIUM PRIORITY**
**File**: `interfaces/eva_cli.py`
**Status**: ❌ Not Implemented

**Requirements**:
- Interactive chat interface
- Session management
- Rich console output (รองรับ Thai)
- Command support (/help, /clear, /status)

**Implementation Tasks**:
```python
class EVAChatCLI:
    def __init__(self, orchestrator: DualPhaseOrchestrator):
        self.orchestrator = orchestrator

    def run(self):
        # Interactive loop
        # Display responses with formatting
        # Handle commands
```

**Dependencies**: Main Orchestrator ❌
**Estimated Complexity**: Low
**Why Important**: User interface สำหรับ testing และ demo

---

### Priority 3: Configuration & Deployment (NICE TO HAVE)

#### 6. **Config System** 🟢 **MEDIUM PRIORITY**
**Files**: `config/default.yaml`, `config/prompts/*.txt`
**Status**: ⚠️ Partial (มีบางส่วนใน PMT)

**Requirements**:
- Centralized configuration
- Environment-specific configs (dev/prod)
- Prompt templates
- Semantic concepts definitions

**Why Important**: Easier to tune และ maintain

---

#### 7. **Logging System** 🟢 **LOW PRIORITY**
**File**: `utils/logger.py`
**Status**: ❌ Not Implemented (มีแค่ print statements)

**Requirements**:
- Structured logging (JSON)
- Log levels (DEBUG, INFO, WARN, ERROR)
- Log rotation
- Performance metrics

**Why Important**: Production monitoring และ debugging

---

#### 8. **Error Recovery** 🟢 **LOW PRIORITY**
**Status**: ⚠️ Partial (Graceful degradation มีแล้ว)

**Requirements**:
- Circuit breaker pattern
- Automatic retry with backoff
- Fallback responses
- Health checks

**Why Important**: Resilience ในการใช้งานจริง

---

## 📋 Implementation Plan (Step-by-Step)

### Phase A: Core Components (Required for Basic Functionality)

**Goal**: ระบบสามารถรับ input และ generate response ได้

#### Step A1: LLM Bridge Implementation
**Tasks**:
1. Setup Gemini API credentials
2. Implement `LLMBridge` class
3. Add function calling support
4. Test with simple prompts
5. Test with CIN Phase 1 prompts

**Acceptance Criteria**:
- ✅ Can call Gemini API
- ✅ Function calling works
- ✅ Returns valid `stimulus_vector` + `tags`
- ✅ Phase 2 continuation works
- ✅ Bilingual responses (Thai/English)

**Blockers**: None

---

#### Step A2: PhysioController Adapter
**Tasks**:
1. Review existing PhysioController API
2. Create `PhysioAdapterV8` wrapper
3. Implement `step(stimulus_vector)`
4. Implement `get_snapshot()`
5. Test with sample stimuli

**Acceptance Criteria**:
- ✅ `get_snapshot()` returns valid baseline
- ✅ `step()` updates physio state
- ✅ CIN can use adapter
- ✅ Timeout handling works

**Blockers**: None

---

#### Step A3: Main Orchestrator Implementation
**Tasks**:
1. Create `DualPhaseOrchestrator` class
2. Implement `process_turn()` method
3. Connect all components
4. Add error handling
5. Add logging

**Acceptance Criteria**:
- ✅ Full dual-phase flow works
- ✅ Context ID stays constant
- ✅ Memory persists to MSP
- ✅ Token budgets enforced
- ✅ Graceful degradation works

**Blockers**: LLMBridge ❌, PhysioAdapter ❌

---

### Phase B: Testing & Validation

#### Step B1: Integration Tests
**Tasks**:
1. Create test suite
2. Mock external dependencies
3. Test happy path
4. Test error scenarios
5. Test memory recall

**Acceptance Criteria**:
- ✅ All integration tests pass
- ✅ Coverage >80%
- ✅ No memory leaks
- ✅ Performance acceptable (<1s per turn)

**Blockers**: Main Orchestrator ❌

---

#### Step B2: Manual Testing
**Tasks**:
1. Create test scenarios document
2. Run manual test cases
3. Document bugs
4. Fix critical bugs
5. Retest

**Acceptance Criteria**:
- ✅ All test scenarios pass
- ✅ No critical bugs
- ✅ Response quality acceptable

**Blockers**: Main Orchestrator ❌

---

### Phase C: Polish & Deploy

#### Step C1: CLI Interface
**Tasks**:
1. Implement basic CLI
2. Add Rich formatting
3. Add session management
4. Test with real conversations

**Acceptance Criteria**:
- ✅ Interactive chat works
- ✅ Thai characters display correctly
- ✅ Commands work (/help, etc.)

**Blockers**: Main Orchestrator ❌

---

#### Step C2: Configuration & Logging
**Tasks**:
1. Create config files
2. Implement logging system
3. Add performance metrics
4. Document configuration options

**Acceptance Criteria**:
- ✅ Config loading works
- ✅ Logs are structured
- ✅ Performance tracked

**Blockers**: None

---

## 🎯 Minimum Viable Product (MVP)

**To reach MVP (usable system), you MUST complete**:

1. ✅ CIN (Done)
2. ❌ LLM Bridge (Critical)
3. ❌ PhysioController Adapter (Critical)
4. ❌ Main Orchestrator (Critical)
5. ✅ HeptStreamRAG (Done)
6. ✅ MSP Client (Done)
7. ✅ RMS (Done)
8. ❌ Basic Integration Tests (Important)

**MVP Status**: 4/8 Complete (50%)

---

## 📊 Component Dependency Graph

```
User Input
    ↓
Main Orchestrator (❌) ← CRITICAL BLOCKER
    ├─→ CIN (✅)
    ├─→ LLM Bridge (❌) ← CRITICAL BLOCKER
    ├─→ PhysioController Adapter (❌) ← CRITICAL BLOCKER
    │   └─→ PhysioController (✅)
    ├─→ HeptStreamRAG (✅)
    │   └─→ MSP Client (✅)
    ├─→ EVA Matrix (✅)
    ├─→ Artifact Qualia (✅)
    └─→ RMS (✅)
        └─→ MSP Client (✅)
```

**Critical Path**: LLM Bridge → PhysioAdapter → Main Orchestrator → Integration Tests

---

## 🚀 Recommended Next Steps (Priority Order)

### Immediate (This Week)
1. **Implement LLM Bridge** (services/llm_bridge.py)
   - Setup Gemini API
   - Implement function calling
   - Test with CIN prompts

2. **Create PhysioController Adapter** (physio_core/physio_adapter_v8.py)
   - Wrapper for existing PhysioController
   - `step()` and `get_snapshot()` methods

3. **Implement Main Orchestrator** (orchestrator/main_orchestrator.py)
   - Connect all components
   - Dual-phase flow

### Next (Following Week)
4. **Write Integration Tests** (tests/test_integration_dual_phase.py)
   - End-to-end testing
   - Error scenarios

5. **Build CLI Interface** (interfaces/eva_cli.py)
   - Interactive chat
   - Session management

### Later (Nice to Have)
6. Configuration system
7. Advanced logging
8. Performance optimization
9. MongoDB/Neo4j integration (optional)

---

## ⚠️ Known Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Gemini API rate limits | High | Medium | Implement rate limiting, backoff |
| PhysioController incompatibility | High | Low | Adapter pattern isolates changes |
| Memory retrieval performance | Medium | Medium | Index optimization, caching |
| Token budget violations | Medium | Low | Already enforced in CIN |
| Unicode issues (Thai) | Low | Low | Already handled with UTF-8 fix |

---

## 📈 Success Metrics

**System is Production-Ready when**:

1. ✅ **Functional**:
   - Can process user input end-to-end
   - Generates embodied responses
   - Persists memories correctly
   - Recalls memories accurately

2. ✅ **Performance**:
   - Phase 1: <200ms
   - Phase 2: <1000ms
   - Total latency: <1.5s per turn

3. ✅ **Quality**:
   - 80% integration test coverage
   - No critical bugs
   - Token budgets enforced
   - Graceful degradation works

4. ✅ **Operational**:
   - Logging in place
   - Config system working
   - CLI interface usable
   - Documentation complete

---

## 📚 Documentation Needed

- [ ] API documentation (LLM Bridge, Main Orchestrator)
- [ ] Integration guide
- [ ] Deployment guide
- [ ] Troubleshooting guide
- [x] Architecture diagrams (Done)
- [x] Specifications (Done)

---

## 🎓 Development Guidelines

### Code Quality Standards
- Type hints for all functions
- Docstrings (Google style)
- Error handling with graceful degradation
- Logging at appropriate levels
- Unit tests for new code (>70% coverage)

### Testing Strategy
- Unit tests: Individual components
- Integration tests: Component interactions
- End-to-end tests: Full flow
- Manual testing: Real conversation scenarios

### Performance Targets
- Phase 1: <200ms (target: <100ms)
- Phase 2: <1000ms (target: ~500ms)
- Memory queries: <800ms
- Total turn: <1.5s

---

## ✅ Definition of Done

**A component is "Done" when**:
1. ✅ Code implemented and tested
2. ✅ Unit tests passing (>70% coverage)
3. ✅ Integration tests passing
4. ✅ Documentation written
5. ✅ Code reviewed
6. ✅ No critical bugs

**The system is "Production Ready" when**:
1. ✅ MVP components complete (8/8)
2. ✅ Integration tests passing (>80% coverage)
3. ✅ Manual testing successful
4. ✅ Performance targets met
5. ✅ CLI working
6. ✅ Documentation complete
7. ✅ No known critical bugs

---

## 📞 Contact & Support

**Project**: EVA 8.1.0 (THA-01-S003)
**Location**: Thailand
**Development Model**: Claude Sonnet 4.5

**Key Files**:
- Architecture: `docs/ARCHITECTURE_FLOW_VALIDATED.md`
- CIN Spec: `specs/CIN_Context_InjectionNode_spec.yaml`
- Project Guide: `CLAUDE.md`

---

**Last Updated**: 2026-01-02
**Next Review**: After LLM Bridge implementation

---

## 🎯 Summary

**Current Progress**: 65% Complete
**MVP Progress**: 50% (4/8 critical components)
**Critical Blockers**: 3 (LLM Bridge, PhysioAdapter, Main Orchestrator)

**Estimated Work to MVP**:
- LLM Bridge: ~200-300 lines
- PhysioAdapter: ~100-150 lines
- Main Orchestrator: ~300-400 lines
- Integration Tests: ~200-300 lines
**Total**: ~800-1150 lines of code

**Focus Now**: Implement the 3 critical blockers in order (LLM Bridge → PhysioAdapter → Main Orchestrator)

**After that**: Integration testing → CLI → Production deployment

---

**ระบบพร้อม Production เมื่อ**: ทำครบ Phase A + Phase B (MVP + Testing)

---

## 📝 Changelog

### 2026-01-02: MSP Client Integration Fix
**Issue**: MSP Client was marked as "Done" but missing 3 critical methods that CIN depends on.
**Root Cause**: CIN implementation called methods that didn't exist in MSPClient:
- `get_recent_turns(limit, timeout_ms)` - Called at cin.py:794
- `get_recent_episodes(limit)` - Called at cin.py:879
- `get_episode_counter()` - Called at cin.py:1021

**Fix Applied**:
- Added `get_recent_turns()` method (wraps `get_recent_history()` with timeout parameter)
- Added `get_recent_episodes()` method (retrieves recent user episodes sorted by timestamp)
- Added `get_episode_counter()` method (returns copy of episode counter dict)

**Testing**: All 3 methods tested and verified working:
- `get_recent_turns()`: Returns list of turn summaries (filesystem fast, timeout ignored)
- `get_recent_episodes()`: Returns 4 episodes found, sorted by timestamp
- `get_episode_counter()`: Returns dict with persona_code='EVA', current_episode=3

**Impact**: MSP Client is now TRULY complete for CIN integration. No runtime errors will occur when CIN calls these methods.

**Status**: ✅ MSP Client 100% complete for production

---

**End of Roadmap**
