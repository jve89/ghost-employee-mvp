# dashboard/job_manager_api.py

from fastapi import APIRouter
from pathlib import Path
import json
import os
from fastapi import Form
import shutil

router = APIRouter()
JOBS_DIR = "jobs"

@router.get("/api/job-manager")
async def list_jobs():
    job_entries = []
    for job_name in os.listdir(JOBS_DIR):
        job_path = os.path.join(JOBS_DIR, job_name)
        config_path = os.path.join(job_path, "config.json")
        status_path = os.path.join(job_path, "status.json")

        if not os.path.isfile(config_path):
            continue

        with open(config_path, "r") as f:
            config = json.load(f)

        status = {}
        if os.path.exists(status_path):
            with open(status_path, "r") as f:
                status = json.load(f)

        job_entries.append({
            "name": config.get("job_name", job_name),
            "folder": job_name,
            "test_mode": config.get("test_mode", False),
            "last_run": status.get("last_run", "-"),
            "status": status.get("status", "unknown"),
        })

    return {"jobs": job_entries}

@router.post("/api/job-manager/toggle-test")
async def toggle_test_mode(folder: str = Form(...)):
    config_path = os.path.join(JOBS_DIR, folder, "config.json")
    if not os.path.exists(config_path):
        return {"error": "Config not found"}

    with open(config_path, "r") as f:
        config = json.load(f)

    config["test_mode"] = not config.get("test_mode", False)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    return {"status": "ok", "test_mode": config["test_mode"]}

@router.post("/api/job-manager/delete")
async def delete_job(folder: str = Form(...)):
    job_path = os.path.join(JOBS_DIR, folder)
    if not os.path.isdir(job_path):
        return {"error": "Job folder not found"}

    shutil.rmtree(job_path)
    return {"status": "deleted"}

@router.post("/api/job-manager/toggle-pause")
async def toggle_pause(folder: str = Form(...)):
    config_path = os.path.join(JOBS_DIR, folder, "config.json")
    if not os.path.exists(config_path):
        return {"error": "Config not found"}

    with open(config_path, "r") as f:
        config = json.load(f)

    config["paused"] = not config.get("paused", False)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    return {"status": "ok", "paused": config["paused"]}
