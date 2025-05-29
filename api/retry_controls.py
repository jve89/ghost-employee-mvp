# ghost_employee/api/retry_controls.py

from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter()

RETRY_QUEUE_TEMPLATE = "jobs/{job_id}/output/retry_queue.json"

def load_retry_queue(job_id: str):
    path = RETRY_QUEUE_TEMPLATE.format(job_id=job_id)
    if not Path(path).exists():
        raise HTTPException(status_code=404, detail="Retry queue not found.")
    with open(path, "r") as f:
        return json.load(f)

def save_retry_queue(job_id: str, queue: list):
    path = RETRY_QUEUE_TEMPLATE.format(job_id=job_id)
    with open(path, "w") as f:
        json.dump(queue, f, indent=2)

@router.get("/retries/{job_id}")
def list_retries(job_id: str):
    return load_retry_queue(job_id)

@router.post("/retries/{job_id}/{task_id}/resolve")
def mark_as_resolved(job_id: str, task_id: str):
    queue = load_retry_queue(job_id)
    updated = False
    for entry in queue:
        if entry.get("task", {}).get("id") == task_id:
            entry["status"] = "resolved"
            entry["retry_result"] = True
            updated = True
    if not updated:
        raise HTTPException(status_code=404, detail="Task ID not found.")
    save_retry_queue(job_id, queue)
    return {"status": "resolved", "task_id": task_id}
