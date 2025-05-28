from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os
import json

router = APIRouter()

@router.get("/api/job-summaries/{job_folder}", response_class=JSONResponse)
async def get_structured_summaries(job_folder: str):
    path = f"jobs/{job_folder}/output/export_log.json"

    if not os.path.exists(path):
        return []
 
    with open(path, "r") as f:
        try:
            data = json.load(f)
            summaries = [
                {
                    "summary": item.get("summary"),
                    "tasks": item.get("tasks", [])
                }
                for item in data if "summary" in item
            ]
            return summaries
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)
