# /dashboard/add_job_ui.py

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import os, json
from pathlib import Path

router = APIRouter()

JOBS_DIR = "jobs"
JOBS_INDEX_PATH = os.path.join(JOBS_DIR, "jobs.json")

@router.get("/add-job", response_class=HTMLResponse)
async def add_job_form():
    return """
    <html>
        <head><title>Add New Job</title></head>
        <body>
            <h2>Create New Job</h2>
            <form action="/add-job" method="post">
                Job Name: <input type="text" name="job_name"><br>
                Summary Prompt: <input type="text" name="summary_prompt" value="Summarise this file and extract tasks."><br>
                Export Targets (comma-separated): <input type="text" name="export_targets" value="sheets"><br>
                Task Rule Keywords (comma-separated): <input type="text" name="task_keywords" value="update, notify, assign"><br>
                <input type="submit" value="Create Job">
            </form>
        </body>
    </html>
    """

@router.post("/add-job")
async def create_job(
    job_name: str = Form(...),
    summary_prompt: str = Form(...),
    export_targets: str = Form(...),
    task_keywords: str = Form(...)
):
    job_path = os.path.join(JOBS_DIR, job_name)
    input_dir = os.path.join(job_path, "input")
    output_dir = os.path.join(job_path, "output")
    task_templates_dir = os.path.join(job_path, "task_templates")

    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(task_templates_dir, exist_ok=True)

    config = {
        "job_name": job_name,
        "summary_prompt": summary_prompt,
        "watch_folder": input_dir,
        "output_log_path": os.path.join(output_dir, "export_log.json"),
        "retry_queue_path": os.path.join(output_dir, "retry_queue.json"),
        "export_targets": [x.strip() for x in export_targets.split(",")],
        "task_extractor_rules": [x.strip() for x in task_keywords.split(",")]
    }

    with open(os.path.join(job_path, "config.json"), "w") as f:
        json.dump(config, f, indent=2)

    # Update jobs.json index
    jobs_index = []
    if Path(JOBS_INDEX_PATH).exists():
        with open(JOBS_INDEX_PATH, "r") as f:
            try:
                jobs_index = json.load(f)
            except:
                pass
    if job_name not in jobs_index:
        jobs_index.append(job_name)
        with open(JOBS_INDEX_PATH, "w") as f:
            json.dump(jobs_index, f, indent=2)

    return RedirectResponse(url="/add-job", status_code=303)
