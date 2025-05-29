# test_notion_export_source_file.py

import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv("NOTION_TOKEN"))
NOTION_DB_ID = os.getenv("NOTION_DATABASE_ID")

# Sample task with source_file
test_task = {
    "title": "Demo task for Notion test",
    "description": "This task is created by test_notion_export_source_file.py",
    "due_date": "2025-06-15",
    "assigned_to": "Unassigned",
    "priority": "Medium",
    "time_slot": "2025-06-15T10:00:00",
    "source_file": "demo_attachment.pdf"
}

response = notion.pages.create(
    parent={"database_id": NOTION_DB_ID},
    properties={
        "Title": {
            "title": [
                {
                    "text": {
                        "content": test_task["title"]
                    }
                }
            ]
        },
        "Description": {
            "rich_text": [
                {
                    "text": {
                        "content": test_task["description"]
                    }
                }
            ]
        },
        "Due Date": {
            "date": {
                "start": test_task["due_date"]
            }
        },
        "Priority": {
            "select": {
                "name": test_task["priority"]
            }
        },
        "Time Slot": {
            "rich_text": [
                {
                    "text": {
                        "content": test_task["time_slot"]
                    }
                }
            ]
        },
        "Source File": {
            "rich_text": [
                {
                    "text": {
                        "content": test_task["source_file"]
                    }
                }
            ]
        }
    }
)

print("✅ Test task sent to Notion.")
print("🔗 View it in your Notion DB to verify 'Source File' was set correctly.")
