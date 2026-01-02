# Documentation

This folder contains all documentation for EVA 8.1.0.

## Architecture & Design

- **ARCHITECTURE_FLOW_VALIDATED.md** - Complete validated architecture flow with examples (450 lines)
  - Detailed flow diagram from user input to MSP archiving
  - Key insights about two-level retrieval
  - Critical clarifications (1 LLM inference, not 2)
  - Validation checklist

- **CLAUDE.md** - Guide for Claude Code when working in this repository
  - Testing commands
  - Architecture overview
  - Core components description
  - Design principles
  - Common pitfalls

- **Dual-Phase one infer Orchestrator.md** - Thai explanation of the one-inference pattern
  - การทำงานแบบ One-Inference ผ่าน Function Calling
  - อธิบายทั้ง 5 phase รวมถึง "The Gap"

## Implementation Status

- **IMPLEMENTATION_SUMMARY.md** - Comprehensive implementation status (~60% complete)
  - What's implemented (CIN, HeptStreamRAG)
  - What's missing (LLM Bridge, Main Orchestrator, MSP Client)
  - Test results
  - Next steps

- **MISSING_COMPONENTS.md** - Gap analysis for EVA 8.1.0 structure
  - Critical missing components
  - Priority recommendations

## Change Logs

- **SPEC_CORRECTIONS.md** - Specification corrections (2025-12-31)
  - Fixed Penta→Hept stream mismatch
  - Added memory_cache storage
  - Standardized context_id format
  - Added response weighting rule

- **SPEC_UPDATE_2025-12-31.md** - Latest specification updates
  - Performance targets added
  - Fallback behaviors defined
  - Implementation guidance
  - Integration examples

## Reading Order (Recommended)

For new developers:
1. **CLAUDE.md** - Start here for overview
2. **ARCHITECTURE_FLOW_VALIDATED.md** - Understand the flow
3. **IMPLEMENTATION_SUMMARY.md** - See what's done/pending
4. **SPEC_UPDATE_2025-12-31.md** - Latest changes

For implementers:
1. **CLAUDE.md** - Architecture & patterns
2. **Specifications** (in ../specs/) - Implementation details
3. **IMPLEMENTATION_SUMMARY.md** - Current status
