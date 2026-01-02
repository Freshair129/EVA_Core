# EVA 8.1.0 - Test History Ledger 📜

This ledger tracks the evolution of verification tests for the EVA 8.1.0 project, ensuring that fix history and architectural changes remain documented.

---

## 📂 Phase: v8.1.0 Compliance & Restructuring
**Date**: 2026-01-02  
**Location**: `tests/v8.1.0_compliance/`

| Test File | Purpose | Key Verification |
|-----------|---------|------------------|
| `test_cin_msp_integration.py` | Integration | Verifies the communication chain between CIN and MSP module. |
| `test_msp_methods.py` | Unit | Verifies new retrieval methods in `MSPClient` (`get_recent_turns`, etc.). |
| `test_session_memory_naming.py` | Compliance | Ensures session filenames follow the `THA-XX-SXXX` standard. |
| `test_episode_id_format.py` | Compliance | Validates the `{Persona}_EPXX` human-readable naming convention. |
| `test_split_episodes.py` | Logic | Verifies the separation of User and LLM data storage. |
| `test_compression_counters.py` | Logic | Ensures `Session_seq` and `Core_seq` counters iterate correctly. |
| `test_schema_v2.py` | Schema | Validates memory entries against the new JSON Schema V2. |

---

## 📂 Phase: Legacy / Core
**Date**: Pre-2026  
**Location**: `tests/`

| Test File | Purpose |
|-----------|---------|
| `test_write_session_memory.py` | Basic | Original verification for session memory writes. |

---

## 🚀 How to Run Tests
From the project root:
```powershell
# Run compliance tests
python tests/v8.1.0_compliance/test_msp_methods.py
```

> [!NOTE]
> All tests in the `v8.1.0_compliance` directory are configured to resolve paths relative to the project root (SSOT Anchor).
