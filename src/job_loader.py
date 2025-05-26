# /src/job_loader.py
import json
import os

JOBS_REGISTRY = "jobs.json"

def load_jobs():
    if not os.path.exists(JOBS_REGISTRY):
        raise FileNotFoundError(f"jobs.json not found at path: {JOBS_REGISTRY}")
    
    with open(JOBS_REGISTRY, "r") as f:
        return json.load(f)
