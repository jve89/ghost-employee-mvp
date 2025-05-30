from fastapi import APIRouter
import json
import os

router = APIRouter()
DEAD_LETTER_PATH = "dead_tasks.json"

@router.get("/api/tiles/dead-tasks")
async def dead_tasks_summary():
    if not os.path.exists(DEAD_LETTER_PATH):
        return {"count": 0, "titles": []}

    with open(DEAD_LETTER_PATH, "r") as f:
        queue = json.load(f)

    titles = [entry["task"].get("title", "[No Title]") for entry in queue]
    return {
        "count": len(queue),
        "titles": titles
    }
