import json
import os
from src.inputs.file_monitor import get_new_files
from src.processing.summary_analyser import summarise_file
from src.processing.task_extractor import extract_tasks
from src.processing.due_date_extractor import recognise_due_dates
from src.processing.task_executor import execute_tasks
from src.outputs.log_manager import log_task_result
from src.outputs.export_manager import export_to_targets
from retry_worker import handle_retries

def run_job_for_folder(job_path):
    config_path = os.path.join(job_path, "config.json")
    if not os.path.exists(config_path):
        print(f"[SKIP] No config.json in {job_path}")
        return

    with open(config_path, "r") as f:
        config = json.load(f)

    input_folder = config.get("watch_folder")
    new_files = get_new_files(input_folder)
    if not new_files:
        print(f"[{config['job_name']}] No new files.")
        return

    print(f"[{config['job_name']}] Processing {len(new_files)} file(s)...")

    for file in new_files:
        summary, tasks = summarise_file(file)
        tasks = recognise_due_dates(tasks)

        export_results = export_to_targets(tasks, config["export_targets"])
        execute_tasks(tasks)  # Removed export_targets from here

        # ✅ Log each task and result separately
        for task, result in zip(tasks, export_results):
            log_task_result(task, result)

        handle_retries(config["retry_queue_path"], tasks, export_results)
