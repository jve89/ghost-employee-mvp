import imaplib
import email
from email.header import decode_header

IMAP_SERVER = 'imap.gmail.com'

def connect_to_mailbox(email_account, email_password):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(email_account, email_password)
    print("[INFO] Connected to mailbox.")
    return mail

def fetch_unseen_emails(mail):
    mail.select("inbox")
    status, messages = mail.search(None, 'UNSEEN')
    if status != "OK":
        print("[ERROR] Failed to search emails.")
        return []

    email_ids = messages[0].split()
    print(f"[INFO] {len(email_ids)} new emails found.")

    emails = []

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

                email_body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            email_body = part.get_payload(decode=True).decode()
                            break
                else:
                    email_body = msg.get_payload(decode=True).decode()

                from_address = email.utils.parseaddr(msg["From"])[1]

                emails.append({
                    'subject': subject,
                    'body': email_body,
                    'from': from_address
                })

    return emails
