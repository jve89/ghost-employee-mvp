from slack_sdk import WebClient
import os
from dotenv import load_dotenv

load_dotenv()

client = WebClient(token=os.getenv("SLACK_API_TOKEN"))

try:
    response = client.chat_postMessage(
        channel="#general",  # Replace with "#aviation" or "#random" if needed
        text="✅ Ghost Employee test message: Slack integration works!"
    )
    print("Message sent successfully:", response["ts"])
except Exception as e:
    print("Slack API error:", e)
