import time

# Existing actions
def send_slack_message(recipient, message):
    print(f"[ACTION] Sending Slack message to {recipient}: {message}")
    time.sleep(1)

def update_crm_case(case_id, note):
    print(f"[ACTION] Updating CRM case {case_id} with note: {note}")
    time.sleep(1)

def create_calendar_event(title, time_slot):
    print(f"[ACTION] Creating calendar event '{title}' at {time_slot}")
    time.sleep(1)

def email_supervisor(subject, message):
    print(f"[ACTION] Emailing supervisor: {subject} — {message}")
    time.sleep(1)

def fallback_action(description):
    print(f"[ACTION] Performing generic action: {description}")
    time.sleep(1)

# New actions for UX Layer
def create_jira_ticket(task_details):
    print(f"[ACTION] Creating JIRA ticket with details: {task_details}")
    time.sleep(1)
    return "JIRA_TICKET_CREATED"

def update_google_sheet(data):
    print(f"[ACTION] Updating Google Sheet with data: {data}")
    time.sleep(1)
    return "GOOGLE_SHEET_UPDATED"

def assign_task_in_clickup(task_info):
    print(f"[ACTION] Assigning task in ClickUp: {task_info}")
    time.sleep(1)
    return "CLICKUP_TASK_ASSIGNED"

def email_hr(subject, body):
    print(f"[ACTION] Emailing HR – Subject: {subject}, Body: {body}")
    time.sleep(1)
    return "EMAIL_HR_SENT"

def create_calendar_event_flexible(details):
    print(f"[ACTION] Creating calendar event with details: {details}")
    time.sleep(1)
    return "CALENDAR_EVENT_CREATED"
