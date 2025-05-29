# test_notion_export.py

import os
from dotenv import load_dotenv
from src.outputs.notion_exporter import push_to_notion

load_dotenv()

sample_tasks = [
    {
        "title": "Test Task from Ghost Employee",
        "description": "This is a test to validate Notion export.",
        "due_date": "2025-05-28",
        "assigned_to": "John Tester",
        "priority": "High",
        "time_slot": "Afternoon"
    }
]

push_to_notion(os.getenv("NOTION_DATABASE_ID"), sample_tasks)
