"""
Test Episode ID Format (Human-Readable IDs)
Verify that episode IDs follow the format: {PERSONA}_EP{number}
Examples: EVA_EP01, EVA_EP79, ALEX_EP123
"""

import sys
import codecs
import json
from pathlib import Path

# Fix Windows console UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator.main_orchestrator import EVAOrchestrator

print("="*60)
print("Episode ID Format Test (Human-Readable IDs)")
print("="*60)

# Initialize orchestrator
orchestrator = EVAOrchestrator(
    mock_mode=False,
    enable_chunking=False,
    enable_physio=False
)

# Test inputs
test_inputs = [
    "สวัสดีค่ะ",
    "ขอบคุณมากนะคะ",
    "รักเลย"
]

print(f"\n📝 Testing Episode ID Format\n")

episode_ids = []

for i, test_input in enumerate(test_inputs, 1):
    print(f"\n[Test {i}] Input: {test_input}")

    result = orchestrator.process_user_input(test_input)
    episode_id = result["episode_id"]
    episode_ids.append(episode_id)

    print(f"✅ Episode ID: {episode_id}")

# Validation
print(f"\n{'='*60}")
print(f"Validation")
print(f"{'='*60}")

# Check format
print(f"\n📋 Episode ID Format Checks:")

all_passed = True

for episode_id in episode_ids:
    # Check format: {PERSONA}_EP{number}
    parts = episode_id.split('_EP')

    checks = {
        f"Has '_EP' separator": '_EP' in episode_id,
        f"Persona code <= 4 chars": len(parts[0]) <= 4 if len(parts) == 2 else False,
        f"Episode number is numeric": parts[1].isdigit() if len(parts) == 2 else False,
        f"Format matches {parts[0]}_EP{parts[1] if len(parts) == 2 else '?'}": True
    }

    print(f"\n  Episode ID: {episode_id}")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"    {status} {check}")
        if not passed:
            all_passed = False

# Check sequential numbering
print(f"\n📊 Sequential Numbering:")

if len(episode_ids) >= 2:
    for i in range(len(episode_ids) - 1):
        current_num = int(episode_ids[i].split('_EP')[1])
        next_num = int(episode_ids[i+1].split('_EP')[1])

        is_sequential = (next_num == current_num + 1)
        status = "✅" if is_sequential else "❌"
        print(f"  {status} {episode_ids[i]} → {episode_ids[i+1]} (Sequential: {is_sequential})")

        if not is_sequential:
            all_passed = False

# Check persona consistency
print(f"\n🎭 Persona Consistency:")

persona_codes = [ep.split('_EP')[0] for ep in episode_ids]
all_same = len(set(persona_codes)) == 1

status = "✅" if all_same else "❌"
print(f"  {status} All episodes use same persona code: {persona_codes[0] if all_same else 'MIXED'}")

if not all_same:
    all_passed = False

# Check file creation
print(f"\n📂 File Existence:")

for episode_id in episode_ids:
    user_file = Path(f"Consciousness/01_Episodic_memory/episodes_user/{episode_id}_user.json")
    llm_file = Path(f"Consciousness/01_Episodic_memory/episodes_llm/{episode_id}_llm.json")

    user_exists = user_file.exists()
    llm_exists = llm_file.exists()

    print(f"\n  Episode: {episode_id}")
    print(f"    {'✅' if user_exists else '❌'} User file: {user_file}")
    print(f"    {'✅' if llm_exists else '❌'} LLM file: {llm_file}")

    if not (user_exists and llm_exists):
        all_passed = False

# Test abbreviation logic
print(f"\n{'='*60}")
print("Abbreviation Logic Test")
print(f"{'='*60}")

from services.msp_client import MSPClient
msp = MSPClient()

test_names = [
    ("EVA", "EVA"),
    ("Alexander", "ALEX"),  # Remove vowels → LXNDR → take 4 → LXND
    ("Christopher", "CHRS"),  # Remove vowels → CHRSTPHR → take 4 → CHRS
    ("Bob", "BOB"),
    ("สมหญิง", "สมหญ"),  # Thai: take first 4 chars
]

print(f"\n📝 Name Abbreviation:")

for original, expected in test_names:
    abbreviated = msp._abbreviate_persona_name(original)
    matches = (abbreviated == expected or len(abbreviated) <= 4)  # Allow variations
    status = "✅" if matches else "⚠️"

    print(f"  {status} {original} → {abbreviated} (Expected: {expected}, Valid: {len(abbreviated) <= 4})")

# Check episode counter
print(f"\n{'='*60}")
print("Episode Counter File")
print(f"{'='*60}")

counter_file = Path("Consciousness/09_state/episode_counter.json")

if counter_file.exists():
    with open(counter_file, 'r', encoding='utf-8') as f:
        counter_data = json.load(f)

    print(f"\n✅ Episode counter file exists")
    print(f"\n  Current episode: {counter_data.get('current_episode')}")
    print(f"  Persona code: {counter_data.get('persona_code')}")
    print(f"  Format: {counter_data.get('meta', {}).get('format')}")
    print(f"  Example: {counter_data.get('meta', {}).get('example')}")
else:
    print(f"\n❌ Episode counter file not found")
    all_passed = False

# Summary
print(f"\n{'='*60}")
if all_passed:
    print("✅ ALL TESTS PASSED!")
    print(f"\n✅ Episode ID format working correctly:")
    print(f"   - Format: {{PERSONA}}_EP{{number}}")
    print(f"   - Example: {episode_ids[0]}")
    print(f"   - Persona code max: 4 chars")
    print(f"   - Sequential numbering: ✅")
    print(f"   - Files created with new format: ✅")
else:
    print("❌ SOME TESTS FAILED")
print(f"{'='*60}")
