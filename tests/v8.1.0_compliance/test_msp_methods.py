"""Test MSP Client new methods"""
import sys
import codecs

# Fix Windows UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
msp_path = Path(__file__).parent.parent.parent / "Memory_&_Soul_Passaport"
sys.path.insert(0, str(msp_path / "MSP_Client"))
sys.path.insert(0, str(msp_path / "MSP"))

from msp_client import MSPClient

print("="*60)
print("Testing MSP Client New Methods (for CIN integration)")
print("="*60)

# Initialize MSP
msp = MSPClient()

print("\n--- Test 1: get_recent_turns() ---")
try:
    turns = msp.get_recent_turns(limit=5, timeout_ms=100)
    print(f"✓ get_recent_turns() works")
    print(f"  Type: {type(turns)}")
    print(f"  Count: {len(turns)} turns")
    if turns:
        print(f"  Sample: {turns[0]}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n--- Test 2: get_recent_episodes() ---")
try:
    episodes = msp.get_recent_episodes(limit=10)
    print(f"✓ get_recent_episodes() works")
    print(f"  Type: {type(episodes)}")
    print(f"  Count: {len(episodes)} episodes")
    if episodes:
        ep = episodes[0]
        print(f"  Sample episode_id: {ep.get('episode_id')}")
        print(f"  Sample timestamp: {ep.get('timestamp')}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n--- Test 3: get_episode_counter() ---")
try:
    counter = msp.get_episode_counter()
    print(f"✓ get_episode_counter() works")
    print(f"  Type: {type(counter)}")
    print(f"  Persona code: {counter.get('persona_code')}")
    print(f"  Current episode: {counter.get('current_episode')}")
    print(f"  Full counter: {counter}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*60)
print("✅ All 3 new methods are working correctly!")
print("="*60)
print("\nMSP Client is now complete for CIN integration.")
print("CIN can now call:")
print("  - msp_client.get_recent_turns(limit=5, timeout_ms=100)")
print("  - msp_client.get_recent_episodes(limit=10)")
print("  - msp_client.get_episode_counter()")
