import os
import json
import datetime

LOGS_FOLDER = "logs"

def save_structured_log(file_path, summary=None, tasks=None, alerts=None):
    if not os.path.exists(LOGS_FOLDER):
        os.makedirs(LOGS_FOLDER)

    if not summary or not isinstance(tasks, list):
        print("[WARN] Skipping log save — missing summary or tasks.")
        return None

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_data = {
        "file": file_path,
        "processed_at": timestamp,
        "summary": summary,
        "tasks": tasks,
        "alerts": alerts or [],
    }

    filename = f"{LOGS_FOLDER}/structured_{timestamp}.json"
    try:
        with open(filename, "w") as f:
            json.dump(log_data, f, indent=4)
        print(f"[STRUCTURED LOG SAVED] {filename}")
        return filename
    except Exception as e:
        print(f"[ERROR] Failed to save structured log: {e}")
        return None

def get_last_log_path():
    logs = [f for f in os.listdir(LOGS_FOLDER) if f.startswith("structured_") and f.endswith(".json")]
    logs.sort(reverse=True)
    if logs:
        return os.path.join(LOGS_FOLDER, logs[0])
    return None
