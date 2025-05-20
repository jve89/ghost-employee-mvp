import os
import json
from datetime import datetime
from openai import OpenAI
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

# Init OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

    matched = False

    def maybe_run(fn, *args):
        if is_real:
            result = fn(*args)
        else:
            print(f"[SIMULATED] Would run: {fn.__name__} with args: {args}")
            result = f"SIMULATED_{fn.__name__.upper()}"
        return result

    # 🔍 Static keyword matching
    if "jira" in task_lower or "ticket" in task_lower:
        result = maybe_run(create_jira_ticket, task)
        matched = True
    elif "spreadsheet" in task_lower or "google sheet" in task_lower or "excel" in task_lower:
        result = maybe_run(update_google_sheet, task)
        matched = True
    elif "clickup" in task_lower or "assign task" in task_lower:
        result = maybe_run(assign_task_in_clickup, task)
        matched = True
    elif "hr" in task_lower and "notify" in task_lower:
        result = maybe_run(email_hr, "HR Notification", description)
        matched = True
    elif "schedule" in task_lower and "meeting" in task_lower:
        result = maybe_run(create_calendar_event_flexible, task)
        matched = True
    elif "slack" in task_lower:
        result = maybe_run(send_slack_message, "Supervisor", description)
        matched = True
    elif "crm" in task_lower or "log" in task_lower:
        result = maybe_run(update_crm_case, "CASE123", description)
        matched = True
    elif "supervisor" in task_lower:
        result = maybe_run(email_supervisor, "Update", description)
        matched = True

    # 🧠 GPT fallback if no static match found
    if not matched:
        result = run_gpt_fallback(description, is_real)

    return {
        "task": description,
        "result": result,
        "mode": "REAL" if is_real else "SIMULATED",
        "source_file": source_file,
        "timestamp": datetime.utcnow().isoformat()
    }


def run_gpt_fallback(task_description, is_real):
    prompt = f"""The following is a workplace task:
\"\"\"{task_description}\"\"\"
Classify it into one of the known actions:
- send_slack_message
- update_crm_case
- create_calendar_event
- email_supervisor
- create_jira_ticket
- update_google_sheet
- assign_task_in_clickup
- email_hr

Reply ONLY with the matching function name.
If none fits, say 'fallback_action'."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        action = response.choices[0].message.content.strip()
        print(f"[GPT-FALLBACK] GPT classified: {action}")

        fn_map = {
            "send_slack_message": send_slack_message,
            "update_crm_case": update_crm_case,
            "create_calendar_event": create_calendar_event,
            "email_supervisor": email_supervisor,
            "create_jira_ticket": create_jira_ticket,
            "update_google_sheet": update_google_sheet,
            "assign_task_in_clickup": assign_task_in_clickup,
            "email_hr": email_hr,
            "fallback_action": fallback_action
        }

        fn = fn_map.get(action, fallback_action)

        if is_real:
            return fn(task_description)
        else:
            print(f"[GPT-FALLBACK] Would run: {action} with '{task_description}'")
            return f"SIMULATED_GPT_{action.upper()}"

    except Exception as e:
        print(f"[GPT-FALLBACK ERROR] {e}")
        return "GPT_FALLBACK_FAILED"


def save_execution_result(result):
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"executed/exec_{ts}.json"
    try:
        with open(filename, "w") as f:
            json.dump(result, f, indent=2)
        print(f"[EXECUTED] Logged to {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to log execution result: {e}")
