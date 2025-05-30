import json
import uuid
from pathlib import Path

RETRY_PATH = Path("jobs/vendor_assistant/output/retry_queue.json")

def patch_retry_queue():
    if not RETRY_PATH.exists():
        print(f"❌ Retry queue not found at {RETRY_PATH}")
        return

    with open(RETRY_PATH, "r") as f:
        queue = json.load(f)

    patched = 0
    for entry in queue:
        task = entry.get("task", {})
        if "id" not in task:
            task["id"] = f"auto-{uuid.uuid4().hex[:8]}"
            patched += 1

    with open(RETRY_PATH, "w") as f:
        json.dump(queue, f, indent=2)

    print(f"✅ Patched {patched} entries with missing task IDs.")

if __name__ == "__main__":
    patch_retry_queue()
