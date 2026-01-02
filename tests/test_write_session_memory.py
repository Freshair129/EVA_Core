"""
Test Session Memory Write
Verify that session memories are correctly written to disk by MSPClient
"""

import sys
import codecs
import json
import os
from pathlib import Path

from pathlib import Path
msp_path = Path(__file__).parent.parent / "Memory_&_Soul_Passaport"
sys.path.insert(0, str(msp_path / "MSP_Client"))
from msp_client import MSPClient

def test_write_session_memory():
    print("="*60)
    print("Testing Session Memory Write")
    print("="*60)

    # Initialize MSP Client
    msp = MSPClient()

    # Dummy session data
    test_data = {
        "summary": "This is a test session snapshot representing a Core compression.",
        "key_points": ["Point A", "Point B", "Point C"],
        "metadata": {
            "test_run": True,
            "complexity": "low"
        }
    }

    print("\n📝 Calling write_session_memory()...")
    try:
        session_id = msp.write_session_memory(test_data)
        print(f"✅ Method returned Session ID: {session_id}")

        # Verify file existence
        expected_path = msp.session_memory_dir / f"{session_id}.json"
        print(f"🧐 Checking for file at: {expected_path}")

        if expected_path.exists():
            print("✅ File found on disk.")
            
            # Verify content
            with open(expected_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            if saved_data["summary"] == test_data["summary"]:
                print("✅ Content integrity verified.")
            else:
                print("❌ Content mismatch!")
                return False
            
            if "compression_counters" in saved_data:
                print(f"✅ Compression counters found: {saved_data['compression_counters']}")
            else:
                print("❌ Compression counters missing from file!")
                return False
                
            return True
        else:
            print("❌ File NOT found!")
            return False

    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    # Fix console encoding
    if sys.platform == 'win32':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

    success = test_write_session_memory()
    
    print("\n" + "="*60)
    if success:
        print("🎉 TEST PASSED!")
    else:
        print("💀 TEST FAILED!")
    print("="*60)
    
    sys.exit(0 if success else 1)
