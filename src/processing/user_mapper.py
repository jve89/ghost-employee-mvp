# /src/processing/user_mapper.py

USER_DIRECTORY = {
    "johan": {
        "name": "Johan van Erkel",
        "email": "youremail@example.com",
        "slack": "@johan",
        "notion_id": "5a2e3241-2f1d-4b8f-b44c-d63528c2ac1b"
    },
    "anna": {
        "name": "Anna",
        "email": "anna@example.com",
        "slack": "@anna"
    },
    "clara": {
        "name": "Clara",
        "email": "clara@example.com",
        "slack": "@clara"
    },
    "hr team": {
        "name": "HR Team",
        "email": "hr@example.com",
        "slack": "@hr"
    },
    "finance": {
        "name": "Finance Team",
        "email": "finance@example.com",
        "slack": "@finance"
    },
    "supervisor": {
        "name": "Supervisor",
        "email": "supervisor@example.com",
        "slack": "@supervisor"
    }
}


def resolve_assigned_user(raw_value):
    if not raw_value:
        return None

    key = raw_value.lower().strip()
    match = USER_DIRECTORY.get(key)

    if match:
        return match
    else:
        return {"name": raw_value}
