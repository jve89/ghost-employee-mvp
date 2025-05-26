from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import json
import os
import asyncio
import time
from src.outputs import export_manager
from dashboard.tiles.export_summary import router as export_summary_router
from dashboard.tiles.retry_delays import router as retry_delays_router
from dashboard.tiles.target_breakdown import router as target_breakdown_router
from dashboard.tiles.stale_tasks import router as stale_tasks_router
from dashboard.tiles.recent_activity import router as recent_activity_router
from dashboard.tiles.dead_tasks import router as dead_tasks_router
from fastapi.responses import FileResponse

app = FastAPI()
app.include_router(export_summary_router)
app.include_router(retry_delays_router)
app.include_router(target_breakdown_router)
app.include_router(stale_tasks_router)
app.include_router(recent_activity_router)
app.include_router(dead_tasks_router)
templates = Jinja2Templates(directory="templates")

RETRY_QUEUE_PATH = "retry_queue.json"

def load_retry_queue():
    if os.path.exists(RETRY_QUEUE_PATH):
        with open(RETRY_QUEUE_PATH, "r") as f:
            try:
                queue = json.load(f)
                for entry in queue:
                    entry.setdefault("retry_result", "-")
                    entry.setdefault("result_timestamp", None)
                return queue
            except Exception:
                return []
    return []

def save_retry_queue(queue):
    with open(RETRY_QUEUE_PATH, "w") as f:
        json.dump(queue, f, indent=2)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    queue = load_retry_queue()
    return templates.TemplateResponse("dashboard.html", {"request": request, "queue": queue})

@app.get("/api/retry-queue", response_class=JSONResponse)
async def get_retry_queue():
    return load_retry_queue()

@app.post("/api/revive-dead")
async def revive_dead_tasks():
    from pathlib import Path

    DEAD_LETTER_PATH = "dead_tasks.json"
    RETRY_QUEUE_PATH = "retry_queue.json"

    if not Path(DEAD_LETTER_PATH).exists():
        return {"revived": 0}

    with open(DEAD_LETTER_PATH, "r") as f:
        dead_tasks = json.load(f)

    revived_count = len(dead_tasks)

    if revived_count == 0:
        return {"revived": 0}

    # Append to retry queue
    if Path(RETRY_QUEUE_PATH).exists():
        with open(RETRY_QUEUE_PATH, "r") as f:
            retry_queue = json.load(f)
    else:
        retry_queue = []

    retry_queue.extend(dead_tasks)

    with open(RETRY_QUEUE_PATH, "w") as f:
        json.dump(retry_queue, f, indent=2)

    # Clear the dead-letter queue
    with open(DEAD_LETTER_PATH, "w") as f:
        json.dump([], f)

    return {"revived": revived_count}

@app.post("/api/retry/{index}")
async def retry_task(index: int):
    queue = load_retry_queue()
    if 0 <= index < len(queue):
        task_entry = queue.pop(index)
        # Try export immediately (could be async)
        success = export_manager.export_to_target(task_entry["task"], task_entry["target"])
        if not success:
            # If fail, put back with incremented attempts
            task_entry["attempts"] = task_entry.get("attempts", 0) + 1
            queue.append(task_entry)
        save_retry_queue(queue)
        return {"status": "success", "retried": success}
    else:
        return {"status": "error", "message": "Invalid task index"}

@app.post("/api/clear-queue")
async def clear_queue():
    save_retry_queue([])
    return {"status": "cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.get("/api/download-dead-tasks")
async def download_dead_tasks():
    return FileResponse("dead_tasks.json", media_type="application/json", filename="dead_tasks.json")

@app.get("/api/tiles/retry-delays", response_class=JSONResponse)
async def retry_delays_tile():
    queue = load_retry_queue()
    delays = []

    now = time.time()
    queue_age = 0
    if queue:
        oldest = min(entry.get("last_attempt", now) or now for entry in queue)
        queue_age = now - oldest

    for entry in queue:
        if entry.get("last_attempt"):
            delay = now - entry["last_attempt"]
            delays.append(delay)

    result = {
        "average_delay": round(sum(delays) / len(delays), 1) if delays else 0,
        "max_delay": round(max(delays), 1) if delays else 0,
        "min_delay": round(min(delays), 1) if delays else 0,
        "queue_age": round(queue_age, 1)
    }
    return result
