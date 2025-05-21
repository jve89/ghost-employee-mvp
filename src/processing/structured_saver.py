# /processing/structured_saver.py

import os
import json
from datetime import datetime
from src.processing.template_filler import fill_template


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

    structured_data = {
        "timestamp": timestamp,
        "summary": summary_data,
        "tasks": tasks,
        "alerts": alerts,
    }

    if attachments:
        structured_data["attachments"] = attachments

    # Save structured summary as JSON
    with open(json_filename, "w") as f:
        json.dump(structured_data, f, indent=4)
    print(f"[STRUCTURED SUMMARY SAVED] {json_filename}")

    # 📄 Build context using real data
    try:
        context = {
            "ClientName": email_from.split("@")[0].capitalize(),
            "Date": timestamp.split("_")[0],
            "Summary": summary_data,
            "TaskCount": len(tasks),
            "AlertCount": len(alerts) if alerts else 0,
            "EmailSubject": email_subject,
            "FirstTaskTitle": tasks[0] if tasks else "N/A",
            "FirstTaskDue": "TBD",  # Future: parse real due dates
            "AttachmentCount": len(attachments) if attachments else 0
        }

        chosen_template = pick_template(summary_data)
        fill_template(chosen_template, context)
    except Exception as e:
        print(f"[WARN] Template not filled: {e}")
