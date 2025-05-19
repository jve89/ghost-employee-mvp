import os
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LOGS_FOLDER = "logs"

class LogEventHandler(FileSystemEventHandler):
    def process_log(self, path):
        if path.endswith(".txt"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n🕒 [{timestamp}] 📥 [LOG WATCHER] New or updated file: {path}\n")
            try:
                with open(path, "r") as f:
                    content = f.read()
                print("📄 [SUMMARY FILE CONTENT]:\n")
                print(content)
                print("\n" + "=" * 100 + "\n")
            except Exception as e:
                print(f"[ERROR] Could not read log file: {e}")

    def on_created(self, event):
        if not event.is_directory:
            self.process_log(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.process_log(event.src_path)

def start_log_watcher():
    if not os.path.exists(LOGS_FOLDER):
        os.makedirs(LOGS_FOLDER)

    event_handler = LogEventHandler()
    observer = Observer()
    observer.schedule(event_handler, LOGS_FOLDER, recursive=False)
    observer.start()
    print(f"✅ [LOG WATCHER STARTED] Monitoring folder: '{LOGS_FOLDER}' for .txt logs...\n(Press Ctrl+C to stop)\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_log_watcher()
