import os
from slack_sdk import WebClient
from dotenv import load_dotenv

load_dotenv()
client = WebClient(token=os.getenv("SLACK_API_TOKEN"))

try:
    response = client.conversations_list()
    print("\n✅ Channels accessible by the bot:\n")
    for channel in response["channels"]:
        print(f"- {channel['name']} → ID: {channel['id']}")
except Exception as e:
    print(f"[ERROR] Could not list channels: {e}")
