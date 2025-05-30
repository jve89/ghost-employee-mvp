# queue_utils.py
import json
import os

RETRY_QUEUE_PATH = "jobs/vendor_assistant/output/retry_queue.json"

def load_retry_queue(job_id="vendor_assistant"):
    path = f"jobs/{job_id}/output/retry_queue.json"
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def save_retry_queue(queue, job_id="vendor_assistant"):
    path = f"jobs/{job_id}/output/retry_queue.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(queue, f, indent=2)
