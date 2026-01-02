"""
Test CIN ↔ MSP Integration
Verify that CIN can successfully call all MSP methods
"""
import sys
import codecs

# Fix Windows UTF-8 encoding (only if not already wrapped)
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
msp_path = Path(__file__).parent.parent.parent / "Memory_&_Soul_Passaport"
sys.path.insert(0, str(msp_path / "MSP_Client"))
sys.path.insert(0, str(msp_path / "MSP"))

from orchestrator.cin.cin import ContextInjectionNode
from msp_client import MSPClient

print("="*70)
print("CIN ↔ MSP Integration Test")
print("="*70)

# Initialize MSP Client
print("\n[1/4] Initializing MSP Client...")
msp = MSPClient()
print("✓ MSP Client initialized")

# Initialize CIN with MSP
print("\n[2/4] Initializing CIN with MSP...")
cin = ContextInjectionNode(
    physio_controller=None,  # Not needed for this test
    msp_client=msp,
    hept_stream_rag=None     # Not needed for this test
)
print("✓ CIN initialized with MSP")

# Test Phase 1 injection (which calls get_recent_episodes and get_recent_turns)
print("\n[3/4] Testing CIN Phase 1 injection (calls MSP methods)...")
try:
    user_input = "สวัสดีค่ะ วันนี้เป็นยังไงบ้าง"
    phase_1_context = cin.inject_phase_1(user_input)

    print("✓ Phase 1 injection successful!")
    print(f"  Context ID: {phase_1_context.get('context_id')}")
    print(f"  Persona loaded: {phase_1_context.get('persona', {}).get('meta', {}).get('name', 'N/A')}")
    print(f"  Turn cache entries: {len(phase_1_context.get('turn_cache', []))}")
    print(f"  Conversation history: {len(phase_1_context.get('conversation_history', []))} episodes")

except AttributeError as e:
    print(f"✗ FAILED: {e}")
    print("  This means CIN tried to call a method that doesn't exist in MSP")
    sys.exit(1)
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# Test direct MSP method calls (simulate what CIN does internally)
print("\n[4/4] Testing direct MSP method calls (what CIN uses)...")
try:
    # Simulate CIN calling get_recent_turns (line 794 in cin.py)
    recent_turns = msp.get_recent_turns(limit=5, timeout_ms=100)
    print(f"✓ get_recent_turns(): {len(recent_turns)} turns")

    # Simulate CIN calling get_recent_episodes (line 879 in cin.py)
    recent_episodes = msp.get_recent_episodes(limit=10)
    print(f"✓ get_recent_episodes(): {len(recent_episodes)} episodes")

    # Simulate CIN calling get_episode_counter (line 1021 in cin.py)
    episode_counter = msp.get_episode_counter()
    print(f"✓ get_episode_counter(): {episode_counter.get('persona_code')}_{episode_counter.get('current_episode')}")

except AttributeError as e:
    print(f"✗ FAILED: Method not found - {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("✅ CIN ↔ MSP Integration Test PASSED")
print("="*70)
print("\nAll CIN dependencies on MSP are satisfied:")
print("  ✓ get_recent_turns(limit, timeout_ms) - Working")
print("  ✓ get_recent_episodes(limit) - Working")
print("  ✓ get_episode_counter() - Working")
print("\nMSP Client is ready for production use with CIN.")
print("="*70)
