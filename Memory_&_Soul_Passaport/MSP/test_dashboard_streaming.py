"""
Test script for dashboard metric registration and streaming buffers.
"""

from pathlib import Path
import sys
import time
import random
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import MSP with absolute path
import importlib.util
spec = importlib.util.spec_from_file_location("msp_engine", Path(__file__).parent / "msp_engine.py")
msp_module = importlib.util.module_from_spec(spec)

# Also need utils module
utils_spec = importlib.util.spec_from_file_location("utils", Path(__file__).parent / "utils.py")
utils_module = importlib.util.module_from_spec(utils_spec)
spec.loader.exec_module(utils_module)
sys.modules['msp.utils'] = utils_module

spec.loader.exec_module(msp_module)
MSP = msp_module.MSP

def test_dashboard_streaming():
    """Test dashboard metric registration with simulated 30 Hz streaming."""
    
    print("[TEST] Initializing MSP...")
    msp = MSP(use_local=True)
    
    # Test 1: Physiological Stream (30 Hz simulation)
    print("\n[TEST] Simulating 30 Hz hormone streaming (3 seconds)...")
    
    hormones = [
        "ESC_H01_ADRENALINE",
        "ESC_H02_CORTISOL",
        "ESC_H05_DOPAMINE",
        "ESC_H06_SEROTONIN",
        "ESC_H09_OXYTOCIN"
    ]
    
    # Simulate 3 seconds @ 30 Hz = 90 samples per hormone
    for i in range(90):
        for hormone in hormones:
            # Simulate fluctuating levels
            value = 10.0 + random.uniform(-2.0, 2.0)
            msp.register_dashboard_metric(
                metric_name=hormone,
                value=value,
                category="physiological_stream"
            )
        
        # Heart rate
        hr = 72 + random.randint(-5, 5)
        msp.register_dashboard_metric(
            metric_name="heart_rate",
            value=hr,
            category="physiological_stream"
        )
        
        # 30 Hz = ~33ms interval
        time.sleep(0.033)
        
        if (i + 1) % 30 == 0:
            print(f"  → {i + 1}/90 samples registered...")
    
    print("✓ Physiological streaming complete")
    
    # Test 2: Cognitive State (Per-Turn)
    print("\n[TEST] Registering cognitive state updates...")
    
    emotions = ["Calm", "Curious", "Engaged", "Thoughtful", "Excited"]
    colors = ["#4A90E2", "#5BC0DE", "#5CB85C", "#F0AD4E", "#D9534F"]
    
    for i in range(10):
        msp.register_dashboard_metric(
            metric_name="emotion_label",
            value=emotions[i % len(emotions)],
            category="cognitive_state"
        )
        
        msp.register_dashboard_metric(
            metric_name="memory_color",
            value=colors[i % len(colors)],
            category="cognitive_state"
        )
        
        print(f"  → Turn {i + 1}: {emotions[i % len(emotions)]} ({colors[i % len(colors)]})")
    
    print("✓ Cognitive state updates complete")
    
    # Test 3: Get Dashboard Snapshot
    print("\n[TEST] Fetching dashboard snapshot...")
    snapshot = msp.get_dashboard_snapshot(include_streaming=True)
    
    print(f"\n[SNAPSHOT] Timestamp: {snapshot['timestamp']}")
    print(f"[SNAPSHOT] Streaming Metrics: {len(snapshot['streaming_metrics'])} metrics")
    
    for metric_name, data in snapshot['streaming_metrics'].items():
        print(f"  → {metric_name}:")
        print(f"     Category: {data['category']}")
        print(f"     Samples: {len(data['values'])}")
        print(f"     Latest: {data['values'][-1] if data['values'] else 'N/A'}")
    
    print("\n[TEST] ✅ All tests passed!")

if __name__ == "__main__":
    test_dashboard_streaming()
