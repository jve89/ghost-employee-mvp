# /src/inputs/attachment_processor.py

import os
from ghost_employee.inputs.file_parser import parse_attachment
from ghost_employee.ai_modules.task_extractor import extract_tasks
from ghost_employee.inputs.archiver import archive_attachment

def process_attachments(attachment_paths):
    """
    Process a list of file paths. Extract tasks from each valid attachment.
    Returns a flat list of enriched tasks.
    """
    all_tasks = []

    for file_path in attachment_paths:
        if not os.path.exists(file_path):
            print(f"[SKIPPED] File not found: {file_path}")
            continue

        print(f"🔍 Processing attachment: {file_path}")
        text_or_tasks = parse_attachment(file_path)

        # CASE 1: Excel returns a list of dicts directly
        if isinstance(text_or_tasks, list):
            for task in text_or_tasks:
                task["source_file"] = os.path.basename(file_path)
            all_tasks.extend(task for task in text_or_tasks if task.get("description"))
            archive_attachment(file_path)

        # CASE 2: Text from DOCX/PDF
        elif isinstance(text_or_tasks, str) and len(text_or_tasks.strip()) >= 30:
            tasks = extract_tasks(text_or_tasks)
            for task in tasks:
                task["source_file"] = os.path.basename(file_path)
            all_tasks.extend(tasks)
            archive_attachment(file_path)

        else:
            print(f"[SKIPPED] Attachment too short or unprocessable: {file_path}")

    print(f"[ATTACHMENT] ✅ Extracted {len(all_tasks)} task(s) from attachments.")
    return all_tasks
