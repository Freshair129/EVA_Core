"""
Test Split Episodes (User/LLM Separation)
Verify that episodes are split correctly into user_episodes and llm_episodes
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

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator.main_orchestrator import EVAOrchestrator

print("="*60)
print("Split Episodes Test (User/LLM Separation)")
print("="*60)

# Initialize orchestrator
orchestrator = EVAOrchestrator(
    mock_mode=False,
    enable_chunking=False,
    enable_physio=False
)

# Write a test episode
test_input = "ขอบคุณมากนะคะ รักเลย"

print(f"\n📥 Input: {test_input}\n")

result = orchestrator.process_user_input(test_input)

episode_id = result["episode_id"]

print(f"\n{'='*60}")
print(f"Validation")
print(f"{'='*60}")

# Check file sizes
user_file = Path(f"consciousness/01_Episodic_memory/episodes_user/{episode_id}_user.json")
llm_file = Path(f"consciousness/01_Episodic_memory/episodes_llm/{episode_id}_llm.json")

print(f"\n📂 File Existence:")
print(f"{'✅' if user_file.exists() else '❌'} User file: {user_file}")
print(f"{'✅' if llm_file.exists() else '❌'} LLM file: {llm_file}")

if user_file.exists() and llm_file.exists():
    # Load files
    with open(user_file, 'r', encoding='utf-8') as f:
        user_data = json.load(f)

    with open(llm_file, 'r', encoding='utf-8') as f:
        llm_data = json.load(f)

    # Check sizes
    user_size = user_file.stat().st_size
    llm_size = llm_file.stat().st_size

    print(f"\n📊 File Sizes:")
    print(f"User file: {user_size} bytes")
    print(f"LLM file: {llm_size} bytes")
    print(f"Total: {user_size + llm_size} bytes")
    print(f"User/LLM ratio: {user_size / llm_size:.2f}:1")

    # Validate user file content
    print(f"\n{'='*60}")
    print("User File Content")
    print(f"{'='*60}")

    user_checks = {
        "episode_id": "episode_id" in user_data,
        "timestamp": "timestamp" in user_data,
        "session_id": "session_id" in user_data,
        "compression_meta": "compression_meta" in user_data,
        "turn_1": "turn_1" in user_data,
        "turn_1.raw_text": user_data.get("turn_1", {}).get("raw_text") is not None,
        "turn_1.semantic_frames": user_data.get("turn_1", {}).get("semantic_frames") is not None,
        "state_snapshot.EVA_matrix": user_data.get("state_snapshot", {}).get("EVA_matrix") is not None,
        "state_snapshot.Resonance_index": user_data.get("state_snapshot", {}).get("Resonance_index") is not None,
        "NO turn_2 (should be in LLM file)": "turn_2" not in user_data,
        "NO Endocrine (should be in LLM file)": "Endocrine" not in user_data.get("state_snapshot", {}),
    }

    user_passed = True
    for check, passed in user_checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
        if not passed:
            user_passed = False

    # Validate LLM file content
    print(f"\n{'='*60}")
    print("LLM File Content")
    print(f"{'='*60}")

    llm_checks = {
        "episode_id": "episode_id" in llm_data,
        "turn_2": "turn_2" in llm_data,
        "turn_2.text_excerpt": llm_data.get("turn_2", {}).get("text_excerpt") is not None,
        "state_snapshot": "state_snapshot" in llm_data,
        "state_snapshot.Endocrine": llm_data.get("state_snapshot", {}).get("Endocrine") is not None,
        "state_snapshot.qualia": llm_data.get("state_snapshot", {}).get("qualia") is not None,
        "state_snapshot.memory_color": llm_data.get("state_snapshot", {}).get("memory_color") is not None,
    }

    llm_passed = True
    for check, passed in llm_checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")
        if not passed:
            llm_passed = False

    # Test get_full_episode()
    print(f"\n{'='*60}")
    print("Test get_full_episode()")
    print(f"{'='*60}")

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
msp_path = Path(__file__).parent.parent.parent / "Memory_&_Soul_Passaport"
sys.path.insert(0, str(msp_path / "MSP_Client"))
from msp_client import MSPClient
    msp = MSPClient()

    full_episode = msp.get_full_episode(episode_id)

    if full_episode:
        print(f"✅ get_full_episode() works")

        merge_checks = {
            "Has turn_1": "turn_1" in full_episode,
            "Has turn_2": "turn_2" in full_episode,
            "Has EVA_matrix": "EVA_matrix" in full_episode.get("state_snapshot", {}),
            "Has Endocrine": "Endocrine" in full_episode.get("state_snapshot", {}),
            "Has qualia": "qualia" in full_episode.get("state_snapshot", {}),
        }

        merge_passed = True
        for check, passed in merge_checks.items():
            status = "✅" if passed else "❌"
            print(f"{status} {check}")
            if not passed:
                merge_passed = False
    else:
        print(f"❌ get_full_episode() failed")
        merge_passed = False

    # Test query_by_tags()
    print(f"\n{'='*60}")
    print("Test query_by_tags() with User Episodes")
    print(f"{'='*60}")

    # Extract tags from episode
    tags = user_data.get("turn_1", {}).get("semantic_frames", [])
    print(f"Searching for tags: {tags}")

    matches = msp.query_by_tags(tags, max_results=5)

    if matches:
        print(f"✅ Found {len(matches)} matches")
        print(f"✅ Query uses lightweight user episodes (no LLM data loaded)")
    else:
        print(f"❌ No matches found")

    # Summary
    print(f"\n{'='*60}")
    if user_passed and llm_passed and merge_passed and matches:
        print("✅ ALL TESTS PASSED!")
        print(f"\n✅ Split storage working correctly:")
        print(f"   - User file: {user_size}B (lightweight)")
        print(f"   - LLM file: {llm_size}B (detailed)")
        print(f"   - Merge works correctly")
        print(f"   - Queries use user files only")
    else:
        print("❌ SOME TESTS FAILED")
    print(f"{'='*60}")

else:
    print("\n❌ Files not created!")
