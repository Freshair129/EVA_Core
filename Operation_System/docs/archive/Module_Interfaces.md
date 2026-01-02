# EVA 8.1.0 Module Interfaces Specification 🧩

เอกสารฉบับนี้สรุป Interface (Methods, Parameters, และ Return types) ของโมดูลหลักในระบบ EVA 8.1.0 เพื่อใช้เป็นมาตรฐานในการพัฒนาและการเชื่อมต่อระหว่างโมดูล (Cross-module Integration)

---

## 1. Cognitive Layer (การรับรู้และความคิด)

### 🧠 EVAOrchestrator
*Main controller for the Dual-Phase One-Inference pipeline.*

- **`process_user_input(user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]`**
  - ประมวลผล Input ตั้งแต่ต้นจนจบ (Perception -> The Gap -> Reasoning)
  - **Return:** รวมผลลัพธ์สุดท้าย (`final_response`, `final_state`, `episode_id`)

- **`_meta_evaluation(user_input: str, response: str, stimulus_vector: Dict, physio_state: Dict) -> Dict`**
  - ตรวจสอบความสอดคล้อง (Persona-Physio balance) ก่อนส่งคำตอบ

- **`_write_to_memory(...) -> str`**
  - บันทึก Episode ลง MSP ตาม Schema V2

---

### ⚡ DynamicChunkingOrchestrator
*Implements sequential 'Micro-Reactions' and retroactive synthesis.*

- **`split_into_chunks(text: str) -> List[str]`**
  - ตัดประโยคตาม Semantic Boundary (punctuation/regex)

- **`process_interaction(user_input: str, context: Dict[str, Any]) -> Dict`**
  - วนลูปประมวลผลแต่ละ Chunk เพื่อหา RIM Impact สะสม

- **`_process_micro_reaction(chunk: str, context: Dict[str, Any]) -> Dict`**
  - วิเคราะห์ RIM/RI ของแต่ละส่วนผ่าน CIN Phase 1

---

### 📡 ContextInjectionNode (CIN)
*Embodied Context Builder & State Manager.*

- **`inject_phase_1(user_input: str) -> Dict`**
  - เตรียมบริบทเบื้องต้น (Persona, Rough History, Physio Baseline)

- **`inject_phase_2(stimulus_vector, tags, updated_physio, memory_matches) -> Dict`**
  - เตรียมบริบทเชิงลึก (Embodied Sensation, Affective Memories)

- **`build_phase_1_prompt(context: Dict) -> str`**
- **`build_phase_2_prompt(context: Dict) -> str`**
  - แปลงบริบทเป็น Prompt String สำหรับ LLM

---

## 2. Physiological Layer (ระบบร่างกาย)

### 💓 PhysioController
*Full physiological pipeline controller (Endocrine -> Autonomic).*

- **`step(eva_stimuli: Dict[str, float], zeitgebers: Dict[str, float], dt: float) -> Dict[str, Any]`**
  - คำนวณการเปลี่ยนแปลงของร่างกายใน 1 Tick (HPA -> Blood -> Receptor -> Reflex -> ANS)
  - **Return:** Snapshot ของเลือด (Blood), เซนเซอร์ (Receptor), และระบบประสาท (ANS)

---

## 3. Memory Layer (หน่วยความจำ)

### 📁 MSPClient
*Memory Service Protocol with Authority over persistence.*

- **`write_episode(episode_data: Dict[str, Any]) -> str`**
  - บันทึก Triple-write (User snapshot, LLM full state, JSONL index)

- **`write_session_memory(session_data: Dict[str, Any]) -> str`**
  - บันทึกความจำระดับ Core/Sphere (Compression Snapshot)

- **`query_by_physio_state(physio_query: Dict, threshold: float = 0.7) -> List`**
  - ค้นหาความจำที่ "รู้สึกเหมือนกัน" (Affective Matching)

---

### 🔍 HeptStreamRAG
*7-Dimensional Affective Memory Retrieval.*

- **`retrieve(query_context: Dict[str, Any], enabled_streams: List[str] = None) -> List[MemoryMatch]`**
  - ดึงความทรงจำจาก 7 สาย (Narrative, Salience, Sensory, Intuition, Emotion, Temporal, Reflection)
  - **Return:** รายการ Memory Match ที่ผ่านการทำ Exponential Temporal Decay แล้ว

---

## 4. LLM & Governance Layer (การควบคุมและเชื่อมต่อ LLM)

### 🌉 LLMBridge
*Real Gemini API Bridge with Function Calling support.*

- **`generate(prompt: str, tools: List[Dict] = None) -> LLMResponse`**
  - ส่ง Prompt ให้ Gemini และจัดการการเรียก Function (sync_biocognitive_state)

- **`continue_with_result(function_result: str) -> LLMResponse`**
  - สานต่อการประมวลผล LLM ทันทีหลังจากได้รับข้อมูลจากร่างกาย (Phase 2)

---

## 5. Psychological & Resonance Layer (สภาวะจิตใจและความสอดคล้อง)

### 💠 EVAMatrixSystem
*Psyche Core System: Owns continuous emotional state (axes_9d).*

- **`process_signals(signals: Dict[str, float]) -> Dict[str, Any]`**
  - ประมวลผลสัญญาณประสาท (Neural Signals) และอัปเดตสภาวะจิตใจ 9 มิติ
  - **Return:** สภาวะ 9D ปัจจุบัน (`axes_9d`) และป้ายกำกับอารมณ์ (`emotion_label`)

- **`get_full_state() -> Dict[str, Any]`**
  - ดึงสถานะจิตใจทั้งหมด (Axes, Momentum, Label) เพื่อการส่งต่อหรือบันทึก

---

### ✨ ArtifactQualiaCore
*Phenomenological Experience Integrator (The "Felt" Experience).*

- **`integrate(eva_state: Dict, rim_semantic: RIMSemantic) -> QualiaSnapshot`**
  - รวมสภาวะจาก Matrix และผลกระทบเชิงความหมาย (RIM) เป็นประสบการณ์ที่ "รู้สึก" ได้
  - **Return:** Snapshot ของประสบการณ์ (Intensity, Tone, Coherence, Texture)

---

### 🧬 RMSEngineV6 (Resonance Memory System)
*Experiential Memory Encoding & Trauma Protection.*

- **`process(eva_matrix, rim_output, reflex_state, ri_total) -> Dict[str, Any]`**
  - แปลงสภาวะภายในเป็นสัญญาณที่พร้อมบันทึกเป็นความทรงจำ (Memory-ready snapshot)
  - จัดการส่วนของ **Trauma Protection** (ลดความเข้มของสีและแสงลงหากตรวจพบภัยคุกคาม)
  - **Return:** ข้อมูลสำหรับ `state_snapshot` ใน Episodic Memory (รวมถึง `memory_color` และ `memory_encoding_level`)
