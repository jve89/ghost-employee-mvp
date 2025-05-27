# dashboard/job_config_api.py

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
import os, json

router = APIRouter()
JOBS_DIR = "jobs"

@router.get("/api/job-config/{folder}", response_class=JSONResponse)
async def get_job_config(folder: str):
    config_path = os.path.join(JOBS_DIR, folder, "config.json")
    if not os.path.exists(config_path):
        return JSONResponse(content={"error": "Config not found"}, status_code=404)
    with open(config_path) as f:
        return json.load(f)

@router.post("/api/job-config/{folder}")
async def update_job_config(folder: str, config_text: str = Form(...)):
    config_path = os.path.join(JOBS_DIR, folder, "config.json")
    try:
        config = json.loads(config_text)
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        return {"status": "ok"}
    except Exception as e:
        return {"error": str(e)}
