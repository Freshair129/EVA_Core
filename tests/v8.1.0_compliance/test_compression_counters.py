"""
Test Compression Counters
Verify that compression counters increment correctly
"""

import sys
import codecs
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Fix Windows console UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
msp_path = Path(__file__).parent.parent.parent / "Memory_&_Soul_Passaport"
sys.path.insert(0, str(msp_path / "MSP_Client"))
from msp_client import MSPClient

print("="*60)
print("Compression Counter Test")
print("="*60)

# Initialize MSP Client
msp = MSPClient()

print(f"\nInitial counters: {msp.compression_counters}")

# Write 10 test episodes
print("\n📝 Writing 10 test episodes...\n")

for i in range(1, 11):
    episode_data = {
        "episode_type": "interaction",
        "session_id": "test_session",
        "event_label": f"test_{i}",
        "episode_tag": "routine",
        "situation_context": {
            "context_id": f"ctx_test_{i}",
            "interaction_mode": "casual",
            "stakes_level": "low",
            "time_pressure": "low"
        },
        "turn_1": {
            "speaker": "user",
            "raw_text": f"Test message {i}",
            "summary": f"Test {i}",
            "affective_inference": {
                "emotion_signal": "neutral",
                "intensity": 0.5,
                "confidence": 0.8
            },
            "semantic_frames": ["test"],
            "salience_anchor": {
                "phrase": f"Test {i}",
                "Resonance_impact": 0.3
            }
        },
        "turn_2": {
            "speaker": "eva",
            "text_excerpt": f"Response {i}",
            "summary": f"Response {i}",
            "epistemic_mode": "assert"
        },
        "state_snapshot": {
            "EVA_matrix": {
                "stress_load": 0.3,
                "social_warmth": 0.5,
                "drive_level": 0.4,
                "cognitive_clarity": 0.7,
                "joy_level": 0.6,
                "emotion_label": "neutral"
            },
            "Endocrine": {
                "ESC_H01_ADRENALINE": 0.3,
                "ESC_H02_CORTISOL": 0.3,
                "ESC_H09_OXYTOCIN": 0.5,
            },
            "Resonance_index": 0.5,
            "memory_encoding_level": "L2_standard",
            "memory_color": "#808080",
            "qualia": {
                "intensity": 0.5
            },
            "reflex": {
                "threat_level": 0.3
            }
        }
    }

    episode_id = msp.write_episode(episode_data)

# Final counters
print(f"\n{'='*60}")
print("Final Counters")
print(f"{'='*60}")

counters_file = Path("consciousness/09_state/compression_counters.json")
with open(counters_file, 'r', encoding='utf-8') as f:
    final_counters = json.load(f)

print(f"Session_seq: {final_counters['Session_seq']}/8")
print(f"Core_seq: {final_counters['Core_seq']}/8")
print(f"Sphere_seq: {final_counters['Sphere_seq']}")

# Expected values after 10 episodes:
# Session_seq = 2 (0→1→2→3→4→5→6→7→reset to 0→1→2)
# Core_seq = 1 (after 8th episode, incremented)
# Sphere_seq = 0 (not enough cores yet)

print(f"\n{'='*60}")
print("Validation")
print(f"{'='*60}")

expected_session = 2
expected_core = 1
expected_sphere = 0

checks = {
    f"Session_seq == {expected_session}": final_counters['Session_seq'] == expected_session,
    f"Core_seq == {expected_core}": final_counters['Core_seq'] == expected_core,
    f"Sphere_seq == {expected_sphere}": final_counters['Sphere_seq'] == expected_sphere,
}

all_passed = True
for check, passed in checks.items():
    status = "✅" if passed else "❌"
    print(f"{status} {check}")
    if not passed:
        all_passed = False

# Check compression_meta in last episode
print(f"\n{'='*60}")
print("Check compression_meta in episodes")
print(f"{'='*60}")

# Read last episode
episodes = sorted(Path("consciousness/01_Episodic_memory/episodes").glob("ep_*.json"))
if episodes:
    with open(episodes[-1], 'r', encoding='utf-8') as f:
        last_ep = json.load(f)

    print(f"Last episode: {last_ep['episode_id']}")
    if "compression_meta" in last_ep:
        print(f"✅ compression_meta exists:")
        print(f"   - session_seq: {last_ep['compression_meta']['session_seq']}")
        print(f"   - core_seq: {last_ep['compression_meta']['core_seq']}")
        print(f"   - sphere_seq: {last_ep['compression_meta']['sphere_seq']}")
    else:
        print(f"❌ compression_meta NOT found!")
        all_passed = False

print(f"\n{'='*60}")
if all_passed:
    print("✅ ALL TESTS PASSED!")
else:
    print("❌ SOME TESTS FAILED")
print(f"{'='*60}")
