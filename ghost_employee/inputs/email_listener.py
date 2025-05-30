import imaplib
import email
from email.header import decode_header
import os
import time
import datetime
from dotenv import load_dotenv
import json
from pathlib import Path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ghost_employee.ai_modules.structured_saver import save_structured_summary  # ✅ added

# Load environment variables
load_dotenv()

EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
ALLOWED_SENDERS = os.getenv("ALLOWED_SENDERS", "").split(",")
ATTACHMENT_RETENTION_DAYS = int(os.getenv("ATTACHMENT_RETENTION_DAYS", 30))
ENFORCE_WHITELIST = os.getenv("ENFORCE_WHITELIST", "True") == "True"

IMAP_SERVER = 'imap.gmail.com'
WATCHED_DIR = "watched"
ATTACHMENTS_DIR = os.path.join(WATCHED_DIR, "inbox", "attachments")

ALLOWED_ATTACHMENT_TYPES = {".txt", ".csv", ".docx", ".pdf", ".xlsx", ".json", ".xml", ".md"}


def connect_to_mailbox():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    print("[INFO] Connected to mailbox.")
    return mail


def clean_old_attachments():
    now = time.time()
    cutoff = now - (ATTACHMENT_RETENTION_DAYS * 86400)
    for filename in os.listdir(ATTACHMENTS_DIR):
        filepath = os.path.join(ATTACHMENTS_DIR, filename)
        if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff:
            os.remove(filepath)
            print(f"[CLEANUP] Deleted old file: {filename}")


def save_email_body(subject, body, sender):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_subject = subject.replace(" ", "_").replace("/", "-")
    filename = f"email_{timestamp}.txt"
    filepath = os.path.join(WATCHED_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"From: {sender}\nSubject: {subject}\n\n{body}")
    print(f"[SAVED] Email body saved as: {filename}")


def save_attachment(part, filename, sender, subject):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base, ext = os.path.splitext(filename)
    saved_filename = f"{base}_{timestamp}{ext}"
    save_path = os.path.join(ATTACHMENTS_DIR, saved_filename)

    with open(save_path, "wb") as f:
        f.write(part.get_payload(decode=True))

    # Save metadata
    metadata = {
        "sender": sender,
        "subject": subject,
        "original_filename": filename,
        "saved_as": saved_filename,
        "saved_to": ATTACHMENTS_DIR,
        "email_received_at": datetime.datetime.utcnow().isoformat()
    }

    metadata_filename = f"{base}_{timestamp}.json"
    metadata_path = os.path.join(ATTACHMENTS_DIR, metadata_filename)
    with open(metadata_path, "w", encoding="utf-8") as meta_file:
        json.dump(metadata, meta_file, indent=4)

    print(f"[ATTACHMENT] Saved: {saved_filename}")
    return True


def fetch_and_process_emails(mail):
    mail.select("inbox")
    status, messages = mail.search(None, 'UNSEEN')
    if status != "OK":
        print("[ERROR] Failed to search emails.")
        return

    email_ids = messages[0].split()
    print(f"[INFO] {len(email_ids)} new emails found.")

    for email_id in email_ids:
        res, msg_data = mail.fetch(email_id, "(RFC822)")
        if res != "OK":
            print("[ERROR] Failed to fetch email.")
            continue

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")

                from_address = email.utils.parseaddr(msg["From"])[1]

                if from_address not in ALLOWED_SENDERS:
                    print(f"[SKIPPED] Sender not allowed: {from_address}")
                    continue

                email_body = ""
                attachments_found = False

                if msg.is_multipart():
                    for part in msg.walk():
                        content_disposition = str(part.get("Content-Disposition", ""))
                        filename = part.get_filename()

                        if filename:
                            ext = Path(filename).suffix.lower()
                            if ext in ALLOWED_ATTACHMENT_TYPES:
                                attachments_found |= save_attachment(part, filename, from_address, subject)
                        elif part.get_content_type() == "text/plain" and "attachment" not in content_disposition:
                            email_body = part.get_payload(decode=True).decode(errors="ignore")
                else:
                    email_body = msg.get_payload(decode=True).decode(errors="ignore")

                if not attachments_found and email_body.strip():
                    save_email_body(subject, email_body, from_address)

                # ✅ Save structured summary + generate docx
                summary = f"Summary derived from email: {subject}"
                tasks = [f"Follow up on topic: {subject}"]
                alerts = [f"New message from {from_address}"]
                attachment_files = [f for f in os.listdir(ATTACHMENTS_DIR) if os.path.isfile(os.path.join(ATTACHMENTS_DIR, f))]

                save_structured_summary(
                    summary_data=summary,
                    tasks=tasks,
                    alerts=alerts,
                    attachments=attachment_files,
                    email_subject=subject,
                    email_from=from_address
                )

if __name__ == "__main__":
    os.makedirs(ATTACHMENTS_DIR, exist_ok=True)
    clean_old_attachments()

    mail = connect_to_mailbox()
    fetch_and_process_emails(mail)
    mail.logout()
