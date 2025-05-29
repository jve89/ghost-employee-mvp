# test_due_date_fallback.py

from src.processing.task_extractor import extract_tasks

summary = """
We need to finalise the Q3 presentation by the end of next week.
Also, ask Clara to prepare talking points for the Monday leadership call.
"""

tasks = extract_tasks(summary)

print("\n[RESULT]")
for i, task in enumerate(tasks, 1):
    print(f"\nTask {i}:")
    for k, v in task.items():
        print(f"  {k}: {v}")
