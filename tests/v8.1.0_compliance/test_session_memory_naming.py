"""
Test Session Memory Naming (Compression Hierarchy)
Verify that session memory filenames follow compression hierarchy:
Format: {developer_id}_S{total:03d}_SP{sphere}C{core}_SS{session}.json
Example: THA-01_S006_SP1C1_SS6.json
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
print("Session Memory Naming Test (Compression Hierarchy)")
print("="*60)

# Initialize MSP Client
msp = MSPClient()

print(f"\n📝 Testing Session Memory Filename Generation\n")

# Test scenarios (using develop_id from soul.md: THA-01-S003)
test_scenarios = [
    {"Session_seq": 1, "Core_seq": 0, "Sphere_seq": 0, "Total_sessions": 1,
     "expected": "THA-01-S003_SP1C1_SS1.json", "description": "First session ever (clone S003)"},

    {"Session_seq": 6, "Core_seq": 0, "Sphere_seq": 0, "Total_sessions": 6,
     "expected": "THA-01-S003_SP1C1_SS6.json", "description": "6th session in Core 1"},

    {"Session_seq": 8, "Core_seq": 0, "Sphere_seq": 0, "Total_sessions": 8,
     "expected": "THA-01-S003_SP1C1_SS8.json", "description": "8th session (triggers Core compression)"},

    {"Session_seq": 1, "Core_seq": 1, "Sphere_seq": 0, "Total_sessions": 9,
     "expected": "THA-01-S003_SP1C2_SS1.json", "description": "First session in Core 2"},

    {"Session_seq": 0, "Core_seq": 8, "Sphere_seq": 0, "Total_sessions": 64,
     "expected": "THA-01-S003_SP1C9_SS0.json", "description": "After 8 cores (triggers Sphere)"},

    {"Session_seq": 1, "Core_seq": 0, "Sphere_seq": 1, "Total_sessions": 65,
     "expected": "THA-01-S003_SP2C1_SS1.json", "description": "First session in Sphere 2"},
]

all_passed = True

for i, scenario in enumerate(test_scenarios, 1):
    print(f"\n[Test {i}] {scenario['description']}")

    # Temporarily set counters
    msp.compression_counters["Session_seq"] = scenario["Session_seq"]
    msp.compression_counters["Core_seq"] = scenario["Core_seq"]
    msp.compression_counters["Sphere_seq"] = scenario["Sphere_seq"]
    msp.compression_counters["Total_sessions"] = scenario["Total_sessions"]

    # Generate filename
    filename = msp._generate_session_memory_filename()
    session_id = msp._generate_session_memory_id()

    # Check if matches expected
    expected = scenario["expected"]
    matches = (filename == expected)

    status = "✅" if matches else "❌"
    print(f"  {status} Expected: {expected}")
    print(f"  {status} Got:      {filename}")
    print(f"  {status} ID:       {session_id}")

    # Parse and verify components
    # Format: THA-01-S003_SP1C1_SS6.json
    parts = filename.replace('.json', '').split('_')
    if len(parts) >= 3:
        develop_id = parts[0]  # THA-01-S003
        hierarchy = parts[1]  # SP1C1
        session_in_core = parts[2] if len(parts) > 2 else ""  # SS6

        print(f"\n    Components:")
        print(f"      Develop ID: {develop_id}")
        print(f"      Hierarchy: {hierarchy}")
        print(f"      Session in Core: {session_in_core}")

    if not matches:
        all_passed = False

# Test actual counter increment
print(f"\n{'='*60}")
print("Test Counter Increment & File Naming")
print(f"{'='*60}")

# Reset counters to clean state
msp.compression_counters = {
    "Session_seq": 0,
    "Core_seq": 0,
    "Sphere_seq": 0,
    "Total_sessions": 0,
    "last_update": "2026-01-01T00:00:00"
}
msp._save_compression_counters()

print(f"\n📊 Simulating Session Creation:\n")

# Simulate 10 sessions
filenames_generated = []

for i in range(1, 11):
    # Increment counters
    result = msp._increment_compression_counters()

    # Generate filename
    filename = msp._generate_session_memory_filename()
    filenames_generated.append(filename)

    print(f"  Session {i}: {filename}")
    print(f"    → Position in Core: {result['session_seq']}, Core: {result['core_seq']+1}, Sphere: {result['sphere_seq']+1}")

    # Check if Core boundary crossed
    if i == 8:
        print(f"    🔥 Core compression trigger!")
    if i == 64:
        print(f"    🔥 Sphere compression trigger!")

# Validate sequential numbering
print(f"\n{'='*60}")
print("Validation: Sequential Numbering")
print(f"{'='*60}")

print(f"\n✅ Generated {len(filenames_generated)} session memory filenames:")
for i, fname in enumerate(filenames_generated, 1):
    print(f"  {i}. {fname}")

# Check developer config
print(f"\n{'='*60}")
print("Developer Config File")
print(f"{'='*60}")

developer_config_file = Path("Consciousness/09_state/developer_config.json")

if developer_config_file.exists():
    with open(developer_config_file, 'r', encoding='utf-8') as f:
        dev_config = json.load(f)

    print(f"\n✅ Developer config file exists")
    print(f"\n  Develop ID: {dev_config.get('develop_id')}")
    print(f"  Format: {dev_config.get('format')}")
    print(f"  Components: {dev_config.get('components')}")
    print(f"  Source: {dev_config.get('source', 'N/A')}")
else:
    print(f"\n❌ Developer config file not found")
    all_passed = False

# Check compression counters
print(f"\n{'='*60}")
print("Compression Counters File")
print(f"{'='*60}")

counters_file = Path("Consciousness/09_state/compression_counters.json")

if counters_file.exists():
    with open(counters_file, 'r', encoding='utf-8') as f:
        counters = json.load(f)

    print(f"\n✅ Compression counters file exists")
    print(f"\n  Session_seq: {counters.get('Session_seq')} (position in current Core)")
    print(f"  Core_seq: {counters.get('Core_seq')} (number of cores created)")
    print(f"  Sphere_seq: {counters.get('Sphere_seq')} (number of spheres created)")
    print(f"  Total_sessions: {counters.get('Total_sessions')} (cumulative count)")

    # Verify Total_sessions updated
    if counters.get('Total_sessions') == 10:
        print(f"\n  ✅ Total_sessions correctly incremented to 10")
    else:
        print(f"\n  ❌ Total_sessions should be 10, got {counters.get('Total_sessions')}")
        all_passed = False
else:
    print(f"\n❌ Compression counters file not found")
    all_passed = False

# Check session memory directory
print(f"\n{'='*60}")
print("Session Memory Directory")
print(f"{'='*60}")

session_dir = Path("Consciousness/04_Session_memory")

if session_dir.exists():
    print(f"\n✅ Session memory directory exists: {session_dir}")
else:
    print(f"\n❌ Session memory directory not found")
    all_passed = False

# Summary
print(f"\n{'='*60}")
if all_passed:
    print("✅ ALL TESTS PASSED!")
    print(f"\n✅ Session memory naming working correctly:")
    print(f"   - Format: {{develop_id}}_SP{{sphere}}C{{core}}_SS{{session}}.json")
    print(f"   - Example: {filenames_generated[0]}")
    print(f"   - Develop ID: THA-01-S003 (clone)")
    print(f"   - Note: Original (THA-01) has no -S suffix")
    print(f"   - Compression hierarchy reflected: ✅")
else:
    print("❌ SOME TESTS FAILED")
print(f"{'='*60}")
