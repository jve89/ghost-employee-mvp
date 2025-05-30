from fastapi import APIRouter
import json
import os
import time

router = APIRouter()
RETRY_QUEUE_PATH = "retry_queue.json"
STALE_THRESHOLD_HOURS = 3

@router.get("/api/tiles/stale-tasks")
async def stale_tasks_tile():
    if not os.path.exists(RETRY_QUEUE_PATH):
        return []

    with open(RETRY_QUEUE_PATH, "r") as f:
        try:
            queue = json.load(f)
        except Exception:
            return []

    now = time.time()
    stale = []

    for entry in queue:
        last = entry.get("last_attempt")
        if last and (now - last) > STALE_THRESHOLD_HOURS * 3600:
            stale.append({
                "title": entry["task"].get("title", "[No Title]"),
                "target": entry.get("target", "-"),
                "hours_ago": round((now - last) / 3600, 1)
            })

    return stale
