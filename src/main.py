from inputs.email_listener import connect_to_mailbox, fetch_unseen_emails
from processing.email_responder import generate_gpt_reply
from outputs.email_sender import send_email

from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

EMAIL_ACCOUNT = os.getenv('EMAIL_ACCOUNT')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SAFE_MODE = os.getenv('SAFE_MODE', 'on').lower() == 'on'

# Parse allowed senders as list
ALLOWED_SENDERS = [email.strip() for email in os.getenv('ALLOWED_SENDERS', '').split(',') if email.strip()]

def main():
    mail = connect_to_mailbox(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    emails = fetch_unseen_emails(mail)
    mail.logout()

    for email_data in emails:
        print(f"[EMAIL] Subject: {email_data['subject']}")
        print(f"[EMAIL] From: {email_data['from']}")
        print(f"[EMAIL] Body: {email_data['body'][:200]}...")

        if email_data['from'] not in ALLOWED_SENDERS:
            print(f"[INFO] Skipping email from {email_data['from']} (not in allowed senders).")
            continue

        reply = generate_gpt_reply(email_data['body'], OPENAI_API_KEY)
        print(f"[GPT REPLY]\n{reply}\n")

        if SAFE_MODE:
            print(f"[SAFE MODE] Reply not sent. Would have sent to: {email_data['from']}")
        else:
            send_email(EMAIL_ACCOUNT, EMAIL_PASSWORD, email_data['from'], email_data['subject'], reply)

if __name__ == "__main__":
    main()
