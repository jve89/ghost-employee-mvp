# ghost_employee/api/retry_controls.py

from fastapi import APIRouter, HTTPException
from pathlib import Path
from ghost_employee.queue.queue_utils import load_retry_queue, save_retry_queue
import json
import uuid

router = APIRouter()

RETRY_QUEUE_TEMPLATE = "jobs/{job_id}/output/retry_queue.json"

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
