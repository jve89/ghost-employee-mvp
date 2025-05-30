import os
import json
from datetime import datetime
from openai import OpenAI
from ghost_employee.ai_modules.role_inferencer import infer_role_from_description
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
    send_to_notion
)

# Load role config
with open("config/roles_config.json", "r") as f:
    ROLES_CONFIG = json.load(f)

# Init OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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


def parse_gpt_output(output: str) -> dict:
    try:
        if output.startswith("```"):
            output = output.strip("```").strip()
            if output.startswith("json"):
                output = output[len("json"):].strip()
        task_data = json.loads(output)
        if "action" not in task_data or "details" not in task_data:
            raise ValueError("Missing required keys in GPT output.")
        return task_data
    except Exception as e:
        print(f"[GPT PARSE ERROR] {e} | Raw output: {output}")
        return None


def execute_task(task, source_file=None):
    description = task.get("description", "") if isinstance(task, dict) else str(task)
    title = task.get("title", "Untitled Task") if isinstance(task, dict) else "Untitled Task"
    due_date = task.get("due_date", None)
    assigned_to = task.get("assigned_to", None)
    priority = task.get("priority", "normal")
    assigned_user = {}

    if assigned_to and assigned_to in ROLES_CONFIG:
        assigned_user = ROLES_CONFIG[assigned_to]
        assigned_user["name"] = assigned_to

    task_lower = description.lower()
    
    # 🔍 Try to infer role if none explicitly assigned
    if not assigned_to:
        inferred_role = infer_role_from_description(description)
        if inferred_role and inferred_role in ROLES_CONFIG:
            assigned_to = inferred_role
            assigned_user = ROLES_CONFIG[inferred_role]
            assigned_user["name"] = inferred_role

    is_real = os.getenv("REAL_EXECUTION", "off") == "on"

    matched = False

    def maybe_run(fn, *args, **kwargs):
        if is_real:
            return fn(*args, **kwargs)
        else:
            print(f"[SIMULATED] Would run: {fn.__name__} with args: {args}, kwargs: {kwargs}")
            return f"SIMULATED_{fn.__name__.upper()}"

    # Static match logic
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
        result = maybe_run(send_slack_message, message=description)
        matched = True
    elif "crm" in task_lower or "log" in task_lower:
        result = maybe_run(update_crm_case, "CASE123", description)
        matched = True
    elif "supervisor" in task_lower:
        result = maybe_run(email_supervisor, "Update", description)
        matched = True
    elif "notion" in task_lower or "database" in task_lower:
        result = maybe_run(send_to_notion, task)
        matched = True

    # GPT fallback if no static match
    if not matched:
        result = run_gpt_fallback(description, is_real)

    return {
        "task": {
            "title": title,
            "description": description,
            "due_date": due_date,
            "assigned_to": assigned_to,
            "priority": priority,
            "assigned_user": assigned_user
        },
        "result": result,
        "mode": "REAL" if is_real else "SIMULATED",
        "source_file": source_file,
        "timestamp": datetime.utcnow().isoformat()
    }


def run_gpt_fallback(task_description, is_real):
    # 👥 Inject available roles into the prompt
    assigned_roles = "\n".join(
        [f"- {name}: Slack ID = <@{info.get('slack_id', 'unknown')}>, Channel = #{info.get('slack_channel', 'general')}" 
         for name, info in ROLES_CONFIG.items()]
    )

    prompt = f"""
You are a task execution assistant. Given the task description below, return a JSON object with:
- action: a string (e.g. "send_slack_message", "send_to_notion")
- details: a dictionary with task-specific fields.

Supported actions include:
- send_slack_message: channel, message, mention (Slack user ID only, e.g. "U02RC5WG3HN" — do not wrap in <@...>)
- send_to_notion: title, description, due_date, assigned_to, priority
- email_supervisor, update_crm_case, etc.

Default to "send_to_notion" for generic or unclassified tasks.

Here are the known roles and their details:
{assigned_roles}

Respond in strict JSON only — no markdown, no comments.

Task:
\"\"\"{task_description}\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        raw_output = response.choices[0].message.content if response.choices else "NO_RESPONSE"
        print(f"[GPT-FALLBACK RAW] {raw_output!r}")

        parsed = parse_gpt_output(raw_output)
        if not parsed:
            return "GPT_PARSE_FAILED"

        action = parsed["action"]
        details = parsed["details"]

        if action == "send_slack_message" and not details.get("message"):
            details["message"] = "🧪 Fallback: auto-generated Slack message."

        if action == "send_slack_message" and "mention" in details:
            mention = details["mention"]
            details["message"] = f"<@{mention}> {details['message']}"
            del details["mention"]

        fn_map = {
            "send_slack_message": send_slack_message,
            "update_crm_case": update_crm_case,
            "create_calendar_event": create_calendar_event_flexible,
            "email_supervisor": email_supervisor,
            "create_jira_ticket": create_jira_ticket,
            "update_google_sheet": update_google_sheet,
            "assign_task_in_clickup": assign_task_in_clickup,
            "email_hr": email_hr,
            "fallback_action": fallback_action,
            "send_to_notion": send_to_notion
        }

        fn = fn_map.get(action, fallback_action)
        return fn(**details) if is_real else f"SIMULATED_GPT_{fn.__name__.upper()}"

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


def execute_tasks(tasks):
    results = []
    for task in tasks:
        result = execute_task(task)
        save_execution_result(result)
        results.append(result)
    return results
