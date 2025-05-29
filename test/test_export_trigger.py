# test_export_trigger.py

from src.outputs.export_manager import export_task

# Sample task to test full export path
sample_task = {
    "title": "Prepare Q2 financial report",
    "description": "Update and finalise the quarterly financials.",
    "priority": "High",
    "tags": ["finance"],
    "assigned_to": "Finance Team",
    "due_date": "2025-06-01",
    "time_slot": "2025-06-30T17:00:00"
}

export_task(sample_task)
