# dashboard/tiles/job_status.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os
import json

router = APIRouter()

JOBS_DIR = "jobs"

@router.get("/api/tiles/job-status", response_class=JSONResponse)
async def job_status_tile():
    job_data = []

    for job_name in os.listdir(JOBS_DIR):
        job_path = os.path.join(JOBS_DIR, job_name)
        status_path = os.path.join(job_path, "status.json")

        if not os.path.isdir(job_path) or not os.path.exists(status_path):
            continue

        with open(status_path, "r") as f:
            try:
                status = json.load(f)
                job_data.append({
                    "name": job_name,
                    "last_run": status.get("last_run"),
                    "status": status.get("status"),
                    "duration": status.get("duration"),
                    "message": status.get("message")
                })
            except Exception as e:
                job_data.append({
                    "name": job_name,
                    "status": "error",
                    "message": f"Failed to read status.json: {e}"
                })

    return job_data
