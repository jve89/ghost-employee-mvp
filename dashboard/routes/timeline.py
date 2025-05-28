# dashboard/tiles/timeline.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os
import json

router = APIRouter()

@router.get("/api/tiles/timeline", response_class=JSONResponse)
async def timeline_tile():
    path = "jobs/vendor_assistant/output/summary_log.json"

    if not os.path.exists(path):
        return {"entries": []}

    try:
        with open(path, "r") as f:
            data = json.load(f)
        # Return the 10 most recent entries (newest first)
        recent = sorted(data, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
        return {"entries": recent}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/api/log/{job}/{timestamp}")
async def get_log_for_entry(job: str, timestamp: str):
    log_path = f"jobs/{job}/output/summary_log.json"
    if not os.path.exists(log_path):
        return JSONResponse(content={"log": "No log file found."}, status_code=404)

    with open(log_path) as f:
        try:
            logs = json.load(f)
            match = next((entry for entry in logs if entry.get("timestamp", "").startswith(timestamp)), None)
            if match:
                return {"log": json.dumps(match, indent=2)}
            return JSONResponse(content={"log": "No matching entry."}, status_code=404)
        except Exception as e:
            return JSONResponse(content={"log": str(e)}, status_code=500)
