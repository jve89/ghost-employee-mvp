import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.core_runner import run_job_for_folder  # ✅ now it will work

JOBS_PATH = "jobs"

for job in os.listdir(JOBS_PATH):
    job_path = os.path.join(JOBS_PATH, job)
    if os.path.isdir(job_path):
        run_job_for_folder(job_path)
