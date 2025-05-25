# /src/processing/utils.py

from collections import defaultdict

def group_tasks_by_source(tasks):
    """
    Groups a flat list of tasks into a dictionary by source_file.
    """
    grouped = defaultdict(list)
    for task in tasks:
        source = task.get("source_file", "unknown_source")
        grouped[source].append(task)
    return dict(grouped)
