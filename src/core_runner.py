import json
import os
from datetime import datetime
from src.inputs.file_monitor import get_new_files
from src.processing.summary_analyser import summarise_file
from src.processing.task_extractor import extract_tasks
from src.processing.due_date_extractor import recognise_due_dates
from src.processing.task_executor import execute_tasks
from src.outputs.log_manager import log_task_result
from src.outputs.export_manager import export_to_targets
from src.outputs.job_alerts import maybe_alert_on_failure
from retry_worker import handle_retries


def run_job_for_folder(folder_path: str):
    config_path = os.path.join(folder_path, "config.json")
    status_path = os.path.join(folder_path, "status.json")
    log_path = os.path.join(folder_path, "log.txt")
    summary_log_path = os.path.join(folder_path, "output", "summary_log.json")

    def log(msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a") as f:
            f.write(f"[{timestamp}] {msg}\n")

    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        log("🔁 Job execution started")

        input_folder = config.get("watch_folder")
        new_files = get_new_files(input_folder)

        if not new_files:
            log("📂 No new files found.")
            raise Exception("No new files found")

        log(f"📂 Found {len(new_files)} new file(s).")

        all_export_results = []
        summary_data = []

        for file in new_files:
            summary, tasks = summarise_file(file)
            tasks = recognise_due_dates(tasks)
            tasks = extract_tasks(summary, tasks)

            export_results = export_to_targets(tasks, config["export_targets"])
            execute_tasks(tasks)

            for task, result in zip(tasks, export_results):
                log_task_result(task, result)

            handle_retries(config["retry_queue_path"], tasks, export_results)
            all_export_results.extend(export_results)

            # Log structured summary
            summary_data.append({
                "timestamp": datetime.now().isoformat(),
                "filename": os.path.basename(file),
                "summary": summary,
                "tasks": tasks
            })

        # Write structured summary log (last 50 entries)
        if os.path.exists(summary_log_path):
            try:
                with open(summary_log_path, "r") as f:
                    existing = json.load(f)
            except:
                existing = []
        else:
            existing = []

        combined = existing + summary_data
        with open(summary_log_path, "w") as f:
            json.dump(combined[-50:], f, indent=2)

        # Update status
        status = {
            "last_run": datetime.now().isoformat(),
            "status": "success",
            "message": f"Processed {len(new_files)} file(s)",
            "duration": None,
            "failure_count": 0
        }
        with open(status_path, "w") as f:
            json.dump(status, f, indent=2)

        log("✅ Job finished successfully")

    except Exception as e:
        log(f"❌ ERROR: {str(e)}")

        # Load existing status if any
        status = {}
        if os.path.exists(status_path):
            with open(status_path, "r") as f:
                status = json.load(f)

        failures = status.get("failure_count", 0) + 1

        status.update({
            "last_run": datetime.now().isoformat(),
            "status": "error",
            "message": str(e),
            "failure_count": failures
        })

        with open(status_path, "w") as f:
            json.dump(status, f, indent=2)

        maybe_alert_on_failure(config, failures, config.get("job_name", "unknown"))
