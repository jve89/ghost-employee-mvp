# /src/processing/structured_saver.py

import os
import json
from datetime import datetime
from src.processing.template_filler import fill_template
from src.inputs.attachment_processor import process_attachments
from src.processing.utils import group_tasks_by_source  # ✅ NEW

def pick_template(summary_text, default_template="templates/sample_template.docx"):
    summary_lower = summary_text.lower()
    template_map = {
        "finance": "templates/finance_template.docx",
        "meeting": "templates/meeting_template.docx",
        "hr": "templates/hr_template.docx",
    }

    for keyword, template_path in template_map.items():
        if keyword in summary_lower and os.path.exists(template_path):
            return template_path

    return default_template


def save_structured_summary(summary_data, tasks, alerts, attachments=None, email_subject="No Subject", email_from="unknown@example.com"):
    timestamp = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
    json_filename = f"logs/{timestamp}_summary.json"
    os.makedirs("logs", exist_ok=True)
    os.makedirs("summaries", exist_ok=True)

    # 🧠 Parse attachments first
    if attachments:
        attachment_tasks = process_attachments(attachments)
    else:
        attachment_tasks = []

    # ✅ Initialise task list
    tasks = tasks + attachment_tasks

    # ✳️ Enrich task objects for audit/export
    enriched_tasks = []
    for task in tasks:
        source = task.get("source_file", "manual")
        task["context"] = task.get("context") or f"Grouped via: {source}"
        enriched_tasks.append({
            "title": task.get("title") or task.get("description", ""),
            "description": task.get("description", ""),
            "due_date": task.get("due_date"),
            "time_slot": task.get("time_slot"),
            "time_slot_source": task.get("time_slot_source"),
            "time_slot_confidence": task.get("time_slot_confidence"),
            "priority": task.get("priority"),
            "assigned_to": task.get("assigned_to"),
            "assigned_user": task.get("assigned_user", {}),
            "context": task["context"],
            "source_file": source
        })

    grouped_tasks = group_tasks_by_source(enriched_tasks)

    structured_data = {
        "timestamp": timestamp,
        "summary": summary_data,
        "tasks": enriched_tasks,
        "alerts": alerts,
        "grouped_by_source": grouped_tasks  # ✅ NEW SECTION
    }

    if attachments:
        structured_data["attachments"] = attachments

    # 💾 Save JSON
    with open(json_filename, "w") as f:
        json.dump(structured_data, f, indent=4, ensure_ascii=False)
    print(f"[STRUCTURED SUMMARY SAVED] {json_filename}")

    # 📄 Generate document
    try:
        context = {
            "ClientName": email_from.split("@")[0].capitalize(),
            "Date": timestamp.split("_")[0],
            "Summary": summary_data,
            "TaskCount": len(tasks),
            "AlertCount": len(alerts) if alerts else 0,
            "EmailSubject": email_subject,
            "FirstTaskTitle": tasks[0].get("title") if tasks else "N/A",
            "FirstTaskDue": tasks[0].get("due_date") if tasks else "TBD",
            "AttachmentCount": len(attachments) if attachments else 0
        }

        chosen_template = pick_template(summary_data)
        fill_template(chosen_template, context)
    except Exception as e:
        print(f"[WARN] Template not filled: {e}")

    # ✅ Run task executor
    try:
        from src.processing.task_executor import execute_tasks_from_log
        execute_tasks_from_log(json_filename)
    except Exception as e:
        print(f"[ERROR] Task execution failed: {e}")
