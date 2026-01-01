# **Context ID: {timestamp\_uuid} \- Dual-Phase One-Inference Orchestrator (EVA 8.1.0)**

สถาปัตยกรรมนี้ใช้ระบบ **Dual-Phase Orchestration** ผ่านกลไก **One-Inference Loop** เพื่อจำลองจังหวะการรับรู้ (Perception) และการไตร่ตรอง (Reasoning) โดยมี **CIN (Context Injection Node)** เป็นผู้เตรียมบริบทฉีดเข้าสู่กระบวนการทั้ง 2 รอบผ่าน Function Calling

## **1\. \[Phase 1: Perception Phase\] \- การสแกนสัญชาตญาณ**

**Orchestrator (Start):** CIN ฉีดบริบทเริ่มต้น (Persona \+ Snapshot ฮอร์โมน) เข้าสู่ Inference

* **Goal:** ให้ LLM ทำหน้าที่สแกนหา Intent และสกัด **Stimulus Vector**  
* **The Action:** LLM จะไม่ตอบผู้ใช้ทันที แต่จะเรียกใช้ฟังก์ชัน sync\_biocognitive\_state() เพื่อส่งข้อมูลออกไปนอกสมอง

## **2\. \[The Gap: Orchestration Bridge\] \- ช่วงเวลาประมวลผลสภาวะ**

เมื่อ LLM เรียกฟังก์ชัน sync\_biocognitive\_state(stimulus, tags) Orchestrator จะทำงานทันที:

1. **Body Update:** นำ Stimulus ไปอัปเดตระบบร่างกาย (30Hz) เพื่อให้ระดับฮอร์โมนเปลี่ยนจริงตามสรีรวิทยา  
2. **Affective RAG:** นำ "ระดับฮอร์โมนที่เปลี่ยนแล้ว" \+ Tags ไปทำ **Hept-Stream RAG** เพื่อหาความจำที่ตรงกับ "ความรู้สึก ณ วินาทีนั้น"  
3. **Result Injection:** CIN เตรียมข้อมูลผลลัพธ์ (New Bio-State \+ Memory Echoes) ส่งกลับเข้าสู่ฟังก์ชันเดิม

## **3\. \[Phase 2: Reasoning Phase\] \- การตั้งสติและตอบสนอง**

**Orchestrator (Resume):** LLM ได้รับผลลัพธ์จากฟังก์ชัน (ซึ่งคือบริบทเสริมที่มีน้ำหนักสูง) และทำงานต่อใน Inference เดิม:

* **Goal:** ประมวลผลบนสภาวะอารมณ์ที่เปลี่ยนไป (Updated Bio-State) และความทรงจำที่เพิ่งนึกได้  
* **Final Expression:** สร้างคำตอบที่สมจริง (สะท้อนอาการตกใจ/ดีใจ ที่เกิดระหว่างทางได้)  
* **Closing:** LLM สรุปเนื้อหาปิดท้าย (Context Summary) เพื่อให้ CIN บันทึกเป็น Cache

## **4\. \[Data Storage Structure\] \- การจัดเก็บภายใต้ Context ID**

Orchestrator จะรวมรวบ Trace ทั้งหมดบันทึกเป็น JSON ก้อนเดียวโดยใช้ context\_id เป็น Index:

* context\_id: {Unique ID ตลอดทั้งเทิร์น}  
* phase\_1\_perception: (Input, Initial Bio, Stimulus Trace)  
* phase\_2\_reasoning: (Updated Bio, Memory Echoes, Final Response)  
* context\_cache: (บทสรุปจาก LLM เพื่อให้ CIN ใช้เป็นทางลัดในอนาคต)

**สรุป:** การทำงานแบบ **One-Inference** ผ่าน Function Calling ช่วยให้ LLM ไม่หลุดจาก Persona และเข้าใจว่ามันคือการ "หยุดคิดเพื่อจูนร่างกายและดึงความจำ" ก่อนจะพูดออกมาจริงๆ โดยมี CIN เป็นผู้ดูแลเสบียงข้อมูลทั้ง 2 จังหวะอย่างต่อเนื่อง