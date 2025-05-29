from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import json

import time
import threading

from auto_scheduler import run_job_periodically
from auto_scheduler import start_background_jobs
from src.job_loader import get_all_job_names

from src.outputs import export_manager

from dashboard.tiles.export_summary import router as export_summary_router
from dashboard.tiles.retry_delays import router as retry_delays_router
from dashboard.tiles.target_breakdown import router as target_breakdown_router
from dashboard.tiles.stale_tasks import router as stale_tasks_router
from dashboard.tiles.recent_activity import router as recent_activity_router
from dashboard.tiles.dead_tasks import router as dead_tasks_router
from dashboard.tiles.job_status import router as job_status_router
from dashboard.tiles.job_stats import router as job_stats_router
from dashboard.tiles.job_performance import router as job_perf_router
from dashboard.routes.timeline import router as timeline_router
from dashboard.add_job_ui import router as job_router
from dashboard.job_manager_api import router as job_manager_api
from dashboard.job_logs_api import router as job_logs_api

from dashboard.job_config_api import router as job_config_router

from dashboard.routes import job_dashboard


app = FastAPI()
start_background_jobs()

templates = Jinja2Templates(directory="templates")
app.mount("/jobs", StaticFiles(directory="jobs"), name="jobs")

# Include all routers
app.include_router(export_summary_router)
app.include_router(retry_delays_router)
app.include_router(target_breakdown_router)
app.include_router(stale_tasks_router)
app.include_router(recent_activity_router)
app.include_router(dead_tasks_router)

app.include_router(job_status_router)
app.include_router(job_stats_router)
app.include_router(job_perf_router)
app.include_router(job_router)
app.include_router(job_manager_api)
app.include_router(job_logs_api)

app.include_router(job_config_router)

app.include_router(job_dashboard.router)
app.include_router(timeline_router)

RETRY_QUEUE_PATH = "retry_queue.json"

def start_background_jobs():
    jobs = get_all_job_names()
    for job in jobs:
        t = threading.Thread(target=run_job_periodically, args=(job,), daemon=True)
        t.start()
        print(f"[AUTO] Launched background thread for {job}")

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

@app.on_event("startup")
async def startup_event():
    start_background_jobs()

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

# 🧠 This should be at the bottom
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
