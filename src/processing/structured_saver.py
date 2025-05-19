import os
import json
import datetime

LOGS_FOLDER = "logs"

def save_structured_data(file_path, summary=None, tasks=None, alerts=None):
    if not os.path.exists(LOGS_FOLDER):
        os.makedirs(LOGS_FOLDER)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_data = {
        "file": file_path,
        "processed_at": timestamp,
        "summary": summary,
        "tasks": tasks,
        "alerts": alerts,
    }

    filename = f"{LOGS_FOLDER}/structured_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(log_data, f, indent=4)

    print(f"[STRUCTURED LOG SAVED] {filename}")
    return filename
