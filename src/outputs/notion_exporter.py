# /src/outputs/notion_exporter.py

from notion_client import Client
import os
from src.processing.user_mapper import resolve_assigned_user

notion = Client(auth=os.getenv("NOTION_TOKEN"))

def push_to_notion(database_id, tasks):
    for task in tasks:
        # Always resolve assigned user here to get the full user dict
        assigned_user = resolve_assigned_user(task.get("assigned_to"))

        print(f"[INFO] Pushing task to Notion: {task.get('title')} (Assigned to: {assigned_user})")

        notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": task.get("title", "Untitled Task")
                            }
                        }
                    ]
                },
                "Description": {
                    "rich_text": [
                        {
                            "text": {
                                "content": task.get("description", "")
                            }
                        }
                    ]
                },
                "Due Date": {
                    "date": {
                        "start": task.get("due_date", None)
                    }
                },
                "Assigned To": {
                    "people": [
                        {
                            "object": "user",
                            "id": assigned_user["notion_id"]
                        }
                    ] if assigned_user and assigned_user.get("notion_id") else []
                },
                "Priority": {
                    "select": {
                        "name": task.get("priority", "Medium")
                    }
                },
                "Time Slot": {
                    "rich_text": [
                        {
                            "text": {
                                "content": task.get("time_slot", "")
                            }
                        }
                    ]
                }
            }
        )

        print(f"[SUCCESS] Task pushed: {task.get('title')}")
