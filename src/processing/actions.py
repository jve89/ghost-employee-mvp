import os
import time
import json
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

try:
    with open("slack_users.json", "r") as f:
        user_map = json.load(f)
except FileNotFoundError:
    user_map = {}

# Check if real execution is enabled
SLACK_TOKEN = os.getenv("SLACK_API_TOKEN")
REAL_EXECUTION = os.getenv("REAL_EXECUTION", "off") == "on"

slack_client = WebClient(token=SLACK_TOKEN)

try:
    with open("slack_channels.json", "r") as f:
        channel_map = json.load(f)
except FileNotFoundError:
    channel_map = {"general": "#general"}

# ✅ Real + Simulated actions

def send_slack_message(channel=None, recipient=None, message=None, **kwargs):
    target = channel or recipient or "general"
    slack_channel = channel_map.get(target.lower(), "#general-updates")

    # 🔁 Replace any @name with Slack ID
    for name, slack_id in user_map.items():
        message = message.replace(f"@{name}", slack_id)

    if REAL_EXECUTION and SLACK_TOKEN:
        try:
            response = slack_client.chat_postMessage(channel=slack_channel, text=message)
            print(f"[REAL SLACK] Sent to {slack_channel}: {message}")
            return response["ts"]
        except SlackApiError as e:
            print(f"[SLACK ERROR] {e.response['error']}")
            return "SLACK_FAILED"
    else:
        print(f"[SIMULATED SLACK] Sending to {slack_channel}: {message}")
        time.sleep(1)
        return "SIMULATED_SLACK_SENT"

def update_crm_case(case_id, note):
    if REAL_EXECUTION:
        print(f"[REAL] Updating CRM case {case_id} with note: {note}")
        # crm.update_case(case_id, note)
    else:
        print(f"[SIMULATED] CRM case {case_id} updated with note: {note}")
    time.sleep(1)
    return "CRM_CASE_UPDATED"

def create_calendar_event(title, time_slot):
    if REAL_EXECUTION:
        print(f"[REAL] Creating calendar event '{title}' at {time_slot}")
        # calendar.create_event(title, time_slot)
    else:
        print(f"[SIMULATED] Calendar event: {title} @ {time_slot}")
    time.sleep(1)
    return "CALENDAR_EVENT_CREATED"

def email_supervisor(subject, message):
    if REAL_EXECUTION:
        print(f"[REAL] Emailing supervisor: {subject} — {message}")
        # email.send(to="supervisor@example.com", subject=subject, body=message)
    else:
        print(f"[SIMULATED] Supervisor Email: {subject} — {message}")
    time.sleep(1)
    return "EMAIL_SUPERVISOR_SENT"

def fallback_action(description):
    print(f"[ACTION] Fallback for: {description}")
    time.sleep(1)
    return "FALLBACK_ACTION_TAKEN"

def create_jira_ticket(task_details):
    if REAL_EXECUTION:
        print(f"[REAL] Creating JIRA ticket: {task_details}")
        # jira.create_ticket(project="TEST", summary=task_details)
    else:
        print(f"[SIMULATED] JIRA ticket: {task_details}")
    time.sleep(1)
    return "JIRA_TICKET_CREATED"

def update_google_sheet(data):
    if REAL_EXECUTION:
        print(f"[REAL] Updating Google Sheet: {data}")
        # sheets.update(sheet_id, range, values)
    else:
        print(f"[SIMULATED] Google Sheet: {data}")
    time.sleep(1)
    return "GOOGLE_SHEET_UPDATED"

def assign_task_in_clickup(task_info):
    if REAL_EXECUTION:
        print(f"[REAL] Assigning ClickUp task: {task_info}")
        # clickup.assign_task(task_info)
    else:
        print(f"[SIMULATED] ClickUp task: {task_info}")
    time.sleep(1)
    return "CLICKUP_TASK_ASSIGNED"

def email_hr(subject, body):
    if REAL_EXECUTION:
        print(f"[REAL] Emailing HR: {subject} – {body}")
        # email.send(to="hr@example.com", subject=subject, body=body)
    else:
        print(f"[SIMULATED] HR Email: {subject} – {body}")
    time.sleep(1)
    return "EMAIL_HR_SENT"

def create_calendar_event_flexible(details):
    if REAL_EXECUTION:
        print(f"[REAL] Calendar (flex): {details}")
        # calendar.create_flexible(details)
    else:
        print(f"[SIMULATED] Calendar (flex): {details}")
    time.sleep(1)
    return "CALENDAR_EVENT_CREATED"
