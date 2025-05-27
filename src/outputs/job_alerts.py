import json
import os
import requests
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def load_alert_settings(config):
    return config.get("alerts", {})

def send_slack_alert(webhook, message):
    try:
        webhook_url = webhook or os.getenv("SLACK_WEBHOOK_URL")
        if not webhook_url:
            print("[ALERT] No webhook URL found")
            return
        requests.post(webhook_url, json={"text": message})
    except Exception as e:
        print(f"[ALERT] Slack failed: {e}")

def send_email_alert(recipient, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = "ghost@localhost"
        msg["To"] = recipient
        with smtplib.SMTP("localhost") as s:
            s.send_message(msg)
    except Exception as e:
        print(f"[ALERT] Email failed: {e}")

def maybe_alert_on_failure(config, failure_count, job_name):
    alerts = load_alert_settings(config)

    threshold = alerts.get("threshold", 1)
    if not alerts.get("on_failure", True):
        return

    if failure_count >= threshold:
        message = f"🚨 Job *{job_name}* failed {failure_count} times in a row!"

        slack_webhook = alerts.get("slack_webhook") or os.getenv("SLACK_WEBHOOK_URL")
        if slack_webhook:
            send_slack_alert(slack_webhook, message)

        if email := alerts.get("email"):
            send_email_alert(email, f"[Ghost Employee Alert] {job_name}", message)
