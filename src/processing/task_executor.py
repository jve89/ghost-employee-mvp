import os
import json
from datetime import datetime
from .actions import (
    send_slack_message,
    update_crm_case,
    create_calendar_event,
    email_supervisor,
    fallback_action,
    create_jira_ticket,
    update_google_sheet,
    assign_task_in_clickup,
    email_hr,
    create_calendar_event_flexible,
)

# Ensure /executed/ folder exists
os.makedirs("executed", exist_ok=True)

def execute_tasks_from_log(log_path):
    print(f"[TASK EXECUTOR] Processing structured log: {log_path}")

    try:
        with open(log_path, 'r') as f:
            data = json.load(f)
            tasks = data.get("tasks", [])

            if not tasks:
                print("[TASK EXECUTOR] No tasks found in log.")
                return

            for task in tasks:
                result = execute_task(task, source_file=os.path.basename(log_path))
                save_execution_result(result)

    except Exception as e:
        print(f"[ERROR] Failed to execute tasks from {log_path}: {e}")

def execute_task(task, source_file=None):
    description = task if isinstance(task, str) else task.get("description", "")
    task_lower = description.lower()
    is_real = os.getenv("REAL_EXECUTION", "off") == "on"

    def maybe_run(fn, *args):
        if is_real:
            result = fn(*args)
        else:
            print(f"[SIMULATED] Would run: {fn.__name__} with args: {args}")
            result = f"SIMULATED_{fn.__name__.upper()}"
        return result

    if "jira" in task_lower or "ticket" in task_lower:
        result = maybe_run(create_jira_ticket, task)

    elif "spreadsheet" in task_lower or "google sheet" in task_lower:
        result = maybe_run(update_google_sheet, task)

    elif "clickup" in task_lower or "assign task" in task_lower:
        result = maybe_run(assign_task_in_clickup, task)

    elif "hr" in task_lower and "notify" in task_lower:
        result = maybe_run(email_hr, "HR Notification", description)

    elif "schedule" in task_lower and "meeting" in task_lower:
        result = maybe_run(create_calendar_event_flexible, task)

    elif "slack" in task_lower:
        result = maybe_run(send_slack_message, "Supervisor", description)

    elif "crm" in task_lower or "log" in task_lower:
        result = maybe_run(update_crm_case, "CASE123", description)

    elif "supervisor" in task_lower:
        result = maybe_run(email_supervisor, "Update", description)

    else:
        result = maybe_run(fallback_action, description)

    return {
        "task": description,
        "result": result,
        "mode": "REAL" if is_real else "SIMULATED",
        "source_file": source_file,
        "timestamp": datetime.utcnow().isoformat()
    }

def save_execution_result(result):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"executed/exec_{ts}.json"
    try:
        with open(filename, "w") as f:
            json.dump(result, f, indent=2)
        print(f"[EXECUTED] Logged to {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to log execution result: {e}")
