from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
import os

router = APIRouter()
JOBS_DIR = "jobs"

@router.get("/api/job-log/{job_folder}", response_class=PlainTextResponse)
async def read_job_log(job_folder: str):
    log_path = os.path.join(JOBS_DIR, job_folder, "log.txt")
    if not os.path.exists(log_path):
        return "No logs found."
    with open(log_path, "r") as f:
        return f.read()
