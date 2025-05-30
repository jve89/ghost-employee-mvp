from fastapi import APIRouter
import os
import json
import time

router = APIRouter()
RETRY_QUEUE_PATH = "retry_queue.json"

@router.get("/api/tiles/retry-delays")
async def retry_delays_tile():
    if not os.path.exists(RETRY_QUEUE_PATH):
        return {
            "average_delay": 0,
            "max_delay": 0,
            "min_delay": 0,
            "queue_age": 0
        }

    with open(RETRY_QUEUE_PATH, "r") as f:
        try:
            queue = json.load(f)
        except Exception:
            queue = []

    now = time.time()
    delays = []
    queue_age = 0

    if queue:
        oldest = min(entry.get("last_attempt", now) or now for entry in queue)
        queue_age = now - oldest

    for entry in queue:
        if entry.get("last_attempt"):
            delay = now - entry["last_attempt"]
            delays.append(delay)

    return {
        "average_delay": round(sum(delays) / len(delays), 1) if delays else 0,
        "max_delay": round(max(delays), 1) if delays else 0,
        "min_delay": round(min(delays), 1) if delays else 0,
        "queue_age": round(queue_age, 1)
    }
