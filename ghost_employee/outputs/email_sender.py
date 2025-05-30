import os
import requests

def send_email(sender_email, sender_password, recipient_email, subject, body):
    api_key = os.getenv("MAILGUN_API_KEY")
    domain = os.getenv("MAILGUN_DOMAIN")
    sender = os.getenv("MAILGUN_FROM")  # e.g. Mailgun Sandbox <postmaster@yourdomain>

    if not api_key or not domain or not sender:
        print("[ERROR] Missing Mailgun credentials in .env")
        return

    url = f"https://api.mailgun.net/v3/{domain}/messages"
    auth = ("api", api_key)

    data = {
        "from": sender,
        "to": recipient_email,
        "subject": subject,
        "text": body
    }

    try:
        print(f"[DEBUG] Sending Mailgun API request to {recipient_email}...")
        response = requests.post(url, auth=auth, data=data)

        if response.status_code == 200:
            print(f"[EMAIL SENT] To: {recipient_email} | Subject: {subject}")
        else:
            print(f"[ERROR] Mailgun API failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"[ERROR] Exception while sending email: {type(e).__name__}: {e}")
