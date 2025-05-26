from notion_client import Client
import os
from src.processing.user_mapper import resolve_assigned_user

notion = Client(auth=os.getenv("NOTION_TOKEN"))
NOTION_DB_ID = os.getenv("NOTION_DATABASE_ID")


def export_to_notion(task):
    """Wrapper for a single task (used by export_manager)."""
    return push_to_notion(NOTION_DB_ID, [task])


def push_to_notion(database_id, tasks):
    for task in tasks:
        assigned_user = resolve_assigned_user(task.get("assigned_to"))

        try:
            properties = {
                "Title": {
                    "title": [
                        {
                            "text": {"content": task.get("title", "Untitled Task")}
                        }
                    ]
                },
                "Description": {
                    "rich_text": [
                        {
                            "text": {"content": task.get("description", "")}
                        }
                    ]
                },
                "Due Date": {
                    "date": {"start": task.get("due_date")}
                } if task.get("due_date") else None,
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
                            "text": {"content": task.get("time_slot", "")}
                        }
                    ]
                },
                "Source File": {
                    "rich_text": [
                        {
                            "text": {"content": task.get("source_file", "")}
                        }
                    ]
                },
                "Time Slot Source": {
                    "rich_text": [
                        {
                            "text": {"content": task.get("time_slot_source", "")}
                        }
                    ] if task.get("time_slot_source") else []
                },
                "Confidence": {
                    "select": {
                        "name": task.get("time_slot_confidence")
                    } if task.get("time_slot_confidence") else None
                }
            }

            cleaned_properties = {k: v for k, v in properties.items() if v not in (None, [], {})}

            notion.pages.create(
                parent={"database_id": database_id},
                properties=cleaned_properties
            )
            print(f"[SUCCESS] Task pushed: {task.get('title', 'Untitled Task')}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to push task '{task.get('title', 'Untitled Task')}': {e}")
            return False
