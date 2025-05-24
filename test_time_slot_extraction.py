from src.processing.task_extractor import extract_tasks
import os
from dotenv import load_dotenv

load_dotenv()

sample_summary = """
- Finalise the presentation by next Friday at 2 PM.
- Schedule the leadership sync for Monday morning.
- Inform the HR team about the intern starting June 1st.
"""

tasks = extract_tasks(sample_summary)

print("\n[EXTRACTED TASKS WITH DUE DATES AND TIME SLOTS]\n")

for idx, task in enumerate(tasks, 1):
    print(f"Task {idx}:")
    for key, value in task.items():
        print(f"  {key}: {value}")
    print()
