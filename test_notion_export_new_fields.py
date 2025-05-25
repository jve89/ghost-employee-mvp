# test_notion_export_new_fields.py

import os
from dotenv import load_dotenv
from src.outputs.notion_exporter import export_to_notion

load_dotenv()

test_task = {
    "title": "Review new onboarding checklist",
    "description": "Make sure the updated onboarding flow is reviewed and signed off",
    "due_date": "2025-06-10",
    "time_slot": "2025-06-05T10:00:00+02:00",
    "time_slot_source": "GPT",
    "time_slot_confidence": "Medium",
    "priority": "High",
    "assigned_to": "HR",  # This will trigger proper lookup now
    "source_file": "onboarding_notes.docx",
    "context": "This came from the HR team’s PDF notes"
}

export_to_notion(test_task)
print("✅ Test task pushed to Notion. Please verify fields in the database UI.")
