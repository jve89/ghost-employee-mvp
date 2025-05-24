import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from processing.task_extractor import extract_tasks

test_summary = """
Clara will lead the Q3 presentation next Wednesday at 2 PM. Please inform HR about the new intern who starts June 5th. 
Also, Anna should schedule the stakeholder meeting on Monday morning.
"""

tasks = extract_tasks(test_summary)

print("\n[EXTRACTED TASKS WITH USER MAPPING]\n")
for i, task in enumerate(tasks, 1):
    print(f"Task {i}:")
    for k, v in task.items():
        print(f"  {k}: {v}")
    print()
