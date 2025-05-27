# dashboard/tiles/job_stats.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os
import json
import time

router = APIRouter()

@router.get("/api/job-stats/{job_folder}", response_class=JSONResponse)
async def job_stats(job_folder: str):
    retry_path = f"jobs/{job_folder}/output/retry_queue.json"
    export_log_path = f"jobs/{job_folder}/output/export_log.json"

    stats = {
        "total_exports": 0,
        "successful_exports": 0,
        "failed_exports": 0,
        "retry_queue_length": 0,
        "retry_queue_age": 0
    }

    if os.path.exists(export_log_path):
        try:
            with open(export_log_path, "r") as f:
                exports = json.load(f)
                stats["total_exports"] = len(exports)
                for entry in exports:
                    if entry.get("status") == "success":
                        stats["successful_exports"] += 1
                    else:
                        stats["failed_exports"] += 1
        except Exception:
            pass

    if os.path.exists(retry_path):
        try:
            with open(retry_path, "r") as f:
                queue = json.load(f)
                stats["retry_queue_length"] = len(queue)
                if queue:
                    oldest = min(entry.get("last_attempt", time.time()) or time.time() for entry in queue)
                    stats["retry_queue_age"] = round(time.time() - oldest, 1)
        except Exception:
            pass

    return stats
