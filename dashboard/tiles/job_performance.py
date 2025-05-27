# dashboard/tiles/job_performance.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os
import json
from datetime import datetime

router = APIRouter()

@router.get("/api/job-performance/{job_folder}", response_class=JSONResponse)
async def job_performance_data(job_folder: str):
    path = f"jobs/{job_folder}/output/export_log.json"
    if not os.path.exists(path):
        return {"timestamps": [], "success": [], "fail": []}

    try:
        with open(path) as f:
            log = json.load(f)
    except Exception:
        return {"timestamps": [], "success": [], "fail": []}

    buckets = {}  # Format: {"2025-05-27 15:00": {"success": 2, "fail": 1}}

    for entry in log:
        ts = datetime.fromtimestamp(entry.get("timestamp", 0))
        key = ts.strftime("%Y-%m-%d %H:00")  # Hourly grouping
        success = entry.get("result", "") == "success"

        if key not in buckets:
            buckets[key] = {"success": 0, "fail": 0}
        buckets[key]["success" if success else "fail"] += 1

    timestamps = sorted(buckets)
    success_data = [buckets[t]["success"] for t in timestamps]
    fail_data = [buckets[t]["fail"] for t in timestamps]

    return {
        "timestamps": timestamps,
        "success": success_data,
        "fail": fail_data
    }
