# run_job_once.py

from src.core_runner import run_job_for_folder

def run_job_once(job_name: str, test_mode: bool = False):
    folder = f"jobs/{job_name}"
    return run_job_for_folder(folder, test_mode=test_mode)
