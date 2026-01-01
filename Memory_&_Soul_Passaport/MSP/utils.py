from pathlib import Path
from datetime import datetime, timezone
import json
import os

def now_iso() -> str:
    """Return current UTC timestamp in ISO format"""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def ensure_dir(p: Path):
    """Ensure directory exists"""
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)

def load_json(path: Path) -> dict:
    """Load JSON file, return empty dict if not exists or error"""
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[MSP-Utils] Load JSON error {path}: {e}")
        return {}

def save_json(path: Path, data: dict):
    """Save JSON file atomically"""
    ensure_dir(path.parent)
    tmp_path = path.with_suffix('.tmp')
    try:
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp_path.replace(path)
    except Exception as e:
        print(f"[MSP-Utils] Save JSON error {path}: {e}")
        if tmp_path.exists():
            os.remove(tmp_path)
