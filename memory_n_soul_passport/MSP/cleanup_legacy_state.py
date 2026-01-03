"""
Legacy State File Cleanup Script

This script archives/removes redundant state files from 09_state directory
and migrates to the new three-tier system (Current/Buffer/History).
"""

from pathlib import Path
import json
import shutil
from datetime import datetime

# Paths
BASE_PATH = Path(__file__).parent.parent
STATE_DIR = BASE_PATH / "consciousness" / "09_state"
ARCHIVE_DIR = STATE_DIR / "archive_legacy"

def cleanup_legacy_files():
    """Archive or remove legacy/redundant state files."""
    
    # Create archive directory
    ARCHIVE_DIR.mkdir(exist_ok=True)
    
    legacy_files = {
        "body_state_history.jsonl": "archive",  # Large, will be replaced by modular logs
        "consciousness_history.jsonl": "archive",  # Redundant with new buffer system
    }
    
    optional_relocate = {
        "developer_config.json": "../configs/developer_config.json",  # Move to configs
        "lingering_stimulus.json": None,  # Evaluate: keep or archive
    }
    
    print("[CLEANUP] Starting legacy file cleanup...")
    
    # Archive legacy files
    for filename, action in legacy_files.items():
        file_path = STATE_DIR / filename
        if file_path.exists():
            if action == "archive":
                archive_path = ARCHIVE_DIR / f"{filename}.{datetime.now().strftime('%Y%m%d')}"
                shutil.move(str(file_path), str(archive_path))
                print(f"[ARCHIVED] {filename} → {archive_path}")
    
    # Relocate config files
    for old_path, new_path in optional_relocate.items():
        if new_path:
            old_file = STATE_DIR / old_path
            new_file = BASE_PATH / new_path
            if old_file.exists():
                new_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(old_file), str(new_file))
                print(f"[MOVED] {old_path} → {new_path}")
    
    print("[CLEANUP] Cleanup complete!")
    print(f"[INFO] Archived files located in: {ARCHIVE_DIR}")

if __name__ == "__main__":
    cleanup_legacy_files()
