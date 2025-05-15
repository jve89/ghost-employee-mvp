import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465

def send_email(email_account, email_password, to_address, subject, body):
    try:
        msg = MIMEText(body)
        msg['From'] = email_account
        msg['To'] = to_address
        msg['Subject'] = f"Re: {subject}"

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(email_account, email_password)
            server.send_message(msg)

        print(f"[INFO] Sent reply to {to_address}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
