# test_task_extractor.py

from src.processing.task_extractor import extract_tasks

sample_summary = """
We had a meeting with the Finance Team to discuss the Q2 report. 
Anna will prepare the draft by May 28. 
Johan should schedule the stakeholder review for early June. 
We also agreed to notify HR about the new intern starting on June 5.
"""

tasks = extract_tasks(sample_summary)

print("\n[EXTRACTED TASKS]")
for i, task in enumerate(tasks, 1):
    print(f"\nTask {i}:")
    for key, value in task.items():
        print(f"  {key}: {value}")
