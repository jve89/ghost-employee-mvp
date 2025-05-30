# /src/outputs/log_manager.py

import os
import json
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log_task_result(task, result):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_id = task.get("id") or task.get("title") or "untitled"
    safe_task_id = "".join(c for c in task_id if c.isalnum() or c in (" ", "-", "_")).rstrip()
    filename = f"{timestamp}_{safe_task_id}.json"
    path = os.path.join(LOG_DIR, filename)

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "task": task,
                "result": result,
                "timestamp": timestamp
            }, f, indent=2)
        print(f"[LogManager] ✅ Logged result to {path}")
    except Exception as e:
        print(f"[LogManager] ⚠️ Failed to log task result: {e}")
