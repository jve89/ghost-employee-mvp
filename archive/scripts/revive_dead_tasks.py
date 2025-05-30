import json
from pathlib import Path
import time

RETRY_QUEUE_PATH = "retry_queue.json"
DEAD_LETTER_PATH = "dead_tasks.json"

def load_json(path):
    if Path(path).exists():
        with open(path, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def revive_tasks():
    retry_queue = load_json(RETRY_QUEUE_PATH)
    dead_tasks = load_json(DEAD_LETTER_PATH)

    revived = 0
    remaining_dead = []

    for task in dead_tasks:
        if not task.get("revived"):
            task["revived"] = True
            task["attempts"] = 0
            task["last_attempt"] = None
            task["result_timestamp"] = None
            task["retry_result"] = "Waiting"
            retry_queue.append(task)
            revived += 1
        else:
            remaining_dead.append(task)

    save_json(RETRY_QUEUE_PATH, retry_queue)
    save_json(DEAD_LETTER_PATH, remaining_dead)

    print(f"✅ Revived {revived} tasks. Remaining in dead-letter queue: {len(remaining_dead)}.")

if __name__ == "__main__":
    revive_tasks()
