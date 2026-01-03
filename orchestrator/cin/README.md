# CIN (Context Injection Node)
## Component ID: SYS-CIN-8.1
**Version: 8.1.0-R1** (Last Updated: 2026-01-03)

**Context Injection Node** is the "Cognitive Firewall" and orchestration brain of EVA. It ensures a strict separation between the LLM and the autonomous systems (Physio, Matrix, MSP), following the principle that "The mind cannot speak directly to the glands."

## 🛡️ The Cognitive Firewall (Strict Bottleneck)
To maintain architectural integrity, the system enforces the following:
1. **No Direct System Access**: The LLM *never* interacts with PhysioCore or EVAMatrix directly.
2. **Tool-Mediated Stimulus**: LLM triggers are channeled through `sync_biocognitive_state`, which is owned and validated by CIN.
3. **Stimulus Normalization**: CIN filters, scales, and validates all extracted triggers against `Input_Stimulus_Contract.yaml` before physical injection.

---

## �️ Working Style & Workflow Rules
เพื่อให้ระบบมีความสอดคล้อง (Consistency) สูงสุด การแก้ไขระบบ CIN จะต้องทำตามกฎ **"Strict Synchronization"** ดังนี้:

### 1. เมื่อมีการเพิ่ม/ลด Input (ข้อมูลขาเข้า)
หากต้องรับข้อมูลใหม่จาก MSP หรือ Physio:
- [ ] **Step 1**: แก้ไข Schema ใน [`validation/input/`](file:///e:/The%20Human%20Algorithm/T2/EVA%208.1.0/orchestrator/cin/validation/input/) (ต้องระบุ `additionalProperties: false`)
- [ ] **Step 2**: แก้ไขไฟล์สัญญาใน [`upstream_contract/`](file:///e:/The%20Human%20Algorithm/T2/EVA%208.1.0/orchestrator/cin/contract/upstream_contract/) ให้ตรงกับสคีม่า
- [ ] **Step 3**: อัปเดตไฟล์ [`configs/CIN_Input_Contract.yaml`](file:///e:/The%20Human%20Algorithm/T2/EVA%208.1.0/orchestrator/cin/configs/CIN_Input_Contract.yaml) ซึ่งเป็นสารบัญรวมของ Input

### 2. เมื่อมีการเพิ่ม/ลด Output (ข้อมูลขาออก)
หากต้องเปลี่ยนค่าที่ส่งให้ Orchestrator หรือส่งไปบันทึก MSP:
- [ ] **Step 1**: แก้ไข [`schema/CIN_Output_Schema.json`](file:///e:/The%20Human%20Algorithm/T2/EVA%208.1.0/orchestrator/cin/schema/CIN_Output_Schema.json)
- [ ] **Step 2**: อัปเดตไฟล์สัญญาใน [`downstream_contract/`](file:///e:/The%20Human%20Algorithm/T2/EVA%208.1.0/orchestrator/cin/contract/downstream_contract/)
- [ ] **Step 3**: อัปเดตไฟล์ [`configs/CIN_Output_Contract.yaml`](file:///e:/The%20Human%20Algorithm/T2/EVA%208.1.0/orchestrator/cin/configs/CIN_Output_Contract.yaml)

### 3. การอัปเดตระบบทะเบียนกลาง
- [ ] หากมีการเปลี่ยนเวอร์ชันหรือโครงสร้างสคีม่า ต้องไปอัปเดตที่ [`operation_system/core_systems.yaml`](file:///e:/The%20Human%20Algorithm/T2/EVA%208.1.0/Operation_System/core_systems.yaml) เสมอ

---

## 📅 Version History (Latest)

### [8.1.0-R1] - 2026-01-03
- **Dual-Phase Split**: แยกการประมวลผลเป็น Phase 1 (Perception/Intuition) และ Phase 2 (Reasoning/Deep Context)
- **Strict Input Validation**: ย้ายสคีม่าทั้งหมดเข้าโฟลเดอร์ `validation/input/` และเปิดใช้ `additionalProperties: false` ทั่วทั้งระบบ
- **Progressive Semantic Chunking**: รองรับการสกัด Stimulus แบบหลายจังหวะ (Multi-chunk) พร้อมระบบ `normalize_stimulus` เพื่อความปลอดภัย
- **Salience Anchor Extraction**: บังคับให้ LLM สกัดจุดเกาะเกี่ยวทางอารมณ์ (Salience Anchor) ในทุก Semantic Chunk
- **Physio & User Profile Integration**: Phase 1 สามารถเข้าถึงข้อมูลร่างกาย (Baseline/Current) และโปรไฟล์ผู้ใช้แบบ Least Privilege
- **3-Stage Context Buffer**: รองรับการสะสมข้อมูลเพื่อบันทึกลง `10_context_storage` (Stage 1+2+3)
- **Registry Alignment**: ลงทะเบียนสคีม่าและเวอร์ชันใน `core_systems.yaml` (v8.1.0-R3)

---

## 📁 Directory Structure
- **`configs/`**: Defines **system behavior** & **Master Registries** (SSOT).
  - `CIN_Interface.yaml`: Public API.
  - `CIN_Input_Contract.yaml`: Master Input Registry.
  - `CIN_Output_Contract.yaml`: Master Output Registry.
- **`contract/`**: Detailed Data Agreements.
  - **`upstream_contract/`**: Contracts with MSP and Physio.
  - **`downstream_contract/`**: Contracts with Orchestrator.
- **`validation/input/`**: JSON Schemas for strict upstream validation.
- **`schema/`**: Internal and Output Data Models.
- **`docs/`**: Conceptual documentation and Technical Requests.
- **`logic/`**: Core python implementation (`cin.py`).
