from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import json
import os
import asyncio
from src.outputs import export_manager

app = FastAPI()
templates = Jinja2Templates(directory="templates")

RETRY_QUEUE_PATH = "retry_queue.json"

def load_retry_queue():
    if os.path.exists(RETRY_QUEUE_PATH):
        with open(RETRY_QUEUE_PATH, "r") as f:
            try:
                return json.load(f)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
