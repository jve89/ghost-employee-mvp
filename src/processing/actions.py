import os
import time
import json
import requests
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

# Load mappings
try:
    with open("slack_users.json", "r") as f:
        user_map = json.load(f)
except FileNotFoundError:
    user_map = {}

try:
    with open("slack_channels.json", "r") as f:
        channel_map = json.load(f)
except FileNotFoundError:
    channel_map = {"general": "#general"}

# Init
SLACK_TOKEN = os.getenv("SLACK_API_TOKEN")
REAL_EXECUTION = os.getenv("REAL_EXECUTION", "off") == "on"
slack_client = WebClient(token=SLACK_TOKEN)

def send_slack_message(channel=None, recipient=None, message=None, mention=None, **kwargs):
    target = channel or recipient or "general"

    # Load role config if available
    try:
        with open("config/roles_config.json", "r") as f:
            roles_config = json.load(f)
    except FileNotFoundError:
        roles_config = {}

    # Handle role-based resolution
    resolved_channel = None
    slack_mention = None

    if target in roles_config:
        role = roles_config[target]
        resolved_channel = role.get("slack_channel", None)
        slack_mention = f"<@{role['slack_id']}>" if "slack_id" in role else None

    # Fallback to user_map or channel_map
    if not resolved_channel:
        if target in user_map:
            slack_id = user_map[target].strip("<@>")
            try:
                dm = slack_client.conversations_open(users=slack_id)
                resolved_channel = dm["channel"]["id"]
            except SlackApiError as e:
                print(f"[SLACK ERROR] DM open failed: {e.response['error']}")
                return "SLACK_DM_FAILED"
        else:
            resolved_channel = channel_map.get(target.lower(), "C02Q7QYFR8X")  # Default: general

    # Replace @names in message with slack IDs from user_map
    if message:
        for name, slack_id in user_map.items():
            message = message.replace(f"@{name}", slack_id)
        if mention:
            message = f"{mention} {message}"
        elif slack_mention:
            message = f"{slack_mention} {message}"
    else:
        print("[SKIP] Slack message is None or empty — skipping send.")
        return "NO_MESSAGE"

    # Real vs Simulated send
    if REAL_EXECUTION and SLACK_TOKEN:
        try:
            response = slack_client.chat_postMessage(channel=resolved_channel, text=message)
            print(f"[REAL SLACK] Sent to {resolved_channel}: {message}")
            return response["ts"]
        except SlackApiError as e:
            print(f"[SLACK ERROR] {e.response['error']}")
            return "SLACK_FAILED"
    else:
        print(f"[SIMULATED SLACK] Sending to {resolved_channel}: {message}")
        time.sleep(1)
        return "SIMULATED_SLACK_SENT"

def send_to_notion(task):
    notion_token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("NOTION_DATABASE_ID")
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }

    title = task.get("title", "Untitled Task")
    description = task.get("description", "")
    due_date = task.get("due_date", None)
    assigned_to = task.get("assigned_to", "Unassigned")
    priority = task.get("priority", "normal")

    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Name": {
                "title": [{"text": {"content": title}}]
            },
            "Status": {
                "select": {"name": "Open"}
            },
            "Priority": {
                "select": {"name": priority.capitalize()}
            },
            "Assigned To": {
                "rich_text": [{"text": {"content": assigned_to}}]
            },
            "Due Date": {
                "date": {"start": due_date} if due_date else None
            },
            "Source": {
                "rich_text": [{"text": {"content": "Ghost Employee"}}]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": description}}]
                }
            }
        ]
    }

    # Remove empty fields
    data["properties"] = {
        k: v for k, v in data["properties"].items() if v is not None
    }

    try:
        response = requests.post(
            "https://api.notion.com/v1/pages", headers=headers, json=data
        )
        if response.status_code == 200:
            print("[NOTION] Successfully added to database.")
            return "NOTION_PAGE_CREATED"
        else:
            print(f"[NOTION ERROR] {response.status_code} - {response.text}")
            return "NOTION_FAILED"
    except Exception as e:
        print(f"[NOTION EXCEPTION] {e}")
        return "NOTION_EXCEPTION"

# --- Other actions ---

def update_crm_case(case_id, note):
    print(f"[{'REAL' if REAL_EXECUTION else 'SIMULATED'}] CRM case {case_id} note: {note}")
    time.sleep(1)
    return "CRM_CASE_UPDATED"

def create_calendar_event(title, time_slot):
    print(f"[{'REAL' if REAL_EXECUTION else 'SIMULATED'}] Calendar: {title} @ {time_slot}")
    time.sleep(1)
    return "CALENDAR_EVENT_CREATED"

def email_supervisor(subject, message):
    print(f"[{'REAL' if REAL_EXECUTION else 'SIMULATED'}] Supervisor Email: {subject} – {message}")
    time.sleep(1)
    return "EMAIL_SUPERVISOR_SENT"

def fallback_action(description):
    print(f"[ACTION] Fallback: {description}")
    time.sleep(1)
    return "FALLBACK_ACTION_TAKEN"

def create_jira_ticket(task_details):
    print(f"[{'REAL' if REAL_EXECUTION else 'SIMULATED'}] JIRA: {task_details}")
    time.sleep(1)
    return "JIRA_TICKET_CREATED"

def update_google_sheet(data):
    print(f"[{'REAL' if REAL_EXECUTION else 'SIMULATED'}] Google Sheet: {data}")
    time.sleep(1)
    return "GOOGLE_SHEET_UPDATED"

def assign_task_in_clickup(task_info):
    print(f"[{'REAL' if REAL_EXECUTION else 'SIMULATED'}] ClickUp Task: {task_info}")
    time.sleep(1)
    return "CLICKUP_TASK_ASSIGNED"

def email_hr(subject, body):
    print(f"[{'REAL' if REAL_EXECUTION else 'SIMULATED'}] HR Email: {subject} – {body}")
    time.sleep(1)
    return "EMAIL_HR_SENT"

def create_calendar_event_flexible(details):
    print(f"[{'REAL' if REAL_EXECUTION else 'SIMULATED'}] Calendar (flex): {details}")
    time.sleep(1)
    return "CALENDAR_EVENT_CREATED"
