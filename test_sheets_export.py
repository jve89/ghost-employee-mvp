from src.outputs.sheets_exporter import push_to_google_sheets

dummy_tasks = [
    {
        "title": "Write test case",
        "description": "Create test data for sheets exporter",
        "due_date": "2025-06-01",
        "assigned_to": "Johan",
        "priority": "High",
        "time_slot": "14:00-16:00",
    }
]

push_to_google_sheets(
    sheet_id="1m6WKFC3Zb1RnYCCddzPWFS-YHEzfrBcQH-j4PklLKWg",
    tasks=dummy_tasks,
    sheet_range="Blad1!A1"
)
