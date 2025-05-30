# /src/controller.py

from src.processing.task_extractor import extract_tasks
from src.processing.task_executor import execute_task
from src.outputs.export_manager import export_task
from src.outputs.log_manager import log_task_result
from datetime import datetime
import os
import shutil

PROCESSED_DIR = "executed"

def move_to_processed(file_path):
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    filename = os.path.basename(file_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"{timestamp}_{filename}"
    new_path = os.path.join(PROCESSED_DIR, new_filename)

    try:
        shutil.move(file_path, new_path)
        print(f"[Controller] Done processing {file_path}, moved to {new_path}")
    except Exception as e:
        print(f"[Controller] ⚠️ Failed to move file '{file_path}' → '{new_path}': {e}")


def process_file(file_path: str):
    print(f"[Controller] Processing file: {file_path}")
    tasks = extract_tasks(file_path)

    if not tasks:
        print(f"[Controller] No tasks found in file: {file_path}")
        return

    for task in tasks:
        print(f"[Controller] Processing task: {task.get('title')}")
        
        # 1. Execute task logic (automated simulation or real)
        result = execute_task(task)

        # 2. Export to Notion, Sheets, etc.
        export_task(task)

        # 3. (Optional) Log or update dashboard in future
        log_task_result(task, result)

    # ✅ Move file and log after all tasks are done
    move_to_processed(file_path)

