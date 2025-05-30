import json
import os
from datetime import datetime
from ghost_employee.inputs.file_monitor import get_new_files
from ghost_employee.ai_modules.summary_analyser import summarise_file, tag_summary
from ghost_employee.ai_modules.task_extractor import extract_tasks
from ghost_employee.ai_modules.due_date_extractor import recognise_due_dates
from ghost_employee.ai_modules.task_executor import execute_tasks
from ghost_employee.outputs.log_manager import log_task_result
from ghost_employee.outputs.export_manager import export_to_targets
from ghost_employee.outputs.job_alerts import maybe_alert_on_failure
from ghost_employee.retry.retry_worker import handle_retries


def run_job_for_folder(folder, test_mode=False):
    config_path = os.path.join(folder, "config.json")
    status_path = os.path.join(folder, "status.json")
    log_path = os.path.join(folder, "log.txt")
    summary_log_path = os.path.join(folder, "output", "summary_log.json")

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
            try:
                summary, tasks = summarise_file(file)
                tag, tag_icon = tag_summary(summary)
                tasks = recognise_due_dates(tasks)
                tasks = extract_tasks(summary)

                export_results = export_to_targets(tasks, config["export_targets"])
                execute_tasks(tasks)

                for task, result in zip(tasks, export_results):
                    log_task_result(task, result)

                handle_retries(config["retry_queue_path"], tasks, export_results)
                all_export_results.extend(export_results)

                structured_summary = {
                    "timestamp": datetime.now().isoformat(),
                    "filename": os.path.basename(file),
                    "summary": summary,
                    "tasks": tasks,
                    "tag": tag,
                    "tag_icon": tag_icon
                }

                summary_data.append(structured_summary)
                print("[DEBUG] Structured summary appended:")
                print(json.dumps(structured_summary, indent=2))
                print(f"[DEBUG] Added summary for {file} with tag {tag_icon} {tag}")
                print(f"[DEBUG] summary_data content: {json.dumps(summary_data, indent=2)}")

            except Exception as e:
                log(f"[ERROR] Failed to process file {file}: {str(e)}")
                print(f"[DEBUG] Skipped file {file} due to error: {str(e)}")

        # 🔐 Only write summary_log.json if there's something to write
        if summary_data:
            os.makedirs(os.path.dirname(summary_log_path), exist_ok=True)

            if os.path.exists(summary_log_path):
                try:
                    with open(summary_log_path, "r") as f:
                        existing = json.load(f)
                except:
                    existing = []
            else:
                existing = []

            combined = existing + summary_data

            print(f"[DEBUG] Writing summary_log.json with {len(summary_data)} new entries")
            print(f"[DEBUG] Final path: {summary_log_path}")

            with open(summary_log_path, "w") as f:
                json.dump(combined[-50:], f, indent=2)
        else:
            print("[DEBUG] No summary_data to write — skipping summary_log.json")

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
