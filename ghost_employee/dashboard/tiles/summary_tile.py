from fastapi import APIRouter
import json
import os

router = APIRouter()
RETRY_QUEUE_PATH = "retry_queue.json"

@router.get("/api/tiles/export-summary")
async def export_summary():
    if not os.path.exists(RETRY_QUEUE_PATH):
        return {
            "total": 0,
            "success": 0,
            "failed": 0,
            "pending": 0
        }

    with open(RETRY_QUEUE_PATH, "r") as f:
        queue = json.load(f)

    total = len(queue)
    success = sum(1 for e in queue if e.get("retry_result") is True)
    failed = sum(1 for e in queue if e.get("retry_result") is False)
    pending = sum(1 for e in queue if e.get("retry_result") not in [True, False])

    return {
        "total": total,
        "success": success,
        "failed": failed,
        "pending": pending
    }
