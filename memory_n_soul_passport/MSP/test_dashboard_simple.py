"""
Simple test for dashboard streaming without complex imports
"""
import sys
from pathlib import Path

# Just test the basic flow without importing MSP
dashboard_dir = Path(r"E:\The Human Algorithm\T2\EVA 8.1.0\consciousness\09_state\dashboard_stream")
dashboard_dir.mkdir(parents=True, exist_ok=True)

print("[TEST] Dashboard streaming directory created successfully")
print(f"[TEST] Location: {dashboard_dir}")

# Create sample metric files
import json
import time

# Test hormone data
for i, hormone in enumerate(["ESC_H01_ADRENALINE", "ESC_H02_CORTISOL", "ESC_H05_DOPAMINE"]):
    metric_data = {
        "metric_name": hormone,
        "category": "physiological_stream",
        "buffer": {
            "size": 900,
            "circular": True,
            "entries": [
                {"timestamp": time.time() + j*0.033, "value": 10.0 + j*0.1}
                for j in range(30)  # 30 samples
            ]
        },
        "metadata": {
            "update_frequency": "30 Hz",
            "last_update": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }
    
    output_file = dashboard_dir / f"{hormone}_dashboard.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metric_data, f, indent=2)
    
    print(f"✓ Created: {hormone}_dashboard.json ({len(metric_data['buffer']['entries'])} samples)")

# Test cognitive state
for metric_name, value in [("emotion_label", "Calm"), ("memory_color", "#4A90E2")]:
    metric_data = {
        "metric_name": metric_name,
        "category": "cognitive_state",
        "buffer": {
            "size": 20,
            "circular": True,
            "entries": [
                {"timestamp": time.time(), "value": value}
            ]
        },
        "metadata": {
            "update_frequency": "per-turn",
            "last_update": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }
    
    output_file = dashboard_dir / f"{metric_name}_dashboard.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metric_data, f, indent=2)
    
    print(f"✓ Created: {metric_name}_dashboard.json")

print("\n[TEST] ✅ All dashboard metrics created successfully!")
print(f"[TEST] Files created: {len(list(dashboard_dir.glob('*_dashboard.json')))}")
