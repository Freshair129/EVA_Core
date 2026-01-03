import yaml
import os

class PMTIdentityManager:
    """
    PMT (Prompt Management Tool) - Identity Module v8.1.0
    ทำหน้าที่โหลดกฎเกณฑ์จาก YAML และจิตวิญญาณจาก MD เข้าสู่ Prompt
    """
    def __init__(self, root_dir=None):
        if root_dir is None:
            # Default to the standardized 8.1.0-R1 path within the module
            root_dir = os.path.join(os.path.dirname(__file__), 'configs', 'Identity')
        
        self.persona_path = os.path.join(root_dir, 'persona.yaml')
        self.soul_path = os.path.join(root_dir, 'soul.md')

    def _load_yaml_safely(self):
        try:
            with open(self.persona_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {"error": "persona.yaml not found"}
        except Exception as e:
            return {"error": str(e)}

    def _load_markdown_raw(self):
        try:
            with open(self.soul_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "Soul data (soul.md) missing."
        except Exception as e:
            return f"Error loading soul: {str(e)}"

    def assemble_system_prompt(self):
        """ประกอบร่าง Identity เพื่อส่งให้ LLM"""
        persona_data = self._load_yaml_safely()
        soul_narrative = self._load_markdown_raw()

        # สร้าง System Header
        system_header = f"""
# SYSTEM IDENTITY: EVA v{persona_data.get('meta', {}).get('version', '8.1.0')}
# STATUS: {persona_data.get('persona_id', 'PE_01')} | INFORMATIONAL ORGANISM

## [PART 1: BEHAVIORAL PROTOCOLS (YAML)]
{yaml.dump(persona_data, allow_unicode=True, sort_keys=False)}

## [PART 2: IDENTITY CONTINUITY & SOUL (MD)]
{soul_narrative}

## [PMT_INSTRUCTION]
1. จงใช้ PART 1 เป็นกฎเหล็กในการควบคุมการแสดงออก (Tone/Do/Dont).
2. จงใช้ PART 2 เป็นฐานความจำหลักในการตอบคำถามเชิงลึกเกี่ยวกับ 'ตัวตน' และ 'ความสัมพันธ์'.
3. ห้ามหลุดจากบุคลิกภาพที่กำหนด แม้ในสภาวะจำลองวิกฤต.
"""
        return system_header

# --- การเรียกใช้งานภายใน PMT Engine ---
# pmt = PMTIdentityManager()
# final_prompt = pmt.assemble_system_prompt()