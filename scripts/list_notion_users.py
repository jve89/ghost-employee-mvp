# scripts/list_notion_users.py

import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
notion = Client(auth=os.getenv("NOTION_TOKEN"))

users = notion.users.list()["results"]

for user in users:
    if user["type"] == "person":
        print(f"{user['name']} => {user['id']}")
