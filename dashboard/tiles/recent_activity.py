# dashboard/tiles/recent_activity.py

from fastapi import APIRouter
import json
import os
import time

router = APIRouter()
RETRY_QUEUE_PATH = "retry_queue.json"

@router.get("/api/tiles/recent-activity")
async def recent_activity():
    if not os.path.exists(RETRY_QUEUE_PATH):
        return []

    with open(RETRY_QUEUE_PATH, "r") as f:
        queue = json.load(f)

    recent = [
        {
            "title": entry["task"].get("title", "[No Title]"),
            "status": str(entry.get("retry_result")),
            "when": entry.get("result_timestamp", 0)
        }
        for entry in queue
        if entry.get("result_timestamp")
    ]

    recent.sort(key=lambda x: x["when"], reverse=True)
    recent = recent[:5]

    for entry in recent:
        entry["when"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry["when"]))

    return recent
