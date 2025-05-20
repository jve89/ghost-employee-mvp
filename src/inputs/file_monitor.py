from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os
import datetime
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

from ..outputs.email_sender import send_email
from ..processing.summary_analyser import analyse_summary
from ..processing.csv_analyser import analyse_csv
from ..processing.task_extractor import extract_tasks
from ..processing.structured_saver import save_structured_log
from ..processing.task_executor import execute_tasks_from_log  # ✅ Proper task executor

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

WATCHED_FOLDER = "watched"

class WatcherHandler(FileSystemEventHandler):
    def process_file(self, file_path):
        if not os.path.exists(file_path):
            print(f"[WARN] File no longer exists: {file_path}")
            return

        try:
            ext = os.path.splitext(file_path)[1].lower()

            if ext == '.txt':
                with open(file_path, 'r') as f:
                    content = f.read()

                if not content.strip():
                    print(f"[INFO] Skipping empty file: {file_path}")
                    return

                print(f"[INFO] Sending content of {file_path} to GPT...")
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that summarises documents."},
                        {"role": "user", "content": f"Summarise the following text:\n\n{content}"}
                    ],
                    max_tokens=300,
                    temperature=0.3,
                )

                summary = response.choices[0].message.content
                print(f"\n[SUMMARY for {file_path}]\n{summary}\n")

                # Step 1: Detect alerts
                alerts = analyse_summary(summary)
                if alerts:
                    print("[ALERTS TRIGGERED]")
                    for alert in alerts:
                        print("🚨", alert)
                    print("=" * 60)

                # Step 2: Extract tasks
                tasks = extract_tasks(summary)
                if tasks:
                    print("[TASKS IDENTIFIED]")
                    for task in tasks:
                        print("📝", task)
                    print("=" * 60)

                # Step 3: Email summary
                recipient = os.getenv("ALLOWED_SENDERS").split(",")[1].strip()
                print(f"[DEBUG] Sending email to {recipient}")
                send_email(
                    sender_email=os.getenv("EMAIL_ACCOUNT"),
                    sender_password=os.getenv("EMAIL_PASSWORD"),
                    recipient_email=recipient,
                    subject=f"Summary: {os.path.basename(file_path)}",
                    body=summary
                )

                # Step 4: Save structured data and execute tasks
                structured_log_path = save_structured_log(
                    file_path=file_path,
                    summary=summary,
                    tasks=tasks,
                    alerts=alerts
                )
                if structured_log_path:
                    execute_tasks_from_log(structured_log_path)

            elif ext == '.csv':
                print(f"[INFO] Analysing CSV file: {file_path}")
                alerts = analyse_csv(file_path)

                if alerts:
                    print("[CSV ALERTS TRIGGERED]")
                    for alert in alerts:
                        print("🚨", alert)
                    print("=" * 60)

                    recipient = os.getenv("ALLOWED_SENDERS").split(",")[1].strip()
                    print(f"[DEBUG] Sending CSV alert email to {recipient}")
                    send_email(
                        sender_email=os.getenv("EMAIL_ACCOUNT"),
                        sender_password=os.getenv("EMAIL_PASSWORD"),
                        recipient_email=recipient,
                        subject=f"CSV Alert: {os.path.basename(file_path)}",
                        body="\n".join(alerts)
                    )

                    # Step 4: Save structured data and execute tasks
                    structured_log_path = save_structured_log(
                        file_path=file_path,
                        summary=None,
                        tasks=None,
                        alerts=alerts
                    )
                    if structured_log_path:
                        execute_tasks_from_log(structured_log_path)
                else:
                    print("[INFO] No issues found in CSV.")

            else:
                print(f"[SKIPPED] Unsupported file type: {file_path}")

        except Exception as e:
            print(f"[ERROR] Failed to process {file_path}: {e}")

    def on_created(self, event):
        if not event.is_directory:
            print(f"[FILE CREATED] {event.src_path}")
            self.process_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            print(f"[FILE MODIFIED] {event.src_path}")
            self.process_file(event.src_path)

def start_file_monitor():
    if not os.path.exists(WATCHED_FOLDER):
        os.makedirs(WATCHED_FOLDER)

    event_handler = WatcherHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCHED_FOLDER, recursive=False)
    observer.start()
    print(f"[INFO] Watching folder: {WATCHED_FOLDER}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_file_monitor()
