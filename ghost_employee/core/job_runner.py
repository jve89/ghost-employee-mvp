# src/job_runner.py

from ghost_employee.core_runner import run_job_for_folder
import os

def run_job_once(job_name, test_mode=False):
    job_path = os.path.join("jobs", job_name)
    return run_job_for_folder(job_path, test_mode=test_mode)
