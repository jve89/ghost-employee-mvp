# /jobs/vendor_assistant/main_job_runner.py

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.job_loader import load_jobs
from src.core_runner import run_job_for_folder

jobs = load_jobs()

for job in jobs:
    print(f"[RUNNER] Running job: {job['name']}")
    run_job_for_folder(job["path"])
