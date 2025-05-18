from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os
import datetime
from openai import OpenAI
from dotenv import load_dotenv
from ..outputs.email_sender import send_email
from ..processing.summary_analyser import analyse_summary

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

WATCHED_FOLDER = "watched"
LOGS_FOLDER = "logs"

class WatcherHandler(FileSystemEventHandler):
    def process_file(self, file_path):
        if not os.path.exists(file_path):
            print(f"[WARN] File no longer exists: {file_path}")
            return

        try:
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

            # Analyse the summary for trigger phrases
            alerts = analyse_summary(summary)
            if alerts:
                print("[ALERTS TRIGGERED]")
                for alert in alerts:
                    print("🚨", alert)
                print("=" * 60)

            # Send summary via email
            recipient = os.getenv("ALLOWED_SENDERS").split(",")[1].strip()
            print(f"[DEBUG] Sending email to {recipient}")
            send_email(
                sender_email=os.getenv("EMAIL_ACCOUNT"),
                sender_password=os.getenv("EMAIL_PASSWORD"),
                recipient_email=recipient,
                subject=f"Summary: {os.path.basename(file_path)}",
                body=summary
            )

            # Save summary to logs folder
            if not os.path.exists(LOGS_FOLDER):
                os.makedirs(LOGS_FOLDER)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"{LOGS_FOLDER}/summary_{timestamp}.txt"

            with open(log_filename, "w") as log_file:
                log_file.write(f"File: {file_path}\n")
                log_file.write(f"Summary generated at: {timestamp}\n\n")
                log_file.write(summary)

            print(f"[LOG SAVED] Summary written to {log_filename}")

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
