"""
Test Schema V2 Compliance
Quick test to verify Schema V2 format is being written correctly
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
print("Schema V2 Compliance Test")
print("="*60)

# Initialize orchestrator
orchestrator = EVAOrchestrator(
    mock_mode=False,
    enable_chunking=False,  # Disable chunking for simpler test
    enable_physio=False
)

# Simple test input
test_input = "ขอบคุณนะคะ"

print(f"\n📥 Input: {test_input}\n")

# Process
result = orchestrator.process_user_input(test_input)

# Get the episode ID
episode_id = result["episode_id"]

print(f"\n✅ Episode ID: {episode_id}")

# Read the episode file
episode_file = Path("Consciousness/01_Episodic_memory/episodes") / f"{episode_id}.json"

if not episode_file.exists():
    print(f"❌ Episode file not found: {episode_file}")
    sys.exit(1)

# Load and validate
with open(episode_file, 'r', encoding='utf-8') as f:
    episode = json.load(f)

print("\n" + "="*60)
print("Schema V2 Validation")
print("="*60)

# Validate Schema V2 structure
checks = {
    "episode_type": "episode_type" in episode,
    "situation_context": "situation_context" in episode,
    "situation_context.context_id": episode.get("situation_context", {}).get("context_id") is not None,
    "turn_1": "turn_1" in episode,
    "turn_1.speaker": episode.get("turn_1", {}).get("speaker") == "user",
    "turn_1.raw_text": episode.get("turn_1", {}).get("raw_text") is not None,
    "turn_1.affective_inference": "affective_inference" in episode.get("turn_1", {}),
    "turn_1.semantic_frames": "semantic_frames" in episode.get("turn_1", {}),
    "turn_1.salience_anchor": "salience_anchor" in episode.get("turn_1", {}),
    "turn_2": "turn_2" in episode,
    "turn_2.speaker": episode.get("turn_2", {}).get("speaker") == "eva",
    "turn_2.text_excerpt": episode.get("turn_2", {}).get("text_excerpt") is not None,
    "state_snapshot": "state_snapshot" in episode,
    "state_snapshot.EVA_matrix": "EVA_matrix" in episode.get("state_snapshot", {}),
    "state_snapshot.Endocrine": "Endocrine" in episode.get("state_snapshot", {}),
    "state_snapshot.Resonance_index": episode.get("state_snapshot", {}).get("Resonance_index") is not None,
    "state_snapshot.memory_encoding_level": "memory_encoding_level" in episode.get("state_snapshot", {}),
    "state_snapshot.memory_color": "memory_color" in episode.get("state_snapshot", {}),
    "state_snapshot.qualia": "qualia" in episode.get("state_snapshot", {}),
    "state_snapshot.reflex": "reflex" in episode.get("state_snapshot", {}),
}

# Legacy fields should NOT exist
legacy_checks = {
    "NO content (legacy)": "content" not in episode,
    "NO response (legacy)": "response" not in episode,
    "NO tags at root (legacy)": "tags" not in episode,
    "NO stimulus_vector at root (legacy)": "stimulus_vector" not in episode,
    "NO physio_state at root (legacy)": "physio_state" not in episode,
}

all_passed = True

for check, passed in checks.items():
    status = "✅" if passed else "❌"
    print(f"{status} {check}")
    if not passed:
        all_passed = False

print("\nLegacy Field Checks:")
for check, passed in legacy_checks.items():
    status = "✅" if passed else "❌"
    print(f"{status} {check}")
    if not passed:
        all_passed = False

# Print key values
print("\n" + "="*60)
print("Sample Data")
print("="*60)
print(f"Episode Type: {episode.get('episode_type')}")
print(f"Context ID: {episode.get('situation_context', {}).get('context_id')}")
print(f"Turn 1 Text: {episode.get('turn_1', {}).get('raw_text')}")
print(f"Turn 1 Tags: {episode.get('turn_1', {}).get('semantic_frames')}")
print(f"Salience Anchor: {episode.get('turn_1', {}).get('salience_anchor')}")
print(f"Turn 2 Text: {episode.get('turn_2', {}).get('text_excerpt')[:80]}...")
print(f"EVA Matrix Stress: {episode.get('state_snapshot', {}).get('EVA_matrix', {}).get('stress_load')}")
print(f"Resonance Index: {episode.get('state_snapshot', {}).get('Resonance_index')}")

print("\n" + "="*60)
if all_passed:
    print("✅ ALL CHECKS PASSED - Schema V2 Compliant!")
else:
    print("❌ SOME CHECKS FAILED - Schema V2 Non-Compliant")
print("="*60)
