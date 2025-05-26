from fastapi import APIRouter
import json
import os
from collections import defaultdict

router = APIRouter()
RETRY_QUEUE_PATH = "retry_queue.json"

@router.get("/api/tiles/target-breakdown")
async def target_breakdown():
    breakdown = defaultdict(int)

    if not os.path.exists(RETRY_QUEUE_PATH):
        return {}

    with open(RETRY_QUEUE_PATH, "r") as f:
        queue = json.load(f)

    for entry in queue:
        target = entry.get("target", "unknown")
        breakdown[target] += 1

    return dict(breakdown)
