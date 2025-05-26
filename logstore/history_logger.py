import json
import time
from pathlib import Path

HISTORY_PATH = "export_history.json"

def load_history():
    if Path(HISTORY_PATH).exists():
        with open(HISTORY_PATH, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_history(history):
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)

def log_export_result(task_id, title, target, status, attempts, message=None):
    entry = {
        "timestamp": time.time(),
        "task_id": task_id,
        "title": title,
        "target": target,
        "status": status,  # "success" or "failure"
        "attempts": attempts,
        "last_attempt": time.time(),
        "message": message or ""
    }

    history = load_history()
    history.append(entry)
    save_history(history)
