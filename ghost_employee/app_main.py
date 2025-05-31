from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uuid
import os
import json
import time
import threading

from ghost_employee.outputs import export_manager
from ghost_employee.dashboard.routes import retry_controls
from ghost_employee.queue.retry_worker import load_retry_queue
from ghost_employee.core.auto_scheduler import start_background_jobs, run_job_periodically
from ghost_employee.core.job_loader import get_all_job_names
from ghost_employee.queue.queue_utils import load_retry_queue, save_retry_queue

from ghost_employee.dashboard.routes.job_dashboard import router as job_dashboard_router

from ghost_employee.dashboard.tiles.task_health_dead import router as dead_tasks_router
from ghost_employee.dashboard.tiles.task_health_stale import router as stale_tasks_router
from ghost_employee.dashboard.tiles.summary_tile import router as summary_tile_router
from ghost_employee.dashboard.tiles.retry_summary import router as retry_summary_router

from ghost_employee.dashboard.routes.add_job_ui import router as job_router
from ghost_employee.dashboard.routes.job_manager_api import router as job_manager_api
from ghost_employee.dashboard.routes.job_logs_api import router as job_logs_api
from ghost_employee.dashboard.routes.job_config_api import router as job_config_router

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/jobs", StaticFiles(directory="jobs"), name="jobs")

# Include all routers
app.include_router(stale_tasks_router)         # from task_health_stale.py
app.include_router(dead_tasks_router)          # from task_health_dead.py
app.include_router(summary_tile_router)        # from summary_tile.py
app.include_router(retry_summary_router)       # from retry_summary.py

app.include_router(job_router)
app.include_router(job_manager_api)
app.include_router(job_logs_api)
app.include_router(job_config_router)
app.include_router(job_dashboard_router)
app.include_router(retry_controls.router)

RETRY_QUEUE_PATH = "retry_queue.json"

if not os.path.exists(RETRY_QUEUE_PATH):
    with open(RETRY_QUEUE_PATH, "w") as f:
        json.dump([], f)

def start_background_jobs():
    jobs = get_all_job_names()
    for job in jobs:
        t = threading.Thread(target=run_job_periodically, args=(job,), daemon=True)
        t.start()
        print(f"[AUTO] Launched background thread for {job}")

@app.on_event("startup")
async def startup_event():
    start_background_jobs()

@app.get("/debug/path")
def debug_path():
    import os
    return {"file": __file__, "cwd": os.getcwd()}

def start_background_jobs():
    jobs = get_all_job_names()
    for job in jobs:
        t = threading.Thread(target=run_job_periodically, args=(job,), daemon=True)
        t.start()
        print(f"[AUTO] Launched background thread for {job}")

@app.on_event("startup")
async def startup_event():
    start_background_jobs()

@app.get("/retries/vendor_assistant")
async def get_vendor_assistant_retries():
    queue = load_retry_queue(job_id="vendor_assistant")  # Pass job_id so it loads from the correct folder
    return {"entries": queue}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    queue = load_retry_queue()
    return templates.TemplateResponse("dashboard.html", {"request": request, "queue": queue})

@app.get("/jobs", response_class=HTMLResponse)
async def job_manager(request: Request):
    return templates.TemplateResponse("job_manager.html", {"request": request})

@app.get("/job/{job_folder}", response_class=HTMLResponse)
async def job_dashboard(request: Request, job_folder: str):
    config_path = f"jobs/{job_folder}/config.json"
    status_path = f"jobs/{job_folder}/status.json"

    config = {}
    status = {}

    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
    if os.path.exists(status_path):
        with open(status_path) as f:
            status = json.load(f)

    return templates.TemplateResponse("job_dashboard.html", {
        "request": request,
        "job_name": config.get("job_name", job_folder),
        "job_folder": job_folder,
        "config": config,
        "status": status
    })

@app.get("/api/retry-queue", response_class=JSONResponse)
async def get_retry_queue():
    return load_retry_queue()

@app.post("/api/retry/{index}")
async def retry_task(index: int):
    queue = load_retry_queue()
    if 0 <= index < len(queue):
        task_entry = queue.pop(index)

        success = export_manager.export_to_target(task_entry["task"], task_entry["target"])
        if not success:

            task_entry["attempts"] = task_entry.get("attempts", 0) + 1
            queue.append(task_entry)
        save_retry_queue(queue)
        return {"status": "success", "retried": success}
    return {"status": "error", "message": "Invalid task index"}

@app.post("/api/clear-queue")
async def clear_queue():
    save_retry_queue([])
    return {"status": "cleared"}

@app.post("/api/revive-dead")
async def revive_dead_tasks():
    DEAD_LETTER_PATH = "dead_tasks.json"
    if not os.path.exists(DEAD_LETTER_PATH):
        return {"revived": 0}

    with open(DEAD_LETTER_PATH, "r") as f:
        dead_tasks = json.load(f)
    revived_count = len(dead_tasks)

    retry_queue = load_retry_queue()
    retry_queue.extend(dead_tasks)
    save_retry_queue(retry_queue)

    with open(DEAD_LETTER_PATH, "w") as f:
        json.dump([], f)

    return {"revived": revived_count}

@app.post("/api/retry-all")
async def retry_all_failed():
    job_id = "vendor_assistant"  # ✅ hardcoded for now — adjust here if needed
    queue = load_retry_queue(job_id)

    failed = [
        entry for entry in queue
        if entry.get("retry_result") not in [True, "resolved", "success"]
    ]

    retried_count = 0

    for entry in failed:
        success = export_manager.export_to_target(entry["task"], entry["target"])
        entry["attempts"] = entry.get("attempts", 0) + 1
        entry["retry_result"] = success
        entry["result_timestamp"] = time.time()
        retried_count += 1

    save_retry_queue(queue, job_id)
    return {"status": "ok", "retried": retried_count}

@app.get("/retries/vendor_assistant")
async def get_queue():
    queue = load_retry_queue("vendor_assistant")
    return {"entries": queue}

@app.get("/api/download-dead-tasks")
async def download_dead_tasks():
    return FileResponse("dead_tasks.json", media_type="application/json", filename="dead_tasks.json")

@app.get("/api/tiles/retry-delays", response_class=JSONResponse)
async def retry_delays_tile():
    queue = load_retry_queue()
    delays = []
    now = time.time()

    if queue:
        oldest = min(entry.get("last_attempt", now) or now for entry in queue)
        queue_age = now - oldest

        for entry in queue:
            if entry.get("last_attempt"):
                delay = now - entry["last_attempt"]
                delays.append(delay)
    else:
        queue_age = 0

    result = {
        "average_delay": round(sum(delays) / len(delays), 1) if delays else 0,
        "max_delay": round(max(delays), 1) if delays else 0,
        "min_delay": round(min(delays), 1) if delays else 0,
        "queue_age": round(queue_age, 1)
    }
    return result

@app.get("/timeline", response_class=JSONResponse)
async def get_global_timeline():
    jobs_root = "jobs"
    timeline_entries = []

    for job_folder in os.listdir(jobs_root):
        summary_log_path = os.path.join(jobs_root, job_folder, "output", "summary_log.json")
        if os.path.exists(summary_log_path):
            try:
                with open(summary_log_path, "r") as f:
                    entries = json.load(f)
                    for entry in entries:
                        entry["job"] = job_folder  # Optional: include job name
                        timeline_entries.append(entry)
            except Exception as e:
                print(f"[ERROR] Failed reading {summary_log_path}: {e}")

    sorted_entries = sorted(timeline_entries, key=lambda x: x.get("timestamp", ""), reverse=True)
    return {"timeline": sorted_entries[-50:][::-1]}  # Return oldest to newest

@app.on_event("startup")
async def startup_message():
    print("✅ Dashboard server is running!")

@app.get("/debug/export-test")
def test_export_debug():
    from ghost_employee.outputs import export_manager
    dummy_task = {
        "description": "Test task for export",
        "id": "debug-task-001"
    }
    try:
        result = export_manager.export_to_target(dummy_task, "sheets")
        return {"status": "ok", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/debug/retry-entries")
async def debug_retry_entries():
    queue = load_retry_queue()
    raw = []
    for i, entry in enumerate(queue):
        raw.append({
            "index": i,
            "description": entry["task"].get("description", "[no desc]"),
            "retry_result": entry.get("retry_result"),
            "attempts": entry.get("attempts"),
            "target": entry.get("target"),
        })
    return {"entries": raw}

# At the bottom:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
