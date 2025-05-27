# workforce_engine.py

import os
import json
import time
from datetime import datetime
from src.core_runner import run_job_for_folder

JOBS_DIR = "jobs"
SLEEP_INTERVAL = 60 * 15  # every 15 min
OFFICE_HOURS_ONLY = True

def load_all_jobs():
    return [
        os.path.join(JOBS_DIR, name)
        for name in os.listdir(JOBS_DIR)
        if os.path.isdir(os.path.join(JOBS_DIR, name))
    ]

def is_within_office_hours():
    now = datetime.now()
    return now.weekday() < 5 and 9 <= now.hour < 17  # Mon–Fri, 9am–5pm

def write_status(job_path, status, duration=None, message=None):
    status_path = os.path.join(job_path, "status.json")
    status_data = {
        "last_run": datetime.now().isoformat(),
        "status": status,
        "duration": duration,
        "message": message or ""
    }
    with open(status_path, "w") as f:
        json.dump(status_data, f, indent=2)

def run_all_jobs():
    print(f"[WORKFORCE] ⏰ Checking jobs at {datetime.now().strftime('%H:%M:%S')}")
    job_paths = load_all_jobs()

    for path in job_paths:
        config_path = os.path.join(path, "config.json")
        if not os.path.exists(config_path):
            print(f"[SKIP] No config.json in {path}")
            write_status(path, "skipped", message="No config.json")
            continue

        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            if config.get("test_mode", False):
                print(f"[TEST MODE] Skipping job: {config['job_name']}")
                write_status(path, "test_mode", message="Test mode enabled")
                continue

            if config.get("paused", False):
                print(f"[SKIP] Job is paused: {config['job_name']}")
                continue

            print(f"[WORKFORCE] ▶️ Running job: {config['job_name']}")
            start = time.time()
            run_job_for_folder(path)
            duration = round(time.time() - start, 2)
            write_status(path, "success", duration)

        except Exception as e:
            duration = round(time.time() - start, 2)
            print(f"[ERROR] Job '{path}' failed: {e}")
            write_status(path, "error", duration, message=str(e))

def main_loop():
    print("[WORKFORCE] 👻 Ghost Employee Workforce Engine Started")
    while True:
        if OFFICE_HOURS_ONLY and not is_within_office_hours():
            print("[WORKFORCE] 💤 Outside office hours. Sleeping...")
        else:
            run_all_jobs()

        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main_loop()
