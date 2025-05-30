import os
import time
from dotenv import load_dotenv
from src.inputs import email_listener
from src.processing import summary_analyser, task_extractor, structured_saver
from src.processing.task_executor import execute_tasks_from_log

load_dotenv()  # Load .env file

EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
POLL_INTERVAL = int(os.getenv("EMAIL_POLL_INTERVAL", "60"))  # seconds

def process_email(email_data):
    body = email_data['body']
    filename = f"email_{int(time.time())}.txt"
    filepath = os.path.join("watched", filename)

    # Save email body as a .txt file in watched folder (reuse existing pipeline)
    with open(filepath, "w") as f:
        f.write(body)

    print(f"[INFO] Saved email body to {filepath}")

    # Run your existing summarisation and task extraction pipeline on saved file
    summary, tasks = summary_analyser.summarise_file(filepath)
    structured_data = {
    "file": filepath,
    "processed_at": time.strftime("%Y%m%d_%H%M%S"),
    "summary": summary,
    "tasks": tasks,
    "alerts": [],  # you can extend alert detection here
    }

    # Save structured data to logs folder
    structured_saver.save_structured_log(structured_data)

    # Execute tasks (simulated or real)
    log_path = structured_saver.get_last_log_path()
    execute_tasks_from_log(log_path)

def main():
    mail = email_listener.connect_to_mailbox(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    print("[INFO] Starting email listener runner...")

    try:
        while True:
            emails = email_listener.fetch_unseen_emails(mail)
            if emails:
                print(f"[INFO] Processing {len(emails)} new emails...")
                for email_data in emails:
                    process_email(email_data)
            else:
                print("[INFO] No new emails found.")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("[INFO] Email listener runner stopped by user.")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

if __name__ == "__main__":
    main()
