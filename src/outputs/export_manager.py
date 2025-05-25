# src/outputs/export_manager.py

import yaml
import os
from src.outputs import notion_exporter, sheets_exporter

# Load config once
CONFIG_PATH = "config.yaml"
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        CONFIG = yaml.safe_load(f)
else:
    CONFIG = {}

# Define priority order for comparison
PRIORITY_ORDER = {"Low": 1, "Medium": 2, "High": 3}


def passes_filters(task: dict) -> bool:
    filters = CONFIG.get("export", {}).get("filters", {})
    min_priority = filters.get("min_priority", "Low")
    allowed_tags = filters.get("allowed_tags", [])
    excluded_users = filters.get("exclude_assigned_to", [])

    task_priority = task.get("priority", "Low")
    task_tags = task.get("tags", [])
    assigned_to = task.get("assigned_to", "")

    # Check priority threshold
    if PRIORITY_ORDER.get(task_priority, 1) < PRIORITY_ORDER.get(min_priority, 1):
        return False

    # If tags are required, task must have at least one allowed
    if allowed_tags and not any(tag in allowed_tags for tag in task_tags):
        return False

    # Exclude based on assigned user
    if assigned_to in excluded_users:
        return False

    return True


def export_task(task: dict):
    enabled_targets = CONFIG.get("export", {}).get("enabled_targets", [])

    if not passes_filters(task):
        print(f"[EXPORT MANAGER] ❌ Task did not pass export filters: {task}")
        return

    print(f"[EXPORT MANAGER] ✅ Exporting task to: {enabled_targets}")

    if "notion" in enabled_targets:
        notion_exporter.export_to_notion(task)

    if "sheets" in enabled_targets:
        sheets_exporter.export_to_sheets(task)
