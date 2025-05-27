# test_slack.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()
webhook = os.getenv("SLACK_WEBHOOK_URL")
requests.post(webhook, json={"text": "✅ Test message from Ghost Employee"})
