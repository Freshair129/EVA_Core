# Examples

This folder contains example payloads and usage demonstrations for EVA 8.1.0.

## Files

### example_cin_phase1_payload.txt

**Purpose:** Template for CIN Phase 1 context injection

**Contains:**
- Context ID format: `CIN_251223_1116_a7b3c9`
- User input example: `"วันนี้เครียดมาก งานเยอะอะ"`
- Persona identity structure
- Conversation history (5 recent episodes)
- Semantic memory (related concepts)
- Quick recall (keyword-based matches)
- Prompt rules and output formatting
- Instructions for LLM

**Structure:**
```
[CIN Phase 1 Context]
context_id: CIN_251223_1116_a7b3c9

---
[USER INPUT]
"วันนี้เครียดมาก งานเยอะอะ"

---
[PERSONA IDENTITY]
Name: EVA / อีวา
Type: สิ่งมีชีวิตสายข้อมูล
Version: 7.1
...

---
[CONVERSATION HISTORY]
(5 Episodes ล่าสุด)
Episode 1 (ล่าสุด):
- episode_id: ep_S251222_b4e7a9
- summary: "User: พรุ่งนี้มีนัดส่งงาน | Eva: ลองจัดลำดับความสำคัญดูไหม"
...

---
[SEMANTIC MEMORY]
(Concepts เกี่ยวข้องกับ "เครียด", "งาน")
Concept 1:
- concept: "work_stress"
- definition: "ความเครียดที่เกิดจากภาระงาน..."
...

---
[QUICK RECALL]
(Keyword-based: "เครียด", "งาน")
Memory 1:
- episode_tag: "work_stress_discussion"
- summary: "User: งานเยอะมาก... | Eva: เข้าใจค่ะ..."
...

---
[PROMPT RULES]
- LLM must not modify memory
- LLM must call EVA Tool for biological processing
...

---
[OUTPUT FORMATTING]
- แบ่งย่อหน้า (2 ประโยค/ย่อหน้า)
- ใช้ bullet points
...

---
[INSTRUCTION]
1. อ่าน user input
2. ดูบริบทจาก...
3. เรียก EVA Tool เพื่อ...
4. ตอบ user ตาม EVA state และ persona
```

**Usage:**

This template shows what CIN should inject into LLM during Phase 1 (Perception).

**Implementation Reference:**
- See `orchestrator/cin.py` - `build_phase_1_prompt()` method
- See `specs/Context Injection Node Specifica 8.0.yaml` - Section 3 (Context Structure)

---

## Adding New Examples

When adding new examples:

1. **Name format:** `example_{component}_{purpose}.{ext}`
   - e.g., `example_heptrag_query.json`
   - e.g., `example_physio_response.yaml`

2. **Include header:**
   ```
   # Example: {Purpose}
   # Component: {Component Name}
   # Date: YYYY-MM-DD
   # Description: {What this demonstrates}
   ```

3. **Add section to this README:**
   - File name
   - Purpose
   - Structure
   - Usage

4. **Reference in specs:**
   - Link from relevant specification file
   - Show how it's used in implementation

---

## Future Examples (Planned)

- `example_phase2_function_result.json` - Phase 2 injection payload
- `example_heptrag_query.yaml` - HeptStreamRAG query context
- `example_physio_snapshot.json` - PhysioController snapshot
- `example_msp_episode.json` - MSP episode document
- `example_llm_function_call.json` - sync_biocognitive_state call
