import threading
import time
import traceback
import os
from datetime import datetime
from run_job_once import run_job_once
from src.job_loader import get_all_job_names
from src.processing.utils import load_json

def run_job_periodically(job_name):
    while True:
        try:
            config_path = f"jobs/{job_name}/config.json"
            if not os.path.exists(config_path):
                print(f"[AUTO] Config not found for {job_name}. Skipping.")
                time.sleep(30)
                continue

            config = load_json(config_path)
            if config.get("paused"):
                print(f"[AUTO] {job_name} is paused.")
                time.sleep(30)
                continue

            print(f"[AUTO] Running job: {job_name}")
            print(f"[AUTO-RUN] {job_name} ran at {datetime.now().isoformat()}")
            result = run_job_once(job_name, test_mode=config.get("test_mode", False))

            if result:
                print(f"[AUTO] {job_name} completed. Tasks: {len(result.get('tasks', []))}")
            else:
                print(f"[AUTO] {job_name} returned no result.")

        except Exception as e:
            print(f"[AUTO] Error in {job_name}: {e}")
            traceback.print_exc()

        time.sleep(60)

def start_background_jobs():
    jobs = get_all_job_names()
    for job in jobs:
        t = threading.Thread(target=run_job_periodically, args=(job,), daemon=True)
        t.start()
        print(f"[AUTO] Launched background thread for {job}")

if os.getenv("RUN_MAIN") == "true":
    print("[AUTO-SCHEDULER] Starting background jobs...")
    start_background_jobs()
