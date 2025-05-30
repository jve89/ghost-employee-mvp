# ghost_employee/api/retry_controls.py

from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
import uuid

router = APIRouter()

RETRY_QUEUE_TEMPLATE = "jobs/{job_id}/output/retry_queue.json"

def load_retry_queue(job_id: str):
    path = RETRY_QUEUE_TEMPLATE.format(job_id=job_id)
    if not Path(path).exists():
        return []
    with open(path, "r") as f:
        return json.load(f)

def save_retry_queue(job_id: str, queue: list):
    path = RETRY_QUEUE_TEMPLATE.format(job_id=job_id)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(queue, f, indent=2)

@router.get("/retries/{job_id}")
def list_retries(job_id: str):
    return load_retry_queue(job_id)

@router.post("/retries/{job_id}/{task_id}/resolve")
def resolve_task(job_id: str, task_id: str):
    queue = load_retry_queue(job_id)
    found = False
    updated_queue = []

    for entry in queue:
        task = entry.get("task", {})
        if "id" not in task:
            task["id"] = f"auto-{uuid.uuid4().hex[:8]}"

        if task["id"] == task_id:
            found = True  # Skip adding this one (we are "resolving" it)
        else:
            updated_queue.append(entry)

    if not found:
        raise HTTPException(status_code=404, detail="Task ID not found.")

    save_retry_queue(job_id, updated_queue)
    return {"status": "resolved", "task_id": task_id}
